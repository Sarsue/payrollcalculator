# ui/settings.py
import tkinter as tk
from tkinter import ttk, messagebox
from db.database import get_company_settings, update_company_settings
from ui.custom_button import CustomButton

class SettingsFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        # Header
        header = tk.Frame(self, bg="#6600cc", height=60)
        header.pack(fill="x")
        tk.Label(header, text="Company Settings", font=("Arial", 20, "bold"), 
                 bg="#6600cc", fg="white").pack(pady=15)
        
        # Main content
        content = tk.Frame(self, padx=20, pady=20)
        content.pack(fill="both", expand=True)
        
        # Instructions
        info_frame = tk.Frame(content, bg="#e8f4f8", relief="solid", borderwidth=1, padx=15, pady=10)
        info_frame.pack(fill="x", pady=(0, 15))
        tk.Label(info_frame, text="ℹ️ Company Information", font=("Arial", 12, "bold"), 
                bg="#e8f4f8", fg="#0066cc").pack(anchor="w")
        tk.Label(info_frame, text="This information will appear on T4 slips and reports. Business Number is required for CRA compliance.", 
                font=("Arial", 10), bg="#e8f4f8", fg="#333333", wraplength=900, justify="left").pack(anchor="w")
        
        # Company Info Form
        form_frame = tk.LabelFrame(content, text="Company Information", padx=15, pady=15, 
                                  font=("Arial", 12, "bold"), fg="#000000")
        form_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        # Company Name
        tk.Label(form_frame, text="Company Name:*", font=("Arial", 11, "bold"), fg="#000000").grid(row=0, column=0, sticky="w", pady=5)
        self.company_name = tk.Entry(form_frame, width=50, font=("Arial", 11))
        self.company_name.grid(row=0, column=1, pady=5, sticky="ew", padx=(10, 0))
        
        # Business Number
        tk.Label(form_frame, text="Business Number (BN):*", font=("Arial", 11, "bold"), fg="#000000").grid(row=1, column=0, sticky="w", pady=5)
        self.business_number = tk.Entry(form_frame, width=50, font=("Arial", 11))
        self.business_number.grid(row=1, column=1, pady=5, sticky="ew", padx=(10, 0))
        tk.Label(form_frame, text="Format: 123456789RP0001", font=("Arial", 9), fg="#666666").grid(row=1, column=2, sticky="w", padx=(5, 0))
        
        # Payroll Account
        tk.Label(form_frame, text="Payroll Account (RP):*", font=("Arial", 11, "bold"), fg="#000000").grid(row=2, column=0, sticky="w", pady=5)
        self.payroll_account = tk.Entry(form_frame, width=50, font=("Arial", 11))
        self.payroll_account.grid(row=2, column=1, pady=5, sticky="ew", padx=(10, 0))
        tk.Label(form_frame, text="Format: RP0001", font=("Arial", 9), fg="#666666").grid(row=2, column=2, sticky="w", padx=(5, 0))
        
        # Address
        tk.Label(form_frame, text="Street Address:", font=("Arial", 11, "bold"), fg="#000000").grid(row=3, column=0, sticky="w", pady=5)
        self.address_street = tk.Entry(form_frame, width=50, font=("Arial", 11))
        self.address_street.grid(row=3, column=1, pady=5, sticky="ew", padx=(10, 0))
        
        tk.Label(form_frame, text="City:", font=("Arial", 11, "bold"), fg="#000000").grid(row=4, column=0, sticky="w", pady=5)
        self.address_city = tk.Entry(form_frame, width=50, font=("Arial", 11))
        self.address_city.grid(row=4, column=1, pady=5, sticky="ew", padx=(10, 0))
        
        tk.Label(form_frame, text="Province:", font=("Arial", 11, "bold"), fg="#000000").grid(row=5, column=0, sticky="w", pady=5)
        self.address_province = ttk.Combobox(form_frame, 
                                            values=["ON", "QC", "BC", "AB", "SK", "MB", "NB", "NS", "PE", "NL", "YT", "NT", "NU"],
                                            state="readonly", width=48, font=("Arial", 11))
        self.address_province.grid(row=5, column=1, pady=5, sticky="ew", padx=(10, 0))
        
        tk.Label(form_frame, text="Postal Code:", font=("Arial", 11, "bold"), fg="#000000").grid(row=6, column=0, sticky="w", pady=5)
        self.address_postal = tk.Entry(form_frame, width=50, font=("Arial", 11))
        self.address_postal.grid(row=6, column=1, pady=5, sticky="ew", padx=(10, 0))
        tk.Label(form_frame, text="Format: A1A 1A1", font=("Arial", 9), fg="#666666").grid(row=6, column=2, sticky="w", padx=(5, 0))
        
        # Contact Info
        tk.Label(form_frame, text="Phone:", font=("Arial", 11, "bold"), fg="#000000").grid(row=7, column=0, sticky="w", pady=5)
        self.phone = tk.Entry(form_frame, width=50, font=("Arial", 11))
        self.phone.grid(row=7, column=1, pady=5, sticky="ew", padx=(10, 0))
        
        tk.Label(form_frame, text="Email:", font=("Arial", 11, "bold"), fg="#000000").grid(row=8, column=0, sticky="w", pady=5)
        self.email = tk.Entry(form_frame, width=50, font=("Arial", 11))
        self.email.grid(row=8, column=1, pady=5, sticky="ew", padx=(10, 0))
        
        # Default Pay Frequency
        tk.Label(form_frame, text="Default Pay Frequency:", font=("Arial", 11, "bold"), fg="#000000").grid(row=9, column=0, sticky="w", pady=5)
        self.pay_frequency = ttk.Combobox(form_frame, 
                                         values=["52 - Weekly", "26 - Bi-weekly", "24 - Semi-monthly", "12 - Monthly"],
                                         state="readonly", width=48, font=("Arial", 11))
        self.pay_frequency.grid(row=9, column=1, pady=5, sticky="ew", padx=(10, 0))
        
        form_frame.columnconfigure(1, weight=1)
        
        # Buttons
        btn_frame = tk.Frame(content)
        btn_frame.pack(fill="x", pady=(0, 10))
        
        # Save button
        save_btn = CustomButton(btn_frame, text="Save Settings", command=self.save_settings,
                                bg_color="#009933", padx=25, pady=10)
        save_btn.pack(side="left", padx=5)
        
        # Load button
        load_btn = CustomButton(btn_frame, text="Reload from Database", command=self.load_settings,
                                bg_color="#0066cc", padx=25, pady=10)
        load_btn.pack(side="left", padx=5)
        
        # Help text
        help_frame = tk.Frame(content, bg="#fff4e6", relief="solid", borderwidth=1, padx=15, pady=10)
        help_frame.pack(fill="x")
        tk.Label(help_frame, text="💡 Tips:", font=("Arial", 11, "bold"), 
                bg="#fff4e6", fg="#cc6600").pack(anchor="w")
        tips = [
            "• Business Number (BN) is a 9-digit number followed by program identifier (e.g., RP0001)",
            "• You can find your BN on CRA correspondence or at canada.ca/business-number",
            "• Payroll account starts with 'RP' and is required for remitting payroll deductions",
            "• All required fields (*) must be filled for T4 generation"
        ]
        for tip in tips:
            tk.Label(help_frame, text=tip, font=("Arial", 10), 
                    bg="#fff4e6", fg="#333333").pack(anchor="w")

    def refresh(self):
        """Load settings when frame is shown."""
        self.load_settings()

    def load_settings(self):
        """Load company settings from database."""
        try:
            settings = get_company_settings()
            
            self.company_name.delete(0, tk.END)
            self.company_name.insert(0, settings['company_name'])
            
            self.business_number.delete(0, tk.END)
            self.business_number.insert(0, settings['business_number'] or "")
            
            self.payroll_account.delete(0, tk.END)
            self.payroll_account.insert(0, settings['payroll_account'] or "")
            
            self.address_street.delete(0, tk.END)
            self.address_street.insert(0, settings['address_street'] or "")
            
            self.address_city.delete(0, tk.END)
            self.address_city.insert(0, settings['address_city'] or "")
            
            self.address_province.set(settings['address_province'] or "ON")
            
            self.address_postal.delete(0, tk.END)
            self.address_postal.insert(0, settings['address_postal'] or "")
            
            self.phone.delete(0, tk.END)
            self.phone.insert(0, settings['phone'] or "")
            
            self.email.delete(0, tk.END)
            self.email.insert(0, settings['email'] or "")
            
            # Set pay frequency
            freq_map = {52: "52 - Weekly", 26: "26 - Bi-weekly", 
                       24: "24 - Semi-monthly", 12: "12 - Monthly"}
            freq = settings['default_pay_frequency'] or 12
            self.pay_frequency.set(freq_map.get(freq, "12 - Monthly"))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load settings: {str(e)}")

    def save_settings(self):
        """Save company settings to database."""
        company_name = self.company_name.get().strip()
        
        if not company_name:
            messagebox.showerror("Validation Error", "Company Name is required.")
            return
        
        try:
            # Parse pay frequency
            freq_str = self.pay_frequency.get()
            if freq_str:
                freq = int(freq_str.split(" - ")[0])
            else:
                freq = 12
            
            update_company_settings(
                company_name=company_name,
                business_number=self.business_number.get().strip(),
                address_street=self.address_street.get().strip(),
                address_city=self.address_city.get().strip(),
                address_province=self.address_province.get(),
                address_postal=self.address_postal.get().strip(),
                phone=self.phone.get().strip(),
                email=self.email.get().strip(),
                payroll_account=self.payroll_account.get().strip(),
                default_pay_frequency=freq
            )
            
            messagebox.showinfo("Success", "Company settings saved successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
