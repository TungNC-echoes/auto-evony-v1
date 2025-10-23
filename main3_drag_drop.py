"""
EVONY AUTO - Drag & Drop Manager
Main GUI application with modular components
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import multiprocessing
import time
from datetime import datetime

# Import components
from components.process_manager import run_single_task_process
from components.device_manager import DeviceManager
from components.ui_builder import UIBuilder
from utils.language_utils import set_language, get_current_language, get_available_languages


class DragDropGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("EVONY AUTO - Drag & Drop Manager")
        self.root.geometry("1920x1080")  # Tăng 20% (1600*1.2=1920, 900*1.2=1080)
        self.root.resizable(True, True)
        
        # Variables
        self.is_running = False
        self.processes = []
        self.log_queue = multiprocessing.Queue()
        self.log_thread = None
        
        # Feature status tracking
        self.feature_status = {
            "rally": {"running": False, "processes": []},
            "buy_meat": {"running": False, "processes": []},
            "war_no_general": {"running": False, "processes": []},
            "attack_boss": {"running": False, "processes": []},
            "open_items": {"running": False, "processes": []},
            "buy_general": {"running": False, "processes": []},
            "advanced_rally": {"running": False, "processes": []},
            "advanced_war": {"running": False, "processes": []}
        }
        
        # Initialize device manager and UI builder
        self.device_manager = DeviceManager(self)
        self.ui_builder = UIBuilder(self)
        
        self.ui_builder.setup_ui()
        self.device_manager.refresh_devices()
        
        # Start UI update timer to handle button states
        self.update_ui_states()
        
        # Initialize attack_boss troops validation
        self.attack_boss_troops_valid = False
    

    
    # Event handlers
    def on_container_enter(self, event, container):
        """Handle hover enter on feature container"""
        container.configure(style="PanelHover.TLabelframe")
    
    def on_container_leave(self, event, container):
        """Handle hover leave on feature container"""
        container.configure(style="Panel.TLabelframe")
    
    def on_feature_tree_enter(self, event):
        """Handle hover enter on feature treeview"""
        event.widget.configure(cursor="hand2")
    
    def on_feature_tree_leave(self, event):
        """Handle hover leave on feature treeview"""
        event.widget.configure(cursor="arrow")
    
    def on_language_change(self, event):
        """Handle language change event"""
        try:
            selected_text = self.language_var.get()
            # Extract language code from "Language Name (code)" format
            if "(" in selected_text and ")" in selected_text:
                language_code = selected_text.split("(")[1].split(")")[0]
                
                # Change language
                if set_language(language_code):
                    self.log_status(f"🌐 Đã chuyển sang ngôn ngữ: {selected_text}")
                    
                    # Update UI to reflect language change
                    self.update_language_ui()
                else:
                    self.log_status(f"❌ Không thể chuyển sang ngôn ngữ: {selected_text}")
                    # Revert selection
                    current_lang = get_current_language()
                    available_languages = get_available_languages()
                    current_lang_name = available_languages.get(current_lang, current_lang)
                    self.language_dropdown.set(f"{current_lang_name} ({current_lang})")
            else:
                self.log_status(f"❌ Định dạng ngôn ngữ không hợp lệ: {selected_text}")
        except Exception as e:
            self.log_status(f"❌ Lỗi khi thay đổi ngôn ngữ: {e}")
    
    def update_language_ui(self):
        """Update UI elements to reflect language change"""
        try:
            # Update language dropdown display
            current_lang = get_current_language()
            available_languages = get_available_languages()
            current_lang_name = available_languages.get(current_lang, current_lang)
            self.language_dropdown.set(f"{current_lang_name} ({current_lang})")
            
            # You can add more UI updates here if needed
            # For example, update button texts, labels, etc.
            
        except Exception as e:
            self.log_status(f"❌ Lỗi khi cập nhật UI ngôn ngữ: {e}")
    
    def on_feature_tree_motion(self, event):
        """Handle hover motion on feature treeview"""
        pass
    
    def on_device_click(self, event):
        """Handle click on device"""
        item = self.device_tree.identify_row(event.y)
        if item:
            self.device_tree.selection_set(item)
    
    def on_device_drag(self, event):
        """Handle drag from device list"""
        if self.device_tree.selection():
            self.device_manager.dragged_devices = list(self.device_tree.selection())
    
    def on_device_release(self, event):
        """Handle release from device list"""
        if hasattr(self.device_manager, 'dragged_devices') and self.device_manager.dragged_devices:
            # Check if dropped on a feature container
            widget = event.widget.winfo_containing(event.x_root, event.y_root)
            if widget:
                # Find which feature container this widget belongs to
                for feature_key in self.device_manager.feature_devices.keys():
                    feature_tree = getattr(self, f"{feature_key}_tree", None)
                    if feature_tree and widget == feature_tree:
                        # Add all selected devices to feature
                        for device_item in self.device_manager.dragged_devices:
                            self.device_manager.add_device_to_feature(device_item, feature_key)
                        break
            
            self.device_manager.dragged_devices = []
    
    def on_device_tree_enter(self, event):
        """Handle hover enter on device treeview"""
        event.widget.configure(cursor="hand2")
    
    def on_device_tree_leave(self, event):
        """Handle hover leave on device treeview"""
        event.widget.configure(cursor="arrow")
    
    def on_device_tree_motion(self, event):
        """Handle hover motion on device treeview"""
        pass
    
    def on_feature_click(self, event, feature_key):
        """Handle click on feature device"""
        item = event.widget.identify_row(event.y)
        if item:
            event.widget.selection_set(item)
    
    def on_feature_drag(self, event, feature_key):
        """Handle drag in feature"""
        if event.widget.selection():
            self.device_manager.dragged_device = event.widget.selection()[0]
            self.device_manager.dragged_from_feature = feature_key
    
    def on_feature_release(self, event, feature_key):
        """Handle release in feature"""
        if hasattr(self.device_manager, 'dragged_device') and self.device_manager.dragged_device:
            # Check if dropped on main device list
            widget = event.widget.winfo_containing(event.x_root, event.y_root)
            if widget == self.device_tree:
                self.device_manager.remove_device_from_feature(self.device_manager.dragged_device, self.device_manager.dragged_from_feature)
            elif widget != event.widget and hasattr(widget, 'winfo_class') and 'Treeview' in widget.winfo_class():
                # Check if dropped on another feature container
                for other_feature_key in self.device_manager.feature_devices.keys():
                    other_feature_tree = getattr(self, f"{other_feature_key}_tree", None)
                    if other_feature_tree and widget == other_feature_tree and other_feature_key != self.device_manager.dragged_from_feature:
                        self.device_manager.move_device_between_features(self.device_manager.dragged_device, self.device_manager.dragged_from_feature, other_feature_key)
                        break
            
            self.device_manager.dragged_device = None
            self.device_manager.dragged_from_feature = None
    
    # Logging methods
    def log_status(self, message):
        """Log message vào status text với hiệu ứng visual"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Determine message type for color coding
        if "✅" in message or "🚀" in message:
            color = "#28a745"  # Green for success
        elif "❌" in message or "⚠️" in message:
            color = "#dc3545"  # Red for errors/warnings
        elif "🔄" in message or "📡" in message:
            color = "#007bff"  # Blue for info/loading
        elif "⏱️" in message or "⏰" in message:
            color = "#ffc107"  # Yellow for time-related
        elif "🎯" in message or "👹" in message:
            color = "#6f42c1"  # Purple for game-related
        else:
            color = "#212529"  # Default dark gray
        
        # Use after() to make it thread-safe
        self.root.after(0, self._update_status_text, f"[{timestamp}] {message}\n", color)
    
    def _update_status_text(self, message, color="#212529"):
        """Update status text (called from main thread) with color coding"""
        # Insert with color tag
        self.status_text.insert(tk.END, message)
        
        # Apply color to the last inserted line
        start_index = self.status_text.index("end-2c linestart")
        end_index = self.status_text.index("end-1c")
        
        # Create tag for this color if it doesn't exist
        tag_name = f"color_{color.replace('#', '')}"
        self.status_text.tag_configure(tag_name, foreground=color)
        self.status_text.tag_add(tag_name, start_index, end_index)
        
        # Auto-scroll to bottom
        self.status_text.see(tk.END)
        
        # Limit the number of lines to prevent memory issues
        lines = int(self.status_text.index('end-1c').split('.')[0])
        if lines > 1000:  # Keep only last 1000 lines
            self.status_text.delete('1.0', f'{lines-500}.0')
    
    # Feature control methods
    def start_all_features(self):
        """Bắt đầu tất cả features"""
        # Check if any feature has devices
        total_devices = sum(len(devices) for devices in self.device_manager.feature_devices.values())
        if total_devices == 0:
            messagebox.showwarning("Cảnh báo", "Vui lòng kéo thả devices vào các tính năng trước!")
            return
        
        # Check if any individual feature is running
        running_features = [key for key, status in self.feature_status.items() if status["running"]]
        if running_features:
            messagebox.showwarning("Cảnh báo", f"Các features sau đang chạy: {', '.join(running_features)}. Vui lòng dừng chúng trước!")
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
    
    def start_feature(self, feature_key):
        """Bắt đầu một feature cụ thể"""
        devices = self.device_manager.feature_devices[feature_key]
        if not devices:
            messagebox.showwarning("Cảnh báo", f"Vui lòng thêm devices vào {feature_key} trước!")
            return
        
        if self.feature_status[feature_key]["running"]:
            messagebox.showinfo("Thông báo", f"{feature_key} đang chạy!")
            return
        
        # Check if "Start All" is running
        if self.is_running:
            messagebox.showwarning("Cảnh báo", "Đang chạy 'Bắt Đầu Tất Cả'. Vui lòng dừng nó trước!")
            return
        
        # Special validation for attack_boss feature
        if feature_key == "attack_boss":
            if not self.attack_boss_troops_valid:
                messagebox.showwarning("Cảnh báo", "Vui lòng nhập số lượng quân hợp lệ cho Attack Boss!")
                return
        
        # Confirm before starting
        feature_names = {
            "rally": "⚔️ Auto Rally",
            "buy_meat": "🛒 Auto Buy Meat", 
            "war_no_general": "🎯 Auto War (No General)",
            "attack_boss": "👹 Auto Attack Boss",
            "open_items": "📦 Auto Open Items",
            "buy_general": "🛒 Auto Buy General",
            "advanced_rally": "⚔️ Advanced Rally",
            "advanced_war": "🎯 Advanced War (No General)"
        }
        
        confirm = messagebox.askyesno("Xác nhận", 
                                    f"Bắt đầu {feature_names[feature_key]} trên {len(devices)} device(s)?")
        if not confirm:
            return
        
        # Start feature
        self.feature_status[feature_key]["running"] = True
        
        # Update UI
        start_button = getattr(self, f"{feature_key}_start_button")
        stop_button = getattr(self, f"{feature_key}_stop_button")
        status_label = getattr(self, f"{feature_key}_status_label")
        
        start_button.config(state=tk.DISABLED)
        stop_button.config(state=tk.NORMAL)
        status_label.config(text="🔄 Running")
        
        # Start automation in background thread
        automation_thread = threading.Thread(target=self.run_feature, args=(feature_key,))
        automation_thread.daemon = True
        automation_thread.start()
        
        self.log_status(f"🚀 Bắt đầu {feature_names[feature_key]} trên {len(devices)} device(s)")
    
    def stop_feature(self, feature_key):
        """Dừng một feature cụ thể"""
        if not self.feature_status[feature_key]["running"]:
            messagebox.showinfo("Thông báo", f"{feature_key} không đang chạy!")
            return
        
        # Stop feature
        self.feature_status[feature_key]["running"] = False
        
        # Wait for processes to finish with better cleanup
        processes_to_cleanup = self.feature_status[feature_key]["processes"].copy()
        for process in processes_to_cleanup:
            try:
                if process.is_alive():
                    # Try graceful termination first
                    process.terminate()
                    process.join(timeout=2.0)
                    
                    # Force kill if still alive
                    if process.is_alive():
                        process.kill()
                        process.join(timeout=1.0)
            except Exception as e:
                self.log_status(f"⚠️ Lỗi khi dừng process trong {feature_key}: {e}")
        
        # Clear process list và mapping
        self.feature_status[feature_key]["processes"].clear()
        self.device_manager.device_process_mapping[feature_key].clear()
        
        # Update UI
        start_button = getattr(self, f"{feature_key}_start_button")
        stop_button = getattr(self, f"{feature_key}_stop_button")
        status_label = getattr(self, f"{feature_key}_status_label")
        
        start_button.config(state=tk.NORMAL)
        stop_button.config(state=tk.DISABLED)
        status_label.config(text="⏸️ Stopped")
        
        feature_names = {
            "rally": "⚔️ Auto Rally",
            "buy_meat": "🛒 Auto Buy Meat", 
            "war_no_general": "🎯 Auto War (No General)",
            "attack_boss": "👹 Auto Attack Boss",
            "open_items": "📦 Auto Open Items",
            "buy_general": "🛒 Auto Buy General",
            "advanced_rally": "⚔️ Advanced Rally",
            "advanced_war": "🎯 Advanced War (No General)"
        }
        
        self.log_status(f"⏹️ Đã dừng {feature_names[feature_key]}")
    
    def run_feature(self, feature_key):
        """Chạy một feature cụ thể"""
        try:
            devices = self.device_manager.feature_devices[feature_key]
            
            # Feature mapping
            feature_mapping = {
                "rally": ("1", "Auto tham gia Rally"),
                "buy_meat": ("2", "Auto mua thịt"),
                "war_no_general": ("3", "Auto tham gia War (không chọn tướng)"),
                "attack_boss": ("4", "Auto tấn công Boss"),
                "open_items": ("5", "Auto mở Items"),
                "buy_general": ("6", "Auto mua tướng"),
                "advanced_rally": ("7", "Advanced Rally với Boss Selection"),
                "advanced_war": ("8", "Advanced War với Boss Selection")
            }
            
            feature_code, feature_name = feature_mapping[feature_key]
            
            # Create tasks for this feature
            tasks = []
            for device in devices:
                task = {
                    'device': device,
                    'feature_code': feature_code,
                    'feature_name': feature_name,
                    'feature_key': feature_key
                }
                
                # Add troops_count for attack_boss feature
                if feature_key == "attack_boss":
                    try:
                        troops_count = int(self.attack_boss_troops_var.get().strip())
                        task['troops_count'] = troops_count
                    except:
                        task['troops_count'] = 1000  # Default fallback
                
                # Add selected_bosses for Advanced features
                if feature_key in ["advanced_rally", "advanced_war"]:
                    selected_bosses = self.get_selected_bosses()
                    task['selected_bosses'] = selected_bosses
                    self.log_status(f"🎯 Debug: {feature_key} - Selected bosses: {selected_bosses} (type: {type(selected_bosses)})")
                
                tasks.append(task)
            
            # Start processes for each task
            processes = []
            for i, task in enumerate(tasks):
                if not self.feature_status[feature_key]["running"]:
                    break  # Stop if feature was stopped
                
                process = multiprocessing.Process(
                    target=run_single_task_process,
                    args=(task, i+1, len(tasks), self.log_queue)
                )
                processes.append(process)
                self.feature_status[feature_key]["processes"].append(process)
                
                # Lưu process vào mapping để track theo device_id
                device_id = task['device']['device_id']
                self.device_manager.device_process_mapping[feature_key][device_id] = process
            
            # Start all processes
            for process in processes:
                if self.feature_status[feature_key]["running"]:
                    process.start()
            
            # Monitor processes without blocking - use a separate thread
            def monitor_processes():
                try:
                    # Wait for all processes to complete, but check running status periodically
                    while self.feature_status[feature_key]["running"]:
                        all_completed = True
                        for process in processes:
                            if process.is_alive():
                                all_completed = False
                                break
                        
                        if all_completed:
                            break
                        
                        # Check every 1 second
                        time.sleep(1)
                    
                    # Update UI when complete (only if feature is still running)
                    if self.feature_status[feature_key]["running"]:
                        self.root.after(0, self.reset_feature_ui, feature_key)
                        
                except Exception as e:
                    self.log_status(f"❌ Lỗi trong monitor processes cho {feature_key}: {e}")
                    if self.feature_status[feature_key]["running"]:
                        self.root.after(0, self.reset_feature_ui, feature_key)
            
            # Start monitoring in a separate thread
            monitor_thread = threading.Thread(target=monitor_processes)
            monitor_thread.daemon = True
            monitor_thread.start()
                
        except Exception as e:
            self.log_status(f"❌ Lỗi trong {feature_key}: {e}")
            self.root.after(0, self.reset_feature_ui, feature_key)
    
    def reset_feature_ui(self, feature_key):
        """Reset UI cho một feature sau khi hoàn thành"""
        self.feature_status[feature_key]["running"] = False
        
        # Update UI
        start_button = getattr(self, f"{feature_key}_start_button")
        stop_button = getattr(self, f"{feature_key}_stop_button")
        status_label = getattr(self, f"{feature_key}_status_label")
        
        start_button.config(state=tk.NORMAL)
        stop_button.config(state=tk.DISABLED)
        status_label.config(text="✅ Completed")
        
        feature_names = {
            "rally": "⚔️ Auto Rally",
            "buy_meat": "🛒 Auto Buy Meat", 
            "war_no_general": "🎯 Auto War (No General)",
            "attack_boss": "👹 Auto Attack Boss",
            "open_items": "📦 Auto Open Items",
            "buy_general": "🛒 Auto Buy General",
            "advanced_rally": "⚔️ Advanced Rally",
            "advanced_war": "🎯 Advanced War (No General)"
        }
        
        self.log_status(f"✅ Hoàn thành {feature_names[feature_key]}")
    
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
                "attack_boss": ("4", "Auto tấn công Boss"),
                "open_items": ("5", "Auto mở Items"),
                "buy_general": ("6", "Auto mua tướng"),
                "advanced_rally": ("7", "Advanced Rally với Boss Selection"),
                "advanced_war": ("8", "Advanced War với Boss Selection")
            }
            
            # Collect all device-feature tasks (đảm bảo mỗi device chỉ chạy 1 feature)
            all_tasks = []
            used_devices = set()  # Theo dõi devices đã được sử dụng
            
            for feature_key, (feature_code, feature_name) in feature_mapping.items():
                devices = self.device_manager.feature_devices[feature_key]
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
    
    def is_any_feature_running(self):
        """Kiểm tra xem có feature nào đang chạy không"""
        return any(status["running"] for status in self.feature_status.values()) or self.is_running
    
    def validate_attack_boss_input(self):
        """Validate troops count input for attack_boss feature"""
        try:
            troops_text = self.attack_boss_troops_var.get().strip()
            validation_label = self.attack_boss_validation_label
            start_button = self.attack_boss_start_button
            
            if not troops_text:
                # Empty input
                validation_label.config(text="⚠️ Nhập số quân", style="Warning.TLabel")
                self.attack_boss_troops_valid = False
                start_button.config(state=tk.DISABLED)
            else:
                try:
                    troops_count = int(troops_text)
                    if troops_count <= 0:
                        # Invalid number
                        validation_label.config(text="⚠️ Số quân > 0", style="Warning.TLabel")
                        self.attack_boss_troops_valid = False
                        start_button.config(state=tk.DISABLED)
                    else:
                        # Valid input
                        validation_label.config(text="✅ OK", style="Success.TLabel")
                        self.attack_boss_troops_valid = True
                        # Enable start button if feature is not running and has devices
                        if not self.feature_status["attack_boss"]["running"] and len(self.device_manager.feature_devices["attack_boss"]) > 0:
                            start_button.config(state=tk.NORMAL)
                except ValueError:
                    # Not a number
                    validation_label.config(text="⚠️ Nhập số hợp lệ", style="Warning.TLabel")
                    self.attack_boss_troops_valid = False
                    start_button.config(state=tk.DISABLED)
        except Exception as e:
            self.log_status(f"❌ Lỗi validation: {e}")
    
    def update_ui_states(self):
        """Cập nhật trạng thái UI để tránh conflict"""
        try:
            # Disable "Start All" button if any individual feature is running
            if any(status["running"] for status in self.feature_status.values()):
                self.start_button.config(state=tk.DISABLED)
            elif not self.is_running:
                self.start_button.config(state=tk.NORMAL)
            
            # Disable individual feature buttons if "Start All" is running
            if self.is_running:
                for feature_key in self.feature_status.keys():
                    start_button = getattr(self, f"{feature_key}_start_button", None)
                    if start_button:
                        start_button.config(state=tk.DISABLED)
            else:
                # Enable individual feature buttons if they're not running
                for feature_key, status in self.feature_status.items():
                    start_button = getattr(self, f"{feature_key}_start_button", None)
                    if start_button and not status["running"]:
                        # Special handling for attack_boss validation
                        if feature_key == "attack_boss":
                            if self.attack_boss_troops_valid and len(self.device_manager.feature_devices["attack_boss"]) > 0:
                                start_button.config(state=tk.NORMAL)
                            else:
                                start_button.config(state=tk.DISABLED)
                        else:
                            # Other features - enable if has devices
                            if len(self.device_manager.feature_devices[feature_key]) > 0:
                                start_button.config(state=tk.NORMAL)
                            else:
                                start_button.config(state=tk.DISABLED)
            
        except Exception as e:
            pass  # Ignore errors in UI updates
        
        # Schedule next update
        self.root.after(1000, self.update_ui_states)  # Update every 1 second


    def get_selected_bosses(self):
        """Get selected bosses from UI"""
        try:
            if not hasattr(self, 'boss_vars'):
                return []
            
            selected_bosses = []
            for boss_name, var in self.boss_vars.items():
                if var.get():
                    selected_bosses.append(boss_name)
            
            return selected_bosses
        except Exception as e:
            print(f"Error getting selected bosses: {e}")
            return []

def main():
    """Hàm chính của chương trình"""
    # Set multiprocessing start method
    multiprocessing.set_start_method('spawn', force=True)
    
    root = tk.Tk()
    app = DragDropGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main() 