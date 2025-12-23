# logic/t4_generator.py
import os
from datetime import date
from utils.resource_path import resource_path
from db.database import get_company_settings

T4_TEMPLATE = resource_path("data/t4_template.html")

def generate_t4_html(employee: dict, year: int, totals: dict) -> str:
    """
    Generate HTML for a T4 slip using the template file.
    Includes company information from database.
    Template supports placeholders for employee, company, and box amounts.
    """
    # Get company settings and convert Row to dict
    company_settings = dict(get_company_settings())
    
    # Format company address
    address_parts = []
    if company_settings['address_street']:
        address_parts.append(company_settings['address_street'])
    if company_settings['address_city']:
        city_prov = company_settings['address_city']
        if company_settings['address_province']:
            city_prov += f", {company_settings['address_province']}"
        if company_settings['address_postal']:
            city_prov += f" {company_settings['address_postal']}"
        address_parts.append(city_prov)
    company_address = ", ".join(address_parts) if address_parts else "Address not provided"
    
    if not os.path.exists(T4_TEMPLATE):
        # fallback simple inline template
        html = f"""
        <html><body>
          <h2>T4 Slip - {year}</h2>
          <h3>Employer: {company_settings.get('company_name', 'N/A')}</h3>
          <p>Business Number: {company_settings.get('business_number', 'N/A')}</p>
          <hr>
          <p>Employee: {employee.get('name')}</p>
          <p>SIN: {employee.get('sin', 'N/A')}</p>
          <hr>
          <p>Box 14 - Employment income: ${totals.get('gross', 0.00):.2f}</p>
          <p>Box 16 - CPP contributions: ${totals.get('cpp_employee', 0.00):.2f}</p>
          <p>Box 18 - EI contributions: ${totals.get('ei_employee', 0.00):.2f}</p>
          <p>Box 22 - Income tax deducted: ${totals.get('tax_withheld', 0.00):.2f}</p>
        </body></html>
        """
        return html
    
    with open(T4_TEMPLATE, "r", encoding="utf-8") as f:
        template = f.read()
    
    # Replace all placeholders
    html = template.format(
        YEAR=year,
        COMPANY_NAME=company_settings.get("company_name", "Not Set"),
        BUSINESS_NUMBER=company_settings.get("business_number", "Not Set"),
        PAYROLL_ACCOUNT=company_settings.get("payroll_account", "Not Set"),
        COMPANY_ADDRESS=company_address,
        EMP_NAME=employee.get("name", ""),
        EMP_SIN=employee.get("sin", "Not Provided"),
        BOX14=f"{totals.get('gross', 0.00):.2f}",
        BOX16=f"{totals.get('cpp_employee', 0.00):.2f}",
        BOX18=f"{totals.get('ei_employee', 0.00):.2f}",
        BOX22=f"{totals.get('tax_withheld', 0.00):.2f}",
    )
    return html
