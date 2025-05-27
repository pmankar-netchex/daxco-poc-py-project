# Payroll Integration App (Daxco)

**Note:** All commands below assume you are in the `backend` directory.

## Project Structure

- `main.py`: Main FastAPI application with all endpoints. Now includes detailed comments and docstrings for each endpoint and core logic.
- `helper_functions/`: Directory containing helper modules for data fetching, transformation, and validation. Each module is documented with docstrings and inline comments.
- `requirements.txt`: Python dependencies for the project.
- `Dockerfile`: Docker configuration to containerize the app.
- `integration_config.yml`: Configuration for integration settings.
- `example_validate.json`: Example output from the `/webhook` endpoint, used for validation and download endpoints.
- `README.md`: Project documentation (this file).

## Integration Flow Overview

1. **CSV Upload**: The `/webhook` endpoint accepts a CSV file upload, validates the integration type/provider, and runs the file through a configurable pipeline of transformation stages (see `integration_config.yml`).
2. **Transformation**: The uploaded file is parsed and transformed using helper functions (e.g., `daxco_transformation`).
3. **Validation**: The `/validate` endpoint is a placeholder that would normally check the transformed data against employee records and payroll rules, but this functionality is currently disabled.
4. **Download**: The `/download` endpoint returns the validated data as a downloadable CSV file.

## Helper Functions

- All helper functions are located in the `helper_functions/` directory and are imported via `helper_functions/__init__.py`.
- Key helpers:
  - `fetch_employees`: *Currently disabled*. Previously fetched employee data from SQL Server database.
  - `daxco_transformation`: Transforms uploaded CSV data into a structured format.
  - `validate_transformation`: Validates transformed data against business rules and employee records.
  - `OUTPUT_COLUMNS`: Defines the output CSV column order.
- Each helper module is documented with docstrings and inline comments for clarity.

## Database Configuration

For SQL Server connectivity, the following environment variables need to be set:

```
DB_SERVER=your_server_address
DB_NAME=HRPremier
DB_USERNAME=your_username
DB_PASSWORD=your_password
DB_DRIVER=ODBC Driver 17 for SQL Server
```

Note: The database connection is currently disabled, but the above configuration would be needed if it is re-enabled.

You'll need to install the SQL Server ODBC driver for your platform:
- Windows: Microsoft ODBC Driver for SQL Server
- macOS: `brew install freetds unixodbc`
- Linux (Ubuntu/Debian): `apt-get install unixodbc-dev freetds-dev tdsodbc`

## Output Format

The application now uses the following output format:

1. **Employee ID** - Netchex Employee Code, Social Security Number, or Clock Sequence Number
2. **Gross to Net Code** - Values:
   - 1 for Earnings Code
   - 3 for Employee Deduction Amount
   - 4 for Employer Deduction Amount
3. **Type Code** - Any Valid Netchex Earnings Code or Fixed Amount Deduction Code
   - Examples: REG, BON, FB, MED
4. **Hours or Amount** - Hours or Amount value
5. **Temporary Rate** - Used if you have a Temporary Rate Earnings Code; otherwise, ignored
6. **Distributed Dept Code** - Department to Distribute to. If blank, the employee's home department is used
   - Examples: 000, 001, PRL

A sample output file is provided in `sample_output.csv`.

## Extending the System

- To add a new integration or provider, update `integration_config.yml` with the new stages and reference the appropriate helper functions.
- To add new transformation or validation logic, create a new helper module in `helper_functions/` and register it in `main.py`'s `FUNCTION_REGISTRY`.
- All new functions should include docstrings and comments for maintainability.

## Sample Input File

The `/webhook` endpoint expects a CSV file as input. You can use your own or create a sample `input_format.csv` in the `backend` directory. Example:

```
first_name,last_name,email
John,Doe,john.doe@example.com
Jane,Smith,jane.smith@example.com
```

## Build and Run with Docker

```sh
docker build -t daxco-payroll-backend .
docker run -p 8000:8000 daxco-payroll-backend
```

## Local Development

```sh
pip install -r requirements.txt
uvicorn main:app --reload
```

## API Endpoints

### 1. Incoming Webhook (Transform & Validate)

```
curl -X POST "http://localhost:8000/webhook?companyId=4394&integration_type=payroll&integration_provider=Daxco" \
  -H "accept: application/json" \
  -F "file=@input_format.csv;type=text/csv"
```

> Ensure `input_format.csv` is present in the `backend` directory.

### 2. Validate (Revalidate Transformation)

```
curl -X POST "http://localhost:8000/validate?companyId=4394" \
  -H "Content-Type: application/json" \
  -d @example_validate.json
```

Where `example_validate.json` is the output from the `/webhook` endpoint.

### 3. Download CSV

```
curl -X POST "http://localhost:8000/download" \
  -H "Content-Type: application/json" \
  -d @example_validate.json --output output.csv
```

## Notes
- The API expects the same input/output format as described in the requirements and sample CSVs.
- The employee API is called live for each request.
- File uploads are limited to 2MB and must be CSV. 
- See code comments and docstrings in `main.py` and `helper_functions/` for further details on logic and extension points. 