# ui/employees.py
import tkinter as tk
from tkinter import ttk, messagebox
from db.database import get_all_employees, add_employee, update_employee, delete_employee, get_employee
from ui.custom_button import CustomButton

class EmployeesFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.selected_employee_id = None
        self.create_widgets()

    def create_widgets(self):
        # Header
        header = tk.Frame(self, bg="#6600cc", height=60)
        header.pack(fill="x")
        tk.Label(header, text="Employee Management", font=("Arial", 20, "bold"), 
                 bg="#6600cc", fg="white").pack(pady=15)
        
        # Main content - split into two columns
        content = tk.Frame(self, padx=20, pady=20)
        content.pack(fill="both", expand=True)
        
        # Left side - Employee list
        left_frame = tk.Frame(content)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        tk.Label(left_frame, text="Employee List", font=("Arial", 13, "bold"), fg="#000000").pack(anchor="w", pady=(0, 5))
        
        # Treeview for employee list
        tree_frame = tk.Frame(left_frame)
        tree_frame.pack(fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")
        
        # Configure style for better readability
        style = ttk.Style()
        # Use a theme that works well on all platforms
        try:
            style.theme_use('clam')  # Works best across platforms
        except:
            pass
        
        style.configure("EmployeeTree.Treeview", 
                       font=("Arial", 10), 
                       rowheight=25,
                       background="white",
                       foreground="black",
                       fieldbackground="white")
        style.configure("EmployeeTree.Treeview.Heading", 
                       font=("Arial", 11, "bold"), 
                       background="#0066cc", 
                       foreground="white",
                       relief="raised",
                       borderwidth=2)
        style.map("EmployeeTree.Treeview", 
                 background=[("selected", "#0066cc")], 
                 foreground=[("selected", "white")])
        style.map("EmployeeTree.Treeview.Heading",
                 background=[("active", "#0088ee")],
                 foreground=[("active", "white")])
        
        self.tree = ttk.Treeview(tree_frame, columns=("ID", "Name", "SIN", "Province"), 
                                 show="headings", yscrollcommand=scrollbar.set,
                                 style="EmployeeTree.Treeview")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("SIN", text="SIN")
        self.tree.heading("Province", text="Province")
        
        self.tree.column("ID", width=50)
        self.tree.column("Name", width=200)
        self.tree.column("SIN", width=120)
        self.tree.column("Province", width=80)
        
        self.tree.pack(fill="both", expand=True)
        scrollbar.config(command=self.tree.yview)
        
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        
        # Right side - Employee form
        right_frame = tk.Frame(content)
        right_frame.pack(side="right", fill="both", padx=(10, 0))
        
        form_frame = tk.LabelFrame(right_frame, text="Employee Details", padx=15, pady=15, 
                                   font=("Arial", 12, "bold"), fg="#000000")
        form_frame.pack(fill="x")
        
        # Name
        tk.Label(form_frame, text="Full Name:", font=("Arial", 11, "bold"), fg="#000000").grid(row=0, column=0, sticky="w", pady=5)
        self.name_entry = tk.Entry(form_frame, width=30, font=("Arial", 11))
        self.name_entry.grid(row=0, column=1, pady=5, sticky="ew")
        
        # SIN
        tk.Label(form_frame, text="SIN (Required):", font=("Arial", 11, "bold"), fg="#000000").grid(row=1, column=0, sticky="w", pady=5)
        self.sin_entry = tk.Entry(form_frame, width=30, font=("Arial", 11))
        self.sin_entry.grid(row=1, column=1, pady=5, sticky="ew")
        tk.Label(form_frame, text="Format: XXX-XXX-XXX", font=("Arial", 9), fg="#666666").grid(row=1, column=2, sticky="w", padx=(5, 0))
        
        # Province
        tk.Label(form_frame, text="Province:", font=("Arial", 11, "bold"), fg="#000000").grid(row=2, column=0, sticky="w", pady=5)
        self.province_var = tk.StringVar(value="ON")
        province_combo = ttk.Combobox(form_frame, textvariable=self.province_var, 
                                      values=["ON", "QC", "BC", "AB", "SK", "MB", "NB", "NS", "PE", "NL", "YT", "NT", "NU"],
                                      state="readonly", width=28, font=("Arial", 11))
        province_combo.grid(row=2, column=1, pady=5, sticky="ew")
        
        form_frame.columnconfigure(1, weight=1)
        
        # Buttons
        btn_frame = tk.Frame(right_frame)
        btn_frame.pack(fill="x", pady=15)
        
        # Add button - custom label-based button
        add_btn = CustomButton(btn_frame, text="Add New", command=self.add_new,
                               bg_color="#009933", padx=15, pady=10)
        add_btn.pack(fill="x", pady=2)
        
        # Update button - custom label-based button
        update_btn = CustomButton(btn_frame, text="Update", command=self.update_existing,
                                  bg_color="#0066cc", padx=15, pady=10)
        update_btn.pack(fill="x", pady=2)
        
        # Delete button - custom label-based button
        delete_btn = CustomButton(btn_frame, text="Delete", command=self.delete_existing,
                                  bg_color="#cc0000", padx=15, pady=10)
        delete_btn.pack(fill="x", pady=2)
        
        # Clear button - custom label-based button
        clear_btn = CustomButton(btn_frame, text="Clear Form", command=self.clear_form,
                                 bg_color="#333333", padx=15, pady=10)
        clear_btn.pack(fill="x", pady=2)

    def refresh(self):
        """Refresh employee list."""
        self.load_employees()

    def load_employees(self):
        """Load all employees into the treeview."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Load employees
        employees = get_all_employees()
        for emp in employees:
            self.tree.insert("", "end", values=(emp['id'], emp['name'], emp['sin'], emp['province']))

    def on_select(self, event):
        """Handle employee selection."""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            values = item['values']
            self.selected_employee_id = values[0]
            
            # Populate form
            employee = get_employee(self.selected_employee_id)
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, employee['name'])
            self.sin_entry.delete(0, tk.END)
            self.sin_entry.insert(0, employee['sin'] or "")
            self.province_var.set(employee['province'])

    def add_new(self):
        """Add a new employee."""
        name = self.name_entry.get().strip()
        sin = self.sin_entry.get().strip()
        province = self.province_var.get()
        
        if not name:
            messagebox.showerror("Invalid Input", "Please enter employee name.")
            return
        
        try:
            employee_id = add_employee(name, sin, province)
            messagebox.showinfo("Success", f"Employee added successfully! (ID: {employee_id})")
            self.load_employees()
            self.clear_form()
            # Notify other frames to refresh their employee lists
            if hasattr(self.controller, 'frames'):
                for frame_name, frame in self.controller.frames.items():
                    if hasattr(frame, 'refresh_employee_list') and frame_name != 'EmployeesFrame':
                        frame.refresh_employee_list(silent=True)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add employee: {str(e)}")

    def update_existing(self):
        """Update selected employee."""
        if not self.selected_employee_id:
            messagebox.showerror("No Selection", "Please select an employee to update.")
            return
        
        name = self.name_entry.get().strip()
        sin = self.sin_entry.get().strip()
        province = self.province_var.get()
        
        if not name:
            messagebox.showerror("Invalid Input", "Please enter employee name.")
            return
        
        try:
            update_employee(self.selected_employee_id, name, sin, province)
            messagebox.showinfo("Success", "Employee updated successfully!")
            self.load_employees()
            self.clear_form()
            # Notify other frames to refresh their employee lists
            if hasattr(self.controller, 'frames'):
                for frame_name, frame in self.controller.frames.items():
                    if hasattr(frame, 'refresh_employee_list') and frame_name != 'EmployeesFrame':
                        frame.refresh_employee_list(silent=True)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update employee: {str(e)}")

    def delete_existing(self):
        """Delete selected employee."""
        if not self.selected_employee_id:
            messagebox.showerror("No Selection", "Please select an employee to delete.")
            return
        
        employee = get_employee(self.selected_employee_id)
        confirm = messagebox.askyesno("Confirm Delete", 
                                      f"Are you sure you want to delete employee '{employee['name']}'?\n\n"
                                      "This will also delete all associated payroll runs.")
        
        if confirm:
            try:
                delete_employee(self.selected_employee_id)
                messagebox.showinfo("Success", "Employee deleted successfully!")
                self.load_employees()
                self.clear_form()
                # Notify other frames to refresh their employee lists
                if hasattr(self.controller, 'frames'):
                    for frame_name, frame in self.controller.frames.items():
                        if hasattr(frame, 'refresh_employee_list') and frame_name != 'EmployeesFrame':
                            frame.refresh_employee_list()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete employee: {str(e)}")

    def clear_form(self):
        """Clear the form."""
        self.name_entry.delete(0, tk.END)
        self.sin_entry.delete(0, tk.END)
        self.province_var.set("ON")
        self.selected_employee_id = None
