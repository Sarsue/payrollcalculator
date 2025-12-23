# ui/run_payroll.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from logic.payroll_calc import compute_payroll
from db.database import get_all_employees, add_payroll_run, get_employee, get_ytd_contributions
from ui.custom_button import CustomButton
from utils.validators import validate_gross_pay, validate_pay_period_count

class RunPayrollFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        # Header
        header = tk.Frame(self, bg="#0066cc", height=60)
        header.pack(fill="x")
        tk.Label(header, text="Run Payroll", font=("Arial", 20, "bold"), 
                 bg="#0066cc", fg="white").pack(pady=15)
        
        # Main content
        content = tk.Frame(self, padx=20, pady=20)
        content.pack(fill="both", expand=True)
        
        # Form frame
        form = tk.LabelFrame(content, text="Payroll Details", padx=15, pady=15, 
                            font=("Arial", 12, "bold"), fg="#000000")
        form.pack(fill="x", pady=(0, 15))
        
        # Employee selection
        tk.Label(form, text="Select Employee:", font=("Arial", 11, "bold"), fg="#000000").grid(row=0, column=0, sticky="w", pady=5)
        self.employee_var = tk.StringVar()
        self.employee_combo = ttk.Combobox(form, textvariable=self.employee_var, state="readonly", width=30, font=("Arial", 11))
        self.employee_combo.grid(row=0, column=1, pady=5, sticky="ew")
        
        # Pay date - use dropdowns for better UX
        tk.Label(form, text="Pay Date:", font=("Arial", 11, "bold"), fg="#000000").grid(row=1, column=0, sticky="w", pady=5)
        date_frame = tk.Frame(form)
        date_frame.grid(row=1, column=1, pady=5, sticky="ew")
        
        # Year dropdown
        current_year = datetime.now().year
        years = [str(y) for y in range(current_year - 2, current_year + 2)]
        self.year_var = tk.StringVar(value=str(current_year))
        year_combo = ttk.Combobox(date_frame, textvariable=self.year_var, values=years, 
                                  state="readonly", width=6, font=("Arial", 11))
        year_combo.pack(side="left", padx=(0, 5))
        
        # Month dropdown
        months = ["01-Jan", "02-Feb", "03-Mar", "04-Apr", "05-May", "06-Jun",
                 "07-Jul", "08-Aug", "09-Sep", "10-Oct", "11-Nov", "12-Dec"]
        self.month_var = tk.StringVar(value=months[datetime.now().month - 1])
        month_combo = ttk.Combobox(date_frame, textvariable=self.month_var, values=months, 
                                   state="readonly", width=10, font=("Arial", 11))
        month_combo.pack(side="left", padx=(0, 5))
        
        # Day dropdown
        days = [str(d).zfill(2) for d in range(1, 32)]
        self.day_var = tk.StringVar(value=str(datetime.now().day).zfill(2))
        day_combo = ttk.Combobox(date_frame, textvariable=self.day_var, values=days, 
                                 state="readonly", width=4, font=("Arial", 11))
        day_combo.pack(side="left")
        
        # Gross pay
        tk.Label(form, text="Gross Pay (Monthly):", font=("Arial", 11, "bold"), fg="#000000").grid(row=2, column=0, sticky="w", pady=5)
        self.gross = tk.Entry(form, width=32, font=("Arial", 11))
        self.gross.insert(0, "3000.00")
        self.gross.grid(row=2, column=1, pady=5, sticky="ew")
        
        # Period count
        tk.Label(form, text="Pay Periods/Year:", font=("Arial", 11, "bold"), fg="#000000").grid(row=3, column=0, sticky="w", pady=5)
        period_frame = tk.Frame(form)
        period_frame.grid(row=3, column=1, pady=5, sticky="ew")
        self.period_count = ttk.Combobox(period_frame, values=["12", "24", "26", "52"], 
                                         state="readonly", width=10, font=("Arial", 11))
        self.period_count.set("12")
        self.period_count.pack(side="left")
        tk.Label(period_frame, text="  (12=Monthly, 24=Semi-monthly, 26=Bi-weekly, 52=Weekly)", 
                font=("Arial", 9), fg="#666666").pack(side="left")
        period_frame.columnconfigure(0, weight=1)
        
        form.columnconfigure(1, weight=1)
        
        # Buttons frame
        btn_frame = tk.Frame(content)
        btn_frame.pack(fill="x", pady=(0, 15))
        
        # Calculate button - custom label-based button
        calc_btn = CustomButton(btn_frame, text="Calculate", command=self.compute,
                                bg_color="#009933", padx=25, pady=10)
        calc_btn.pack(side="left", padx=5)
        
        # Save button - custom label-based button
        save_btn = CustomButton(btn_frame, text="Save Payroll Run", command=self.save_run,
                                bg_color="#0066cc", padx=25, pady=10)
        save_btn.pack(side="left", padx=5)
        
        # Clear button - custom label-based button
        clear_btn = CustomButton(btn_frame, text="Clear", command=self.clear_form,
                                 bg_color="#333333", padx=25, pady=10)
        clear_btn.pack(side="left", padx=5)
        
        # Results frame
        results_frame = tk.LabelFrame(content, text="Payroll Results", padx=15, pady=15, 
                                     font=("Arial", 12, "bold"), fg="#000000")
        results_frame.pack(fill="both", expand=True)
        
        self.output = tk.Text(results_frame, height=12, font=("Courier", 11), wrap="word", 
                             bg="#ffffff", fg="#000000", relief="solid", borderwidth=1)
        self.output.pack(fill="both", expand=True)
        
        # Store last calculation
        self.last_result = None

    def get_pay_date(self):
        """Get pay date in YYYY-MM-DD format from dropdowns."""
        year = self.year_var.get()
        month = self.month_var.get().split('-')[0]  # Extract '01' from '01-Jan'
        day = self.day_var.get()
        return f"{year}-{month}-{day}"

    def refresh(self):
        """Refresh employee list when frame is shown."""
        self.refresh_employee_list()

    def refresh_employee_list(self, silent=False):
        """Refresh the employee dropdown list."""
        employees = get_all_employees()
        employee_names = [f"{emp['id']}: {emp['name']} ({emp['province']})" for emp in employees]
        self.employee_combo['values'] = employee_names
        if employee_names:
            # Try to keep the same selection if it still exists
            current_selection = self.employee_var.get()
            if current_selection in employee_names:
                self.employee_combo.set(current_selection)
            else:
                self.employee_combo.current(0)
        else:
            self.employee_var.set("")
            if not silent:
                messagebox.showinfo("No Employees", "No employees found. Please add employees first.")

    def compute(self):
        """Calculate payroll deductions."""
        try:
            gross = float(self.gross.get())
            period_count = int(self.period_count.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numeric values for gross pay and period count.")
            return
        
        # Validate gross pay
        is_valid, error_msg = validate_gross_pay(gross)
        if not is_valid:
            messagebox.showerror("Invalid Gross Pay", error_msg)
            return
        
        # Validate period count
        is_valid, error_msg = validate_pay_period_count(period_count)
        if not is_valid:
            messagebox.showerror("Invalid Pay Period", error_msg)
            return
        
        if not self.employee_var.get():
            messagebox.showerror("No Employee", "Please select an employee.")
            return
        
        # Get employee ID from selection
        employee_id = int(self.employee_var.get().split(":")[0])
        employee = get_employee(employee_id)
        
        # Check if employee exists
        if not employee:
            messagebox.showerror("Employee Not Found", 
                               "The selected employee no longer exists. Please refresh the employee list.")
            return
        
        province = employee['province']
        
        # Get YTD contributions for this employee up to the pay date
        pay_date = self.get_pay_date()
        
        # Validate pay date format
        try:
            from datetime import datetime
            datetime.strptime(pay_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Invalid Date", "Pay date must be in YYYY-MM-DD format.")
            return
        
        ytd_data = get_ytd_contributions(employee_id, pay_date)
        
        # Calculate payroll with YTD tracking
        result = compute_payroll(gross, province, period_count, 
                                ytd_cpp=ytd_data['ytd_cpp'], 
                                ytd_ei=ytd_data['ytd_ei'])
        self.last_result = result
        
        # Display results
        self.output.delete("1.0", "end")
        output_text = f"""
PAYROLL CALCULATION RESULTS
{'='*50}

Employee:          {employee['name']}
Province:          {province}
Pay Date:          {self.get_pay_date()}
Pay Periods/Year:  {period_count}

{'='*50}
EARNINGS
{'='*50}
Gross Pay:                             ${result['gross']:>10.2f}

DEDUCTIONS
{'='*50}
CPP Employee Contribution:             ${result['cpp_employee']:>10.2f}
EI Employee Premium:                   ${result['ei_employee']:>10.2f}
Federal Income Tax:                    ${result['federal_withholding']:>10.2f}
Provincial Income Tax:                 ${result['provincial_withholding']:>10.2f}
{'='*50}
Total Deductions:                      ${result['total_deductions']:>10.2f}

{'='*50}
NET PAY:                               ${result['net']:>10.2f}
{'='*50}

EMPLOYER COSTS
{'='*50}
CPP Employer Contribution:             ${result['cpp_employer']:>10.2f}
EI Employer Premium:                   ${result['ei_employer']:>10.2f}
Total Employer Cost:                   ${result['cpp_employer'] + result['ei_employer']:>10.2f}

{'='*50}
CRA REMITTANCE (Amount to Send to CRA)
{'='*50}
Employee CPP:                          ${result['cpp_employee']:>10.2f}
Employee EI:                           ${result['ei_employee']:>10.2f}
Federal Income Tax:                    ${result['federal_withholding']:>10.2f}
Provincial Income Tax:                 ${result['provincial_withholding']:>10.2f}
Employer CPP:                          ${result['cpp_employer']:>10.2f}
Employer EI:                           ${result['ei_employer']:>10.2f}
{'='*50}
TOTAL CRA REMITTANCE:                  ${result['cpp_employee'] + result['ei_employee'] + result['federal_withholding'] + result['provincial_withholding'] + result['cpp_employer'] + result['ei_employer']:>10.2f}
{'='*50}

{'='*50}
YEAR-TO-DATE TRACKING
{'='*50}
YTD CPP (before this pay):             ${ytd_data['ytd_cpp']:>10.2f}
YTD EI (before this pay):              ${ytd_data['ytd_ei']:>10.2f}
YTD CPP (after this pay):              ${result['ytd_cpp_after']:>10.2f}
YTD EI (after this pay):               ${result['ytd_ei_after']:>10.2f}

{'='*50}
⚠️  IMPORTANT TAX WITHHOLDING NOTICE
{'='*50}
Tax withholding is SIMPLIFIED and does NOT account for:
- Basic Personal Amount (BPA)
- TD1 claim codes or credits
- CPP/EI deductions reducing taxable income

This will result in OVER-WITHHOLDING of taxes.

For CRA-compliant withholding, use:
- CRA PDOC (Payroll Deductions Online Calculator)
- T4127 tables with proper claim codes

This tool is for estimation only. Verify actual
withholding amounts before processing payroll.
"""
        self.output.insert("1.0", output_text)

    def save_run(self):
        """Save the payroll run to the database."""
        if not self.last_result:
            messagebox.showerror("No Calculation", "Please calculate payroll first before saving.")
            return
        
        if not self.employee_var.get():
            messagebox.showerror("No Employee", "Please select an employee.")
            return
        
        try:
            employee_id = int(self.employee_var.get().split(":")[0])
            pay_date = self.get_pay_date()
            period_count = int(self.period_count.get())
            
            # Validate date format
            try:
                datetime.strptime(pay_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Invalid Date", "Please enter date in YYYY-MM-DD format.")
                return
            
            run_id = add_payroll_run(employee_id, pay_date, self.last_result, period_count)
            messagebox.showinfo("Success", f"Payroll run saved successfully! (ID: {run_id})")
            
        except ValueError as e:
            # This catches duplicate payroll run errors from the database
            messagebox.showerror("Duplicate Payroll Run", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save payroll run: {str(e)}")

    def clear_form(self):
        """Clear the form and results."""
        self.gross.delete(0, tk.END)
        self.gross.insert(0, "3000.00")
        self.period_count.set("12")
        # Reset date to today
        current_year = datetime.now().year
        current_month = datetime.now().month
        current_day = datetime.now().day
        self.year_var.set(str(current_year))
        months = ["01-Jan", "02-Feb", "03-Mar", "04-Apr", "05-May", "06-Jun",
                 "07-Jul", "08-Aug", "09-Sep", "10-Oct", "11-Nov", "12-Dec"]
        self.month_var.set(months[current_month - 1])
        self.day_var.set(str(current_day).zfill(2))
        self.output.delete("1.0", "end")
        self.last_result = None
