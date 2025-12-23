# ui/generate_t4.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import os
from db.database import get_all_employees, get_payroll_runs_by_year, get_employee
from logic.t4_generator import generate_t4_html
from ui.custom_button import CustomButton

class GenerateT4Frame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        # Header
        header = tk.Frame(self, bg="#009999", height=60)
        header.pack(fill="x")
        tk.Label(header, text="Generate T4 Slip", font=("Arial", 20, "bold"), 
                 bg="#009999", fg="white").pack(pady=15)
        
        # Main content
        content = tk.Frame(self, padx=20, pady=20)
        content.pack(fill="both", expand=True)
        
        # Form frame
        form_frame = tk.LabelFrame(content, text="T4 Generation Parameters", padx=15, pady=15, 
                                  font=("Arial", 12, "bold"), fg="#000000")
        form_frame.pack(fill="x", pady=(0, 15))
        
        # Employee selection
        tk.Label(form_frame, text="Select Employee:", font=("Arial", 11, "bold"), fg="#000000").grid(row=0, column=0, sticky="w", pady=5)
        self.employee_var = tk.StringVar()
        self.employee_combo = ttk.Combobox(form_frame, textvariable=self.employee_var, state="readonly", width=40, font=("Arial", 11))
        self.employee_combo.grid(row=0, column=1, pady=5, sticky="ew")
        
        # Year selection
        tk.Label(form_frame, text="Tax Year:", font=("Arial", 11, "bold"), fg="#000000").grid(row=1, column=0, sticky="w", pady=5)
        current_year = datetime.now().year
        self.year_var = tk.StringVar(value=str(current_year))
        year_combo = ttk.Combobox(form_frame, textvariable=self.year_var, 
                                  values=[str(y) for y in range(current_year - 5, current_year + 1)],
                                  state="readonly", width=40, font=("Arial", 11))
        year_combo.grid(row=1, column=1, pady=5, sticky="ew")
        
        form_frame.columnconfigure(1, weight=1)
        
        # Buttons
        btn_frame = tk.Frame(content)
        btn_frame.pack(fill="x", pady=(0, 15))
        
        # Calculate button - custom label-based button
        calc_btn = CustomButton(btn_frame, text="Calculate Totals", command=self.calculate_totals,
                                bg_color="#009933", padx=25, pady=10)
        calc_btn.pack(side="left", padx=5)
        
        # Generate button - custom label-based button
        gen_btn = CustomButton(btn_frame, text="Generate T4 HTML", command=self.generate_t4,
                               bg_color="#0066cc", padx=25, pady=10)
        gen_btn.pack(side="left", padx=5)
        
        # Save button - custom label-based button
        save_btn = CustomButton(btn_frame, text="Save T4 to File", command=self.save_t4,
                                bg_color="#6600cc", padx=25, pady=10)
        save_btn.pack(side="left", padx=5)
        
        # Results frame
        results_frame = tk.LabelFrame(content, text="T4 Summary", padx=15, pady=15, 
                                     font=("Arial", 12, "bold"), fg="#000000")
        results_frame.pack(fill="both", expand=True)
        
        self.output = tk.Text(results_frame, height=15, font=("Courier", 11), wrap="word",
                             bg="#ffffff", fg="#000000", relief="solid", borderwidth=1)
        scrollbar = tk.Scrollbar(results_frame, command=self.output.yview)
        self.output.config(yscrollcommand=scrollbar.set)
        self.output.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Store last T4 HTML
        self.last_t4_html = None

    def refresh(self):
        """Refresh employee list when frame is shown."""
        employees = get_all_employees()
        employee_names = [f"{emp['id']}: {emp['name']}" for emp in employees]
        self.employee_combo['values'] = employee_names
        if employee_names:
            self.employee_combo.current(0)

    def calculate_totals(self):
        """Calculate year-end totals for T4."""
        if not self.employee_var.get():
            messagebox.showerror("No Employee", "Please select an employee.")
            return
        
        try:
            employee_id = int(self.employee_var.get().split(":")[0])
            year = int(self.year_var.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Invalid employee or year selection.")
            return
        
        # Get employee info
        employee = get_employee(employee_id)
        if not employee:
            messagebox.showerror("Error", "Employee not found.")
            return
        
        # Get all payroll runs for the year
        runs = get_payroll_runs_by_year(employee_id, year)
        
        if not runs:
            messagebox.showinfo("No Records", f"No payroll records found for {employee['name']} in {year}.")
            self.output.delete("1.0", "end")
            return
        
        # Calculate totals from ALL payroll runs for the year
        total_gross = sum(run['gross'] for run in runs)
        total_cpp = sum(run['cpp_employee'] for run in runs)
        total_ei = sum(run['ei_employee'] for run in runs)
        total_fed = sum(run['federal_withholding'] for run in runs)
        total_prov = sum(run['provincial_withholding'] for run in runs)
        total_tax = total_fed + total_prov
        
        # Check annual maximums (2025 values)
        from logic import tax_tables
        max_cpp = (tax_tables.CPP_YMPE_2025 - tax_tables.CPP_BASIC_EXEMPTION) * tax_tables.CPP_RATE_2025
        max_ei = tax_tables.EI_MAX_INSURABLE_2025 * tax_tables.EI_RATE_2025
        cpp_at_max = total_cpp >= max_cpp
        ei_at_max = total_ei >= max_ei
        
        # Display results
        self.output.delete("1.0", "end")
        output_text = f"""
T4 SUMMARY FOR {year}
{'='*60}

Employee Information:
  Name:              {employee['name']}
  SIN:               {employee['sin'] or 'Not provided'}
  Province:          {employee['province']}

{'='*60}
Number of Pay Periods: {len(runs)}

T4 BOX TOTALS (YEAR-END CUMULATIVE):
{'='*60}
Box 14 - Employment income:              ${total_gross:>12.2f}
Box 16 - CPP contributions:              ${total_cpp:>12.2f}
         {'✓ Maximum reached' if cpp_at_max else f'  (Max: ${max_cpp:.2f})'}
Box 18 - EI premiums:                    ${total_ei:>12.2f}
         {'✓ Maximum reached' if ei_at_max else f'  (Max: ${max_ei:.2f})'}
Box 22 - Income tax deducted:            ${total_tax:>12.2f}
         (Federal: ${total_fed:.2f}, Provincial: ${total_prov:.2f})
{'='*60}

CONTRIBUTION TRACKING:
  Total CPP Employee:  ${total_cpp:.2f} {'(AT ANNUAL MAX)' if cpp_at_max else ''}
  Total EI Employee:   ${total_ei:.2f} {'(AT ANNUAL MAX)' if ei_at_max else ''}
  
  These totals are calculated by summing ALL {len(runs)} 
  payroll runs for {year}, ensuring accurate year-end reporting.
{'='*60}

Pay Period Details with YTD Progression:
"""
        # Show cumulative progression through the year
        ytd_cpp_running = 0
        ytd_ei_running = 0
        for run in runs:
            ytd_cpp_running += run['cpp_employee']
            ytd_ei_running += run['ei_employee']
            output_text += f"  {run['pay_date']}:  Gross ${run['gross']:>8.2f}  "
            output_text += f"CPP ${run['cpp_employee']:>6.2f} (YTD: ${ytd_cpp_running:>8.2f})  "
            output_text += f"EI ${run['ei_employee']:>6.2f} (YTD: ${ytd_ei_running:>7.2f})\n"
        
        self.output.insert("1.0", output_text)
        
        # Store totals for T4 generation
        self.totals = {
            "gross": total_gross,
            "cpp_employee": total_cpp,
            "ei_employee": total_ei,
            "tax_withheld": total_tax
        }
        self.current_employee = employee
        self.current_year = year

    def generate_t4(self):
        """Generate T4 HTML."""
        if not hasattr(self, 'totals'):
            messagebox.showerror("No Calculation", "Please calculate totals first.")
            return
        
        try:
            # Convert sqlite3.Row to dict for template compatibility
            employee_dict = dict(self.current_employee)
            html = generate_t4_html(employee_dict, self.current_year, self.totals)
            self.last_t4_html = html
            
            # Show preview in a new window
            preview_window = tk.Toplevel(self)
            preview_window.title(f"T4 Preview - {self.current_employee['name']} - {self.current_year}")
            preview_window.geometry("700x500")
            
            # Header
            header = tk.Frame(preview_window, bg="#009999", height=50)
            header.pack(fill="x")
            tk.Label(header, text="T4 Slip Preview", 
                    font=("Arial", 16, "bold"), bg="#009999", fg="white").pack(pady=10)
            
            # HTML preview (as text)
            preview_frame = tk.Frame(preview_window, padx=20, pady=20)
            preview_frame.pack(fill="both", expand=True)
            
            text_widget = tk.Text(preview_frame, font=("Courier", 10), wrap="word",
                                 bg="#ffffff", fg="#000000", relief="solid", borderwidth=1)
            scrollbar = tk.Scrollbar(preview_frame, command=text_widget.yview)
            text_widget.config(yscrollcommand=scrollbar.set)
            text_widget.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            text_widget.insert("1.0", html)
            
            # Close button - custom label-based button
            close_btn = CustomButton(preview_window, text="Close", command=preview_window.destroy,
                                     bg_color="#333333", padx=25, pady=10)
            close_btn.pack(pady=10)
            
            messagebox.showinfo("Success", "T4 HTML generated successfully! Use 'Save T4 to File' to export.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate T4: {str(e)}")

    def save_t4(self):
        """Save T4 HTML to file."""
        if not self.last_t4_html:
            messagebox.showerror("No T4", "Please generate T4 first.")
            return
        
        # Ask user for save location
        filename = f"T4_{self.current_employee['name'].replace(' ', '_')}_{self.current_year}.html"
        filepath = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML files", "*.html"), ("All files", "*.*")],
            initialfile=filename
        )
        
        if filepath:
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(self.last_t4_html)
                messagebox.showinfo("Success", f"T4 saved to:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save T4: {str(e)}")
