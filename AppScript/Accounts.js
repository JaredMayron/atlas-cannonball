/**
 * @OnlyCurrentDoc
 * Fetches and categorizes Pocketsmith accounts, then writes two separate tables 
 * to two different tabs in the active spreadsheet.
 */
function fetchAndCategorizeAccounts() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();

  // Define sheet names
  const CATEGORIZED_SHEET_NAME = 'Account Categorization';
  const GROUPED_SHEET_NAME = 'Accounts By Type';

  // --- Secure Parameter Retrieval ---
  const properties = PropertiesService.getScriptProperties();
  const API_KEY = properties.getProperty('POCKETSMITH_API_KEY');
  const USER_ID = properties.getProperty('POCKETSMITH_USER_ID');

  if (!API_KEY || !USER_ID) {
    throw new Error("POCKETSMITH_API_KEY or USER_ID not found in script properties.");
  }

  // --- API Call ---
  const url = `https://api.pocketsmith.com/v2/users/${USER_ID}/accounts`;
  const options = {
    'method': 'get',
    'headers': {
      'Accept': 'application/json',
      'X-Developer-Key': API_KEY
    },
    'muteHttpExceptions': true
  };

  try {
    const response = UrlFetchApp.fetch(url, options);
    const responseCode = response.getResponseCode();
    if (responseCode !== 200) {
      throw new Error(`API Request Failed with Status: ${responseCode}. Response: ${response.getContentText()}`);
    }
    const jsonData = JSON.parse(response.getContentText());

    // 1. Get raw data with categorization as an Array of Objects
    const categorizedDataObjects = categorizeData(jsonData);

    // 2. Write the raw categorized list to its sheet
    const categorizedDataArray = convertObjectsToArrays(categorizedDataObjects);
    writeToSheet(ss, CATEGORIZED_SHEET_NAME, categorizedDataArray, { formatColumn: 2, isCurrency: false });

    // ----------------------------------------------------
    // 3. Group the Data (Replicating the M-code Table.Group)
    // ----------------------------------------------------
    const dataRows = categorizedDataObjects.slice(1); // Pass only the data rows (exclude the header)
    const groupedDataArray = groupAndSumBalances(dataRows);

    // 4. Write GROUPED Data to the "Accounts By Type" tab
    writeToSheet(ss, GROUPED_SHEET_NAME, groupedDataArray, { formatColumn: 2, isCurrency: false });

    Logger.log('Finished updating both categorized and grouped data sheets.');

  } catch (e) {
    Logger.log('Error fetching or processing Pocketsmith data: ' + e.message);
    throw e;
  }
}

// ----------------------------------------------------------------------------------
// HELPER FUNCTIONS FOR ACCOUNTS.GS
// (These can be kept in the same file or moved to a separate 'Helpers.gs' file)
// ----------------------------------------------------------------------------------

/**
 * Categorizes and prepares the raw data as an array of objects.
 */
function categorizeData(jsonData) {
  const properties = PropertiesService.getScriptProperties();

  // Account Lists (Scrubbed - Set via Script Properties)
  const CASH_TITLES = (properties.getProperty('CASH_TITLES') || "").toUpperCase().split(',').map(s => s.trim()).filter(s => s !== "");
  const INVESTMENT_TITLES = (properties.getProperty('INVESTMENT_TITLES') || "").toUpperCase().split(',').map(s => s.trim()).filter(s => s !== "");
  const CAR_IDENTIFIER = (properties.getProperty('CAR_IDENTIFIER') || "").toUpperCase();
  const CONDO_IDENTIFIER = (properties.getProperty('CONDO_IDENTIFIER') || "").toUpperCase();

  // Add Header Object for consistency (optional, but good practice)
  const data = [{ Title: "Title", Balance: "Balance", Type: "Type" }];

  jsonData.forEach(record => {
    const title = record.title || '';
    let balance = (record.current_balance || 0); // Apply the 100x fix
    let type = '';
    const titleUpper = title.toUpperCase();

    // Categorization Logic
    if (type === '' && CASH_TITLES.length > 0 && CASH_TITLES.includes(titleUpper)) {
      type = "Cash";
    } else if (type === '' && INVESTMENT_TITLES.length > 0 && INVESTMENT_TITLES.includes(titleUpper)) {
      type = "Investment";
    } else if (type === '' && CAR_IDENTIFIER !== "" && titleUpper.includes(CAR_IDENTIFIER)) {
      type = "Car";
    } else if (type === '' && CONDO_IDENTIFIER !== "" && titleUpper === CONDO_IDENTIFIER) {
      type = "Condo";
    }

    data.push({
      Title: title,
      Balance: balance,
      Type: type
    });
  });

  return data;
}

/**
 * Converts an array of objects into a 2D array (Array of Arrays) for setValues().
 * @param {Array<Object>} objects - Array of objects with consistent keys.
 * @returns {Array<Array<any>>} 2D array including header row.
 */
function convertObjectsToArrays(objects) {
  if (!objects || objects.length === 0) return [[]];

  // Assumes the first object is the header (keys)
  const header = Object.keys(objects[0]);

  // Create the final array starting with the header
  const array2D = [header];

  // Map the remaining objects (data rows) to arrays
  for (let i = 1; i < objects.length; i++) {
    const row = header.map(key => objects[i][key]);
    array2D.push(row);
  }
  return array2D;
}