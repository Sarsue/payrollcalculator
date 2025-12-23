# logic/payroll_calc.py
from typing import Tuple
import math
from . import tax_tables

def calc_cpp_for_period(gross: float, period_count: int = 12, ytd_cpp: float = 0.0) -> Tuple[float, float]:
    """
    Calculate CPP employee and employer contribution for ONE pay period.
    Considers YTD contributions to respect annual maximum.
    Returns (employee_cpp, employer_cpp).
    """
    # Calculate annual maximum CPP contribution
    max_pensionable = tax_tables.CPP_YMPE_2025 - tax_tables.CPP_BASIC_EXEMPTION
    annual_max_cpp = max_pensionable * tax_tables.CPP_RATE_2025
    
    # Check if already at max
    if ytd_cpp >= annual_max_cpp:
        return (0.0, 0.0)
    
    # Calculate normal per-period contribution
    annual_gross = gross * period_count
    pensionable = max(0.0, min(annual_gross - tax_tables.CPP_BASIC_EXEMPTION, max_pensionable))
    annual_cpp = pensionable * tax_tables.CPP_RATE_2025
    per_period = annual_cpp / period_count
    
    # Limit to remaining room
    remaining_room = annual_max_cpp - ytd_cpp
    per_period = min(per_period, remaining_room)
    
    return (round(per_period, 2), round(per_period, 2))

def calc_ei_for_period(gross: float, period_count: int = 12, ytd_ei: float = 0.0) -> Tuple[float, float]:
    """
    Calculate EI employee and employer per-pay-period premiums.
    Considers YTD contributions to respect annual maximum.
    """
    # Calculate annual maximum EI contribution
    annual_max_ei = tax_tables.EI_MAX_INSURABLE_2025 * tax_tables.EI_RATE_2025
    
    # Check if already at max
    if ytd_ei >= annual_max_ei:
        return (0.0, 0.0)
    
    # Calculate normal per-period contribution
    annual_gross = gross * period_count
    insurable = min(annual_gross, tax_tables.EI_MAX_INSURABLE_2025)
    annual_ei = insurable * tax_tables.EI_RATE_2025
    per_period_emp = annual_ei / period_count
    
    # Limit to remaining room
    remaining_room = annual_max_ei - ytd_ei
    per_period_emp = min(per_period_emp, remaining_room)
    
    employer = per_period_emp * tax_tables.EI_EMPLOYER_MULTIPLIER
    return (round(per_period_emp, 2), round(employer, 2))

def progressive_tax_from_brackets(amount: float, brackets: list) -> float:
    """
    Generic progressive tax calculator given brackets list of (upper_limit, rate).
    amount is annual taxable income.
    """
    prev = 0.0
    tax = 0.0
    for upper, rate in brackets:
        taxable = max(0.0, min(amount, upper) - prev)
        tax += taxable * rate
        prev = upper
        if amount <= upper:
            break
    return tax

def calc_federal_and_provincial_withholding(gross: float, province: str = "ON", period_count: int = 12) -> Tuple[float, float]:
    """
    Approximate withholding: annualize gross, compute federal & provincial tax, then divide by periods.
    This is a simplified withholding (does not consider credits, personal amounts, CPP/EI reductions).
    For production, consult T4127 tables or PDOC for exact payroll withholding.
    """
    annual = gross * period_count
    fed_tax = progressive_tax_from_brackets(annual, tax_tables.FEDERAL_BRACKETS_2025)
    prov_brackets = tax_tables.PROVINCIAL_BRACKETS_2025.get(province.upper())
    if not prov_brackets:
        prov_tax = 0.0
    else:
        prov_tax = progressive_tax_from_brackets(annual, prov_brackets)
    # divide back to per-period withholding
    return (round(fed_tax / period_count,2), round(prov_tax / period_count,2))

def compute_payroll(gross: float, province: str="ON", period_count:int=12, ytd_cpp: float=0.0, ytd_ei: float=0.0):
    """
    Compute all deductions and return a dict.
    Includes YTD tracking to respect CPP/EI annual maximums.
    { gross, cpp_employee, cpp_employer, ei_employee, ei_employer, federal, provincial, net }
    """
    cpp_emp, cpp_er = calc_cpp_for_period(gross, period_count, ytd_cpp)
    ei_emp, ei_er = calc_ei_for_period(gross, period_count, ytd_ei)
    fed, prov = calc_federal_and_provincial_withholding(gross, province, period_count)
    total_deductions = round(cpp_emp + ei_emp + fed + prov, 2)
    net = round(gross - total_deductions, 2)
    return {
        "gross": round(gross,2),
        "cpp_employee": cpp_emp,
        "cpp_employer": cpp_er,
        "ei_employee": ei_emp,
        "ei_employer": ei_er,
        "federal_withholding": fed,
        "provincial_withholding": prov,
        "total_deductions": total_deductions,
        "net": net,
        "ytd_cpp_after": round(ytd_cpp + cpp_emp, 2),
        "ytd_ei_after": round(ytd_ei + ei_emp, 2)
    }
