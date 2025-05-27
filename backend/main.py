"""
main.py - FastAPI backend for integration processing

This module provides API endpoints for uploading, validating, and downloading CSV data for various integrations (e.g., payroll providers).

Endpoints:
- /webhook: Accepts CSV uploads, processes them through configured integration stages, and returns the transformed data.
- /validate: Validates transformed data against company employee records.
- /download: Returns validated data as a downloadable CSV file.
- /health: Health check endpoint for monitoring the API status.

Configuration:
- Integrations and their processing stages are defined in integration_config.yml.
- Helper functions for data fetching, transformation, and validation are imported from helper_functions.py.

Security:
- CORS is enabled for all origins (adjust in production).
- File size and type checks are enforced for uploads.

Error Handling:
- Database connection timeouts are properly handled with appropriate status codes.
- Comprehensive logging for debugging and monitoring.

"""
import time
import sys
from fastapi import FastAPI, File, UploadFile, Query, HTTPException, Body, status
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware
import io
import csv
import yaml
import os
import logging
from logging.handlers import RotatingFileHandler
from helper_functions import (
    fetch_employees, daxco_transformation, validate_transformation, OUTPUT_COLUMNS
)
from helper_functions.constants import Output
from dotenv import load_dotenv

load_dotenv()

# Configure logging
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

# Set up rotating log handler
log_file = os.path.join(LOG_DIR, 'app.log')
file_handler = RotatingFileHandler(log_file, maxBytes=10485760, backupCount=5)  # 10 MB per file, keep 5 backups
file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_format)

# Configure root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(file_handler)

# Add stdout handler for console output
console_handler = logging.StreamHandler()
console_handler.setFormatter(file_format)
root_logger.addHandler(console_handler)

logging.info("Application starting up...")

FUNCTION_REGISTRY = {
    'fetch_employees': fetch_employees,
    'daxco_transformation': daxco_transformation,
    'validate_transformation': validate_transformation,
}

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_integration_config():
    with open('integration_config.yml', 'r') as f:
        return yaml.safe_load(f)

INTEGRATION_CONFIG = load_integration_config()

def run_integration_stages(stages, context):
    for stage in stages:
        func = FUNCTION_REGISTRY[stage["function"]]
        args = [context[k] for k in stage["input_stage"]]
        try:
            result = func(*args)
            context[stage["output_stage"]] = result
        except RuntimeError as e:
            if "timeout expired" in str(e).lower() or "login timeout" in str(e).lower():
                logging.error(f"Database connection timeout in stage {stage['name']}: {str(e)}")
                raise HTTPException(
                    status_code=503, 
                    detail="Database connection timed out. The server may be temporarily unavailable. Please try again later."
                )
            logging.error(f"Error in stage {stage['name']}: {str(e)}")
            raise  # Re-raise the exception to stop the pipeline
        except Exception as e:
            logging.error(f"Error in stage {stage['name']}: {str(e)}")
            raise  # Re-raise the exception to stop the pipeline
    return context

@app.get('/health')
def health_check():
    """
    Health check endpoint for Docker health checks.
    Returns a 200 OK response if the API is running.
    Also attempts a lightweight database connection check.
    """
    health_info = {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": time.time(),
        "database": {
            "status": "unknown"
        }
    }
    
    # Attempt a lightweight database connectivity test
    try:
        from helper_functions.db_utils import get_connection_string, connect_with_retry
        import pyodbc
        
        # Just test connection without running a query
        connection_string = get_connection_string()
        if connection_string:
            try:
                conn = connect_with_retry(connection_string)
                conn.close()
                health_info["database"]["status"] = "connected"
            except Exception as e:
                health_info["database"]["status"] = "disconnected"
                health_info["database"]["error"] = str(e)
        else:
            health_info["database"]["status"] = "not_configured"
    except Exception as e:
        health_info["database"]["status"] = "error"
        health_info["database"]["error"] = str(e)
    
    # Overall status depends on database connection
    if health_info["database"]["status"] != "connected" and health_info["database"]["status"] != "not_configured":
        health_info["status"] = "degraded"
    
    return health_info

