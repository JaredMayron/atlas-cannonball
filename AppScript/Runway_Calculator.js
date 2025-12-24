/**
 * @OnlyCurrentDoc
 * Calculates the financial runway (in days and years) based on Cash on Hand 
 * and Grand Total Mandatory Spend.
 * Requires: The 'Accounts By Type' and 'Mandatory Spending' sheets to exist.
 * * FIX: Assumes Burn_Rate (Grand Total Mandatory Spend) is read as a POSITIVE cost.
 */
function calculateRunway() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const RUNWAY_SHEET_NAME = 'Runway';
  
  try {
    // --- 1. READ INPUT DATA ---
    
    // Get Cash_On_Hand from 'Accounts By Type'
    const cashOnHand = getCellValueRC(ss, 'Accounts By Type', 'Cash', 'Type', 'Balance');
    
    // Get Burn_Rate from 'Mandatory Spending'
    const burnRate = getCellValueRC(ss, 'Mandatory Spending', 'Grand Total Mandatory Spend', 'Expense Category', 'Estimated Annual Spend');

    if (typeof cashOnHand !== 'number' || typeof burnRate !== 'number' || burnRate <= 0) {
        // If burnRate is zero or negative, we cannot calculate a runway, or the input is wrong.
        throw new Error(`Invalid input data. Cash: ${cashOnHand}, Burn Rate: ${burnRate}. Ensure Cash is positive and Burn Rate is positive.`);
    }

    // --- 2. CALCULATIONS (Porting M-code logic) ---
    
    // Burn_Rate is now treated as a positive cost.
    const runwayYears = cashOnHand / burnRate;

    // M-code: Runway_Days = Number.Round(365 * Runway_Years,0)
    const runwayDays = Math.round(365 * runwayYears);
    
    // M-code: Last Until = Date.AddDays(Date.From(DateTime.LocalNow()),Runway_Days)
    const lastUntilDate = new Date();
    // Use the current time (Dec 16, 2025) as the starting point for the calculation
    lastUntilDate.setDate(lastUntilDate.getDate() + runwayDays);

    // Format the date for the table output
    const lastUntilFormatted = Utilities.formatDate(lastUntilDate, ss.getSpreadsheetTimeZone(), "yyyy-MM-dd");

    // --- 3. ASSEMBLE OUTPUT TABLE ---
    
    // M-code: Runway_Table = #table({"Metric", "Value"}, { ... })
    const runwayTable = [
      ["Metric", "Value"],
      ["Runway (Days)", runwayDays],
      ["Runway (Years)", runwayYears.toFixed(1)], // Number.Round(Runway_Years, 1)
      ["Last Until", lastUntilFormatted]
    ];

    // --- 4. WRITE TO SHEET ---
    writeToSheetRC(ss, RUNWAY_SHEET_NAME, runwayTable);
    
    Logger.log('Runway calculation complete.');

  } catch (e) {
    Logger.log('Error calculating runway: ' + e.message);
    // Use the spreadsheet's message box for immediate user feedback on failure
    Browser.msgBox('Runway Calculation Failed', e.message, Browser.Buttons.OK);
  }
}

// =========================================================================
// HELPER FUNCTION: getCellValueRC (Reads data from other sheets)
// =========================================================================

/**
 * Reads a specific cell value by searching for a key in one column and returning 
 * the value from a different column on the same row.
 */
function getCellValueRC(ss, sheetName, key, keyColumnHeader, valueColumnHeader) {
  const sheet = ss.getSheetByName(sheetName);
  if (!sheet) {
    throw new Error(`Sheet not found: ${sheetName}`);
  }

  const range = sheet.getDataRange();
  const values = range.getValues();
  const headers = values[0]; // Assuming header is in the first row

  // Find column indices
  const keyColIndex = headers.indexOf(keyColumnHeader);
  const valueColIndex = headers.indexOf(valueColumnHeader);

  if (keyColIndex === -1 || valueColIndex === -1) {
    throw new Error(`Required columns not found in '${sheetName}'. Check headers: ${keyColumnHeader}, ${valueColumnHeader}`);
  }

  // Search for the key and return the corresponding value
  for (let i = 1; i < values.length; i++) {
    if (values[i][keyColIndex] === key) {
      const value = values[i][valueColIndex];
      // Attempt to convert to number, handling formatted currency strings
      if (typeof value === 'string') {
        // We use Math.abs() to ensure the result is positive, aligning with the "positive burn rate" requirement
        const cleanedValue = value.replace(/[^0-9.-]+/g, ""); 
        const num = Math.abs(Number(cleanedValue)); 
        return isNaN(num) ? null : num;
      }
      // If the value is a number, return its absolute value
      return typeof value === 'number' ? Math.abs(value) : null;
    }
  }

  throw new Error(`Key '${key}' not found in column '${keyColumnHeader}' on sheet '${sheetName}'.`);
}


// =========================================================================
// GENERIC HELPER FUNCTION: writeToSheetRC (Included for self-contained testing)
// =========================================================================

/**
 * Writes the final data array to the specified Google Sheet tab.
 */
function writeToSheetRC(ss, sheetName, data, options = {}) {
  let sheet = ss.getSheetByName(sheetName);
  if (!sheet) { sheet = ss.insertSheet(sheetName); }
  if (data.length > 0) {
    const numRows = data.length;
    const numCols = data[0].length;
    sheet.clearContents(); 
    sheet.getRange(1, 1, numRows, numCols).setValues(data);
    
    // Apply formatting to the second column (Column B) if specified
    if (options.formatColumn && numRows > 1) {
        const formatRange = sheet.getRange(2, options.formatColumn, numRows - 1, 1);
        if (options.isCurrency) { formatRange.setNumberFormat("$#,##0.00"); } 
        else { formatRange.setNumberFormat("0.00"); }
    }
  }
}