# ui/main_window.py
import tkinter as tk
from tkinter import ttk
from ui.run_payroll import RunPayrollFrame
from ui.employees import EmployeesFrame
from ui.records import RecordsFrame
from ui.generate_t4 import GenerateT4Frame
from ui.settings import SettingsFrame
from ui.custom_button import CustomButton

class MainWindow(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.create_widgets()

    def create_widgets(self):
        nav = tk.Frame(self, bg="#1a1a1a", height=50)
        nav.pack(side="top", fill="x")
        
        # Store button references for active highlighting
        self.nav_buttons = {}
        
        # Navigation buttons - match colors to tab headers
        self.nav_buttons['run'] = CustomButton(nav, text="Run Payroll", command=self.show_run,
                              bg_color="#0066cc", padx=15, pady=10)  # Blue
        self.nav_buttons['run'].pack(side="left", padx=3, pady=5)
        
        self.nav_buttons['employees'] = CustomButton(nav, text="Employees", command=self.show_employees,
                              bg_color="#6600cc", padx=15, pady=10)  # Purple
        self.nav_buttons['employees'].pack(side="left", padx=3, pady=5)
        
        self.nav_buttons['records'] = CustomButton(nav, text="Records", command=self.show_records,
                                  bg_color="#cc6600", padx=15, pady=10)  # Orange
        self.nav_buttons['records'].pack(side="left", padx=3, pady=5)
        
        self.nav_buttons['t4'] = CustomButton(nav, text="Generate T4", command=self.show_t4,
                             bg_color="#009999", padx=15, pady=10)  # Teal
        self.nav_buttons['t4'].pack(side="left", padx=3, pady=5)
        
        self.nav_buttons['settings'] = CustomButton(nav, text="Settings", command=self.show_settings,
                                    bg_color="#6600cc", padx=15, pady=10)  # Purple
        self.nav_buttons['settings'].pack(side="left", padx=3, pady=5)
        
        # Track active tab
        self.active_tab = None

        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        self.frames = {}
        for F in (RunPayrollFrame, EmployeesFrame, RecordsFrame, GenerateT4Frame, SettingsFrame):
            page = F(self.container, self)
            self.frames[F.__name__] = page
            page.grid(row=0, column=0, sticky="nsew")
        self.show_run()

    def highlight_active_tab(self, active_key):
        """Highlight the active tab button."""
        # Base colors matching tab headers
        base_colors = {
            'run': '#0066cc',       # Blue
            'employees': '#6600cc', # Purple
            'records': '#cc6600',   # Orange
            't4': '#009999',        # Teal
            'settings': '#6600cc'   # Purple
        }
        
        # Bright colors for active state
        active_colors = {
            'run': '#0088ff',       # Bright blue
            'employees': '#8800ff', # Bright purple
            'records': '#ff8800',   # Bright orange
            't4': '#00cccc',        # Bright teal
            'settings': '#8800ff'   # Bright purple
        }
        
        # Reset all buttons to base colors
        for key, btn in self.nav_buttons.items():
            btn.bg_color = base_colors[key]
            btn.config(bg=base_colors[key])
        
        # Brighten the active button
        if active_key in self.nav_buttons:
            self.nav_buttons[active_key].bg_color = active_colors[active_key]
            self.nav_buttons[active_key].config(bg=active_colors[active_key])
    
    def show_frame(self, name, tab_key):
        self.frames[name].tkraise()
        self.highlight_active_tab(tab_key)
        # Refresh the frame if it has a refresh method
        if hasattr(self.frames[name], 'refresh'):
            self.frames[name].refresh()

    def show_run(self): self.show_frame("RunPayrollFrame", 'run')
    def show_employees(self): self.show_frame("EmployeesFrame", 'employees')
    def show_records(self): self.show_frame("RecordsFrame", 'records')
    def show_t4(self): self.show_frame("GenerateT4Frame", 't4')
    def show_settings(self): self.show_frame("SettingsFrame", 'settings')