@app.post('/webhook')
def webhook(
    company_id: int = Query(..., alias="companyId"),
    integration_type: str = Query(...),
    integration_provider: str = Query(...),
    file: UploadFile = File(...)
):
    """
    Receives a CSV file upload and processes it through the integration pipeline.
    - Validates integration type/provider and file type/size.
    - Runs configured transformation stages.
    - Returns the final output as JSON.
    
    Returns:
        JSONResponse: The transformed data or appropriate error response
        
    Raises:
        HTTPException: For client errors (400) or server errors (503)
    """
    request_start_time = time.time()
    
    try:
        logging.info(f"Received webhook: company_id={company_id}, integration_type={integration_type}, integration_provider={integration_provider}, filename={file.filename}")
        
        # Check if integration type/provider is supported
        if integration_type not in INTEGRATION_CONFIG or integration_provider not in INTEGRATION_CONFIG[integration_type]:
            logging.error(f"Unsupported integration: {integration_type}/{integration_provider}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Unsupported integration')
        
        # Only accept CSV files
        if file.content_type not in ['text/csv', 'application/vnd.ms-excel']:
            logging.error(f"Unsupported file type: {file.content_type}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Only CSV files are accepted')
        
        contents = file.file.read()
        logging.info(f"Read {len(contents)} bytes from uploaded file")
        
        # Enforce file size limit (2MB)
        if len(contents) > 2 * 1024 * 1024:
            logging.error(f"File too large: {len(contents)} bytes")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='File too large (max 2MB)')
        
        # Prepare context for integration pipeline
        context = {"file_bytes": contents, "company_id": company_id}
        stages = INTEGRATION_CONFIG[integration_type][integration_provider]
        logging.debug(f"Integration stages: {stages}")
        
        # Run the integration pipeline
        try:
            context = run_integration_stages(stages, context)
        except HTTPException:
            # Let HTTP exceptions pass through (they're already formatted properly)
            raise
        except RuntimeError as e:
            if "timeout expired" in str(e).lower() or "login timeout" in str(e).lower() or "connection failed" in str(e).lower():
                logging.error(f"Database connection error: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Database connection failed. The server may be temporarily unavailable. Please try again later."
                )
            logging.error(f"Runtime error during integration: {str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        
        result = context[stages[-1]["output_stage"]]
        
        # If result is a list of Output, convert to dicts
        if isinstance(result, list) and result and isinstance(result[0], Output):
            result = [r.to_dict() for r in result]
            
        request_duration = time.time() - request_start_time
        logging.info(f"Webhook processing complete in {request_duration:.2f}s, returning {len(result) if isinstance(result, list) else 'non-list'} rows")
        return JSONResponse(content=result)
    except HTTPException as he:
        # Already handled, just re-raise
        raise
    except Exception as e:
        # Catch all other exceptions
        error_message = f"Unexpected error processing webhook: {str(e)}"
        logging.error(error_message)
        logging.error(f"Exception details: {type(e).__name__}")
        # Log the full stack trace for debugging
        import traceback
        logging.error(traceback.format_exc())
        
        # Return a generic error to the client
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing your request."
        )
    except HTTPException as he:
        # Already handled, just re-raise
        raise he
    except Exception as e:
        import traceback
        logging.error(f"Unhandled exception in /webhook: {e}\n{traceback.format_exc()}")
        return JSONResponse(status_code=500, content={"error": str(e), "trace": traceback.format_exc()})

@app.post('/validate')
def validate(
    company_id: int = Query(..., alias="companyId"),
    integration_type: str = Query(...),
    integration_provider: str = Query(...),
    rows: dict = Body(...)
):
    """
    Validates transformed rows against company employee records.
    - Returns validation results as JSON.
    """
    if integration_type not in INTEGRATION_CONFIG or integration_provider not in INTEGRATION_CONFIG[integration_type]:
        raise HTTPException(status_code=400, detail='Unsupported integration')
    if integration_type != "payroll":
        raise HTTPException(status_code=400, detail='Validation only supported for integration_type=payroll')
    
    # Fetch employees for validation
    try:
        employees = fetch_employees(company_id)
        logging.info(f"Validating {len(rows['rows'])} rows against {len(employees)} employees")
        # Convert dicts to Output objects if needed
        
        input_rows = rows['rows']
        if input_rows and isinstance(input_rows[0], dict) and not isinstance(input_rows[0], Output):
            input_rows = [Output(**r) for r in input_rows]
        validated = validate_transformation(input_rows, employees)
        return JSONResponse(content=validated)
    except Exception as e:
        import traceback
        logging.error(f"Error during validation: {str(e)}\n{traceback.format_exc()}")
        return JSONResponse(status_code=500, content={"error": str(e), "trace": traceback.format_exc()})

@app.post('/download')
def download(data: dict):
    """
    Returns the provided data as a downloadable CSV file.
    - Expects a dict with a 'rows' key containing a list of dicts.
    - Uses OUTPUT_COLUMNS for CSV header and column order.
    """
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=OUTPUT_COLUMNS)
    writer.writeheader()
    for row in data['rows']:
        writer.writerow({col: row.get(col, '') for col in OUTPUT_COLUMNS})
    output.seek(0)
    return StreamingResponse(iter([output.getvalue()]), media_type='text/csv', headers={
        'Content-Disposition': 'attachment; filename=output.csv'
    })