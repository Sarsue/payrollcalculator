# db/database.py
import sqlite3
import os
from datetime import datetime
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.validators import validate_sin, format_sin

DB_PATH = "db/payroll.db"

def get_connection():
    """Get a connection to the SQLite database."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # Enable foreign key constraints (off by default in SQLite)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    """Initialize database with schema and seed data."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create employees table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            sin TEXT,
            province TEXT DEFAULT 'ON',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create payroll_runs table with CASCADE delete
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payroll_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            pay_date TEXT NOT NULL,
            gross REAL NOT NULL,
            cpp_employee REAL,
            cpp_employer REAL,
            ei_employee REAL,
            ei_employer REAL,
            federal_withholding REAL,
            provincial_withholding REAL,
            total_deductions REAL,
            net REAL,
            period_count INTEGER DEFAULT 12,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
        )
    """)
    
    # Create company_settings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS company_settings (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            company_name TEXT NOT NULL DEFAULT 'My Company',
            business_number TEXT DEFAULT '',
            address_street TEXT DEFAULT '',
            address_city TEXT DEFAULT '',
            address_province TEXT DEFAULT 'ON',
            address_postal TEXT DEFAULT '',
            phone TEXT DEFAULT '',
            email TEXT DEFAULT '',
            payroll_account TEXT DEFAULT '',
            default_pay_frequency INTEGER DEFAULT 12,
            logo_path TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

# Employee CRUD operations
def check_sin_exists(sin: str, exclude_employee_id: int = None) -> bool:
    """Check if SIN already exists for another employee."""
    if not sin:
        return False
    
    sin_cleaned = format_sin(sin)
    conn = get_connection()
    cursor = conn.cursor()
    
    if exclude_employee_id:
        cursor.execute("""
            SELECT id FROM employees 
            WHERE sin = ? AND id != ?
        """, (sin_cleaned, exclude_employee_id))
    else:
        cursor.execute("""
            SELECT id FROM employees 
            WHERE sin = ?
        """, (sin_cleaned,))
    
    result = cursor.fetchone()
    conn.close()
    return result is not None

def add_employee(name: str, sin: str = "", province: str = "ON"):
    """Add a new employee. Validates SIN format and uniqueness."""
    # Validate SIN
    is_valid, error_msg = validate_sin(sin)
    if not is_valid:
        raise ValueError(error_msg)
    
    # Check for duplicate SIN
    if check_sin_exists(sin):
        raise ValueError(f"An employee with SIN {format_sin(sin)} already exists")
    
    # Format SIN to standard format
    sin_formatted = format_sin(sin)
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO employees (name, sin, province)
        VALUES (?, ?, ?)
    """, (name, sin_formatted, province))
    conn.commit()
    employee_id = cursor.lastrowid
    conn.close()
    return employee_id

def get_all_employees():
    """Get all employees."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employees ORDER BY name")
    employees = cursor.fetchall()
    conn.close()
    return employees

def get_employee(employee_id: int):
    """Get a single employee by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employees WHERE id = ?", (employee_id,))
    employee = cursor.fetchone()
    conn.close()
    return employee

def update_employee(employee_id: int, name: str, sin: str = "", province: str = "ON"):
    """Update an employee. Validates SIN format and uniqueness."""
    # Validate SIN
    is_valid, error_msg = validate_sin(sin)
    if not is_valid:
        raise ValueError(error_msg)
    
    # Check for duplicate SIN (excluding current employee)
    if check_sin_exists(sin, exclude_employee_id=employee_id):
        raise ValueError(f"Another employee with SIN {format_sin(sin)} already exists")
    
    # Format SIN to standard format
    sin_formatted = format_sin(sin)
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE employees 
        SET name = ?, sin = ?, province = ?
        WHERE id = ?
    """, (name, sin_formatted, province, employee_id))
    conn.commit()
    conn.close()

def delete_employee(employee_id: int):
    """Delete an employee and all associated payroll runs (CASCADE)."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Manually delete payroll runs first (failsafe in case CASCADE not enabled)
    cursor.execute("DELETE FROM payroll_runs WHERE employee_id = ?", (employee_id,))
    
    # Then delete employee
    cursor.execute("DELETE FROM employees WHERE id = ?", (employee_id,))
    conn.commit()
    conn.close()

