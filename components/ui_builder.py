"""
UI Builder Component
Handles the creation and setup of the main GUI interface
"""

import tkinter as tk
from tkinter import ttk
from components.ui_styles import setup_styles


class UIBuilder:
    def __init__(self, gui_instance):
        self.gui = gui_instance
        self.root = gui_instance.root
    
    def setup_ui(self):
        """Setup the main UI components"""
        # Configure styles for better appearance
        setup_styles()
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title with gradient effect
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        title_frame.columnconfigure(0, weight=1)
        
        title_label = ttk.Label(title_frame, text="EVONY AUTO - Drag & Drop Manager", 
                               font=("Arial", 18, "bold"), style="Title.TLabel")
        title_label.grid(row=0, column=0)
        
        # Left panel - Device list
        left_panel = ttk.LabelFrame(main_frame, text="📱 Danh Sách Devices", padding="10", style="Panel.TLabelframe")
        left_panel.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        left_panel.columnconfigure(0, weight=1)
        left_panel.rowconfigure(1, weight=1)
        
        # Device list buttons with better styling
        device_buttons_frame = ttk.Frame(left_panel)
        device_buttons_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(device_buttons_frame, text="🔄 Refresh", 
                  command=self.gui.device_manager.refresh_devices, style="Action.TButton").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(device_buttons_frame, text="🔄 Refresh All", 
                  command=self.gui.device_manager.refresh_all_devices, style="Action.TButton").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(device_buttons_frame, text="📋 Select All", 
                  command=self.gui.device_manager.select_all_devices, style="Action.TButton").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(device_buttons_frame, text="❌ Clear All", 
                  command=self.gui.device_manager.clear_all_devices, style="Action.TButton").pack(side=tk.LEFT, padx=(0, 5))
        
        # Add All Selected to Feature dropdown
        self.gui.add_all_frame = ttk.Frame(device_buttons_frame)
        self.gui.add_all_frame.pack(side=tk.LEFT, padx=(10, 0))
        
        ttk.Label(self.gui.add_all_frame, text="Add to:", style="Count.TLabel").pack(side=tk.LEFT, padx=(0, 5))
        
        # Create dropdown for feature selection
        self.gui.feature_var = tk.StringVar()
        feature_dropdown = ttk.Combobox(self.gui.add_all_frame, textvariable=self.gui.feature_var, 
                                       values=["⚔️ Auto Rally", "🛒 Auto Buy Meat", "🎯 Auto War (No General)", "👹 Auto Attack Boss"],
                                       state="readonly", width=25)
        feature_dropdown.pack(side=tk.LEFT, padx=(0, 5))
        feature_dropdown.set("⚔️ Auto Rally")  # Default selection
        
        # Add button
        ttk.Button(self.gui.add_all_frame, text="➕ Add All", 
                  command=self.gui.device_manager.add_all_selected_to_feature, style="Action.TButton").pack(side=tk.LEFT)
        
        # Device list with scrollbar
        device_list_frame = ttk.Frame(left_panel)
        device_list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        device_list_frame.columnconfigure(0, weight=1)
        device_list_frame.rowconfigure(0, weight=1)
        
        # Create Treeview for devices with custom style
        columns = ("Device", "Status")
        self.gui.device_tree = ttk.Treeview(device_list_frame, columns=columns, show="headings", height=15, style="Device.Treeview")
        
        # Configure columns
        self.gui.device_tree.heading("Device", text="Device Name")
        self.gui.device_tree.heading("Status", text="Status")
        
        self.gui.device_tree.column("Device", width=200)
        self.gui.device_tree.column("Status", width=100)
        
        # Scrollbar for device list
        device_scrollbar = ttk.Scrollbar(device_list_frame, orient=tk.VERTICAL, command=self.gui.device_tree.yview)
        self.gui.device_tree.configure(yscrollcommand=device_scrollbar.set)
        
        self.gui.device_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        device_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Bind drag events and hover effects
        self.gui.device_tree.bind("<Button-1>", self.gui.on_device_click)
        self.gui.device_tree.bind("<B1-Motion>", self.gui.on_device_drag)
        self.gui.device_tree.bind("<ButtonRelease-1>", self.gui.on_device_release)
        self.gui.device_tree.bind("<Enter>", self.gui.on_device_tree_enter)
        self.gui.device_tree.bind("<Leave>", self.gui.on_device_tree_leave)
        self.gui.device_tree.bind("<Motion>", self.gui.on_device_tree_motion)
        
        # Right panel - Feature containers
        right_panel = ttk.Frame(main_frame)
        right_panel.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_panel.columnconfigure(0, weight=1)
        right_panel.columnconfigure(1, weight=1)
        right_panel.rowconfigure(0, weight=1)
        right_panel.rowconfigure(1, weight=1)
        
        # Feature containers
        self.create_feature_container(right_panel, "⚔️ Auto Rally", "rally", 0, 0)
        self.create_feature_container(right_panel, "🛒 Auto Buy Meat", "buy_meat", 0, 1)
        self.create_feature_container(right_panel, "🎯 Auto War (No General)", "war_no_general", 1, 0)
        self.create_feature_container(right_panel, "👹 Auto Attack Boss", "attack_boss", 1, 1)
        
        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=2, column=0, columnspan=2, pady=(20, 0))
        
        self.gui.start_button = ttk.Button(control_frame, text="🚀 Bắt Đầu Tất Cả", 
                                          command=self.gui.start_all_features, style="Start.TButton")
        self.gui.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.gui.stop_button = ttk.Button(control_frame, text="⏹️ Dừng Tất Cả", 
                                         command=self.gui.stop_all_features, state=tk.DISABLED, style="Stop.TButton")
        self.gui.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(control_frame, text="🗑️ Clear All Features", 
                  command=self.gui.device_manager.clear_all_features, style="Action.TButton").pack(side=tk.LEFT)
        
        # Status section
        status_frame = ttk.LabelFrame(main_frame, text="📊 Trạng Thái", padding="10", style="Panel.TLabelframe")
        status_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        status_frame.columnconfigure(0, weight=1)
        status_frame.rowconfigure(0, weight=1)
        
        # Status text with scrollbar
        status_text_frame = ttk.Frame(status_frame)
        status_text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        status_text_frame.columnconfigure(0, weight=1)
        status_text_frame.rowconfigure(0, weight=1)
        
        self.gui.status_text = tk.Text(status_text_frame, height=8, wrap=tk.WORD, 
                                     font=("Consolas", 9), bg="#f8f9fa", fg="#212529",
                                     insertbackground="#007bff", selectbackground="#007bff",
                                     selectforeground="white", relief="flat", borderwidth=1)
        status_scrollbar = ttk.Scrollbar(status_text_frame, orient=tk.VERTICAL, command=self.gui.status_text.yview)
        self.gui.status_text.configure(yscrollcommand=status_scrollbar.set)
        
        self.gui.status_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        status_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configure main frame grid weights
        main_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
    
    def create_feature_container(self, parent, title, feature_key, row, col):
        """Tạo container cho một tính năng"""
        container = ttk.LabelFrame(parent, text=title, padding="10", style="Panel.TLabelframe")
        container.grid(row=row, column=col, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(1, weight=1)
        
        # Add hover effect to container
        container.bind("<Enter>", lambda e, c=container: self.gui.on_container_enter(e, c))
        container.bind("<Leave>", lambda e, c=container: self.gui.on_container_leave(e, c))
        
        # Header với số lượng devices và buttons
        header_frame = ttk.Frame(container)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Left side - Device count label
        left_frame = ttk.Frame(header_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        count_label = ttk.Label(left_frame, text="0 devices", style="Count.TLabel")
        count_label.pack(side=tk.LEFT)
        setattr(self.gui, f"{feature_key}_count_label", count_label)
        
        # Right side - Buttons
        right_frame = ttk.Frame(header_frame)
        right_frame.pack(side=tk.RIGHT)
        
        # Add Selected button
        add_button = ttk.Button(right_frame, text="➕ Add Selected", width=10,
                               command=lambda: self.gui.device_manager.add_selected_to_feature(feature_key), 
                               style="Action.TButton")
        add_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Clear button
        clear_button = ttk.Button(right_frame, text="❌", width=3,
                                 command=lambda: self.gui.device_manager.clear_feature_devices(feature_key), 
                                 style="Clear.TButton")
        clear_button.pack(side=tk.LEFT)
        
        # Device list for this feature
        feature_list_frame = ttk.Frame(container)
        feature_list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        feature_list_frame.columnconfigure(0, weight=1)
        feature_list_frame.rowconfigure(0, weight=1)
        
        # Create Treeview for feature devices
        columns = ("Device", "Status")
        feature_tree = ttk.Treeview(feature_list_frame, columns=columns, show="headings", height=6, style="Feature.Treeview")
        
        feature_tree.heading("Device", text="Device")
        feature_tree.heading("Status", text="Status")
        
        feature_tree.column("Device", width=180)
        feature_tree.column("Status", width=80)
        
        # Scrollbar for feature list
        feature_scrollbar = ttk.Scrollbar(feature_list_frame, orient=tk.VERTICAL, command=feature_tree.yview)
        feature_tree.configure(yscrollcommand=feature_scrollbar.set)
        
        feature_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        feature_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Store reference to feature tree
        setattr(self.gui, f"{feature_key}_tree", feature_tree)
        
        # Feature control buttons frame
        control_frame = ttk.Frame(container)
        control_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Start button for this feature
        start_button = ttk.Button(control_frame, text="▶️ Start", width=8,
                                 command=lambda: self.gui.start_feature(feature_key), 
                                 style="Start.TButton")
        start_button.pack(side=tk.LEFT, padx=(0, 5))
        setattr(self.gui, f"{feature_key}_start_button", start_button)
        
        # Stop button for this feature
        stop_button = ttk.Button(control_frame, text="⏹️ Stop", width=8,
                                command=lambda: self.gui.stop_feature(feature_key), 
                                style="Stop.TButton", state=tk.DISABLED)
        stop_button.pack(side=tk.LEFT, padx=(0, 5))
        setattr(self.gui, f"{feature_key}_stop_button", stop_button)
        
        # Status label for this feature
        status_label = ttk.Label(control_frame, text="⏸️ Stopped", style="Count.TLabel")
        status_label.pack(side=tk.RIGHT)
        setattr(self.gui, f"{feature_key}_status_label", status_label)
        
        # Bind drop events and hover effects
        feature_tree.bind("<Button-1>", lambda e: self.gui.on_feature_click(e, feature_key))
        feature_tree.bind("<B1-Motion>", lambda e: self.gui.on_feature_drag(e, feature_key))
        feature_tree.bind("<ButtonRelease-1>", lambda e: self.gui.on_feature_release(e, feature_key))
        feature_tree.bind("<Enter>", lambda e: self.gui.on_feature_tree_enter(e))
        feature_tree.bind("<Leave>", lambda e: self.gui.on_feature_tree_leave(e))
        feature_tree.bind("<Motion>", lambda e: self.gui.on_feature_tree_motion(e))
