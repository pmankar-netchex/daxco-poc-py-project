import os
import logging
from dataclasses import dataclass, asdict
from typing import Optional, List, Any

@dataclass
class Output:
    first_name: str
    last_name: str
    department: str
    adjustments: Any
    time_clock_hours: Any
    scheduled_hours: Any
    scheduled_payroll: Any
    total_hours: Any
    details: Any
    employee_code: Any
    
    # Validation fields (optional, used in validation step)
    employee_code_valid: Optional[bool] = None
    possible_employee_codes: Optional[List[Any]] = None
    scheduled_payroll_valid: Optional[bool] = None

    def to_dict(self):
        return asdict(self)

OUTPUT_COLUMNS = [
    'first_name','last_name','department','adjustments','time_clock_hours',
    'scheduled_hours','scheduled_payroll','total_hours','details','employee_code'
] 