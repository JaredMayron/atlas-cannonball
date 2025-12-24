/**
 * @OnlyCurrentDoc
 * Appends a daily snapshot of the calculated "Runway (Days)" and 
 * "Last Until" date to the 'Runway History' sheet for historical tracking.
 * Requires: The 'Runway' sheet to exist and contain both metrics.
 */
function updateRunwayHistory() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const HISTORY_SHEET_NAME = 'Runway History';
  
  // Metrics to retrieve from the 'Runway' sheet
  const RUNWAY_DAYS_METRIC = 'Runway (Days)'; 
  const LAST_UNTIL_METRIC = 'Last Until';

  try {
    // --- 1. GET INPUT DATA ---
    
    // 1a. Get Runway Days (as a number)
    const runwayDays = getCellValueRH(ss, 'Runway', RUNWAY_DAYS_METRIC, 'Metric', 'Value');
    if (typeof runwayDays !== 'number' || runwayDays === null) {
      throw new Error(`Could not find a valid number for '${RUNWAY_DAYS_METRIC}' on the 'Runway' sheet.`);
    }

    // 1b. Get Last Until Date (as a date string)
    // Note: getCellValueRH returns the raw value, which for the date will be a string/date object.
    const lastUntilDateString = getCellValueRH(ss, 'Runway', LAST_UNTIL_METRIC, 'Metric', 'Value');
    if (!lastUntilDateString) {
      throw new Error(`Could not find a valid value for '${LAST_UNTIL_METRIC}' on the 'Runway' sheet.`);
    }

    // --- 2. PREPARE NEW ROW ---
    
    // Get the current date (Date of the snapshot)
    const snapshotDate = new Date();
    const formattedSnapshotDate = Utilities.formatDate(snapshotDate, ss.getSpreadsheetTimeZone(), "yyyy-MM-dd");

    // The new row to append: [Snapshot Date, Runway Days (Number), Last Until Date (String)]
    const newHistoryRow = [formattedSnapshotDate, Math.round(runwayDays), lastUntilDateString]; 

    // --- 3. READ EXISTING HISTORY ---
    let historySheet = ss.getSheetByName(HISTORY_SHEET_NAME);
    let existingData = [];
    
    // Updated Header to include both metrics
    const NEW_HEADER = ["Date", RUNWAY_DAYS_METRIC, LAST_UNTIL_METRIC];
    
    if (!historySheet) {
        historySheet = ss.insertSheet(HISTORY_SHEET_NAME);
        existingData = [NEW_HEADER]; 
    } else {
        const range = historySheet.getDataRange();
        if (range.getNumRows() > 0) {
            existingData = range.getValues();
            // Optional: Check if header matches, if not, adjust/warn. 
            // For now, assume a 3-column structure is needed.
        } else {
            existingData = [NEW_HEADER]; 
        }
    }
    
    // --- 4. APPEND, CLEAN, AND SORT (Deduplication Logic Re-used) ---
    
    const headerRow = existingData.shift(); 
    let historyRows = existingData;
    
    // Append the new row 
    historyRows.push(newHistoryRow);

    // 4a. Remove Duplicates (Logic from previous step, prioritizing the latest entry)
    const uniqueDates = {};
    const finalHistory = [headerRow]; 
    
    for (let i = historyRows.length - 1; i >= 0; i--) {
        const row = historyRows[i];
        let dateValue = row[0];
        let dateKey;
        
        // Ensure all date keys are standardized for deduplication
        if (dateValue instanceof Date) {
            dateKey = Utilities.formatDate(dateValue, ss.getSpreadsheetTimeZone(), "yyyy-MM-dd");
        } else if (typeof dateValue === 'string') {
            dateKey = dateValue;
        } else {
            continue;
        }

        if (!uniqueDates[dateKey]) {
            uniqueDates[dateKey] = true;
            finalHistory.push(row);
        }
    }
    
    // 4b. Final Sort (By Date, Descending)
    const dataForSort = finalHistory.slice(1);
    dataForSort.sort((a, b) => new Date(b[0]).getTime() - new Date(a[0]).getTime());
    
    const finalSortedData = [headerRow, ...dataForSort];

    // --- 5. WRITE FINAL HISTORY TO SHEET ---
    writeToSheetRH(ss, HISTORY_SHEET_NAME, finalSortedData);

    // Formatting: Col 1 (Snapshot Date) and Col 3 (Runway Date) as dates. Col 2 (Days) as number.
    if (finalSortedData.length > 1) {
        // Column A (Snapshot Date)
        historySheet.getRange(2, 1, finalSortedData.length - 1, 1).setNumberFormat("yyyy-MM-dd"); 
        // Column C (Last Until Date)
        historySheet.getRange(2, 3, finalSortedData.length - 1, 1).setNumberFormat("yyyy-MM-dd"); 
        // Column B (Runway Days)
        historySheet.getRange(2, 2, finalSortedData.length - 1, 1).setNumberFormat("#,##0"); 
    }
    
    Logger.log('Runway History sheet updated with Days and Date.');

  } catch (e) {
    Logger.log('Error updating runway history: ' + e.message);
    Browser.msgBox('Runway History Update Failed', e.message, Browser.Buttons.OK);
  }
}

// =========================================================================
// HELPER FUNCTION: getCellValueRH (Reads data from other sheets)
// (Function logic remains the same, handles both number and string return values)
// =========================================================================
function getCellValueRH(ss, sheetName, key, keyColumnHeader, valueColumnHeader) {
  const sheet = ss.getSheetByName(sheetName);
  if (!sheet) {
    throw new Error(`Sheet not found: ${sheetName}`);
  }

  const range = sheet.getDataRange();
  const values = range.getValues();
  const headers = values[0]; 

  const keyColIndex = headers.indexOf(keyColumnHeader);
  const valueColIndex = headers.indexOf(valueColumnHeader);

  if (keyColIndex === -1 || valueColIndex === -1) {
    throw new Error(`Required columns not found in '${sheetName}'. Check headers: ${keyColumnHeader}, ${valueColumnHeader}`);
  }

  for (let i = 1; i < values.length; i++) {
    if (values[i][keyColIndex] === key) {
      const value = values[i][valueColIndex];
      // For numerical metrics, convert string currency to number
      if (key === 'Runway (Days)' || key === 'Runway (Years)') {
        if (typeof value === 'string') {
          const cleanedValue = value.replace(/[^0-9.-]+/g, ""); 
          const num = Number(cleanedValue);
          return isNaN(num) ? null : num;
        }
        return typeof value === 'number' ? value : null;
      }
      // For date metrics, return the raw value (Date object or string)
      return value;
    }
  }

  return null; 
}


// =========================================================================
// GENERIC HELPER FUNCTION: writeToSheetRH
// =========================================================================
function writeToSheetRH(ss, sheetName, data, options = {}) {
  let sheet = ss.getSheetByName(sheetName);
  if (!sheet) { sheet = ss.insertSheet(sheetName); }
  if (data.length > 0) {
    const numRows = data.length;
    const numCols = data[0].length;
    sheet.clearContents(); 
    sheet.getRange(1, 1, numRows, numCols).setValues(data);
    
    if (options.formatColumn && numRows > 1) {
        const formatRange = sheet.getRange(2, options.formatColumn, numRows - 1, 1);
        if (options.isCurrency) { formatRange.setNumberFormat("$#,##0.00"); } 
        else { formatRange.setNumberFormat("0.00"); }
    }
  }
}