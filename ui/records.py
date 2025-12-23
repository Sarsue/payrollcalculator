# ui/records.py
import tkinter as tk
from tkinter import ttk, messagebox
from db.database import get_all_payroll_runs
from ui.custom_button import CustomButton

class RecordsFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        # Header
        header = tk.Frame(self, bg="#cc6600", height=60)
        header.pack(fill="x")
        tk.Label(header, text="Payroll Records", font=("Arial", 20, "bold"), 
                 bg="#cc6600", fg="white").pack(pady=15)
        
        # Main content
        content = tk.Frame(self, padx=20, pady=20)
        content.pack(fill="both", expand=True)
        
        # Top controls
        controls = tk.Frame(content)
        controls.pack(fill="x", pady=(0, 10))
        
        # Refresh button - custom label-based button
        refresh_btn = CustomButton(controls, text="Refresh", command=self.load_records,
                                   bg_color="#0066cc", padx=20, pady=10)
        refresh_btn.pack(side="left", padx=5)
        
        # Details button - custom label-based button
        details_btn = CustomButton(controls, text="View Details", command=self.view_details,
                                   bg_color="#009933", padx=20, pady=10)
        details_btn.pack(side="left", padx=5)
        
        # Treeview for records
        tree_frame = tk.Frame(content)
        tree_frame.pack(fill="both", expand=True)
        
        scrollbar_y = tk.Scrollbar(tree_frame)
        scrollbar_y.pack(side="right", fill="y")
        
        scrollbar_x = tk.Scrollbar(tree_frame, orient="horizontal")
        scrollbar_x.pack(side="bottom", fill="x")
        
        # Configure style for better readability
        style = ttk.Style()
        # Use a theme that works well on all platforms
        try:
            style.theme_use('clam')  # Works best across platforms
        except:
            pass
        
        style.configure("RecordsTree.Treeview", 
                       font=("Arial", 10), 
                       rowheight=25,
                       background="white",
                       foreground="black",
                       fieldbackground="white")
        style.configure("RecordsTree.Treeview.Heading", 
                       font=("Arial", 11, "bold"),
                       background="#cc6600",
                       foreground="white",
                       relief="raised",
                       borderwidth=2)
        style.map("RecordsTree.Treeview", 
                 background=[("selected", "#cc6600")], 
                 foreground=[("selected", "white")])
        style.map("RecordsTree.Treeview.Heading",
                 background=[("active", "#ff8800")],
                 foreground=[("active", "white")])
        
        self.tree = ttk.Treeview(tree_frame, 
                                 columns=("ID", "Employee", "Date", "Gross", "CPP", "EI", "Fed Tax", "Prov Tax", "Total Ded", "Net"),
                                 show="headings", 
                                 yscrollcommand=scrollbar_y.set,
                                 xscrollcommand=scrollbar_x.set,
                                 style="RecordsTree.Treeview")
        
        # Column headings
        self.tree.heading("ID", text="ID")
        self.tree.heading("Employee", text="Employee")
        self.tree.heading("Date", text="Pay Date")
        self.tree.heading("Gross", text="Gross")
        self.tree.heading("CPP", text="CPP (Emp)")
        self.tree.heading("EI", text="EI (Emp)")
        self.tree.heading("Fed Tax", text="Fed Tax")
        self.tree.heading("Prov Tax", text="Prov Tax")
        self.tree.heading("Total Ded", text="Total Ded")
        self.tree.heading("Net", text="Net Pay")
        
        # Column widths
        self.tree.column("ID", width=50)
        self.tree.column("Employee", width=150)
        self.tree.column("Date", width=100)
        self.tree.column("Gross", width=80)
        self.tree.column("CPP", width=80)
        self.tree.column("EI", width=80)
        self.tree.column("Fed Tax", width=80)
        self.tree.column("Prov Tax", width=80)
        self.tree.column("Total Ded", width=90)
        self.tree.column("Net", width=90)
        
        self.tree.pack(fill="both", expand=True)
        scrollbar_y.config(command=self.tree.yview)
        scrollbar_x.config(command=self.tree.xview)
        
        # Summary frame
        summary_frame = tk.LabelFrame(content, text="Summary", padx=15, pady=10, 
                                     font=("Arial", 12, "bold"), fg="#000000")
        summary_frame.pack(fill="x", pady=(10, 0))
        
        self.summary_label = tk.Label(summary_frame, text="No records loaded", 
                                      font=("Arial", 11, "bold"), fg="#000000")
        self.summary_label.pack()

    def refresh(self):
        """Refresh records when frame is shown."""
        self.load_records()

    def load_records(self):
        """Load all payroll records."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Load records
        records = get_all_payroll_runs()
        
        total_gross = 0.0
        total_net = 0.0
        total_deductions = 0.0
        total_cra_remittance = 0.0
        
        for record in records:
            # Calculate CRA remittance for this record
            cra_remittance = (
                record['cpp_employee'] + 
                record['ei_employee'] + 
                record['federal_withholding'] + 
                record['provincial_withholding'] + 
                record['cpp_employer'] + 
                record['ei_employer']
            )
            
            self.tree.insert("", "end", values=(
                record['id'],
                record['employee_name'],
                record['pay_date'],
                f"${record['gross']:.2f}",
                f"${record['cpp_employee']:.2f}",
                f"${record['ei_employee']:.2f}",
                f"${record['federal_withholding']:.2f}",
                f"${record['provincial_withholding']:.2f}",
                f"${record['total_deductions']:.2f}",
                f"${record['net']:.2f}"
            ))
            
            total_gross += record['gross']
            total_net += record['net']
            total_deductions += record['total_deductions']
            total_cra_remittance += cra_remittance
        
        # Update summary
        count = len(records)
        if count > 0:
            self.summary_label.config(
                text=f"Total Records: {count} | Gross: ${total_gross:.2f} | "
                     f"Net: ${total_net:.2f} | CRA Remittance: ${total_cra_remittance:.2f}"
            )
        else:
            self.summary_label.config(text="No records found")

    def view_details(self):
        """View detailed information for selected record."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a payroll record to view details.")
            return
        
        item = self.tree.item(selection[0])
        values = item['values']
        
        # Create detail window
        detail_window = tk.Toplevel(self)
        detail_window.title(f"Payroll Record Details - ID {values[0]}")
        detail_window.geometry("500x400")
        
        # Header
        header = tk.Frame(detail_window, bg="#0066cc", height=50)
        header.pack(fill="x")
        tk.Label(header, text=f"Payroll Record - ID {values[0]}", 
                font=("Arial", 16, "bold"), bg="#0066cc", fg="white").pack(pady=10)
        
        # Details
        details_frame = tk.Frame(detail_window, padx=20, pady=20)
        details_frame.pack(fill="both", expand=True)
        
        details_text = f"""
PAYROLL RECORD DETAILS
{'='*50}

Record ID:         {values[0]}
Employee:          {values[1]}
Pay Date:          {values[2]}

{'='*50}
EARNINGS
{'='*50}
Gross Pay:                             {values[3]}

DEDUCTIONS
{'='*50}
CPP Employee Contribution:             {values[4]}
EI Employee Premium:                   {values[5]}
Federal Income Tax:                    {values[6]}
Provincial Income Tax:                 {values[7]}
{'='*50}
Total Deductions:                      {values[8]}

{'='*50}
NET PAY:                               {values[9]}
{'='*50}
"""
        
        text_widget = tk.Text(details_frame, font=("Courier", 11, "bold"), wrap="word",
                             bg="#ffffff", fg="#000000", relief="solid", borderwidth=1)
        text_widget.pack(fill="both", expand=True)
        text_widget.insert("1.0", details_text)
        text_widget.config(state="disabled")
        
        # Close button - custom label-based button
        close_btn = CustomButton(detail_window, text="Close", command=detail_window.destroy,
                                 bg_color="#333333", padx=25, pady=10)
        close_btn.pack(pady=10)
