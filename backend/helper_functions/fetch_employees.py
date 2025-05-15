import requests
import logging
from fastapi import HTTPException
from .secrets import get_api_config

EMPLOYEE_API_PATH = "/api/v3/Employees"

def fetch_employees(company_id, environment="tequila"):
    """
    Fetch a list of employees for a given company from the remote Employee API.

    Args:
        company_id (str or int): The unique identifier for the company whose employees are to be fetched.
        environment (str): The environment to use for API config (default: 'tequila').

    Returns:
        list[dict]: A list of employee dictionaries, each containing 'first_name', 'last_name', and 'employee_id'.

    Raises:
        HTTPException: If the API request fails or returns a non-200 status code.

    Example:
        >>> fetch_employees(123)
        [{'first_name': 'John', 'last_name': 'Doe', 'employee_id': 1}, ...]
    """
    logging.info(f"Fetching employees for company_id={company_id} in environment={environment}")
    api_config = get_api_config(environment)
    api_url = api_config["base_endpoint"].rstrip("/") + EMPLOYEE_API_PATH
    api_key = api_config["api_key"]
    headers = {
        'accept': 'application/json',
        'Netchex-Shared-Key': api_key
    }
    params = {'companyId': company_id}
    try:
        # Make the API request to fetch employees
        resp = requests.get(api_url, headers=headers, params=params)
        logging.info(f"Employee API response status: {resp.status_code}")
        if resp.status_code != 200:
            logging.error(f"Failed to fetch employees: {resp.text}")
            raise HTTPException(status_code=500, detail='Failed to fetch employees')
        data = resp.json()
        logging.info(f"Fetched {len(data)} employees for company_id={company_id}")
        # Process and return the employee data in a simplified format
        result = [
            {
                'first_name': e.get('firstName'),
                'last_name': e.get('lastName'),
                'employee_id': e.get('id')
            } for e in data
        ]
        logging.info(f"Processed {len(result)} employees for company_id={company_id}")
        print(f"[DEBUG] fetch_employees: {len(result)} employees fetched. Sample: {result[:3]}")
        return result
    except Exception as e:
        logging.exception(f"Exception in fetch_employees: {e}")
        raise 