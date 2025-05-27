import os
import platform
import logging
import urllib.parse
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_db_config():
    """
    Get database configuration from environment variables.
    Returns:
        dict: A dictionary containing database connection parameters.
    """
    default_driver = "ODBC Driver 17 for SQL Server"
    # if platform.machine().lower() in ['arm64', 'aarch64']:
    #     default_driver = "FreeTDS"
    #     logging.info(f"ARM64 architecture detected, using {default_driver} as default driver")
    driver = os.getenv("DB_DRIVER", default_driver)
    logging.info(f"Using database driver: {driver}")
    return {
        "server": os.getenv("DB_SERVER", "localhost"),
        "database": os.getenv("DB_NAME", "HRPremier"),
        "username": os.getenv("DB_USERNAME"),
        "password": os.getenv("DB_PASSWORD"),
        "driver": driver,
        "connect_timeout": int(os.getenv("DB_CONNECT_TIMEOUT", "30")),
        "query_timeout": int(os.getenv("DB_QUERY_TIMEOUT", "30")),
        "max_retries": int(os.getenv("DB_MAX_RETRIES", "3")),
        "retry_delay": int(os.getenv("DB_RETRY_DELAY", "5"))
    }

def get_connection_string():
    """
    Generate a connection string using environment variables.
    Returns:
        str: A formatted connection string for pyodbc.
    """
    config = get_db_config()
    if not all([config["username"], config["password"], config["server"]]):
        logging.error("Missing required database connection parameters")
        return None
    
    password = config["password"]
    # For SQL Server, the proper timeout parameter is just "Timeout", not "Connection Timeout"
    connection_string = (
        f"DRIVER={{{config['driver']}}};"
        f"SERVER={config['server']};"
        f"DATABASE={config['database']};"
        f"UID={config['username']};"
        f"PWD={password};"
        f"Timeout={config['connect_timeout']};"
    )
    return connection_string

def check_db_config():
    """
    Check if all required database environment variables are set.
    Returns:
        bool: True if all required variables are set, False otherwise
    """
    # required_vars = ["DB_SERVER", "DB_NAME", "DB_USERNAME", "DB_PASSWORD"]
    # missing_vars = [var for var in required_vars if not os.getenv(var)]
    # if missing_vars:
    #     logging.warning("Database connection parameters not fully configured in .env file")
    #     logging.info("Please ensure the following environment variables are set:")
    #     for var in missing_vars:
    #         logging.info(f"  {var}")
    #     return False
    return True

def connect_with_retry(connection_string):
    """
    Attempt to connect to the database with retry logic
    
    Args:
        connection_string (str): The connection string to use
        
    Returns:
        Connection object if successful, None otherwise
        
    Raises:
        RuntimeError: If connection fails after all retries
    """
    import pyodbc
    
    config = get_db_config()
    max_retries = config['max_retries']
    retry_delay = config['retry_delay']
    
    # Mask password in the connection string for logging
    masked_conn_string = connection_string
    if config["password"]:
        masked_conn_string = connection_string.replace(config["password"], "********")
    
    logging.info(f"Connecting to database with timeout: {config['connect_timeout']} seconds")
    logging.info(f"Using driver: {config['driver']}")
    logging.debug(f"Connection string (masked): {masked_conn_string}")
    
    for attempt in range(1, max_retries + 1):
        try:
            logging.info(f"Database connection attempt {attempt} of {max_retries}")
            
            # Log more information about the driver and connection
            drivers = [x for x in pyodbc.drivers()]
            logging.info(f"Available ODBC drivers: {drivers}")
            
            conn = pyodbc.connect(connection_string)
            logging.info("Database connection successful")
            return conn
        except pyodbc.Error as e:
            error_message = str(e)
            error_code = ''
            if hasattr(e, 'args') and len(e.args) > 0:
                error_code = e.args[0]
            
            logging.warning(f"Connection attempt {attempt} failed with code {error_code}: {error_message}")
            
            # Log possible solutions based on error
            if 'timeout' in error_message.lower():
                logging.info("Connection timeout may be due to:")
                logging.info("1. Database server is unreachable or behind firewall")
                logging.info("2. Server is overloaded")
                logging.info("3. Network connectivity issues")
            elif 'login' in error_message.lower():
                logging.info("Login failure may be due to:")
                logging.info("1. Incorrect username or password")
                logging.info("2. Account is locked or disabled")
                logging.info("3. SQL Server authentication is not enabled")
            
            if attempt < max_retries:
                logging.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logging.error(f"Failed to connect after {max_retries} attempts")
                raise RuntimeError(f"Database connection failed after {max_retries} attempts: {error_message}")
