# logic/tax_tables.py
"""
Tax tables loader - reads from JSON config files.
Loads tax rates from data/tax_rates_{year}.json
Falls back to hardcoded 2025 values if JSON not found.
"""
import json
import os
from datetime import datetime

# Hardcoded fallback values for 2025 (in case JSON fails to load)
_FALLBACK_FEDERAL_BRACKETS = [
    (57375, 0.15),
    (114750, 0.205),
    (177882, 0.26),
    (253414, 0.29),
    (float("inf"), 0.33),
]

_FALLBACK_PROVINCIAL_BRACKETS = {
    "ON": [(52886, 0.0505), (105775, 0.0915), (150000, 0.1116), (220000, 0.1216), (float("inf"), 0.1316)],
    "QC": [(53255, 0.14), (106495, 0.19), (129590, 0.24), (float("inf"), 0.2575)],
    "BC": [(49279, 0.0506), (98560, 0.077), (113158, 0.105), (137407, 0.1229), (186306, 0.147), (259829, 0.168), (float("inf"), 0.205)],
    "AB": [(148269, 0.10), (177922, 0.12), (237230, 0.13), (355845, 0.14), (float("inf"), 0.15)],
    "SK": [(52057, 0.105), (148734, 0.125), (float("inf"), 0.145)],
    "MB": [(47000, 0.108), (100000, 0.1275), (float("inf"), 0.174)],
    "NB": [(49958, 0.094), (99916, 0.14), (185064, 0.16), (float("inf"), 0.195)],
    "NS": [(29590, 0.0879), (59180, 0.1495), (93000, 0.1667), (150000, 0.175), (float("inf"), 0.21)],
    "PE": [(32656, 0.098), (64313, 0.138), (105000, 0.167), (140000, 0.18), (float("inf"), 0.1867)],
    "NL": [(43198, 0.087), (86395, 0.145), (154244, 0.158), (215943, 0.173), (float("inf"), 0.208)],
    "YT": [(55867, 0.064), (111733, 0.09), (173205, 0.109), (500000, 0.128), (float("inf"), 0.15)],
    "NT": [(50597, 0.059), (101198, 0.086), (164525, 0.122), (float("inf"), 0.1405)],
    "NU": [(53268, 0.04), (106537, 0.07), (173205, 0.09), (float("inf"), 0.115)],
}

_FALLBACK_CPP_RATE = 0.0595
_FALLBACK_CPP_YMPE = 71300
_FALLBACK_CPP_BASIC_EXEMPTION = 3500
_FALLBACK_EI_RATE = 0.0164
_FALLBACK_EI_MAX_INSURABLE = 65700
_FALLBACK_EI_EMPLOYER_MULTIPLIER = 1.4

# Cache for loaded tax rates
_tax_rates_cache = {}

def load_tax_rates(year: int = None):
    """
    Load tax rates from JSON config file for specified year.
    If year is None, uses current year.
    Returns dict with all tax rate data.
    """
    if year is None:
        year = datetime.now().year
    
    # Check cache first
    if year in _tax_rates_cache:
        return _tax_rates_cache[year]
    
    # Try to load from JSON
    json_path = os.path.join(os.path.dirname(__file__), "..", "data", f"tax_rates_{year}.json")
    
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
            
        # Parse brackets and convert "Infinity" strings to float("inf")
        federal_brackets = [(b["limit"] if b["limit"] != "Infinity" else float("inf"), b["rate"]) 
                           for b in data["federal_brackets"]]
        
        provincial_brackets = {}
        for prov, brackets in data["provincial_brackets"].items():
            provincial_brackets[prov] = [(b["limit"] if b["limit"] != "Infinity" else float("inf"), b["rate"]) 
                                        for b in brackets]
        
        rates = {
            "year": data["year"],
            "cpp_rate": data["cpp"]["rate"],
            "cpp_ympe": data["cpp"]["ympe"],
            "cpp_basic_exemption": data["cpp"]["basic_exemption"],
            "ei_rate": data["ei"]["rate"],
            "ei_max_insurable": data["ei"]["max_insurable"],
            "ei_employer_multiplier": data["ei"]["employer_multiplier"],
            "federal_brackets": federal_brackets,
            "provincial_brackets": provincial_brackets,
        }
        
        _tax_rates_cache[year] = rates
        return rates
        
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        # Fall back to hardcoded 2025 values
        print(f"Warning: Could not load tax rates for {year}, using fallback values. Error: {e}")
        rates = {
            "year": 2025,
            "cpp_rate": _FALLBACK_CPP_RATE,
            "cpp_ympe": _FALLBACK_CPP_YMPE,
            "cpp_basic_exemption": _FALLBACK_CPP_BASIC_EXEMPTION,
            "ei_rate": _FALLBACK_EI_RATE,
            "ei_max_insurable": _FALLBACK_EI_MAX_INSURABLE,
            "ei_employer_multiplier": _FALLBACK_EI_EMPLOYER_MULTIPLIER,
            "federal_brackets": _FALLBACK_FEDERAL_BRACKETS,
            "provincial_brackets": _FALLBACK_PROVINCIAL_BRACKETS,
        }
        _tax_rates_cache[year] = rates
        return rates

# Load current year rates by default
_current_rates = load_tax_rates()

# Export as module-level variables for backward compatibility
CPP_RATE_2025 = _current_rates["cpp_rate"]
CPP_YMPE_2025 = _current_rates["cpp_ympe"]
CPP_BASIC_EXEMPTION = _current_rates["cpp_basic_exemption"]
EI_RATE_2025 = _current_rates["ei_rate"]
EI_MAX_INSURABLE_2025 = _current_rates["ei_max_insurable"]
EI_EMPLOYER_MULTIPLIER = _current_rates["ei_employer_multiplier"]
FEDERAL_BRACKETS_2025 = _current_rates["federal_brackets"]
PROVINCIAL_BRACKETS_2025 = _current_rates["provincial_brackets"]
