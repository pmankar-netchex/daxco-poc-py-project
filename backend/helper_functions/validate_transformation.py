import logging
from .constants import Output
from .validation_result import ValidationResult, RowValidation, FieldValidation, ExactMatch, EmployeeMatch
import json

def validate_employee_id(row, employees):
    """
    Validate the employee ID in a row against a list of employees.
    
    This function checks if the employee_id in the row exists in the employees list.
    If the employee_id is not found, it tries to find possible matches based on first_name and last_name.

    Args:
        row (dict): The data row containing 'first_name', 'last_name', and 'employee_id'.
        employees (list[dict]): List of employee dictionaries.

    Returns:
        tuple: (employee_id_valid (bool), possible_ids (list))
            - employee_id_valid: True if employee_id is found in employees list or if no employees to validate against.
            - possible_ids: List of possible employee IDs that match based on name similarity.
    """
    # If no employees to validate against, consider it valid
    if not employees:
        logging.warning("No employees available for validation - skipping employee ID validation")
        return True, []
    
    # Log the validation attempt
    #print(f"Validating employee file: {row}")
    #print(f"Validating employee DB: {employees}")
    print(f"Validating employee: {row}")
    first_name = row.get('first_name', '')
    last_name = row.get('last_name', '')
    employee_id = row.get('employee_id', '')
    
    #logging.info(f"Validating employee: ID={employee_id}, name={first_name} {last_name}")
    
    # Check if the employee_id exists in the employees list
    if employee_id:
        # Try to find the employee by ID
        exact_match = next((emp for emp in employees if str(emp.get('employee_id', '')).strip() == str(employee_id).strip()), None)
        if exact_match:
            logging.info(f"Found exact match for employee_id={employee_id}: {exact_match.get('first_name', '')} {exact_match.get('last_name', '')}")
            return True, []
    
    # If we have name data, try to find possible matches based on name
    possible_matches = []
    print(f"Checking for possible matches for employee: {first_name} {last_name}")
    if first_name or last_name:
        for emp in employees:
            emp_first = str(emp.get('first_name', '')).lower().strip()
            emp_last = str(emp.get('last_name', '')).lower().strip()
            
            row_first = first_name.lower().strip() if first_name else ''
            row_last = last_name.lower().strip() if last_name else ''
            print(f"Comparing: {row_first} {row_last} with {emp_first} {emp_last}")
            # Check for name similarity
            if (row_first and row_first == emp_first) and (row_last and row_last == emp_last):
                possible_matches.append(emp.get('employee_id', ''))
    
    # Check if we found any possible matches
    if possible_matches:
        #logging.info(f"Found {len(possible_matches)} possible employee matches: {possible_matches}")
        return False, possible_matches
    
    #logging.warning(f"No match found for employee: ID={employee_id}, name={first_name} {last_name}")
    return False, []


def validate_hours_or_amount(row, idx=None):
    """
    Validate the hours or amount value from a row.

    Args:
        row (dict): The data row containing 'hours_or_amount'.
        idx (int, optional): Row index for logging purposes.

    Returns:
        tuple: (hours_or_amount_valid (bool), hours_or_amount_val (float))
            - hours_or_amount_valid: True if the value is valid (non-negative), False otherwise.
            - hours_or_amount_val: The parsed float value (0.0 if invalid).
    """
    hours_or_amount_raw = row.get('hours_or_amount', '')
    hours_or_amount_val = 0.0
    hours_or_amount_valid = True
    try:
        # Remove currency symbols and commas, then convert to float
        hours_or_amount_str = str(hours_or_amount_raw).replace('$', '').replace(',', '').strip()
        hours_or_amount_val = float(hours_or_amount_str) if hours_or_amount_str else 0.0
        if hours_or_amount_val < 0:
            hours_or_amount_valid = False
    except Exception as e:
        hours_or_amount_valid = False
        hours_or_amount_val = 0.0
        if idx is not None:
            logging.warning(f"Row {idx} Hours or Amount parse error: {hours_or_amount_raw}")
    return hours_or_amount_valid, hours_or_amount_val


def validate_transformation(data, employees):
    """
    Validate a list of transformed payroll data rows against employee data and payroll rules.

    Args:
        data (list[Output]): List of payroll data rows to validate.
        employees (list[dict]): List of employee dictionaries.

    Returns:
        dict: {
            'rows': list of validated rows formatted according to the new validation schema,
            'all_valid': bool indicating if all rows are valid
        }
    """
    logging.info(f"Validating transformation for {len(data)} rows and {len(employees)} employees")
    
    if employees:
        # Log some sample employee data to help with debugging
        sample_employee = employees[0]
        employee_fields = list(sample_employee.keys())
        #logging.info(f"Employee data fields: {employee_fields}")
        #logging.info(f"Sample employee data: {sample_employee}")
    else:
        logging.warning("No employee data available for validation")
    
    # First, run our legacy validation to maintain compatibility with existing clients
    legacy_validation = []
    all_valid = True
    
    for idx, row in enumerate(data):
        # If row is a dict, convert to Output
        if not isinstance(row, Output):
            row = Output(**row)
        
        # Log row data for debugging
        logging.debug(f"Validating row {idx}: employee_id={row.employee_id}, first_name={row.first_name}, last_name={row.last_name}")
        
        # Validate employee ID and hours/amount for each row
        employee_id_valid, possible_ids = validate_employee_id(row.__dict__, employees)
        hours_or_amount_valid, hours_or_amount_val = validate_hours_or_amount(row.__dict__, idx)
        
        # Update the row with validation results
        out_row = Output(
            **{**row.__dict__,
               'first_name': row.first_name.title() if row.first_name else '',
               'last_name': row.last_name.title() if row.last_name else '',
               'employee_id_valid': employee_id_valid,
               'possible_employee_ids': possible_ids,
               'hours_or_amount': hours_or_amount_val,
               'hours_or_amount_valid': hours_or_amount_valid,
               # Maintain compatibility with old validation fields
               'employee_code_valid': employee_id_valid,
               'possible_employee_codes': possible_ids,
               'scheduled_payroll_valid': True  # Not validating this in new format
              }
        )
        legacy_validation.append(out_row)
        if not employee_id_valid or not hours_or_amount_valid:
            logging.warning(f"Row {idx} invalid: employee_id_valid={employee_id_valid}, hours_or_amount_valid={hours_or_amount_valid}")
            logging.debug(f"Possible employee IDs: {possible_ids}")
            all_valid = False
    
    # Now create new validation format
    # all_valid should only be true if ALL rows have valid employee IDs and valid hours/amounts
    all_rows_valid = all(
        row.employee_id_valid and row.hours_or_amount_valid
        for row in legacy_validation
    )
    
    validation_result = ValidationResult(all_valid=all_rows_valid)
    
    for row in legacy_validation:
        row_validation = RowValidation.from_output(row, employees)
        validation_result.rows.append(row_validation)
    
    logging.info(f"Validation complete. All valid: {all_rows_valid}")
    
    return validation_result.to_dict()