import logging
from .safe_get import safe_get
from .parse_currency_value import parse_currency_value
import os
import difflib
import pandas as pd
import io
from .constants import Output


def get_department_from_bytes(file_bytes):
    file_text = file_bytes.decode('utf-8')
    for line in file_text.splitlines():
        first_col = line.split(',')[0].strip().strip('"')
        # Remove colon for fuzzy match
        if difflib.get_close_matches(first_col.lower().replace(':', ''), ['department'], n=1, cutoff=0.7):
            return line.split(',')[1].strip().strip('"').split(',')[0].strip()
    return None

def daxco_transformation(file_bytes, employees):
    """
    Transform a Daxco payroll CSV file into a list of structured dictionaries using the new format.

    Args:
        file_bytes (bytes): The raw bytes of the uploaded CSV file.
        employees (list[dict]): List of employee dictionaries with 'first_name', 'last_name', and 'employee_id'.

    Returns:
        list[dict]: List of transformed payroll data rows, each as a dictionary with keys:
            'employee_id', 'gross_to_net_code', 'type_code', 'hours_or_amount', 
            'temporary_rate', 'distributed_dept_code'.

    Raises:
        ValueError: If the header row cannot be found in the CSV file.
    """
    logging.info(f"Parsing CSV file bytes for Daxco transformation")
    department = get_department_from_bytes(file_bytes)
    try:
        # Decode bytes to string and split into lines
        file_text = file_bytes.decode('utf-8')
        lines = file_text.splitlines()
        header_indices = []
        # Find the header row index by fuzzy matching first column to 'Staff First Name'
        for idx, line in enumerate(lines):
            first_col = line.split(',')[0].strip().strip('"')
            if difflib.get_close_matches(first_col.lower(), ['staff first name'], n=1, cutoff=0.7):
                header_indices.append(idx)
        if not header_indices:
            raise ValueError("Could not find header row with 'Staff First Name'")
        header_idx = header_indices[-1]  # Use the latest (last) index
        # Read the CSV into a DataFrame, skipping rows before the header
        df = pd.read_csv(io.BytesIO(file_bytes), skiprows=header_idx)
        logging.info(f"Parsed CSV with shape {df.shape}")
    except Exception as e:
        logging.exception(f"Exception in parse_csv: {e}")
        raise
    logging.info(f"Transforming data with {len(df)} rows and {len(employees)} employees")
    out = []
    for idx, row in df.iterrows():
        # Extract first and last name from the row
        first = safe_get(row, 'Staff First Name')
        last = safe_get(row, 'Staff Last Name')
        
        # Since fetch_employees is disabled, we won't have employee data
        # We'll use the data directly from the CSV file instead
        first_name = first.title() if first else ''
        last_name = last.title() if last else ''
        
        # Since we don't have employee data, we'll use placeholder values
        emp_code = ''
        dept_code = department or ""
        
        # Store original values for validation and reference
        adjustments = parse_currency_value(safe_get(row, 'Adjustments'))
        time_clock_hours = safe_get(row, 'Time Clock Hours')
        scheduled_hours = safe_get(row, 'Scheduled Hours')
        scheduled_payroll = safe_get(row, 'Scheduled Payroll')
        total_hours = safe_get(row, 'Total Hours')
        details = safe_get(row, 'Details')
        
        # Transform to new format
        output_row = Output(
            # New format fields
            employee_id=str(emp_code),
            gross_to_net_code="1",  # Default to Earnings Code
            type_code="REG",  # Default to Regular earnings
            hours_or_amount= scheduled_payroll or scheduled_hours or time_clock_hours or 0,
            temporary_rate="",  # Default to empty
            distributed_dept_code=dept_code or department or "4287",  # Default to 4287 if empty
            
            # Keep original values for reference and validation
            first_name=first_name,
            last_name=last_name,
            department=department,
            adjustments=adjustments,
            time_clock_hours=time_clock_hours,
            scheduled_hours=scheduled_hours,
            scheduled_payroll=scheduled_payroll,
            total_hours=total_hours,
            details=details,
            employee_code=emp_code
        )
        out.append(output_row)
        if idx < 5:  # Log first few rows for debugging
            logging.debug(f"Transformed row {idx}: {output_row}")
    logging.info(f"Transformed {len(out)} rows")
    return out