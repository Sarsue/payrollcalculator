# main.py
import tkinter as tk
from tkinter import ttk
import sys
from ui.main_window import MainWindow
from db.database import init_db

def main():
    # Initialize database
    init_db()
    
    # Create main window
    root = tk.Tk()
    
    # Force classic theme on macOS to allow button color customization
    try:
        # On macOS, the aqua theme overrides button colors
        # We need to use the classic theme to enable custom button colors
        if sys.platform == "darwin":  # macOS
            root.tk.call('tk', 'useinputmethods', 'false')
            # Set button background color support
            root.option_add('*Button.background', '#0066cc')
            root.option_add('*Button.foreground', 'white')
    except:
        pass
    
    root.title("Payroll Calculator - MVP")
    root.geometry("1000x700")
    
    # Set minimum window size
    root.minsize(900, 600)
    
    # Create app
    app = MainWindow(root)
    
    # Start the application
    root.mainloop()

if __name__ == "__main__":
    main()
