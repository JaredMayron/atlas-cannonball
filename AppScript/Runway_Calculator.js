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
    const cashRaw = getCellValue(ss, 'Accounts By Type', 'Cash', 'Type', 'Balance');
    const cashOnHand = parseAsPositiveNumber(cashRaw); // Ensure positive

    // Get Burn_Rate from 'Mandatory Spending'
    const burnRaw = getCellValue(ss, 'Mandatory Spending', 'Grand Total Mandatory Spend', 'Expense Category', 'Estimated Annual Spend');
    const burnRate = parseAsPositiveNumber(burnRaw); // Ensure positive

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
    writeToSheet(ss, RUNWAY_SHEET_NAME, runwayTable);

    Logger.log('Runway calculation complete.');

  } catch (e) {
    Logger.log('Error calculating runway: ' + e.message);
    // Use the spreadsheet's message box for immediate user feedback on failure
    Browser.msgBox('Runway Calculation Failed', e.message, Browser.Buttons.OK);
  }
}


/**
 * Local helper to ensure values are treated as positive numbers (magnitude).
 * Handles currency strings and converts to absolute number.
 */
function parseAsPositiveNumber(value) {
  if (value === null || value === undefined) return null;

  if (typeof value === 'string') {
    const cleanedValue = value.replace(/[^0-9.-]+/g, "");
    const num = Math.abs(Number(cleanedValue));
    return isNaN(num) ? null : num;
  }

  return typeof value === 'number' ? Math.abs(value) : null;
}