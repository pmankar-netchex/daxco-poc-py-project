"""
This module contains SQL queries used throughout the application.
Each query is defined as a constant to promote reusability and maintainability.
"""

# Simple query to test database connectivity
TEST_CONNECTION_QUERY = """
SELECT * FROM HRPremier.dbo.Person_Main WHERE CompanyId = ?
"""

# Query to fetch employee data including earnings and deductions
FETCH_EMPLOYEES_QUERY = """
SELECT 
    -- Employee ID options (Employee Code, SSN, or Clock Number)
    PM.Employee_Cd AS employee_id,
    PM.Ssn_Nbr AS SSN,
    PU.UserDefined2_Txt AS ClockNumber,

    -- Employee Name
    PM.First_Name_Txt AS first_name,
    PM.Last_Name_Txt AS last_name,

    -- Gross to Net Code
    CASE 
        WHEN PC.Pay_Cd IS NOT NULL THEN 1 -- Earnings Code
        WHEN CDC.Deduction_Cd IS NOT NULL AND PDD.Deduction_Amt > 0 THEN 3 -- Employee Deduction
        WHEN CDC.Deduction_Cd IS NOT NULL AND CDC.CompanyPremium_Amt > 0 THEN 4 -- Employer Deduction
        ELSE NULL
    END AS gross_to_net_code,

    -- Type Code (Earnings or Deduction Code)
    COALESCE(PC.Pay_Cd, CDC.Deduction_Cd) AS type_code,
    -- Temporary Rate (only used for earnings)
    CASE 
        WHEN PC.Pay_Cd IS NOT NULL THEN PPD.Current_Units_Amt
        ELSE NULL
    END AS temporary_rate,

    -- Distributed Department Code (or employee's home department if blank)
    COALESCE(PPLD.Department_Cd, PM.Department_Cd) AS distributed_dept_code,

    -- Department Description for reference
    D.Department_Desc
FROM 
    HRPremier.dbo.Person_Main PM
    LEFT JOIN HRPremier.dbo.Person_UserDefined PU ON PM.Employee_Cd = PU.Employee_Cd
    LEFT JOIN HRPremier.dbo.Person_PayData PPD ON PM.Employee_Cd = PPD.Employee_Cd
    LEFT JOIN HRPremier.dbo.Company_PayCodes PC ON PPD.Pay_Cd = PC.Pay_Cd AND PM.Company_Cd = PC.Company_Cd
    LEFT JOIN HRPremier.dbo.Person_DeductionData PDD ON PM.Employee_Cd = PDD.Employee_Cd
    LEFT JOIN HRPremier.dbo.Company_DeductionCodes CDC ON PDD.Deduction_Cd = CDC.Deduction_Cd AND PM.Company_Cd = CDC.Company_Cd
    LEFT JOIN HRPremier.dbo.Person_PayrollLaborDistribution PPLD ON PM.Employee_Cd = PPLD.Employee_Cd AND PPLD.Active_Ind = 1
    LEFT JOIN HRPremier.dbo.Department D ON PM.Company_Cd = D.Company_Cd 
        AND COALESCE(PPLD.Department_Cd, PM.Department_Cd) = D.Department_Cd
        AND PM.Division_Cd = D.Division_Cd
        AND PM.MajorFunction_Cd = D.MajorFunction_Cd
WHERE 
    PM.CompanyId = ? -- Use parameter for company ID
ORDER BY 
    PM.Employee_Cd, 
    gross_to_net_code, 
    type_code;
"""