# Payroll run operations
def check_payroll_run_exists(employee_id: int, pay_date: str):
    """Check if a payroll run already exists for the given employee and month."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Extract year and month from pay_date
    year_month = pay_date[:7]  # Gets YYYY-MM
    
    cursor.execute("""
        SELECT id FROM payroll_runs 
        WHERE employee_id = ? 
        AND strftime('%Y-%m', pay_date) = ?
    """, (employee_id, year_month))
    
    result = cursor.fetchone()
    conn.close()
    
    return result is not None

def get_latest_payroll_date(employee_id: int) -> str:
    """Get the most recent payroll run date for an employee."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT pay_date FROM payroll_runs 
        WHERE employee_id = ? 
        ORDER BY pay_date DESC 
        LIMIT 1
    """, (employee_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    return result['pay_date'] if result else None

def add_payroll_run(employee_id: int, pay_date: str, payroll_data: dict, period_count: int = 12):
    """Add a new payroll run. Raises ValueError if a run already exists for this month."""
    # Check for duplicate
    if check_payroll_run_exists(employee_id, pay_date):
        year_month = pay_date[:7]
        raise ValueError(f"A payroll run already exists for this employee in {year_month}. Each employee can only have one payroll run per month.")
    
    # Check chronological order
    latest_date = get_latest_payroll_date(employee_id)
    if latest_date and pay_date < latest_date:
        raise ValueError(f"Pay date {pay_date} cannot be earlier than the most recent payroll run ({latest_date}). Payroll runs must be in chronological order to maintain accurate YTD calculations.")
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO payroll_runs 
        (employee_id, pay_date, gross, cpp_employee, cpp_employer, 
         ei_employee, ei_employer, federal_withholding, provincial_withholding,
         total_deductions, net, period_count)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        employee_id, pay_date, payroll_data['gross'],
        payroll_data['cpp_employee'], payroll_data['cpp_employer'],
        payroll_data['ei_employee'], payroll_data['ei_employer'],
        payroll_data['federal_withholding'], payroll_data['provincial_withholding'],
        payroll_data['total_deductions'], payroll_data['net'], period_count
    ))
    conn.commit()
    run_id = cursor.lastrowid
    conn.close()
    return run_id

def get_all_payroll_runs():
    """Get all payroll runs with employee names."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.*, e.name as employee_name 
        FROM payroll_runs p
        JOIN employees e ON p.employee_id = e.id
        ORDER BY p.pay_date DESC
    """)
    runs = cursor.fetchall()
    conn.close()
    return runs

def get_payroll_runs_by_employee(employee_id: int):
    """Get all payroll runs for a specific employee."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM payroll_runs 
        WHERE employee_id = ?
        ORDER BY pay_date DESC
    """, (employee_id,))
    runs = cursor.fetchall()
    conn.close()
    return runs

def get_payroll_runs_by_year(employee_id: int, year: int):
    """Get all payroll runs for a specific employee and year."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM payroll_runs 
        WHERE employee_id = ? AND strftime('%Y', pay_date) = ?
        ORDER BY pay_date
    """, (employee_id, str(year)))
    runs = cursor.fetchall()
    conn.close()
    return runs

def get_ytd_contributions(employee_id: int, pay_date: str):
    """
    Get year-to-date CPP and EI contributions for an employee up to (but not including) the given pay date.
    Returns dict with ytd_cpp and ytd_ei.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Extract year from pay_date
    year = pay_date[:4]
    
    cursor.execute("""
        SELECT 
            COALESCE(SUM(cpp_employee), 0) as ytd_cpp,
            COALESCE(SUM(ei_employee), 0) as ytd_ei
        FROM payroll_runs 
        WHERE employee_id = ? 
        AND strftime('%Y', pay_date) = ?
        AND pay_date < ?
    """, (employee_id, year, pay_date))
    
    result = cursor.fetchone()
    conn.close()
    
    return {
        'ytd_cpp': float(result['ytd_cpp']),
        'ytd_ei': float(result['ytd_ei'])
    }

# Company settings operations
def get_company_settings():
    """Get company settings. Creates default if none exist."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM company_settings WHERE id = 1")
    settings = cursor.fetchone()
    
    # Create default settings if none exist
    if not settings:
        cursor.execute("""
            INSERT INTO company_settings (id, company_name) 
            VALUES (1, 'My Company')
        """)
        conn.commit()
        cursor.execute("SELECT * FROM company_settings WHERE id = 1")
        settings = cursor.fetchone()
    
    conn.close()
    return settings

def update_company_settings(company_name: str, business_number: str = "", 
                            address_street: str = "", address_city: str = "",
                            address_province: str = "ON", address_postal: str = "",
                            phone: str = "", email: str = "", 
                            payroll_account: str = "", default_pay_frequency: int = 12):
    """Update company settings."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO company_settings (id, company_name, business_number, 
                                     address_street, address_city, address_province, 
                                     address_postal, phone, email, payroll_account, 
                                     default_pay_frequency, updated_at)
        VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(id) DO UPDATE SET
            company_name = excluded.company_name,
            business_number = excluded.business_number,
            address_street = excluded.address_street,
            address_city = excluded.address_city,
            address_province = excluded.address_province,
            address_postal = excluded.address_postal,
            phone = excluded.phone,
            email = excluded.email,
            payroll_account = excluded.payroll_account,
            default_pay_frequency = excluded.default_pay_frequency,
            updated_at = CURRENT_TIMESTAMP
    """, (company_name, business_number, address_street, address_city, 
          address_province, address_postal, phone, email, payroll_account, 
          default_pay_frequency))
    conn.commit()
    conn.close()
