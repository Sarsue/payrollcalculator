# ui/custom_button.py
"""
Custom button widget using Label that maintains consistent appearance on macOS
regardless of window focus state. Labels don't get macOS focus styling.
"""
import tkinter as tk

class CustomButton(tk.Label):
    """
    A button using Label that looks consistent on macOS.
    Labels bypass the Aqua theme button styling completely.
    """
    def __init__(self, parent, text, command, bg_color, fg_color="white", 
                 font=("Arial", 11, "bold"), padx=25, pady=10, **kwargs):
        self.command = command
        self.bg_color = bg_color
        self.hover_color = self.lighten_color(bg_color)
        
        super().__init__(parent, text=text, bg=bg_color, fg=fg_color,
                        font=font, padx=padx, pady=pady, cursor="hand2",
                        relief="flat", **kwargs)
        
        self.bind_events()
    
    def lighten_color(self, color):
        """Lighten a hex color by 20% for hover effect"""
        color = color.lstrip('#')
        r = int(color[0:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:6], 16)
        r = min(255, int(r * 1.3))
        g = min(255, int(g * 1.3))
        b = min(255, int(b * 1.3))
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def bind_events(self):
        """Bind mouse events for hover and click"""
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
    
    def on_enter(self, event):
        """Mouse hover - lighten background"""
        self.config(bg=self.hover_color)
    
    def on_leave(self, event):
        """Mouse leave - restore original background"""
        self.config(bg=self.bg_color)
    
    def on_click(self, event):
        """Button clicked - execute command"""
        if self.command:
            self.command()
