from dataclasses import dataclass, asdict, field
from typing import List, Dict, Any, Optional, Union


@dataclass
class ExactMatch:
    """Class representing an exact match for a field validation."""
    employee_id: Optional[int] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    net_code: Optional[int] = None
    dept_code: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class EmployeeMatch:
    """Class representing a possible employee match in validation results."""
    employee_id: int
    first_name: str
    last_name: str
    home_department: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FieldValidation:
    """Class representing validation results for a single field."""
    exact_match: Optional[ExactMatch] = None
    possible_matches: List[Union[ExactMatch, EmployeeMatch, Dict[str, Any]]] = field(default_factory=list)
    valid: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        result = {"valid": self.valid}
        if self.exact_match:
            result["exact_match"] = self.exact_match.to_dict()
        else:
            result["exact_match"] = None
            
        if self.possible_matches:
            result["possible_matches"] = [
                match.to_dict() if hasattr(match, "to_dict") else match 
                for match in self.possible_matches
            ]
        else:
            result["possible_matches"] = []
            
        return result


@dataclass
class RowValidation:
    """Class representing validation results for a single row."""
    Employee: FieldValidation
    gross_to_net_code: FieldValidation
    type_code: FieldValidation
    hours_or_amount: Any
    temporary_rate: Any
    distributed_dept_code: FieldValidation
    
    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        # Convert snake_case field names back to original display names
        field_mapping = {
            "gross_to_net_code": "Gross to Net Code",
            "type_code": "Type Code",
            "hours_or_amount": "Hours or Amount",
            "temporary_rate": "Temporary Rate",
            "distributed_dept_code": "Distributed Dept Code"
        }
        
        for key, value in list(result.items()):
            if isinstance(value, FieldValidation):
                result[key] = value.to_dict()
            
            # Rename fields back to their display names
            if key in field_mapping:
                result[field_mapping[key]] = result.pop(key)
                
        return result
    
    @classmethod
    def from_output(cls, output, employees):
        """
        Create a RowValidation instance from an Output instance.
        
        Args:
            output: An Output instance.
            employees: List of employee dictionaries.
            
        Returns:
            A RowValidation instance.
        """
        from .validate_transformation import validate_employee_id, validate_hours_or_amount
        
        # Validate employee
        employee_id_valid, possible_ids = validate_employee_id(output.__dict__, employees)
        
        # Create Employee field validation
        employee_validation = FieldValidation(valid=employee_id_valid)
        if output.employee_id and employee_id_valid:
            # Find the matching employee
            matching_employee = next(
                (e for e in employees if str(e['employee_id']) == str(output.employee_id)), 
                None
            )
            if matching_employee:
                employee_validation.exact_match = ExactMatch(
                    employee_id=matching_employee['employee_id'],
                    first_name=matching_employee['first_name'],
                    last_name=matching_employee['last_name']
                )
        
        # Create possible employee matches
        if possible_ids:
            employee_validation.possible_matches = [
                EmployeeMatch(
                    employee_id=e['employee_id'],
                    first_name=e['first_name'],
                    last_name=e['last_name'],
                    home_department=e.get('dept_codes', [''])[0] if e.get('dept_codes') else ''
                )
                for e in employees if e['employee_id'] in possible_ids
            ]
        
        # Validate gross to net code (always valid in current implementation)
        gross_to_net_validation = FieldValidation(valid=True)
        if output.gross_to_net_code:
            gross_to_net_validation.exact_match = ExactMatch(net_code=output.gross_to_net_code)
        
        # Validate type code (always valid in current implementation)
        type_code_validation = FieldValidation(valid=True)
        if output.type_code:
            type_code_validation.exact_match = ExactMatch(net_code=output.type_code)
        
        # Validate hours or amount
        hours_valid, hours_value = validate_hours_or_amount(output.__dict__)
        
        # Validate distributed dept code (always valid in current implementation)
        dept_code_validation = FieldValidation(valid=True)
        if output.distributed_dept_code:
            dept_code_validation.exact_match = ExactMatch(dept_code=output.distributed_dept_code)
        
        return cls(
            Employee=employee_validation,
            gross_to_net_code=gross_to_net_validation,
            type_code=type_code_validation,
            hours_or_amount=hours_value,
            temporary_rate=output.temporary_rate or "",
            distributed_dept_code=dept_code_validation
        )



@dataclass
class ValidationResult:
    """Class representing the overall validation results."""
    all_valid: bool = False
    rows: List[RowValidation] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "all_valid": self.all_valid,
            "rows": [row.to_dict() for row in self.rows]
        }
