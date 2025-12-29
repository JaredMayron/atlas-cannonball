/**
 * Main function to run all data updates and calculations.
 * This is the only function you should assign a time-based trigger to.
 */
function runAllDataRefresh() {
  Logger.log("--- Starting Daily Data Refresh ---");
  
  // 1. Fetch and process Accounts data
  fetchAndCategorizeAccounts(); 

  // 2. Fetch and process Mandatory Spending data
  fetchMandatorySpending();
  
  // 3. Perform final derived calculations
  calculateRunway()

  // 4. Update History
  updateRunwayHistory()
  
  Logger.log("--- Refresh Complete ---");
}