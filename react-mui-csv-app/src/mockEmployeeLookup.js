/**
 * Mock employee data for testing when backend fetch_employees function is disabled
 */

// Sample employee database
const MOCK_EMPLOYEES = [
  {
    employee_id: 1001,
    first_name: 'John',
    last_name: 'Smith',
    home_department: 'Sales'
  },
  {
    employee_id: 1002,
    first_name: 'Jane',
    last_name: 'Doe',
    home_department: 'Marketing'
  },
  {
    employee_id: 1003,
    first_name: 'Michael',
    last_name: 'Johnson',
    home_department: 'Finance'
  },
  {
    employee_id: 1004,
    first_name: 'Emily',
    last_name: 'Williams',
    home_department: 'HR'
  },
  {
    employee_id: 1005,
    first_name: 'David',
    last_name: 'Brown',
    home_department: 'IT'
  },
  {
    employee_id: 1006,
    first_name: 'Sarah',
    last_name: 'Miller',
    home_department: 'Operations'
  },
  {
    employee_id: 1007,
    first_name: 'Robert',
    last_name: 'Davis',
    home_department: 'Customer Support'
  },
  {
    employee_id: 1008,
    first_name: 'Jennifer',
    last_name: 'Garcia',
    home_department: 'Product'
  },
  {
    employee_id: 1009,
    first_name: 'William',
    last_name: 'Rodriguez',
    home_department: 'R&D'
  },
  {
    employee_id: 1010,
    first_name: 'Lisa',
    last_name: 'Martinez',
    home_department: 'Legal'
  }
];

/**
 * Search for employees in mock database by matching name parts
 * @param {string} query - Search term to look for in first/last names
 * @returns {Array} - List of matching employee objects
 */
export const searchEmployees = (query = "") => {
  if (!query) return [];
  
  const searchTerms = query.toLowerCase().split(/\s+/);
  
  return MOCK_EMPLOYEES.filter(employee => {
    const firstNameLower = employee.first_name.toLowerCase();
    const lastNameLower = employee.last_name.toLowerCase();
    
    // Check if any search term is found in employee first or last name
    return searchTerms.some(term => 
      firstNameLower.includes(term) || 
      lastNameLower.includes(term) ||
      String(employee.employee_id).includes(term)
    );
  });
};

/**
 * Get employee by exact employee id
 * @param {number|string} employeeId - Employee ID to find
 * @returns {Object|null} - Matching employee or null
 */
export const getEmployeeById = (employeeId) => {
  if (!employeeId) return null;
  
  const id = parseInt(employeeId, 10);
  return MOCK_EMPLOYEES.find(emp => emp.employee_id === id) || null;
};

/**
 * Enhanced version of updateEmployeeId to use with mock data
 * @param {Array} rows - Current rows state  
 * @param {number} rowIndex - Index of the row being updated
 * @param {number|string} employeeId - ID of the selected employee
 * @returns {Object} - Updated row with employee data
 */
export const updateRowWithEmployeeId = (rows, rowIndex, employeeId) => {
  // Make a copy of the rows
  const newRows = [...rows];
  const row = newRows[rowIndex];
  
  // Find the employee in our mock database
  const employee = getEmployeeById(employeeId);
  
  // Handle both new and legacy formats
  if (row.Employee) {
    // New format
    row.Employee = {
      ...row.Employee,
      valid: !!employee, // Valid if found
      exact_match: employee ? {
        employee_id: employee.employee_id,
        first_name: employee.first_name,
        last_name: employee.last_name
      } : null
    };
  } else {
    // Legacy format  
    row.employee_id = employee ? employee.employee_id : "";
    row.employee_id_valid = !!employee;
    row.first_name = employee ? employee.first_name : "";
    row.last_name = employee ? employee.last_name : "";
  }
  
  return newRows;
};
