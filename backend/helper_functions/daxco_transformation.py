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
    Transform a Daxco payroll CSV file into a list of structured dictionaries.

    Args:
        file_bytes (bytes): The raw bytes of the uploaded CSV file.
        employees (list[dict]): List of employee dictionaries with 'first_name', 'last_name', and 'employee_id'.

    Returns:
        list[dict]: List of transformed payroll data rows, each as a dictionary with keys:
            'first_name', 'last_name', 'department', 'adjustments', 'time_clock_hours',
            'scheduled_hours', 'scheduled_payroll', 'total_hours', 'details', 'employee_code'.

    Raises:
        ValueError: If the header row cannot be found in the CSV file.

    Example:
        >>> daxco_transformation(file_bytes, employees)
        [{...}, ...]
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
        # Convert to uppercase for case-insensitive matching
        first_upper = first.upper() if first else ''
        last_upper = last.upper() if last else ''
        # Match employee by first and last name (case-insensitive)
        emp_matches = [e for e in employees if e['first_name'].upper() == first_upper and e['last_name'].upper() == last_upper]
        emp_code = emp_matches[0]['employee_id'] if len(emp_matches) == 1 else ''
        # Store/display names in title case
        output_row = Output(
            first_name=first.title() if first else '',
            last_name=last.title() if last else '',
            department=department,
            adjustments=parse_currency_value(safe_get(row, 'Adjustments')),
            time_clock_hours=safe_get(row, 'Time Clock Hours'),
            scheduled_hours=safe_get(row, 'Scheduled Hours'),
            scheduled_payroll=safe_get(row, 'Scheduled Payroll'),
            total_hours=safe_get(row, 'Total Hours'),
            details=safe_get(row, 'Details'),
            employee_code=emp_code
        )
        out.append(output_row)
        if idx < 5:  # Log first few rows for debugging
            logging.debug(f"Transformed row {idx}: {output_row}")
    logging.info(f"Transformed {len(out)} rows")
    return out 