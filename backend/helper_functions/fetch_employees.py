import logging
import os

# Initialize pyodbc as None
pyodbc = None

# Import packages with error handling
try:
    import pyodbc
except ImportError:
    logging.error("pyodbc package not installed. Please install it with pip install pyodbc")
    
try:
    from dotenv import load_dotenv
except ImportError:
    logging.error("python-dotenv package not installed. Please install it with pip install python-dotenv")
    def load_dotenv():
        logging.warning("load_dotenv function is a placeholder because python-dotenv is not installed")
        return None
        
try:
    from .db_utils import get_db_config, get_connection_string, check_db_config, connect_with_retry
    from .sql_queries import FETCH_EMPLOYEES_QUERY, TEST_CONNECTION_QUERY
except ImportError as e:
    logging.error(f"Error importing required modules: {str(e)}")
    # Define placeholders if imports fail
    def get_db_config():
        return {}
    def get_connection_string():
        return None
    def check_db_config():
        return False
    def connect_with_retry(connection_string):
        return None
    FETCH_EMPLOYEES_QUERY = ""
    TEST_CONNECTION_QUERY = ""

def test_connection(company_id):
    """
    Tests connection to the HRPremier SQL Server database using a simple query.
    
    This function connects to the SQL Server database and retrieves basic employee data
    to verify that the connection works correctly.
    
    Args:
        company_id (str or int): The unique identifier for the company
        environment (str, optional): Environment setting (used to determine which DB config to use)
        
    Returns:
        list[dict]: A list of basic employee data records or empty list if connection fails
    """
    # Check if required packages are available
    if pyodbc is None:
        error_msg = "Cannot test connection: pyodbc package is not installed"
        logging.error(error_msg)
        raise RuntimeError(error_msg)
    try:
        # Use new db_utils helpers
        if not check_db_config():
            raise RuntimeError("Database connection parameters not fully configured")
        connection_string = get_connection_string()
        if not connection_string:
            raise RuntimeError("Failed to generate connection string")
        logging.info(f"Testing connection to database using connection string (password masked)")
        # Use the new retry logic for connection
        with connect_with_retry(connection_string) as conn:
            with conn.cursor() as cursor:
                cursor.execute(TEST_CONNECTION_QUERY, [company_id])
                columns = [column[0] for column in cursor.description]
                employees = [dict(zip(columns, row)) for row in cursor.fetchmany(5)]
                logging.info(f"Connection test successful. Retrieved {len(employees)} employee records for company_id={company_id}")
                return employees
    except pyodbc.Error as e:
        error_msg = f"Database error occurred during connection test: {str(e)}"
        logging.error(error_msg)
        raise RuntimeError(error_msg)
    except Exception as e:
        error_msg = f"Error testing connection: {str(e)}"
        logging.error(error_msg)
        raise RuntimeError(error_msg)

def fetch_employees(company_id):
    """
    Fetches employee data from the HRPremier SQL Server database.
    
    This function connects to the SQL Server database and retrieves employee 
    information including earnings and deductions data.
    
    Args:
        company_id (str or int): The unique identifier for the company
        environment (str, optional): Environment setting (used to determine which DB config to use)
        
    Returns:
        list[dict]: A list of employee dictionaries with their earnings and deductions
        
    Notes:
        This function uses a connection to the SQL Server database.
        Make sure the database connection parameters are properly set in the environment variables.
    """
    logging.info(f"fetch_employees called with company_id={company_id}")
    
    # Check if required packages are available
    if pyodbc is None:
        error_msg = "Cannot fetch employees: pyodbc package is not installed"
        logging.error(error_msg)
        raise RuntimeError(error_msg)
    try:
        if not check_db_config():
            raise RuntimeError("Database connection parameters not fully configured")
        connection_string = get_connection_string()
        if not connection_string:
            raise RuntimeError("Failed to generate connection string")
        masked_connection = connection_string.replace(os.getenv('DB_PASSWORD', ''), '********')
        logging.debug(f"Connection string: {masked_connection}")
        logging.debug(f"Attempting to connect to database with driver: {get_db_config().get('driver')}")
        
        # Use the new retry logic for connection
        with connect_with_retry(connection_string) as conn:
            with conn.cursor() as cursor:
                logging.debug(f"Executing SQL query: {FETCH_EMPLOYEES_QUERY} with parameter: {company_id}")
                # Set query timeout through the execute method instead of cursor.timeout
                cursor.execute(FETCH_EMPLOYEES_QUERY, [company_id])
                columns = [column[0] for column in cursor.description]
                logging.debug(f"Retrieved columns: {columns}")
                employees = [dict(zip(columns, row)) for row in cursor.fetchall()]
                # if employees:
                #     logging.info("=== Retrieved Employee Data ===")
                #     logging.info(f"Total employees found: {len(employees)}")
                #     logging.info("Column names from database:")
                #     logging.info(f"{', '.join(columns)}")
                #     logging.info("\nFirst 5 employees:")
                #     for idx, emp in enumerate(employees[:5]):
                #         logging.info(f"\nEmployee {idx + 1}:")
                #         for key, value in emp.items():
                #             logging.info(f"{key}: {value}")
                    
                    # Check for duplicate names
                #     name_count = {}
                #     for emp in employees:
                #         full_name = f"{emp.get('first_name', '')} {emp.get('last_name', '')}"
                #         name_count[full_name] = name_count.get(full_name, 0) + 1
                    
                #     duplicates = {name: count for name, count in name_count.items() if count > 1}
                #     if duplicates:
                #         logging.info("\n=== Duplicate Names Found ===")
                #         for name, count in duplicates.items():
                #             logging.info(f"{name}: {count} occurrences")
                #             # Print details of employees with duplicate names
                #             logging.info("Details of employees with this name:")
                            
                #             for emp in employees:
                #                 if f"{emp.get('first_name', '')} {emp.get('last_name', '')}" == name:
                #                     logging.info(f"Employee ID: {emp.get('employee_id', 'N/A')}, "
                #                                f"First Name: {emp.get('first_name', 'N/A')}, "
                #                                f"Last Name: {emp.get('last_name', 'N/A')}")
                # else:
                #     logging.warning(f"No employee records found for company_id={company_id}")
                # logging.info(f"Successfully fetched {len(employees)} employee records for company_id={company_id}")
                # return employees
        return employees
    except pyodbc.Error as e:
        error_msg = f"Database error occurred: {str(e)}"
        logging.error(error_msg)
        raise RuntimeError(error_msg)
    except Exception as e:
        error_msg = f"Error fetching employees: {str(e)}"
        logging.error(error_msg)
        import traceback
        logging.error(f"Stack trace: {traceback.format_exc()}")
        raise RuntimeError(error_msg)