import logging
from .constants import Output


def validate_employee_code(row, employees):
    """
    Validate the employee code in a row against a list of employees.

    Args:
        row (dict): The data row containing 'first_name', 'last_name', and 'employee_code'.
        employees (list[dict]): List of employee dictionaries with 'first_name', 'last_name', and 'employee_id'.

    Returns:
        tuple: (employee_code_valid (bool), possible_codes (list))
            - employee_code_valid: True if the code is valid, False otherwise.
            - possible_codes: List of possible employee IDs if ambiguous or invalid.
    """
    first = row['first_name']
    last = row['last_name']
    # Find all employees matching the first and last name (case-insensitive)
    first_upper = first.upper() if first else ''
    last_upper = last.upper() if last else ''
    emp_matches = [e for e in employees if e['first_name'].upper() == first_upper and e['last_name'].upper() == last_upper]
    emp_code = row.get('employee_code', '')
    try:
        emp_code_int = int(emp_code) if emp_code != '' else ''
    except Exception:
        emp_code_int = ''
    employee_code_valid = True
    possible_codes = []
    if emp_code_int == '':
        if len(emp_matches) == 0:
            employee_code_valid = False
            possible_codes = []
        elif len(emp_matches) > 1:
            employee_code_valid = False
            possible_codes = [e['employee_id'] for e in emp_matches]
    else:
        if not any(e['employee_id'] == emp_code_int for e in employees):
            employee_code_valid = False
            possible_codes = [e['employee_id'] for e in emp_matches]
    return employee_code_valid, possible_codes


def validate_scheduled_payroll(row, idx=None):
    """
    Validate and parse the scheduled payroll value from a row.

    Args:
        row (dict): The data row containing 'scheduled_payroll'.
        idx (int, optional): Row index for logging purposes.

    Returns:
        tuple: (scheduled_payroll_valid (bool), scheduled_payroll_val (float))
            - scheduled_payroll_valid: True if the value is valid (non-negative float), False otherwise.
            - scheduled_payroll_val: The parsed float value (0.0 if invalid).
    """
    scheduled_payroll_raw = row.get('scheduled_payroll', '')
    scheduled_payroll_val = 0.0
    scheduled_payroll_valid = True
    try:
        # Remove currency symbols and commas, then convert to float
        scheduled_payroll_str = str(scheduled_payroll_raw).replace('$', '').replace(',', '').strip()
        scheduled_payroll_val = float(scheduled_payroll_str) if scheduled_payroll_str else 0.0
        if scheduled_payroll_val < 0:
            scheduled_payroll_valid = False
    except Exception as e:
        scheduled_payroll_valid = False
        scheduled_payroll_val = 0.0
        if idx is not None:
            logging.warning(f"Row {idx} Scheduled Payroll parse error: {scheduled_payroll_raw}")
    return scheduled_payroll_valid, scheduled_payroll_val


def validate_transformation(data, employees):
    """
    Validate a list of transformed payroll data rows against employee data and payroll rules.

    Args:
        data (list[Output]): List of payroll data rows to validate.
        employees (list[dict]): List of employee dictionaries.

    Returns:
        dict: {
            'rows': list of validated rows (with validation fields),
            'all_valid': bool indicating if all rows are valid
        }
    """
    logging.info(f"Validating transformation for {len(data)} rows and {len(employees)} employees")
    validation = []
    all_valid = True  # Kept for summary, but not used for row-level valid
    for idx, row in enumerate(data):
        # If row is a dict, convert to Output
        if not isinstance(row, Output):
            row = Output(**row)
        # Validate employee code and scheduled payroll for each row
        employee_code_valid, possible_codes = validate_employee_code(row.__dict__, employees)
        scheduled_payroll_valid, scheduled_payroll_val = validate_scheduled_payroll(row.__dict__, idx)
        out_row = Output(
            **{**row.__dict__,
               'first_name': row.first_name.title() if row.first_name else '',
               'last_name': row.last_name.title() if row.last_name else '',
               'employee_code_valid': employee_code_valid,
               'possible_employee_codes': possible_codes,
               'scheduled_payroll': scheduled_payroll_val,
               'scheduled_payroll_valid': scheduled_payroll_valid}
        )
        validation.append(out_row)
        if not employee_code_valid or not scheduled_payroll_valid:
            logging.warning(f"Row {idx} invalid: {out_row}")
            all_valid = False
    logging.info(f"Validation complete. All valid: {all_valid}")
    return {
        'rows': [r.to_dict() for r in validation],
        'all_valid': all_valid
    } 