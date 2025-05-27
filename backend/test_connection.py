import pyodbc
import os
from dotenv import load_dotenv

load_dotenv()

def test_connection():
    conn_str = (
        f"DRIVER={{FreeTDS}};"
        f"SERVER={os.getenv('DB_SERVER')};"
        f"DATABASE={os.getenv('DB_NAME')};"
        f"UID={os.getenv('DB_USERNAME')};"
        f"PWD={os.getenv('DB_PASSWORD')};"
        f"TDS_Version=7.3;"
    )
    
    try:
        print("Attempting to connect to the database...")
        conn = pyodbc.connect(conn_str)
        print("Successfully connected to the database!")
        
        cursor = conn.cursor()
        cursor.execute("SELECT @@version")
        row = cursor.fetchone()
        print(f"\nSQL Server version:\n{row[0]}")
        
        conn.close()
        print("\nConnection test completed successfully!")
        return True
    except pyodbc.Error as e:
        print(f"\nError connecting to database:")
        print(f"Error message: {str(e)}")
        return False

if __name__ == "__main__":
    test_connection()
