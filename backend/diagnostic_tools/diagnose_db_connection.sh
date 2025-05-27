#!/bin/bash

# Database Connection Diagnostic Script
# This script helps diagnose SQL Server connection issues

# ---------- Environment Setup ----------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARENT_DIR="$(dirname "$SCRIPT_DIR")"

# Source .env file if it exists
if [ -f "$PARENT_DIR/.env" ]; then
  echo "Loading environment variables from .env file..."
  export $(grep -v '^#' $PARENT_DIR/.env | xargs)
else
  echo "No .env file found at $PARENT_DIR/.env"
  exit 1
fi

# ---------- Display Configuration ----------
echo "========================================="
echo "SQL Server Connection Diagnostic Tool"
echo "========================================="
echo "Date: $(date)"
echo "Host OS: $(uname -a)"
echo "Python Version: $(python3 --version)"

# ---------- Check Environment Variables ----------
echo
echo "Checking environment variables:"
echo "----------------------------------------"

# Required variables
REQUIRED_VARS=("DB_SERVER" "DB_NAME" "DB_USERNAME" "DB_PASSWORD" "DB_DRIVER")
MISSING_VARS=0

for VAR in "${REQUIRED_VARS[@]}"; do
  if [ -z "${!VAR}" ]; then
    echo "❌ $VAR is not set"
    MISSING_VARS=$((MISSING_VARS + 1))
  else
    if [ "$VAR" = "DB_PASSWORD" ]; then
      echo "✅ $VAR is set (value hidden)"
    else
      echo "✅ $VAR is set to: ${!VAR}"
    fi
  fi
done

if [ $MISSING_VARS -gt 0 ]; then
  echo "⚠️  $MISSING_VARS required variables are missing!"
else
  echo "✅ All required variables are set"
fi

# ---------- Check Network Connectivity ----------
echo
echo "Checking network connectivity:"
echo "----------------------------------------"

# Extract server and port (assuming format SERVER,PORT or just SERVER)
if [[ "$DB_SERVER" == *,* ]]; then
  SERVER=$(echo $DB_SERVER | cut -d',' -f1)
  PORT=$(echo $DB_SERVER | cut -d',' -f2)
else
  SERVER=$DB_SERVER
  PORT=1433  # Default SQL Server port
fi

# Ping test
echo "Trying to ping $SERVER..."
if ping -c 3 $SERVER > /dev/null 2>&1; then
  echo "✅ Ping to $SERVER successful"
else
  echo "❌ Cannot ping $SERVER"
fi

# Port test using nc (netcat) if available
echo "Checking if port $PORT is open on $SERVER..."
if command -v nc > /dev/null; then
  if nc -z -w 5 $SERVER $PORT; then
    echo "✅ Port $PORT is open on $SERVER"
  else
    echo "❌ Port $PORT is not reachable on $SERVER"
  fi
else
  echo "⚠️  'nc' command not available, skipping port check"
fi

# ---------- Check ODBC Driver ----------
echo
echo "Checking ODBC drivers:"
echo "----------------------------------------"

# Check if odbcinst exists
if command -v odbcinst > /dev/null; then
  echo "ODBC drivers installed on this system:"
  odbcinst -q -d | sed 's/\[//g' | sed 's/\]//g'
  
  # Check if our driver is listed
  if odbcinst -q -d | grep -i "$DB_DRIVER" > /dev/null; then
    echo "✅ Driver '$DB_DRIVER' is installed"
  else
    echo "❌ Driver '$DB_DRIVER' is NOT installed"
  fi
else
  echo "⚠️  odbcinst command not found, cannot list ODBC drivers"
  
  # On macOS, check for specific drivers in known locations
  if [ "$(uname)" = "Darwin" ]; then
    echo "Checking for ODBC drivers in known locations on macOS..."
    if [ -d "/usr/local/lib/libtdsodbc.so" ]; then
      echo "✅ FreeTDS ODBC driver found"
    fi
    if [ -d "/opt/microsoft/msodbcsql17" ]; then
      echo "✅ Microsoft ODBC Driver 17 for SQL Server found"
    fi
  fi
fi

# ---------- Test Python Connection ----------
echo
echo "Testing Python connection to the database:"
echo "----------------------------------------"

# Create a temporary Python script to test connection
TMP_SCRIPT=$(mktemp)
cat > $TMP_SCRIPT << 'EOF'
import os
import sys
import time

try:
    import pyodbc
    print("✅ pyodbc is installed")
except ImportError:
    print("❌ pyodbc is not installed")
    sys.exit(1)

# Get connection parameters from environment
server = os.environ.get('DB_SERVER')
database = os.environ.get('DB_NAME')
username = os.environ.get('DB_USERNAME')
password = os.environ.get('DB_PASSWORD')
driver = os.environ.get('DB_DRIVER')

# Form connection string
conn_str = f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};UID={username};PWD={password};Timeout=30;"

# Try to connect
print(f"Attempting connection with driver: {driver}")
print(f"Server: {server}, Database: {database}")

start_time = time.time()
try:
    print("Connecting to database...")
    with pyodbc.connect(conn_str) as conn:
        print(f"✅ Connected successfully in {time.time() - start_time:.2f} seconds")
        
        # Get server info
        cursor = conn.cursor()
        cursor.execute("SELECT @@version")
        version = cursor.fetchone()[0]
        print(f"SQL Server Version: {version}")
        
        # Check if we can run a simple query
        print("Testing simple query...")
        cursor.execute("SELECT 1 AS test")
        result = cursor.fetchone()
        print(f"Query result: {result[0]}")
        
except pyodbc.Error as e:
    print(f"❌ Connection failed after {time.time() - start_time:.2f} seconds")
    print(f"Error: {e}")
    
    # More detailed error information
    if hasattr(e, 'args'):
        print("\nDetailed error information:")
        for i, arg in enumerate(e.args):
            print(f"  Arg {i}: {arg}")
    
    # Suggest fixes for common issues
    if "timeout" in str(e).lower():
        print("\nPossible solutions for timeout issues:")
        print("1. Verify the server is running and accessible from this network")
        print("2. Check if there's a firewall blocking the connection")
        print("3. Increase the connection timeout value")
    elif "login" in str(e).lower():
        print("\nPossible solutions for login issues:")
        print("1. Verify username and password are correct")
        print("2. Check that the user has access to the database")
        print("3. Ensure SQL authentication is enabled on the server")
    elif "driver" in str(e).lower():
        print("\nPossible solutions for driver issues:")
        print("1. Verify the ODBC driver is correctly installed")
        print("2. Check that the driver name matches exactly what's installed")
        print("3. On MacOS, ensure you've installed the correct architecture version")
EOF

# Run the Python test script
echo "Running Python connection test..."
python3 $TMP_SCRIPT

# Clean up temporary file
rm $TMP_SCRIPT

# ---------- Summary ----------
echo
echo "========================================="
echo "Diagnostic Summary"
echo "========================================="
echo "This information can help you troubleshoot connection issues."
echo "Common solutions:"
echo "1. Verify the SQL Server is running and accepting connections"
echo "2. Check that the firewall allows connections from this machine"
echo "3. Verify the ODBC driver is correctly installed for your OS"
echo "4. Ensure the connection string is correctly formatted"
echo
echo "For FreeTDS issues on macOS/Linux, check your freetds.conf file"
echo "For Microsoft ODBC driver issues, verify the installation was successful"
echo "========================================="
