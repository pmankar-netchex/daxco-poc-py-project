#!/usr/bin/env python3
"""
Test script for the SQL server connection and employee data fetching.
This script attempts to connect to the SQL server and fetch employee data.
"""

import os
import sys
import logging
from helper_functions.db_utils import check_db_config

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the database testing functions
from helper_functions.fetch_employees import test_connection, fetch_employees

def main():
    # Check if DB environment variables are set
    if not check_db_config():
        return
    
    # Call the test_connection function with a test company ID
    company_id = 4287  # Company ID for the test
    logging.info(f"Attempting to test connection for company_id={company_id}")
    
    # Test the connection with a simple query
    basic_employees = test_connection(company_id)
    
    if not basic_employees:
        logging.error("Connection test failed. Cannot continue with further tests.")
        return
    
    logging.info("Connection test successful. Testing full employee data fetch...")
    
    # Test the full employee data fetch
    employees = fetch_employees(company_id)
    
    if employees:
        logging.info(f"Successfully fetched {len(employees)} detailed employee records")
        # Display the first employee as a sample
        if len(employees) > 0:
            logging.info("Sample employee record:")
            for key, value in employees[0].items():
                logging.info(f"  {key}: {value}")
    else:
        logging.warning(f"No detailed employee data fetched for company_id={company_id}")
    
if __name__ == "__main__":
    main()
