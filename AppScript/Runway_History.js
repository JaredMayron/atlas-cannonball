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
    let runwayDays = getCellValue(ss, 'Runway', RUNWAY_DAYS_METRIC, 'Metric', 'Value');
    // Sanitize if string
    if (typeof runwayDays === 'string') {
      runwayDays = Number(runwayDays.replace(/[^0-9.-]+/g, ""));
    }

    if (typeof runwayDays !== 'number' || runwayDays === null || isNaN(runwayDays)) {
      throw new Error(`Could not find a valid number for '${RUNWAY_DAYS_METRIC}' on the 'Runway' sheet.`);
    }

    // 1b. Get Last Until Date (as a date string)
    // Note: getCellValue returns the raw value, which for the date will be a string/date object.
    const lastUntilDateString = getCellValue(ss, 'Runway', LAST_UNTIL_METRIC, 'Metric', 'Value');
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
    writeToSheet(ss, HISTORY_SHEET_NAME, finalSortedData);

    // Formatting: Col 1 (Snapshot Date) and Col 3 (Runway Date) as dates. Col 2 (Days) as number.
    if (finalSortedData.length > 1) {
      // Column A (Snapshot Date)
      historySheet.getRange(2, 1, finalSortedData.length - 1, 1).setNumberFormat("yyyy-MM-dd");
      // Column C (Last Until Date)
      historySheet.getRange(2, 3, finalSortedData.length - 1, 1).setNumberFormat("yyyy-MM-dd");
      // Column B (Runway Days)
      historySheet.getRange(2, 2, finalSortedData.length - 1, 1).setNumberFormat("0");
    }

    Logger.log('Runway History sheet updated with Days and Date.');

  } catch (e) {
    Logger.log('Error updating runway history: ' + e.message);
    Browser.msgBox('Runway History Update Failed', e.message, Browser.Buttons.OK);
  }
}
