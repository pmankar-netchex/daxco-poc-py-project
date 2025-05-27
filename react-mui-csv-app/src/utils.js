// Helper functions for formatting and data transformation
export const formatCurrency = (value) => {
  if (value === null || value === undefined || value === '') return '';
  if (typeof value !== 'number') {
    const parsed = parseFloat(value);
    if (isNaN(parsed)) return value;
    value = parsed;
  }
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value);
};

export const formatNumber = (value) => {
  if (value === null || value === undefined || value === '') return '';
  if (typeof value !== 'number') {
    const parsed = parseFloat(value);
    if (isNaN(parsed)) return value;
    value = parsed;
  }
  return new Intl.NumberFormat('en-US').format(value);
};

// Map of gross to net codes to display text
export const GROSS_TO_NET_CODES = {
  '1': '1 - Earnings',
  '3': '3 - Employee Deduction',
  '4': '4 - Employer Deduction'
};

// Map of available type codes
export const TYPE_CODES = ['REG', 'BON', 'FB', 'MED'];

// Map of common department codes
export const DEPARTMENT_CODES = ['000', '001', 'PRL', '4287'];
