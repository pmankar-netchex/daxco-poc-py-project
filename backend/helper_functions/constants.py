import os
import logging
from dataclasses import dataclass, asdict
from typing import Optional, List, Any

@dataclass
class Output:
    employee_id: str  # Netchex Employee Code, SSN, or Clock Sequence Number
    gross_to_net_code: str  # 1 for Earnings Code, 3 for Employee Deduction Amount, 4 for Employer Deduction Amount
    type_code: str  # Valid Netchex Earnings Code or Fixed Amount Deduction Code
    hours_or_amount: Any  # Hours or Amount
    temporary_rate: Any  # Used for Temporary Rate Earnings Code
    distributed_dept_code: str  # Department to Distribute to
    
    # Original fields kept for transformation process
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    department: Optional[str] = None
    adjustments: Optional[Any] = None
    time_clock_hours: Optional[Any] = None
    scheduled_hours: Optional[Any] = None
    scheduled_payroll: Optional[Any] = None
    total_hours: Optional[Any] = None
    details: Optional[Any] = None
    employee_code: Optional[Any] = None
    
    # Validation fields (optional, used in validation step)
    employee_id_valid: Optional[bool] = None
    possible_employee_ids: Optional[List[Any]] = None
    hours_or_amount_valid: Optional[bool] = None
    
    # Legacy validation fields for backward compatibility
    employee_code_valid: Optional[bool] = None
    possible_employee_codes: Optional[List[Any]] = None
    scheduled_payroll_valid: Optional[bool] = None

    def to_dict(self):
        return asdict(self)

OUTPUT_COLUMNS = [
    'employee_id', 'gross_to_net_code', 'type_code', 
    'hours_or_amount', 'temporary_rate', 'distributed_dept_code'
]