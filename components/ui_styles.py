"""
UI Styles for EVONY AUTO
Contains all styling configurations for the GUI
"""

from tkinter import ttk


def setup_styles():
    """Setup custom styles for better UI appearance"""
    style = ttk.Style()
    
    # Configure theme
    style.theme_use('clam')
    
    # Title style
    style.configure("Title.TLabel", 
                   font=("Arial", 18, "bold"),
                   foreground="#2c3e50",
                   background="#ecf0f1",
                   padding=(10, 5))
    
    # Panel style
    style.configure("Panel.TLabelframe", 
                   background="#ffffff",
                   borderwidth=2,
                   relief="solid",
                   padding=10)
    style.configure("Panel.TLabelframe.Label", 
                   font=("Arial", 12, "bold"),
                   foreground="#2c3e50",
                   background="#ffffff")
    
    # Button styles
    style.configure("Action.TButton",
                   font=("Arial", 9, "bold"),
                   padding=(8, 4),
                   background="#3498db",
                   foreground="white")
    style.map("Action.TButton",
             background=[("active", "#2980b9"), ("pressed", "#21618c")],
             foreground=[("active", "white"), ("pressed", "white")])
    
    style.configure("Start.TButton",
                   font=("Arial", 10, "bold"),
                   padding=(12, 6),
                   background="#27ae60",
                   foreground="white")
    style.map("Start.TButton",
             background=[("active", "#229954"), ("pressed", "#1e8449")],
             foreground=[("active", "white"), ("pressed", "white")])
    
    style.configure("Stop.TButton",
                   font=("Arial", 10, "bold"),
                   padding=(12, 6),
                   background="#e74c3c",
                   foreground="white")
    style.map("Stop.TButton",
             background=[("active", "#c0392b"), ("pressed", "#a93226")],
             foreground=[("active", "white"), ("pressed", "white")])
    
    # Treeview styles
    style.configure("Device.Treeview",
                   background="#ffffff",
                   foreground="#2c3e50",
                   fieldbackground="#ffffff",
                   font=("Arial", 9),
                   rowheight=25)
    style.configure("Device.Treeview.Heading",
                   font=("Arial", 10, "bold"),
                   background="#34495e",
                   foreground="white",
                   relief="flat")
    style.map("Device.Treeview",
             background=[("selected", "#3498db")],
             foreground=[("selected", "white")])
    
    # Feature treeview style
    style.configure("Feature.Treeview",
                   background="#f8f9fa",
                   foreground="#495057",
                   fieldbackground="#f8f9fa",
                   font=("Arial", 9),
                   rowheight=22)
    style.configure("Feature.Treeview.Heading",
                   font=("Arial", 9, "bold"),
                   background="#6c757d",
                   foreground="white",
                   relief="flat")
    style.map("Feature.Treeview",
             background=[("selected", "#007bff")],
             foreground=[("selected", "white")])

    # New styles for hover effects
    style.configure("PanelHover.TLabelframe",
                   background="#f8f9fa",
                   borderwidth=2,
                   relief="solid",
                   padding=10)
    style.configure("PanelHover.TLabelframe.Label",
                   font=("Arial", 12, "bold"),
                   foreground="#2c3e50",
                   background="#f8f9fa")
    style.configure("Count.TLabel",
                   font=("Arial", 10, "bold"),
                   foreground="#2c3e50",
                   background="#ffffff")
    style.configure("Clear.TButton",
                   font=("Arial", 9, "bold"),
                   padding=(8, 4),
                   background="#e74c3c",
                   foreground="white")
    style.map("Clear.TButton",
             background=[("active", "#c0392b"), ("pressed", "#a93226")],
             foreground=[("active", "white"), ("pressed", "white")])
    
    # Warning label style
    style.configure("Warning.TLabel",
                   font=("Arial", 8),
                   foreground="#e74c3c",
                   background="#ffffff")
    
    # Success label style
    style.configure("Success.TLabel",
                   font=("Arial", 8),
                   foreground="#27ae60",
                   background="#ffffff")