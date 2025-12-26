/**
 * @OnlyCurrentDoc
 * FINAL PRODUCTION VERSION: Fetches mandatory spending using the Pocketsmith transactions endpoint, 
 * calculates the grand total mandatory spend, and writes the results to the 'Mandatory Spending' sheet.
 * Includes pagination logic for full data retrieval.
 */
function fetchMandatorySpending() {
  const ss = SpreadsheetApp.getActiveSpreadsheet(); 
  const SHEET_NAME = 'Mandatory Spending';
  
  // --- Secure Parameter Retrieval ---
  const properties = PropertiesService.getScriptProperties();
  const API_KEY = properties.getProperty('POCKETSMITH_API_KEY');
  const USER_ID = properties.getProperty('POCKETSMITH_USER_ID');
  if (!API_KEY || !USER_ID) { throw new Error("Authentication keys not found."); }

  // --- 1. CONFIGURATION & DATE CALCULATION ---
  const yesterday = new Date();
  yesterday.setDate(yesterday.getDate() - 1);
  const YESTERDAY_DATE = Utilities.formatDate(yesterday, ss.getSpreadsheetTimeZone(), "yyyy-MM-dd");

  const oneYearBeforeYesterday = new Date(yesterday);
  oneYearBeforeYesterday.setFullYear(oneYearBeforeYesterday.getFullYear() - 1);
  const ONE_YEAR_BEFORE_YESTERDAY_DATE = Utilities.formatDate(oneYearBeforeYesterday, ss.getSpreadsheetTimeZone(), "yyyy-MM-dd");

  // Mandatory expense categories (Case-Sensitive)
  const API_CALCULATED_CATEGORIES = [
    "Mortgages", "Homeowners Association", "Auto Insurance", 
    "Healthcare & Medical", "Car", "Utilities", 
    "Dues and Subscriptions", "State Tax", 
    "Yearly Subscriptions", "Fees & Charges", "Hair", 
    "Gas & Fuel", "Education", "Tax Preparation"
  ];
  
  // Manual estimates (Restored to original non-zero values)
  const MANUAL_ESTIMATES = [
    ["Groceries Estimate", 4,364.28],
    ["Restaurant Estimate", 8,710.92],
    ["Health Insurance Estimate", 6500.00]
  ];

  // Base URL for the paginated fetch
  const baseUrl = `https://api.pocketsmith.com/v2/users/${USER_ID}/transactions?` +
              `start_date=${ONE_YEAR_BEFORE_YESTERDAY_DATE}&` +
              `end_date=${YESTERDAY_DATE}&` +
              `uncategorised=0&` +
              `type=debit`;
  
  // --- 2. PAGINATED DATA RETRIEVAL ---
  try {
    const allTransactionRecords = fetchPaginatedTransactions(baseUrl, API_KEY);
    
    if (allTransactionRecords.length === 0) {
        Logger.log("No transactions found in the specified range and filters. Writing manual estimates only.");
        // If no transactions, still calculate totals based on 0 API spend
        const emptyApiSpendingRow = ["Pocketsmith Mandatory Spend (API Calculated)", 0.00];
        writeFinalTable(ss, SHEET_NAME, emptyApiSpendingRow, MANUAL_ESTIMATES);
        return; 
    }

    // --- 3. DATA TRANSFORMATION & CALCULATION ---
    let apiSubtotal = 0;    
    
    allTransactionRecords.forEach(transaction => {
        const categoryTitle = transaction.category?.title || "Uncategorized";
        const categoryUpper = categoryTitle.toUpperCase();
        
        // Amount is 1x (dollars)
        const amount = transaction.amount || 0; 
        
        // FilterAPIOnlyCategories (Exact Match)
        if (API_CALCULATED_CATEGORIES.includes(categoryTitle)) {
            
            // FilterOutGroceries (Case-Insensitive check)
            if (!categoryUpper.includes("GROCERIES")) {
                apiSubtotal += amount; 
            }
        }
    });
    
    // 4. FINAL CALCULATIONS
    const apiSpendingTotal = apiSubtotal; 
    const apiSpendingRow = ["Pocketsmith Mandatory Spend (API Calculated)", -apiSpendingTotal];

    // 5. Write results to the Google Sheet
    writeFinalTable(ss, SHEET_NAME, apiSpendingRow, MANUAL_ESTIMATES);
    
    Logger.log('Mandatory Spending sheet successfully updated.');

  } catch (e) {
    Logger.log('Error in fetchMandatorySpending: ' + e.message);
    throw e; 
  }
}

// =========================================================================
// PAGINATION HELPER FUNCTION
// =========================================================================

/**
 * Executes a loop to fetch all pages of transactions from the Pocketsmith API.
 */
function fetchPaginatedTransactions(baseUrl, API_KEY) {
    let allTransactions = [];
    let page = 1; 
    let hasMorePages = true;
    
    const options = { 
        'method': 'get', 
        'headers': { 
            'Accept': 'application/json', 
            'X-Developer-Key': API_KEY 
        }, 
        'muteHttpExceptions': true 
    };
    
    while (hasMorePages) {
        const url = `${baseUrl}&page=${page}`;
        Logger.log(`Fetching page: ${page}`);
        
        try {
            const response = UrlFetchApp.fetch(url, options);
            if (response.getResponseCode() !== 200) {
                Logger.log(`API call failed on page ${page} with status: ${response.getResponseCode()}`);
                break;
            }
            
            const transactions = JSON.parse(response.getContentText());
            
            if (transactions.length === 0) {
                hasMorePages = false;
            } else {
                allTransactions = allTransactions.concat(transactions);
                page++;
            }
        } catch (e) {
            Logger.log('Error during paginated fetch: ' + e.message);
            hasMorePages = false;
        }
    }
    
    return allTransactions;
}

// =========================================================================
// OUTPUT ASSEMBLY HELPER FUNCTION
// =========================================================================

/**
 * Assembles and writes the final table, including API-derived and manual rows.
 */
function writeFinalTable(ss, sheetName, apiRow, manualRows) {
    
    let grandTotalAmount = apiRow[1]; 
    manualRows.forEach(row => { grandTotalAmount += row[1]; });

    const grandTotalRows = [
        ["Grand Total Mandatory Spend", grandTotalAmount],
        ["Total Mandatory Spend (Daily)", grandTotalAmount / 365],
        ["Total Mandatory Spend (2 Months)", grandTotalAmount / 6]
    ];

    const finalTable = [
      ["Expense Category", "Estimated Annual Spend"], 
      apiRow,
      ...manualRows,
      ...grandTotalRows
    ];

    writeToSheetMS(ss, sheetName, finalTable, {formatColumn: 2, isCurrency: true});
}

// =========================================================================
// GENERIC HELPER FUNCTION
// =========================================================================

function writeToSheetMS(ss, sheetName, data, options = {}) {
  let sheet = ss.getSheetByName(sheetName);
  if (!sheet) { sheet = ss.insertSheet(sheetName); }
  if (data.length > 0) {
    const numRows = data.length;
    const numCols = data[0].length;
    sheet.clearContents(); 
    sheet.getRange(1, 1, numRows, numCols).setValues(data);
    if (options.formatColumn && numRows > 1) {
        const formatRange = sheet.getRange(2, options.formatColumn, numRows - 1, 1);
        if (options.isCurrency) { formatRange.setNumberFormat("0.00"); } 
        else { formatRange.setNumberFormat("0.00"); }
    }
  }
}