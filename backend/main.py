"""
main.py - FastAPI backend for integration processing

This module provides API endpoints for uploading, validating, and downloading CSV data for various integrations (e.g., payroll providers).

Endpoints:
- /webhook: Accepts CSV uploads, processes them through configured integration stages, and returns the transformed data.
- /validate: Validates transformed data against company employee records.
- /download: Returns validated data as a downloadable CSV file.

Configuration:
- Integrations and their processing stages are defined in integration_config.yml.
- Helper functions for data fetching, transformation, and validation are imported from helper_functions.py.

Security:
- CORS is enabled for all origins (adjust in production).
- File size and type checks are enforced for uploads.

"""
from fastapi import FastAPI, File, UploadFile, Query, HTTPException, Body
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import io
import csv
import yaml
from helper_functions import (
    fetch_employees, daxco_transformation, validate_transformation, OUTPUT_COLUMNS
)
from helper_functions.constants import Output
import logging

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
        result = func(*args)
        context[stage["output_stage"]] = result
    return context

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
    """
    try:
        logging.info(f"Received webhook: company_id={company_id}, integration_type={integration_type}, integration_provider={integration_provider}, filename={file.filename}")
        # Check if integration type/provider is supported
        if integration_type not in INTEGRATION_CONFIG or integration_provider not in INTEGRATION_CONFIG[integration_type]:
            logging.error(f"Unsupported integration: {integration_type}/{integration_provider}")
            raise HTTPException(status_code=400, detail='Unsupported integration')
        # Only accept CSV files
        if file.content_type not in ['text/csv', 'application/vnd.ms-excel']:
            logging.error(f"Unsupported file type: {file.content_type}")
            raise HTTPException(status_code=400, detail='Only CSV files are accepted')
        contents = file.file.read()
        logging.info(f"Read {len(contents)} bytes from uploaded file")
        # Enforce file size limit (2MB)
        if len(contents) > 2 * 1024 * 1024:
            logging.error(f"File too large: {len(contents)} bytes")
            raise HTTPException(status_code=400, detail='File too large')
        # Prepare context for integration pipeline
        context = {"file_bytes": contents, "company_id": company_id}
        stages = INTEGRATION_CONFIG[integration_type][integration_provider]
        logging.debug(f"Integration stages: {stages}")
        # Run the integration pipeline
        context = run_integration_stages(stages, context)
        result = context[stages[-1]["output_stage"]]
        # If result is a list of Output, convert to dicts
        if isinstance(result, list) and result and isinstance(result[0], Output):
            result = [r.to_dict() for r in result]
        logging.info(f"Webhook processing complete, returning {len(result) if isinstance(result, list) else 'non-list'} rows")
        return JSONResponse(content=result)
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
    - Fetches employees for the company.
    - Validates each row using the validate_transformation helper (only for payroll integration_type).
    - Returns validation results as JSON.
    """
    if integration_type not in INTEGRATION_CONFIG or integration_provider not in INTEGRATION_CONFIG[integration_type]:
        raise HTTPException(status_code=400, detail='Unsupported integration')
    if integration_type != "payroll":
        raise HTTPException(status_code=400, detail='Validation only supported for integration_type=payroll')
    employees = fetch_employees(company_id)
    print(f"[DEBUG] Number of employees fetched: {len(employees)}")
    print(f"[DEBUG] Sample employees: {employees[:3]}")
    # Convert dicts to Output objects if needed
    input_rows = rows['rows']
    if input_rows and isinstance(input_rows[0], dict) and not isinstance(input_rows[0], Output):
        input_rows = [Output(**r) for r in input_rows]
    validated = validate_transformation(input_rows, employees)
    return JSONResponse(content=validated)

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