# utils/validators.py
"""
Validation utilities for payroll data.
Ensures compliance with Canadian business rules.
"""
import re
from typing import Tuple


def validate_sin(sin: str) -> Tuple[bool, str]:
    """
    Validate Canadian Social Insurance Number (SIN).
    
    SIN Rules:
    - Must be exactly 9 digits
    - Must pass Luhn algorithm check (mod 10)
    - Cannot be all zeros
    
    Returns:
        (is_valid, error_message)
    """
    if not sin:
        return (False, "SIN is required for CRA T4 reporting")
    
    # Remove spaces and hyphens
    sin_cleaned = re.sub(r'[\s\-]', '', sin)
    
    # Check if it's exactly 9 digits
    if not re.match(r'^\d{9}$', sin_cleaned):
        return (False, "SIN must be exactly 9 digits (format: XXX-XXX-XXX)")
    
    # Check if all zeros
    if sin_cleaned == "000000000":
        return (False, "Invalid SIN: cannot be all zeros")
    
    # Luhn algorithm validation
    if not _luhn_check(sin_cleaned):
        return (False, "Invalid SIN: failed checksum validation")
    
    return (True, "")


def _luhn_check(sin: str) -> bool:
    """
    Validate SIN using Luhn algorithm (mod 10 check).
    
    Algorithm:
    1. Starting from rightmost digit (excluding check digit)
    2. Double every second digit
    3. If result > 9, subtract 9
    4. Sum all digits
    5. Check if sum % 10 == 0
    """
    digits = [int(d) for d in sin]
    
    # Double every second digit (from right, positions 1, 3, 5, 7)
    for i in range(1, 9, 2):
        digits[i] *= 2
        if digits[i] > 9:
            digits[i] -= 9
    
    # Sum all digits
    total = sum(digits)
    
    # Check if divisible by 10
    return total % 10 == 0


def format_sin(sin: str) -> str:
    """
    Format SIN to standard XXX-XXX-XXX format.
    """
    sin_cleaned = re.sub(r'[\s\-]', '', sin)
    if len(sin_cleaned) == 9:
        return f"{sin_cleaned[0:3]}-{sin_cleaned[3:6]}-{sin_cleaned[6:9]}"
    return sin


def validate_gross_pay(amount: float) -> Tuple[bool, str]:
    """
    Validate gross pay amount.
    
    Rules:
    - Must be positive
    - Must be reasonable (between $0.01 and $1,000,000 per period)
    
    Returns:
        (is_valid, error_message)
    """
    if amount <= 0:
        return (False, "Gross pay must be greater than zero")
    
    if amount < 0.01:
        return (False, "Gross pay must be at least $0.01")
    
    if amount > 1000000:
        return (False, "Gross pay exceeds reasonable limit ($1,000,000 per period)")
    
    return (True, "")


def validate_pay_period_count(period_count: int) -> Tuple[bool, str]:
    """
    Validate pay period count.
    
    Standard Canadian pay periods:
    - 52: Weekly
    - 26: Bi-weekly
    - 24: Semi-monthly
    - 12: Monthly
    
    Returns:
        (is_valid, error_message)
    """
    valid_periods = [12, 24, 26, 52]
    
    if period_count not in valid_periods:
        return (False, f"Pay period count must be one of: {', '.join(map(str, valid_periods))} "
                      f"(12=Monthly, 24=Semi-monthly, 26=Bi-weekly, 52=Weekly)")
    
    return (True, "")
