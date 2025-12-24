/**
 * Replicates the M-code Table.Group operation: groups records by 'Type' 
 * and sums the 'Balance' for each group.
 * * @param {Array<Object>} dataRows - Array of data objects (EXCLUDING HEADER).
 * @returns {Array<Array<any>>} A sorted array of arrays (table format) ready for sheet writing (INCLUDES HEADER).
 */
function groupAndSumBalances(dataRows) {
  
  // 1. Grouping and Summing (Replicates Table.Group)
  const groupedData = {};

  dataRows.forEach(row => {
    const type = row.Type || 'Uncategorized'; // Handle null/empty types gracefully
    const balance = row.Balance || 0; 

    if (groupedData[type]) {
      groupedData[type] += balance;
    } else {
      groupedData[type] = balance;
    }
  });

  // 2. Convert Map to Array 
  
  // Prepare output array with header
  const finalTable = [
    ["Type", "Balance"] 
  ];

  for (const type in groupedData) {
    if (groupedData.hasOwnProperty(type)) {
      finalTable.push([
        type, 
        groupedData[type]
      ]);
    }
  }

  // 3. Sorting (Replicates Table.Sort)
  // Sort the data rows (starting from index 1) by the 'Type' column (index 0)
  const dataForSorting = finalTable.slice(1);

  dataForSorting.sort((a, b) => {
    const typeA = a[0] === null ? '' : a[0].toUpperCase();
    const typeB = b[0] === null ? '' : b[0].toUpperCase();
    
    if (typeA < typeB) { return -1; }
    if (typeA > typeB) { return 1; }
    return 0;
  });
  
  // Recombine header and sorted data and apply currency formatting
  const header = finalTable[0];
  const outputArray = [header, ...dataForSorting];
  
  return outputArray;
}

/**
 * Writes the final data array to the specified Google Sheet tab.
 * (Keeping this separate for maximum re-use by all API-fetching scripts)
 * @param {GoogleAppsScript.Spreadsheet.Spreadsheet} ss - The active Spreadsheet object.
 * @param {string} sheetName - The name of the tab to write to.
 * @param {Array<Array<any>>} data - The array of arrays to write.
 */
function writeToSheet(ss, sheetName, data) {
  let sheet = ss.getSheetByName(sheetName);

  if (!sheet) {
    sheet = ss.insertSheet(sheetName);
  }

  if (data.length > 0) {
    const numRows = data.length;
    const numCols = data[0].length;
    
    sheet.clearContents(); 
    
    sheet.getRange(1, 1, numRows, numCols).setValues(data);
    
    // Apply number formatting to the Balance column (Column B)
    if (numRows > 1) { // Only apply if there is data beyond the header
        sheet.getRange(2, 2, numRows - 1, 1).setNumberFormat("$#,##0.00");
    }
  }
}