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
