/**
 * @OnlyCurrentDoc
 * Helper functions shared across multiple scripts.
 */

/**
 * Writes data to a specified Google Sheet tab.
 * Handles clearing existing content, writing new values, and optional column formatting.
 * 
 * @param {GoogleAppsScript.Spreadsheet.Spreadsheet} ss - The active Spreadsheet object.
 * @param {string} sheetName - The name of the tab to write to.
 * @param {Array<Array<any>>} data - The array of arrays to write.
 * @param {Object} [options] - Optional settings.
 * @param {number} [options.formatColumn] - 1-based index of column to format (default: null).
 * @param {boolean} [options.isCurrency] - If true, formats as currency "$#,##0.00", else "0.00" (default: false).
 */
function writeToSheet(ss, sheetName, data, options = {}) {
    let sheet = ss.getSheetByName(sheetName);

    if (!sheet) {
        sheet = ss.insertSheet(sheetName);
    }

    if (data.length > 0) {
        const numRows = data.length;
        const numCols = data[0].length;

        sheet.clearContents();

        // Write data
        sheet.getRange(1, 1, numRows, numCols).setValues(data);

        // Apply formatting if requested
        if (options.formatColumn && numRows > 1) {
            // Apply to all rows except header (assumes header is row 1)
            const formatRange = sheet.getRange(2, options.formatColumn, numRows - 1, 1);
            if (options.isCurrency) {
                formatRange.setNumberFormat("$#,##0.00");
            } else {
                formatRange.setNumberFormat("0.00");
            }
        }
    }
}

/**
 * Reads a specific cell value by searching for a key in one column and returning 
 * the value from a different column on the same row.
 * 
 * @param {GoogleAppsScript.Spreadsheet.Spreadsheet} ss - The active Spreadsheet object.
 * @param {string} sheetName - The name of the sheet to search.
 * @param {string|number} key - The value to search for in the key column.
 * @param {string} keyColumnHeader - The header name of the column to search in.
 * @param {string} valueColumnHeader - The header name of the column to return value from.
 * @returns {any} The found value, or null if key or columns not found.
 */
function getCellValue(ss, sheetName, key, keyColumnHeader, valueColumnHeader) {
    const sheet = ss.getSheetByName(sheetName);
    if (!sheet) {
        Logger.log(`Sheet not found: ${sheetName}`);
        return null;
    }

    const range = sheet.getDataRange();
    const values = range.getValues();
    if (values.length === 0) return null;

    const headers = values[0];
    const keyColIndex = headers.indexOf(keyColumnHeader);
    const valueColIndex = headers.indexOf(valueColumnHeader);

    if (keyColIndex === -1 || valueColIndex === -1) {
        Logger.log(`Required columns not found in '${sheetName}'. Check headers: ${keyColumnHeader}, ${valueColumnHeader}`);
        return null;
    }

    // Search for the key (skipping header)
    for (let i = 1; i < values.length; i++) {
        if (values[i][keyColIndex] === key) {
            return values[i][valueColIndex];
        }
    }

    return null;
}
