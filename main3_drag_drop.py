import tkinter as tk
from tkinter import ttk, messagebox
import threading
import multiprocessing
import time
import random
from datetime import datetime
from actions.war_actions import join_war_sequence, continue_war_sequence, join_war_sequence_no_general
from utils.image_utils import check_button_exists, find_and_click_button
from utils.adb_utils import swipe_up, swipe_down, select_memu_devices, set_device, get_memu_devices
from actions.rally import auto_join_rally
from actions.market_actions import auto_buy_meat

# Import cho attack boss
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from actions.user_interface import get_boss_selection, display_boss_list
from actions.get_location_boss import get_boss_locations, save_to_json
from actions.boss_data_manager import load_boss_data, group_bosses_by_name
from actions.boss_attacker import attack_selected_bosses

def run_single_task_process(task, task_index, total_tasks, log_queue):
    """Hàm chạy trong process con - không có GUI"""
    try:
        device = task['device']
        feature_code = task['feature_code']
        feature_name = task['feature_name']
        device_id = device['device_id']
        
        log_queue.put(f"🔄 [Task {task_index}/{total_tasks}] Bắt đầu {feature_name} trên {device['name']} (Device ID: {device_id})")
        
        # Thiết lập device
        set_device(device_id)
        
        # Chạy feature tương ứng
        if feature_code == "1":
            run_rally_direct_process(device_id, use_general=True, log_queue=log_queue)
        elif feature_code == "2":
            run_buy_meat_direct_process(device_id, log_queue=log_queue)
        elif feature_code == "3":
            run_rally_direct_process(device_id, use_general=False, log_queue=log_queue)
        elif feature_code == "4":
            run_attack_boss_direct_process(device_id, log_queue=log_queue)
        
        log_queue.put(f"✅ [Task {task_index}/{total_tasks}] Hoàn thành {feature_name} trên {device['name']}")
            
    except Exception as e:
        log_queue.put(f"❌ Lỗi nghiêm trọng trong task {task_index}: {e}")

def run_rally_direct_process(device_id, use_general=True, log_queue=None):
    """Chạy auto_join_rally trong process con"""
    try:
        if log_queue:
            log_queue.put(f"⚔️ Bắt đầu auto rally trên device {device_id}")
        auto_join_rally(device_id, use_general)
    except Exception as e:
        if log_queue:
            log_queue.put(f"❌ Lỗi khi chạy auto rally trên {device_id}: {e}")

def run_buy_meat_direct_process(device_id, log_queue=None):
    """Chạy auto_buy_meat trong process con"""
    try:
        if log_queue:
            log_queue.put(f"🛒 Bắt đầu auto buy meat trên device {device_id}")
        auto_buy_meat(device_id)
    except Exception as e:
        if log_queue:
            log_queue.put(f"❌ Lỗi khi chạy auto buy meat trên {device_id}: {e}")

def run_attack_boss_direct_process(device_id, log_queue=None):
    """Chạy attack_boss trong process con"""
    try:
        if log_queue:
            log_queue.put(f"👹 Bắt đầu tấn công boss trên device {device_id}")
        
        # Bước 1: Cập nhật vị trí boss từ thiết bị
        if log_queue:
            log_queue.put(f"📡 Đang cập nhật vị trí boss từ thiết bị {device_id}...")
        bosses = get_boss_locations()
        
        if not bosses:
            if log_queue:
                log_queue.put("❌ Không tìm thấy thông tin boss!")
            return
            
        # Lưu thông tin boss vào file
        if not save_to_json(bosses, device_id=device_id):
            if log_queue:
                log_queue.put("❌ Không thể lưu thông tin boss vào file!")
            return
        
        # Bước 2: Tự động chọn tất cả boss
        boss_groups = group_bosses_by_name(bosses)
        initial_selection = []
        
        # Chọn tất cả boss có sẵn
        for boss_name, boss_group in boss_groups.items():
            initial_selection.append(boss_group)
        
        if not initial_selection:
            if log_queue:
                log_queue.put("❌ Không có boss nào để tấn công!")
            return
        
        if log_queue:
            log_queue.put(f"✅ Đã tự động chọn {len(initial_selection)} loại boss để tấn công")
        
        # Bước 3: Bắt đầu vòng lặp tấn công
        start_time = time.time()
        is_running = True
        while is_running:
            # Kiểm tra số boss chưa tấn công
            unattacked_count = sum(1 for group in initial_selection
                                 for _, boss in group
                                 if not boss.get('attacked', 0))
            
            remaining_time = int(1800 - (time.time() - start_time))  # 30 phút
            if log_queue:
                log_queue.put(f"⏱️ Còn {unattacked_count} boss, thời gian: {remaining_time}s")
            
            # Thực hiện tấn công
            result = attack_selected_bosses(initial_selection, bosses, start_time)
            
            # Kiểm tra kết quả
            if result == "update_required" or remaining_time <= 0:
                if log_queue:
                    log_queue.put("⏰ Đã đủ 30 phút, kết thúc tấn công boss...")
                break
            elif unattacked_count == 0:
                if log_queue:
                    log_queue.put("🎯 Đã hết boss, kết thúc tấn công boss...")
                break
            
            time.sleep(1)
                 
    except Exception as e:
        if log_queue:
            log_queue.put(f"❌ Lỗi khi tấn công boss trên {device_id}: {e}")

class DragDropGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("EVONY AUTO - Drag & Drop Manager")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)
        
        # Variables
        self.devices = []
        self.dragged_device = None
        self.is_running = False
        self.processes = []
        self.log_queue = multiprocessing.Queue()
        self.log_thread = None
        
        # Feature containers - mỗi feature sẽ chứa devices được kéo vào
        self.feature_devices = {
            "rally": [],
            "buy_meat": [],
            "war_no_general": [],
            "attack_boss": []
        }
        
        self.setup_ui()
        self.refresh_devices()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="EVONY AUTO - Drag & Drop Manager", 
                               font=("Arial", 18, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Left panel - Device list
        left_panel = ttk.LabelFrame(main_frame, text="📱 Danh Sách Devices", padding="10")
        left_panel.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        left_panel.columnconfigure(0, weight=1)
        left_panel.rowconfigure(1, weight=1)
        
        # Device list buttons
        device_buttons_frame = ttk.Frame(left_panel)
        device_buttons_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(device_buttons_frame, text="🔄 Refresh", 
                  command=self.refresh_devices).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(device_buttons_frame, text="📋 Select All", 
                  command=self.select_all_devices).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(device_buttons_frame, text="❌ Clear All", 
                  command=self.clear_all_devices).pack(side=tk.LEFT)
        
        # Device list with scrollbar
        device_list_frame = ttk.Frame(left_panel)
        device_list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        device_list_frame.columnconfigure(0, weight=1)
        device_list_frame.rowconfigure(0, weight=1)
        
        # Create Treeview for devices
        columns = ("Device", "Status")
        self.device_tree = ttk.Treeview(device_list_frame, columns=columns, show="headings", height=15)
        
        # Configure columns
        self.device_tree.heading("Device", text="Device Name")
        self.device_tree.heading("Status", text="Status")
        
        self.device_tree.column("Device", width=150)
        self.device_tree.column("Status", width=80)
        
        # Scrollbar for device list
        device_scrollbar = ttk.Scrollbar(device_list_frame, orient=tk.VERTICAL, command=self.device_tree.yview)
        self.device_tree.configure(yscrollcommand=device_scrollbar.set)
        
        self.device_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        device_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Bind drag events
        self.device_tree.bind("<Button-1>", self.on_device_click)
        self.device_tree.bind("<B1-Motion>", self.on_device_drag)
        self.device_tree.bind("<ButtonRelease-1>", self.on_device_release)
        
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
        
        self.start_button = ttk.Button(control_frame, text="🚀 Bắt Đầu Tất Cả", 
                                      command=self.start_all_features, style="Accent.TButton")
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(control_frame, text="⏹️ Dừng Tất Cả", 
                                     command=self.stop_all_features, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(control_frame, text="🗑️ Clear All Features", 
                  command=self.clear_all_features).pack(side=tk.LEFT)
        
        # Status section
        status_frame = ttk.LabelFrame(main_frame, text="📊 Trạng Thái", padding="10")
        status_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        status_frame.columnconfigure(0, weight=1)
        status_frame.rowconfigure(0, weight=1)
        
        # Status text with scrollbar
        status_text_frame = ttk.Frame(status_frame)
        status_text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        status_text_frame.columnconfigure(0, weight=1)
        status_text_frame.rowconfigure(0, weight=1)
        
        self.status_text = tk.Text(status_text_frame, height=8, wrap=tk.WORD)
        status_scrollbar = ttk.Scrollbar(status_text_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=status_scrollbar.set)
        
        self.status_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        status_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configure main frame grid weights
        main_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
    
    def create_feature_container(self, parent, title, feature_key, row, col):
        """Tạo container cho một tính năng"""
        container = ttk.LabelFrame(parent, text=title, padding="10")
        container.grid(row=row, column=col, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(1, weight=1)
        
        # Header với số lượng devices
        header_frame = ttk.Frame(container)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.feature_devices[feature_key] = []
        
        # Device count label
        count_label = ttk.Label(header_frame, text="0 devices")
        count_label.pack(side=tk.LEFT)
        setattr(self, f"{feature_key}_count_label", count_label)
        
        # Clear button
        ttk.Button(header_frame, text="❌", width=3,
                  command=lambda: self.clear_feature_devices(feature_key)).pack(side=tk.RIGHT)
        
        # Device list for this feature
        feature_list_frame = ttk.Frame(container)
        feature_list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        feature_list_frame.columnconfigure(0, weight=1)
        feature_list_frame.rowconfigure(0, weight=1)
        
        # Create Treeview for feature devices
        columns = ("Device", "Status")
        feature_tree = ttk.Treeview(feature_list_frame, columns=columns, show="headings", height=6)
        
        feature_tree.heading("Device", text="Device")
        feature_tree.heading("Status", text="Status")
        
        feature_tree.column("Device", width=120)
        feature_tree.column("Status", width=60)
        
        # Scrollbar for feature list
        feature_scrollbar = ttk.Scrollbar(feature_list_frame, orient=tk.VERTICAL, command=feature_tree.yview)
        feature_tree.configure(yscrollcommand=feature_scrollbar.set)
        
        feature_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        feature_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Store reference to feature tree
        setattr(self, f"{feature_key}_tree", feature_tree)
        
        # Bind drop events
        feature_tree.bind("<Button-1>", lambda e: self.on_feature_click(e, feature_key))
        feature_tree.bind("<B1-Motion>", lambda e: self.on_feature_drag(e, feature_key))
        feature_tree.bind("<ButtonRelease-1>", lambda e: self.on_feature_release(e, feature_key))
    
    def refresh_devices(self):
        """Refresh danh sách devices"""
        try:
            self.log_status("🔄 Đang tải danh sách devices...")
            self.devices = get_memu_devices()
            
            # Clear existing items
            for item in self.device_tree.get_children():
                self.device_tree.delete(item)
            
            # Add devices to treeview
            for device in self.devices:
                device_id = device['device_id']
                device_name = device['name']
                
                # Add to treeview
                item = self.device_tree.insert("", tk.END, values=(device_name, "Ready"))
                
                # Store device info in item
                self.device_tree.item(item, tags=(device_id,))
            
            self.log_status(f"✅ Đã tải {len(self.devices)} devices")
            
        except Exception as e:
            self.log_status(f"❌ Lỗi khi tải devices: {e}")
            messagebox.showerror("Lỗi", f"Không thể tải danh sách devices:\n{e}")
    
    def select_all_devices(self):
        """Chọn tất cả devices (highlight)"""
        for item in self.device_tree.get_children():
            self.device_tree.selection_add(item)
    
    def clear_all_devices(self):
        """Clear selection"""
        self.device_tree.selection_remove(self.device_tree.selection())
    
    def on_device_click(self, event):
        """Handle click on device"""
        item = self.device_tree.identify_row(event.y)
        if item:
            self.device_tree.selection_set(item)
    
    def on_device_drag(self, event):
        """Handle drag from device list"""
        if self.device_tree.selection():
            self.dragged_device = self.device_tree.selection()[0]
    
    def on_device_release(self, event):
        """Handle release from device list"""
        if self.dragged_device:
            # Check if dropped on a feature container
            widget = event.widget.winfo_containing(event.x_root, event.y_root)
            if widget:
                # Find which feature container this widget belongs to
                for feature_key in self.feature_devices.keys():
                    feature_tree = getattr(self, f"{feature_key}_tree", None)
                    if feature_tree and widget == feature_tree:
                        self.add_device_to_feature(self.dragged_device, feature_key)
                        break
            
            self.dragged_device = None
    
    def add_device_to_feature(self, device_item, feature_key):
        """Thêm device vào feature container"""
        if device_item:
            # Get device info
            device_id = self.device_tree.item(device_item, "tags")[0]
            device_name = self.device_tree.item(device_item, "values")[0]
            
            # Check if device already in this feature
            for device in self.feature_devices[feature_key]:
                if device['device_id'] == device_id:
                    self.log_status(f"⚠️ Device {device_name} đã có trong {feature_key}")
                    return
            
            # Add device to feature
            device_info = {'device_id': device_id, 'name': device_name}
            self.feature_devices[feature_key].append(device_info)
            
            # Add to feature tree
            feature_tree = getattr(self, f"{feature_key}_tree")
            feature_tree.insert("", tk.END, values=(device_name, "Ready"), tags=(device_id,))
            
            # Remove device from main device list
            self.device_tree.delete(device_item)
            
            # Update count
            count_label = getattr(self, f"{feature_key}_count_label")
            count_label.config(text=f"{len(self.feature_devices[feature_key])} devices")
            
            self.log_status(f"✅ Đã thêm {device_name} vào {feature_key}")
    
    def clear_feature_devices(self, feature_key):
        """Clear tất cả devices trong một feature"""
        # Get all devices from this feature
        devices_to_restore = self.feature_devices[feature_key].copy()
        
        # Clear feature devices
        self.feature_devices[feature_key].clear()
        feature_tree = getattr(self, f"{feature_key}_tree")
        for item in feature_tree.get_children():
            feature_tree.delete(item)
        
        # Restore devices to main device list
        for device_info in devices_to_restore:
            device_id = device_info['device_id']
            device_name = device_info['name']
            
            # Add back to main device tree
            item = self.device_tree.insert("", tk.END, values=(device_name, "Ready"))
            self.device_tree.item(item, tags=(device_id,))
        
        count_label = getattr(self, f"{feature_key}_count_label")
        count_label.config(text="0 devices")
        
        self.log_status(f"🗑️ Đã clear {feature_key} và trả lại {len(devices_to_restore)} devices")
    
    def clear_all_features(self):
        """Clear tất cả features"""
        total_restored = 0
        for feature_key in self.feature_devices.keys():
            # Get count before clearing
            device_count = len(self.feature_devices[feature_key])
            total_restored += device_count
            
            # Clear feature devices
            devices_to_restore = self.feature_devices[feature_key].copy()
            self.feature_devices[feature_key].clear()
            feature_tree = getattr(self, f"{feature_key}_tree")
            for item in feature_tree.get_children():
                feature_tree.delete(item)
            
            # Restore devices to main device list
            for device_info in devices_to_restore:
                device_id = device_info['device_id']
                device_name = device_info['name']
                
                # Add back to main device tree
                item = self.device_tree.insert("", tk.END, values=(device_name, "Ready"))
                self.device_tree.item(item, tags=(device_id,))
            
            # Update count
            count_label = getattr(self, f"{feature_key}_count_label")
            count_label.config(text="0 devices")
        
        self.log_status(f"🗑️ Đã clear tất cả features và trả lại {total_restored} devices")
    
    def remove_device_from_feature(self, device_item, feature_key):
        """Xóa device khỏi feature và trả về danh sách gốc"""
        if device_item:
            # Get device info
            feature_tree = getattr(self, f"{feature_key}_tree")
            device_id = feature_tree.item(device_item, "tags")[0]
            device_name = feature_tree.item(device_item, "values")[0]
            
            # Remove from feature
            self.feature_devices[feature_key] = [
                device for device in self.feature_devices[feature_key] 
                if device['device_id'] != device_id
            ]
            
            # Remove from feature tree
            feature_tree.delete(device_item)
            
            # Add back to main device tree
            item = self.device_tree.insert("", tk.END, values=(device_name, "Ready"))
            self.device_tree.item(item, tags=(device_id,))
            
            # Update count
            count_label = getattr(self, f"{feature_key}_count_label")
            count_label.config(text=f"{len(self.feature_devices[feature_key])} devices")
            
            self.log_status(f"🔄 Đã trả {device_name} về danh sách gốc từ {feature_key}")
    
    def move_device_between_features(self, device_item, from_feature_key, to_feature_key):
        """Di chuyển device từ feature này sang feature khác"""
        if device_item:
            # Get device info
            from_feature_tree = getattr(self, f"{from_feature_key}_tree")
            device_id = from_feature_tree.item(device_item, "tags")[0]
            device_name = from_feature_tree.item(device_item, "values")[0]
            
            # Remove from source feature
            self.feature_devices[from_feature_key] = [
                device for device in self.feature_devices[from_feature_key] 
                if device['device_id'] != device_id
            ]
            from_feature_tree.delete(device_item)
            
            # Add to target feature
            device_info = {'device_id': device_id, 'name': device_name}
            self.feature_devices[to_feature_key].append(device_info)
            
            to_feature_tree = getattr(self, f"{to_feature_key}_tree")
            to_feature_tree.insert("", tk.END, values=(device_name, "Ready"), tags=(device_id,))
            
            # Update counts
            from_count_label = getattr(self, f"{from_feature_key}_count_label")
            from_count_label.config(text=f"{len(self.feature_devices[from_feature_key])} devices")
            
            to_count_label = getattr(self, f"{to_feature_key}_count_label")
            to_count_label.config(text=f"{len(self.feature_devices[to_feature_key])} devices")
            
            self.log_status(f"🔄 Đã chuyển {device_name} từ {from_feature_key} sang {to_feature_key}")
    
    def on_feature_click(self, event, feature_key):
        """Handle click on feature device"""
        item = event.widget.identify_row(event.y)
        if item:
            event.widget.selection_set(item)
    
    def on_feature_drag(self, event, feature_key):
        """Handle drag in feature"""
        if event.widget.selection():
            self.dragged_device = event.widget.selection()[0]
            self.dragged_from_feature = feature_key
    
    def on_feature_release(self, event, feature_key):
        """Handle release in feature"""
        if hasattr(self, 'dragged_device') and self.dragged_device:
            # Check if dropped on main device list
            widget = event.widget.winfo_containing(event.x_root, event.y_root)
            if widget == self.device_tree:
                self.remove_device_from_feature(self.dragged_device, self.dragged_from_feature)
            elif widget != event.widget and hasattr(widget, 'winfo_class') and 'Treeview' in widget.winfo_class():
                # Check if dropped on another feature container
                for other_feature_key in self.feature_devices.keys():
                    other_feature_tree = getattr(self, f"{other_feature_key}_tree", None)
                    if other_feature_tree and widget == other_feature_tree and other_feature_key != self.dragged_from_feature:
                        self.move_device_between_features(self.dragged_device, self.dragged_from_feature, other_feature_key)
                        break
            
            self.dragged_device = None
            self.dragged_from_feature = None
    
    def log_status(self, message):
        """Log message vào status text"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        # Use after() to make it thread-safe
        self.root.after(0, self._update_status_text, f"[{timestamp}] {message}\n")
    
    def _update_status_text(self, message):
        """Update status text (called from main thread)"""
        self.status_text.insert(tk.END, message)
        self.status_text.see(tk.END)
    
    def start_all_features(self):
        """Bắt đầu tất cả features"""
        # Check if any feature has devices
        total_devices = sum(len(devices) for devices in self.feature_devices.values())
        if total_devices == 0:
            messagebox.showwarning("Cảnh báo", "Vui lòng kéo thả devices vào các tính năng trước!")
            return
        
        # Confirm before starting
        confirm = messagebox.askyesno("Xác nhận", 
                                    f"Bắt đầu chạy tất cả features trên {total_devices} device(s)?")
        if not confirm:
            return
        
        # Start automation
        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # Start automation in background thread
        automation_thread = threading.Thread(target=self.run_all_features)
        automation_thread.daemon = True
        automation_thread.start()
    
    def stop_all_features(self):
        """Dừng tất cả features"""
        self.is_running = False
        
        # Wait for all processes to finish
        for process in self.processes:
            if process.is_alive():
                process.join(timeout=1.0)
                if process.is_alive():
                    process.terminate()
        
        self.processes.clear()
        
        # Stop log thread
        if self.log_thread and self.log_thread.is_alive():
            self.log_thread.join(timeout=1.0)
        
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.log_status("⏹️ Đã dừng tất cả features")
    
    def run_all_features(self):
        """Chạy tất cả features song song với multiprocessing"""
        try:
            self.log_status("🚀 Bắt đầu chạy tất cả features song song...")
            
            # Feature mapping
            feature_mapping = {
                "rally": ("1", "Auto tham gia Rally"),
                "buy_meat": ("2", "Auto mua thịt"),
                "war_no_general": ("3", "Auto tham gia War (không chọn tướng)"),
                "attack_boss": ("4", "Auto tấn công Boss")
            }
            
            # Collect all device-feature tasks (đảm bảo mỗi device chỉ chạy 1 feature)
            all_tasks = []
            used_devices = set()  # Theo dõi devices đã được sử dụng
            
            for feature_key, (feature_code, feature_name) in feature_mapping.items():
                devices = self.feature_devices[feature_key]
                for device in devices:
                    device_id = device['device_id']
                    
                    # Kiểm tra xem device đã được sử dụng chưa
                    if device_id in used_devices:
                        self.log_status(f"⚠️ Device {device['name']} đã được assign cho feature khác, bỏ qua {feature_name}")
                        continue
                    
                    # Thêm device vào danh sách đã sử dụng
                    used_devices.add(device_id)
                    
                    all_tasks.append({
                        'device': device,
                        'feature_code': feature_code,
                        'feature_name': feature_name,
                        'feature_key': feature_key
                    })
            
            if not all_tasks:
                self.log_status("❌ Không có device nào để chạy!")
                return
            
            self.log_status(f"📋 Tổng cộng {len(all_tasks)} task cần thực hiện")
            
            # Start processes for each task (mỗi device-feature một process)
            self.processes = []
            for i, task in enumerate(all_tasks):
                self.log_status(f"🔄 Khởi động task {i+1}/{len(all_tasks)}: {task['feature_name']} trên {task['device']['name']}")
                
                # Create process for this specific device-feature combination
                process = multiprocessing.Process(
                    target=run_single_task_process,
                    args=(task, i+1, len(all_tasks), self.log_queue)
                )
                self.processes.append(process)
            
            # Start ALL processes at once
            for process in self.processes:
                process.start()
            
            self.log_status(f"🔄 Đã khởi động {len(self.processes)} processes song song")
            
            # Start log monitoring thread
            self.log_thread = threading.Thread(target=self.monitor_log_queue)
            self.log_thread.daemon = True
            self.log_thread.start()
            
            # Wait for all processes to complete
            for process in self.processes:
                process.join()
            
            self.log_status("✅ Hoàn thành tất cả features")
            
        except Exception as e:
            self.log_status(f"❌ Lỗi trong automation: {e}")
        finally:
            # Reset UI in main thread
            self.root.after(0, self.reset_ui_after_completion)
    
    def reset_ui_after_completion(self):
        """Reset UI sau khi hoàn thành"""
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
    
    def monitor_log_queue(self):
        """Monitor log queue từ processes và update UI"""
        while self.is_running:
            try:
                # Try to get message from queue with timeout
                message = self.log_queue.get(timeout=0.1)
                if message:
                    # Update UI in main thread
                    self.root.after(0, self.log_status, message)
            except:
                # Timeout or queue empty, continue
                continue

def main():
    """Hàm chính của chương trình"""
    # Set multiprocessing start method
    multiprocessing.set_start_method('spawn', force=True)
    
    root = tk.Tk()
    app = DragDropGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 