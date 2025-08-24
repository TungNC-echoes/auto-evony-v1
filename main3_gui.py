import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import random
from multiprocessing import Manager, Lock
from actions.war_actions import join_war_sequence, continue_war_sequence, join_war_sequence_no_general
from utils.image_utils import check_button_exists, find_and_click_button
from utils.adb_utils import swipe_up, swipe_down, select_memu_devices, set_device, get_memu_devices
from actions.rally import auto_join_rally
from actions.market_actions import auto_buy_meat

# Import cho attack boss
import sys
import os
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from actions.user_interface import get_boss_selection, display_boss_list
from actions.get_location_boss import get_boss_locations, save_to_json
from actions.boss_data_manager import load_boss_data, group_bosses_by_name
from actions.boss_attacker import attack_selected_bosses

class EVONYAutoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("EVONY AUTO - Multi Device Manager")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Variables
        self.devices = []
        self.selected_devices = []
        self.device_vars = {}
        self.feature_var = tk.StringVar(value="1")
        self.is_running = False
        self.processes = []
        
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
        
        # Title
        title_label = ttk.Label(main_frame, text="EVONY AUTO - Multi Device Manager", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Device selection section
        device_frame = ttk.LabelFrame(main_frame, text="Chọn Devices", padding="10")
        device_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        device_frame.columnconfigure(0, weight=1)
        
        # Device list with scrollbar
        device_list_frame = ttk.Frame(device_frame)
        device_list_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        device_list_frame.columnconfigure(0, weight=1)
        device_list_frame.rowconfigure(0, weight=1)
        
        # Create Treeview for devices
        columns = ("Device", "Status", "Select")
        self.device_tree = ttk.Treeview(device_list_frame, columns=columns, show="headings", height=8)
        
        # Configure columns
        self.device_tree.heading("Device", text="Device Name")
        self.device_tree.heading("Status", text="Status")
        self.device_tree.heading("Select", text="Select")
        
        self.device_tree.column("Device", width=200)
        self.device_tree.column("Status", width=100)
        self.device_tree.column("Select", width=80)
        
        # Scrollbar for device list
        device_scrollbar = ttk.Scrollbar(device_list_frame, orient=tk.VERTICAL, command=self.device_tree.yview)
        self.device_tree.configure(yscrollcommand=device_scrollbar.set)
        
        self.device_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        device_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Device buttons
        device_buttons_frame = ttk.Frame(device_frame)
        device_buttons_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        ttk.Button(device_buttons_frame, text="Refresh Devices", 
                  command=self.refresh_devices).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(device_buttons_frame, text="Select All", 
                  command=self.select_all_devices).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(device_buttons_frame, text="Deselect All", 
                  command=self.deselect_all_devices).pack(side=tk.LEFT)
        
        # Feature selection section
        feature_frame = ttk.LabelFrame(main_frame, text="Chọn Tính Năng", padding="10")
        feature_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        features = [
            ("1", "Auto tham gia Rally"),
            ("2", "Auto mua thịt"),
            ("3", "Auto tham gia War (không chọn tướng)"),
            ("4", "Auto tấn công Boss")
        ]
        
        for i, (value, text) in enumerate(features):
            ttk.Radiobutton(feature_frame, text=text, variable=self.feature_var, 
                           value=value).grid(row=i, column=0, sticky=tk.W, pady=2)
        
        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=3, column=0, columnspan=3, pady=(10, 0))
        
        self.start_button = ttk.Button(control_frame, text="Bắt Đầu", 
                                      command=self.start_automation, style="Accent.TButton")
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(control_frame, text="Dừng", 
                                     command=self.stop_automation, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT)
        
        # Status section
        status_frame = ttk.LabelFrame(main_frame, text="Trạng Thái", padding="10")
        status_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
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
        main_frame.rowconfigure(4, weight=1)
    
    def refresh_devices(self):
        """Refresh danh sách devices"""
        try:
            self.log_status("Đang tải danh sách devices...")
            self.devices = get_memu_devices()
            
            # Clear existing items
            for item in self.device_tree.get_children():
                self.device_tree.delete(item)
            
            # Add devices to treeview
            for device in self.devices:
                device_id = device['device_id']
                device_name = device['name']
                
                # Create checkbox variable
                var = tk.BooleanVar()
                self.device_vars[device_id] = var
                
                # Add to treeview
                item = self.device_tree.insert("", tk.END, values=(device_name, "Ready", "☐"))
                
                # Store device_id in item for later reference
                self.device_tree.set(item, "Device", device_name)
                self.device_tree.item(item, tags=(device_id,))
            
            # Bind click event to the entire treeview
            self.device_tree.bind("<Button-1>", self.on_treeview_click)
            
            self.log_status(f"Đã tải {len(self.devices)} devices")
            
        except Exception as e:
            self.log_status(f"Lỗi khi tải devices: {e}")
            messagebox.showerror("Lỗi", f"Không thể tải danh sách devices:\n{e}")
    
    def on_treeview_click(self, event):
        """Handle click event on treeview"""
        region = self.device_tree.identify("region", event.x, event.y)
        if region == "cell":
            column = self.device_tree.identify_column(event.x)
            if column == "#3":  # Select column
                item = self.device_tree.identify_row(event.y)
                if item:
                    # Get device_id from item tags
                    tags = self.device_tree.item(item, "tags")
                    if tags:
                        device_id = tags[0]
                        self.toggle_device_selection(device_id)
    
    def toggle_device_selection(self, device_id):
        """Toggle selection của device"""
        if device_id in self.device_vars:
            var = self.device_vars[device_id]
            var.set(not var.get())
            
            # Update treeview display
            for item in self.device_tree.get_children():
                tags = self.device_tree.item(item, "tags")
                if tags and device_id in tags:
                    if var.get():
                        self.device_tree.set(item, "Select", "☑")
                    else:
                        self.device_tree.set(item, "Select", "☐")
                    break
    
    def select_all_devices(self):
        """Chọn tất cả devices"""
        for device_id, var in self.device_vars.items():
            var.set(True)
        
        # Update treeview
        for item in self.device_tree.get_children():
            self.device_tree.set(item, "Select", "☑")
    
    def deselect_all_devices(self):
        """Bỏ chọn tất cả devices"""
        for device_id, var in self.device_vars.items():
            var.set(False)
        
        # Update treeview
        for item in self.device_tree.get_children():
            self.device_tree.set(item, "Select", "☐")
    
    def get_selected_devices(self):
        """Lấy danh sách devices đã chọn"""
        selected = []
        for device in self.devices:
            device_id = device['device_id']
            if device_id in self.device_vars and self.device_vars[device_id].get():
                selected.append(device)
        return selected
    
    def log_status(self, message):
        """Log message vào status text"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.see(tk.END)
        self.root.update_idletasks()
    
    def start_automation(self):
        """Bắt đầu automation"""
        selected_devices = self.get_selected_devices()
        
        if not selected_devices:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn ít nhất một device!")
            return
        
        feature_choice = self.feature_var.get()
        
        # Confirm before starting
        feature_names = {
            "1": "Auto tham gia Rally",
            "2": "Auto mua thịt", 
            "3": "Auto tham gia War (không chọn tướng)",
            "4": "Auto tấn công Boss"
        }
        
        confirm = messagebox.askyesno("Xác nhận", 
                                    f"Bắt đầu {feature_names[feature_choice]} trên {len(selected_devices)} device(s)?")
        if not confirm:
            return
        
        # Start automation in separate thread
        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # Start automation thread
        automation_thread = threading.Thread(target=self.run_automation, 
                                           args=(selected_devices, feature_choice))
        automation_thread.daemon = True
        automation_thread.start()
    
    def stop_automation(self):
        """Dừng automation"""
        self.is_running = False
        
        # Wait for all threads to finish
        for thread in self.processes:
            if thread.is_alive():
                thread.join(timeout=1.0)  # Wait up to 1 second for each thread
        
        self.processes.clear()
        
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.log_status("Đã dừng automation")
    
    def run_automation(self, devices, feature_choice):
        """Chạy automation trong thread riêng"""
        try:
            self.log_status(f"Bắt đầu chạy trên {len(devices)} device(s)...")
            
            # Tạo lock cho mỗi thiết bị
            device_locks = {device['device_id']: threading.Lock() for device in devices}
            
            # Tạo và khởi chạy các thread
            self.processes = []
            for device in devices:
                thread = threading.Thread(
                    target=self.run_feature_for_device,
                    args=(device, feature_choice, device_locks[device['device_id']])
                )
                thread.daemon = True
                self.processes.append(thread)
                thread.start()
                self.log_status(f"Đã khởi động thread cho {device['name']}")
            
            # Chờ tất cả các thread hoàn thành
            for thread in self.processes:
                thread.join()
                
            self.log_status("Hoàn thành automation")
            
        except Exception as e:
            self.log_status(f"Lỗi trong automation: {e}")
        finally:
            # Reset UI
            self.root.after(0, self.reset_ui_after_completion)
    
    def reset_ui_after_completion(self):
        """Reset UI sau khi hoàn thành"""
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
    
    def run_feature_for_device(self, device, feature_choice, device_lock):
        """Chạy tính năng cho một thiết bị cụ thể"""
        try:
            self.log_status(f"Bắt đầu chạy trên {device['name']}...")
            self.run_feature_with_retry(device, feature_choice, device_lock)
        except Exception as e:
            self.log_status(f"Lỗi nghiêm trọng khi chạy trên {device['name']}: {e}")
    
    def run_feature_with_retry(self, device, feature_choice, device_lock):
        """Chạy tính năng với cơ chế thử lại liên tục"""
        max_retries = 3
        retry_count = 0
        
        while self.is_running:  # Vòng lặp vô hạn để tiếp tục chạy
            try:
                with device_lock:
                    set_device(device['device_id'])
                
                if feature_choice == "1":
                    self.log_status(f"Bắt đầu auto tham gia Rally trên {device['name']}...")
                    auto_join_rally(device['device_id'], use_general=True)
                elif feature_choice == "2":
                    self.log_status(f"Bắt đầu auto mua thịt trên {device['name']}...")
                    auto_buy_meat(device['device_id'])
                elif feature_choice == "3":
                    self.log_status(f"Bắt đầu auto tham gia War (không chọn tướng) trên {device['name']}...")
                    auto_join_rally(device['device_id'], use_general=False)
                elif feature_choice == "4":
                    self.log_status(f"Bắt đầu auto tấn công Boss trên {device['name']}...")
                    self.run_attack_boss_for_device(device['device_id'])
                    
                # Reset số lần thử lại khi thành công
                retry_count = 0
                    
            except Exception as e:
                self.log_status(f"Lỗi trên {device['name']}: {e}")
                retry_count += 1
                
                if retry_count >= max_retries:
                    self.log_status(f"Đã thử lại {max_retries} lần không thành công, đợi thêm thời gian...")
                    time.sleep(30)
                    retry_count = 0
                    continue
                
                if "libpng error" in str(e):
                    self.log_status(f"Lỗi đọc ảnh trên {device['name']}, đang thử lại... (Lần {retry_count}/{max_retries})")
                    time.sleep(5)
                    continue
                    
                elif "Không ở trong chợ đen" in str(e):
                    self.log_status(f"Không ở trong chợ đen trên {device['name']}, đang thử vào lại... (Lần {retry_count}/{max_retries})")
                    time.sleep(3)
                    continue
                    
                else:
                    self.log_status(f"Lỗi khác trên {device['name']}, đang thử lại... (Lần {retry_count}/{max_retries})")
                    time.sleep(2)
                    continue
    
    def run_attack_boss_for_device(self, device_id):
        """Chạy attack_boss cho một device cụ thể"""
        try:
            # Thiết lập device
            set_device(device_id)
            
            self.log_status(f"Bắt đầu tấn công boss trên device {device_id}")
            
            # Bước 1: Cập nhật vị trí boss từ thiết bị
            self.log_status(f"Đang cập nhật vị trí boss từ thiết bị {device_id}...")
            bosses = get_boss_locations()
            
            if not bosses:
                self.log_status("Không tìm thấy thông tin boss!")
                return
                
            # Lưu thông tin boss vào file
            if not save_to_json(bosses, device_id=device_id):
                self.log_status("Không thể lưu thông tin boss vào file!")
                return
            
            # Bước 2: Tự động chọn tất cả boss (tránh input trong multi-process)
            boss_groups = group_bosses_by_name(bosses)
            initial_selection = []
            
            # Chọn tất cả boss có sẵn
            for boss_name, boss_group in boss_groups.items():
                initial_selection.append(boss_group)
            
            if not initial_selection:
                self.log_status("Không có boss nào để tấn công!")
                return
            
            self.log_status(f"Đã tự động chọn {len(initial_selection)} loại boss để tấn công")
            
            # Bước 3: Bắt đầu vòng lặp tấn công
            start_time = time.time()
            while self.is_running:
                # Kiểm tra số boss chưa tấn công và hiển thị thông tin
                unattacked_count = sum(1 for group in initial_selection
                                     for _, boss in group
                                     if not boss.get('attacked', 0))
                
                remaining_time = int(1800 - (time.time() - start_time))  # 30 phút = 1800 giây
                self.log_status(f"Còn {unattacked_count} boss chưa tấn công, thời gian còn lại: {remaining_time} giây")
                
                # Thực hiện tấn công các boss đã chọn
                result = attack_selected_bosses(initial_selection, bosses, start_time)
                
                # Kiểm tra kết quả
                if result == "update_required" or remaining_time <= 0:
                    self.log_status("Đã đủ 30 phút, kết thúc tấn công boss...")
                    break  # Thoát vòng lặp tấn công
                elif unattacked_count == 0:
                    self.log_status("Đã hết boss, kết thúc tấn công boss...")
                    break  # Thoát vòng lặp tấn công
                
                time.sleep(1)
                    
        except Exception as e:
            self.log_status(f"Lỗi khi tấn công boss trên {device_id}: {e}")

def main():
    """Hàm chính của chương trình"""
    root = tk.Tk()
    app = EVONYAutoGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 