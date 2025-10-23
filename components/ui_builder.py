"""
UI Builder Component
Handles the creation and setup of the main GUI interface
"""

import tkinter as tk
from tkinter import ttk
import os
from components.ui_styles import setup_styles
from utils.language_utils import set_language, get_current_language, get_available_languages


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
        
        # Configure grid weights - thu nhỏ left panel, mở rộng right panel
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)  # Left panel - thu nhỏ
        main_frame.columnconfigure(1, weight=12)  # Right panel - tăng mạnh hơn (1:12)
        main_frame.rowconfigure(1, weight=1)
        
        # Title with gradient effect
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        title_frame.columnconfigure(0, weight=1)
        
        title_label = ttk.Label(title_frame, text="EVONY AUTO - Drag & Drop Manager", 
                               font=("Arial", 18, "bold"), style="Title.TLabel")
        title_label.grid(row=0, column=0)
        
        # Left panel - Device list (thu nhỏ)
        left_panel = ttk.LabelFrame(main_frame, text="📱 Devices", padding="8", style="Panel.TLabelframe")
        left_panel.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        left_panel.columnconfigure(0, weight=1)
        left_panel.rowconfigure(1, weight=1)
        
        # Device list buttons - 1 dòng compact
        device_buttons_frame = ttk.Frame(left_panel)
        device_buttons_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        
        # Row 1: Basic buttons
        row1_frame = ttk.Frame(device_buttons_frame)
        row1_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(row1_frame, text="🔄 Refresh", 
                  command=self.gui.device_manager.refresh_devices, style="Action.TButton").pack(side=tk.LEFT, padx=(0, 3))
        ttk.Button(row1_frame, text="🔄 All", 
                  command=self.gui.device_manager.refresh_all_devices, style="Action.TButton").pack(side=tk.LEFT, padx=(0, 3))
        ttk.Button(row1_frame, text="📋 Select", 
                  command=self.gui.device_manager.select_all_devices, style="Action.TButton").pack(side=tk.LEFT, padx=(0, 3))
        ttk.Button(row1_frame, text="❌ Clear", 
                  command=self.gui.device_manager.clear_all_devices, style="Action.TButton").pack(side=tk.LEFT, padx=(0, 3))
        
        # Row 2: Add to feature dropdown - compact
        row2_frame = ttk.Frame(device_buttons_frame)
        row2_frame.pack(fill=tk.X)
        
        ttk.Label(row2_frame, text="Add to:", style="Count.TLabel").pack(side=tk.LEFT, padx=(0, 3))
        
        # Create dropdown for feature selection - compact
        self.gui.feature_var = tk.StringVar()
        feature_dropdown = ttk.Combobox(row2_frame, textvariable=self.gui.feature_var, 
                                       values=["⚔️ Rally", "🛒 Buy Meat", "🎯 War", "👹 Attack Boss", "📦 Open Items", "⚔️ Advanced Rally", "🎯 Advanced War"],
                                       state="readonly", width=15)
        feature_dropdown.pack(side=tk.LEFT, padx=(0, 3))
        feature_dropdown.set("⚔️ Rally")  # Default selection
        
        # Add button
        ttk.Button(row2_frame, text="➕ Add", 
                  command=self.gui.device_manager.add_all_selected_to_feature, style="Action.TButton").pack(side=tk.LEFT)
        
        # Device list with scrollbar
        device_list_frame = ttk.Frame(left_panel)
        device_list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        device_list_frame.columnconfigure(0, weight=1)
        device_list_frame.rowconfigure(0, weight=1)
        
        # Create Treeview for devices - compact
        columns = ("Device", "Status")
        self.gui.device_tree = ttk.Treeview(device_list_frame, columns=columns, show="headings", height=4, style="Device.Treeview")
        
        # Configure columns - thu nhỏ
        self.gui.device_tree.heading("Device", text="Device")
        self.gui.device_tree.heading("Status", text="Status")
        
        self.gui.device_tree.column("Device", width=120)  # Thu nhỏ
        self.gui.device_tree.column("Status", width=60)   # Thu nhỏ
        
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
        
        # Right panel - Feature containers with scroll
        right_panel = ttk.Frame(main_frame)
        right_panel.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(0, weight=1)

        # Create scrollable frame for features
        features_canvas = tk.Canvas(right_panel, bg="#f8f9fa")
        features_scrollbar = ttk.Scrollbar(right_panel, orient=tk.VERTICAL, command=features_canvas.yview)
        scrollable_features_frame = ttk.Frame(features_canvas)

        scrollable_features_frame.bind(
            "<Configure>",
            lambda e: features_canvas.configure(scrollregion=features_canvas.bbox("all"))
        )

        features_canvas.create_window((0, 0), window=scrollable_features_frame, anchor="nw")
        features_canvas.configure(yscrollcommand=features_scrollbar.set)

        features_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        features_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Bind mouse wheel to canvas - chỉ cho features canvas
        def _on_mousewheel(event):
            features_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        features_canvas.bind("<MouseWheel>", _on_mousewheel)

        # Configure scrollable frame - 2 columns bằng nhau
        scrollable_features_frame.columnconfigure(0, weight=1, minsize=670)  # Column đầu tiên - bằng nhau
        scrollable_features_frame.columnconfigure(1, weight=1, minsize=670)  # Column thứ 2 - bằng nhau
        scrollable_features_frame.rowconfigure(0, weight=1)     # Row đầu tiên
        scrollable_features_frame.rowconfigure(1, weight=1)     # Row thứ 2 bằng nhau
        scrollable_features_frame.rowconfigure(2, weight=1)     # Row thứ 3 (Auto Open Items + Buy General)
        scrollable_features_frame.rowconfigure(3, weight=1)     # Row thứ 4 (Boss Selection)
        scrollable_features_frame.rowconfigure(4, weight=1)     # Row thứ 5 (Advanced Features)

        # Feature containers (2 features per row)
        self.create_feature_container(scrollable_features_frame, "⚔️ Auto Rally", "rally", 0, 0)
        self.create_feature_container(scrollable_features_frame, "🛒 Auto Buy Meat", "buy_meat", 0, 1)
        self.create_feature_container(scrollable_features_frame, "🎯 Auto War (No General)", "war_no_general", 1, 0)
        self.create_feature_container(scrollable_features_frame, "👹 Auto Attack Boss", "attack_boss", 1, 1)
        self.create_feature_container(scrollable_features_frame, "📦 Auto Open Items", "open_items", 2, 0)
        self.create_feature_container(scrollable_features_frame, "🛒 Auto Buy General", "buy_general", 2, 1)
        
        # Boss selection section
        self.setup_boss_selection_ui(scrollable_features_frame)
        
        # Advanced features (1 row, 2 columns)
        self.create_feature_container(scrollable_features_frame, "⚔️ Advanced Rally", "advanced_rally", 4, 0)
        self.create_feature_container(scrollable_features_frame, "🎯 Advanced War (No General)", "advanced_war", 4, 1)
        
        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=2, column=0, columnspan=2, pady=(20, 0))
        
        # Language selection - mở rộng
        language_frame = ttk.Frame(control_frame)
        language_frame.pack(side=tk.LEFT, padx=(0, 30))
        
        ttk.Label(language_frame, text="🌐 Ngôn ngữ:", style="Count.TLabel").pack(side=tk.LEFT, padx=(0, 8))
        
        # Language dropdown - mở rộng
        self.gui.language_var = tk.StringVar()
        available_languages = get_available_languages()
        language_values = [f"{name} ({code})" for code, name in available_languages.items()]
        
        self.gui.language_dropdown = ttk.Combobox(language_frame, textvariable=self.gui.language_var, 
                                                 values=language_values, state="readonly", width=18)
        self.gui.language_dropdown.pack(side=tk.LEFT, padx=(0, 8))
        
        # Set current language
        current_lang = get_current_language()
        current_lang_name = available_languages.get(current_lang, current_lang)
        self.gui.language_dropdown.set(f"{current_lang_name} ({current_lang})")
        
        # Bind language change event
        self.gui.language_dropdown.bind("<<ComboboxSelected>>", self.gui.on_language_change)
        
        # Main control buttons - mở rộng
        self.gui.start_button = ttk.Button(control_frame, text="🚀 Bắt Đầu Tất Cả", 
                                          command=self.gui.start_all_features, style="Start.TButton")
        self.gui.start_button.pack(side=tk.LEFT, padx=(0, 15))
        
        self.gui.stop_button = ttk.Button(control_frame, text="⏹️ Dừng Tất Cả", 
                                         command=self.gui.stop_all_features, state=tk.DISABLED, style="Stop.TButton")
        self.gui.stop_button.pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Button(control_frame, text="🗑️ Clear All Features", 
                  command=self.gui.device_manager.clear_all_features, style="Action.TButton").pack(side=tk.LEFT, padx=(0, 15))
        
        # Thêm thông tin trạng thái
        status_info_frame = ttk.Frame(control_frame)
        status_info_frame.pack(side=tk.RIGHT)
        
        ttk.Label(status_info_frame, text="💡 Thu nhỏ Devices để mở rộng Features", 
                 style="Count.TLabel", font=("Arial", 9)).pack()
        
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
    
    def create_feature_container(self, parent, title, feature_key, row, col, columnspan=1):
        """Tạo container cho một tính năng"""
        container = ttk.LabelFrame(parent, text=title, padding="10", style="Panel.TLabelframe")
        container.grid(row=row, column=col, columnspan=columnspan, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
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
        
        # Special input for attack_boss feature
        if feature_key == "attack_boss":
            # Input frame for troops count
            input_frame = ttk.Frame(control_frame)
            input_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
            
            # Troops count input
            ttk.Label(input_frame, text="Troops:", style="Count.TLabel").pack(side=tk.LEFT, padx=(0, 5))
            
            troops_var = tk.StringVar()
            troops_entry = ttk.Entry(input_frame, textvariable=troops_var, width=10, font=("Arial", 9))
            troops_entry.pack(side=tk.LEFT, padx=(0, 5))
            setattr(self.gui, f"{feature_key}_troops_var", troops_var)
            setattr(self.gui, f"{feature_key}_troops_entry", troops_entry)
            
            # Validation label
            validation_label = ttk.Label(input_frame, text="⚠️ Nhập số quân", style="Warning.TLabel")
            validation_label.pack(side=tk.LEFT)
            setattr(self.gui, f"{feature_key}_validation_label", validation_label)
            
            # Bind validation on input change
            troops_var.trace('w', lambda *args: self.gui.validate_attack_boss_input())
        
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
    
    def setup_boss_selection_ui(self, parent):
        """Tạo UI cho việc chọn boss types"""
        import os
        
        # Boss selection frame
        boss_frame = ttk.LabelFrame(parent, text="👹 Select Boss Types", padding="10", style="Panel.TLabelframe")
        boss_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        boss_frame.columnconfigure(0, weight=1)
        
        # Language selection for boss images
        lang_frame = ttk.Frame(boss_frame)
        lang_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(lang_frame, text="Language:", style="Count.TLabel").pack(side=tk.LEFT, padx=(0, 10))
        
        # Language dropdown
        self.gui.boss_language_var = tk.StringVar(value="English (en)")
        boss_language_combo = ttk.Combobox(lang_frame, textvariable=self.gui.boss_language_var, 
                                          values=["English (en)", "Vietnamese (vi)"], 
                                          state="readonly", width=15)
        boss_language_combo.pack(side=tk.LEFT)
        boss_language_combo.bind("<<ComboboxSelected>>", self.on_boss_language_change)
        
        # Check All / Uncheck All buttons
        check_all_btn = ttk.Button(lang_frame, text="Check All", 
                                  command=self.check_all_bosses, width=10)
        check_all_btn.pack(side=tk.LEFT, padx=(10, 5))
        
        uncheck_all_btn = ttk.Button(lang_frame, text="Uncheck All", 
                                    command=self.uncheck_all_bosses, width=10)
        uncheck_all_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Boss checkboxes frame
        self.gui.boss_checkboxes_frame = ttk.Frame(boss_frame)
        self.gui.boss_checkboxes_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        # Configure columns - chỉ cột đầu có weight, các cột khác không có weight để dồn về trái
        self.gui.boss_checkboxes_frame.columnconfigure(0, weight=1)
        for i in range(1, 5):  # Cột 1-4 không có weight
            self.gui.boss_checkboxes_frame.columnconfigure(i, weight=0)
        
        # Initialize boss variables
        self.gui.boss_vars = {}
        
        # Load boss checkboxes
        self.setup_boss_checkboxes()
    
    def setup_boss_checkboxes(self):
        """Tạo checkboxes cho boss types"""
        import os
        
        # Clear existing checkboxes
        for widget in self.gui.boss_checkboxes_frame.winfo_children():
            widget.destroy()
        
        # Get current language
        current_lang = self.gui.boss_language_var.get().split(" ")[-1].strip("()")
        boss_dir = f"images/{current_lang}/buttons/rally_advance_boss"
        
        if not os.path.exists(boss_dir):
            ttk.Label(self.gui.boss_checkboxes_frame, 
                     text=f"Boss directory not found: {boss_dir}", 
                     style="Count.TLabel").grid(row=0, column=0, sticky=tk.W)
            return
        
        # Get boss image files
        boss_files = []
        for file in os.listdir(boss_dir):
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                boss_name = os.path.splitext(file)[0]
                boss_files.append((boss_name, file))
        
        if not boss_files:
            ttk.Label(self.gui.boss_checkboxes_frame, 
                     text="No boss images found", 
                     style="Count.TLabel").grid(row=0, column=0, sticky=tk.W)
            return
        
        # Create checkboxes - 5 boss per row, dồn về trái
        for i, (boss_name, filename) in enumerate(boss_files):
            row = i // 5  # 5 boss per row
            col = i % 5   # 5 columns

            # Create variable for checkbox
            var = tk.BooleanVar()
            self.gui.boss_vars[boss_name] = var

            # Create checkbox
            checkbox = ttk.Checkbutton(self.gui.boss_checkboxes_frame,
                                       text=boss_name.replace('_', ' ').title(),
                                       variable=var,
                                       style="Boss.TCheckbutton")
            checkbox.grid(row=row, column=col, sticky=tk.W, padx=5, pady=2)

    def on_boss_language_change(self, event=None):
        """Handle boss language change"""
        try:
            # Refresh boss checkboxes when language changes
            self.setup_boss_checkboxes()
        except Exception as e:
            print(f"Error changing boss language: {e}")
    
    def check_all_bosses(self):
        """Check tất cả boss checkboxes"""
        try:
            if hasattr(self.gui, 'boss_vars'):
                for var in self.gui.boss_vars.values():
                    var.set(True)
                print("✅ Đã check tất cả boss")
        except Exception as e:
            print(f"❌ Lỗi khi check all bosses: {e}")
    
    def uncheck_all_bosses(self):
        """Uncheck tất cả boss checkboxes"""
        try:
            if hasattr(self.gui, 'boss_vars'):
                for var in self.gui.boss_vars.values():
                    var.set(False)
                print("✅ Đã uncheck tất cả boss")
        except Exception as e:
            print(f"❌ Lỗi khi uncheck all bosses: {e}")
