"""
Device Manager for EVONY AUTO
Handles device operations, drag & drop, and device state management
"""

import tkinter as tk
from tkinter import ttk, messagebox
from utils.adb_utils import get_memu_devices


class DeviceManager:
    """Manages device operations and state"""
    
    def __init__(self, gui_instance):
        self.gui = gui_instance
        self.devices = []
        self.dragged_devices = []
        self.dragged_device = None
        self.dragged_from_feature = None
        
        # Feature containers - mỗi feature sẽ chứa devices được kéo vào
        self.feature_devices = {
            "rally": [],
            "buy_meat": [],
            "war_no_general": [],
            "attack_boss": []
        }
    
    def refresh_devices(self):
        """Refresh danh sách devices - chỉ load những device chưa được assign"""
        try:
            self.gui.log_status("🔄 Đang tải danh sách devices...")
            all_devices = get_memu_devices()
            
            # Lấy danh sách device IDs đã được assign vào các feature
            assigned_device_ids = set()
            for feature_devices in self.feature_devices.values():
                for device in feature_devices:
                    assigned_device_ids.add(device['device_id'])
            
            # Lọc ra những device chưa được assign
            available_devices = []
            for device in all_devices:
                if device['device_id'] not in assigned_device_ids:
                    available_devices.append(device)
            
            # Clear existing items
            for item in self.gui.device_tree.get_children():
                self.gui.device_tree.delete(item)
            
            # Add available devices to treeview with alternating colors
            for i, device in enumerate(available_devices):
                device_id = device['device_id']
                device_name = device['name']
                
                # Add to treeview
                item = self.gui.device_tree.insert("", tk.END, values=(device_name, "Ready"))
                
                # Store device info in item
                self.gui.device_tree.item(item, tags=(device_id,))
                
                # Add alternating row colors for better visual separation
                if i % 2 == 0:
                    self.gui.device_tree.tag_configure("evenrow", background="#f8f9fa")
                    self.gui.device_tree.item(item, tags=(device_id, "evenrow"))
                else:
                    self.gui.device_tree.tag_configure("oddrow", background="#ffffff")
                    self.gui.device_tree.item(item, tags=(device_id, "oddrow"))
            
            # Cập nhật danh sách devices hiện tại
            self.devices = available_devices
            
            self.gui.log_status(f"✅ Đã tải {len(available_devices)} devices khả dụng (tổng cộng {len(all_devices)} devices)")
            
        except Exception as e:
            self.gui.log_status(f"❌ Lỗi khi tải devices: {e}")
            messagebox.showerror("Lỗi", f"Không thể tải danh sách devices:\n{e}")
    
    def refresh_all_devices(self):
        """Refresh toàn bộ danh sách devices từ ADB"""
        try:
            self.gui.log_status("🔄 Đang tải danh sách devices từ ADB...")
            all_devices = get_memu_devices()
            
            # Clear existing items
            for item in self.gui.device_tree.get_children():
                self.gui.device_tree.delete(item)
            
            # Add all devices to treeview with alternating colors
            for i, device in enumerate(all_devices):
                device_id = device['device_id']
                device_name = device['name']
                
                # Add to treeview
                item = self.gui.device_tree.insert("", tk.END, values=(device_name, "Ready"))
                
                # Store device info in item
                self.gui.device_tree.item(item, tags=(device_id,))
                
                # Add alternating row colors for better visual separation
                if i % 2 == 0:
                    self.gui.device_tree.tag_configure("evenrow", background="#f8f9fa")
                    self.gui.device_tree.item(item, tags=(device_id, "evenrow"))
                else:
                    self.gui.device_tree.tag_configure("oddrow", background="#ffffff")
                    self.gui.device_tree.item(item, tags=(device_id, "oddrow"))
            
            self.devices = all_devices
            self.gui.log_status(f"✅ Đã tải {len(all_devices)} devices từ ADB")
        except Exception as e:
            self.gui.log_status(f"❌ Lỗi khi tải devices từ ADB: {e}")
            messagebox.showerror("Lỗi", f"Không thể tải danh sách devices từ ADB:\n{e}")
    
    def select_all_devices(self):
        """Chọn tất cả devices (highlight)"""
        for item in self.gui.device_tree.get_children():
            self.gui.device_tree.selection_add(item)
    
    def clear_all_devices(self):
        """Clear selection"""
        self.gui.device_tree.selection_remove(self.gui.device_tree.selection())
    
    def add_device_to_feature(self, device_item, feature_key, show_log=True):
        """Thêm device vào feature container - trả về True nếu thành công"""
        if device_item:
            # Get device info
            device_id = self.gui.device_tree.item(device_item, "tags")[0]
            device_name = self.gui.device_tree.item(device_item, "values")[0]
            
            # Check if device already in this feature
            for device in self.feature_devices[feature_key]:
                if device['device_id'] == device_id:
                    if show_log:
                        self.gui.log_status(f"⚠️ Device {device_name} đã có trong {feature_key}")
                    return False
            
            # Add device to feature
            device_info = {'device_id': device_id, 'name': device_name}
            self.feature_devices[feature_key].append(device_info)
            
            # Add to feature tree with visual feedback
            feature_tree = getattr(self.gui, f"{feature_key}_tree")
            item = feature_tree.insert("", tk.END, values=(device_name, "Ready"), tags=(device_id,))
            
            # Add visual styling for the new item
            feature_tree.tag_configure("newitem", background="#d4edda", foreground="#155724")
            feature_tree.item(item, tags=(device_id, "newitem"))
            
            # Remove the highlight after a short delay
            self.gui.root.after(2000, lambda: self.remove_highlight(feature_tree, item, device_id))
            
            # Remove device from main device list
            self.gui.device_tree.delete(device_item)
            
            # Update count
            count_label = getattr(self.gui, f"{feature_key}_count_label")
            count_label.config(text=f"{len(self.feature_devices[feature_key])} devices")
            
            if show_log:
                self.gui.log_status(f"✅ Đã thêm {device_name} vào {feature_key}")
            
            return True
        return False
    
    def remove_highlight(self, tree, item, device_id):
        """Remove highlight from device item after animation"""
        try:
            # Remove the "newitem" tag but keep the device_id tag
            tree.item(item, tags=(device_id,))
        except:
            pass  # Item might have been deleted
    
    def clear_feature_devices(self, feature_key):
        """Clear tất cả devices trong một feature"""
        # Get all devices from this feature
        devices_to_restore = self.feature_devices[feature_key].copy()
        
        # Clear feature devices
        self.feature_devices[feature_key].clear()
        feature_tree = getattr(self.gui, f"{feature_key}_tree")
        for item in feature_tree.get_children():
            feature_tree.delete(item)
        
        # Restore devices to main device list
        for device_info in devices_to_restore:
            device_id = device_info['device_id']
            device_name = device_info['name']
            
            # Add back to main device tree
            item = self.gui.device_tree.insert("", tk.END, values=(device_name, "Ready"))
            self.gui.device_tree.item(item, tags=(device_id,))
        
        count_label = getattr(self.gui, f"{feature_key}_count_label")
        count_label.config(text="0 devices")
        
        self.gui.log_status(f"🗑️ Đã clear {feature_key} và trả lại {len(devices_to_restore)} devices")
    
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
            feature_tree = getattr(self.gui, f"{feature_key}_tree")
            for item in feature_tree.get_children():
                feature_tree.delete(item)
            
            # Restore devices to main device list
            for device_info in devices_to_restore:
                device_id = device_info['device_id']
                device_name = device_info['name']
                
                # Add back to main device tree
                item = self.gui.device_tree.insert("", tk.END, values=(device_name, "Ready"))
                self.gui.device_tree.item(item, tags=(device_id,))
            
            # Update count
            count_label = getattr(self.gui, f"{feature_key}_count_label")
            count_label.config(text="0 devices")
        
        self.gui.log_status(f"🗑️ Đã clear tất cả features và trả lại {total_restored} devices")
    
    def remove_device_from_feature(self, device_item, feature_key):
        """Xóa device khỏi feature và trả về danh sách gốc"""
        if device_item:
            # Get device info
            feature_tree = getattr(self.gui, f"{feature_key}_tree")
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
            item = self.gui.device_tree.insert("", tk.END, values=(device_name, "Ready"))
            self.gui.device_tree.item(item, tags=(device_id,))
            
            # Update count
            count_label = getattr(self.gui, f"{feature_key}_count_label")
            count_label.config(text=f"{len(self.feature_devices[feature_key])} devices")
            
            self.gui.log_status(f"🔄 Đã trả {device_name} về danh sách gốc từ {feature_key}")
    
    def move_device_between_features(self, device_item, from_feature_key, to_feature_key):
        """Di chuyển device từ feature này sang feature khác"""
        if device_item:
            # Get device info
            from_feature_tree = getattr(self.gui, f"{from_feature_key}_tree")
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
            
            to_feature_tree = getattr(self.gui, f"{to_feature_key}_tree")
            to_feature_tree.insert("", tk.END, values=(device_name, "Ready"), tags=(device_id,))
            
            # Update counts
            from_count_label = getattr(self.gui, f"{from_feature_key}_count_label")
            from_count_label.config(text=f"{len(self.feature_devices[from_feature_key])} devices")
            
            to_count_label = getattr(self.gui, f"{to_feature_key}_count_label")
            to_count_label.config(text=f"{len(self.feature_devices[to_feature_key])} devices")
            
            self.gui.log_status(f"🔄 Đã chuyển {device_name} từ {from_feature_key} sang {to_feature_key}")
    
    def add_all_selected_to_feature(self):
        """Thêm tất cả devices đã chọn vào feature được chọn từ dropdown"""
        selected_items = self.gui.device_tree.selection()
        if not selected_items:
            self.gui.log_status("⚠️ Vui lòng chọn ít nhất 1 device trước!")
            return
        
        # Map dropdown selection to feature key
        feature_mapping = {
            "⚔️ Auto Rally": "rally",
            "🛒 Auto Buy Meat": "buy_meat", 
            "🎯 Auto War (No General)": "war_no_general",
            "👹 Auto Attack Boss": "attack_boss"
        }
        
        selected_feature = self.gui.feature_var.get()
        feature_key = feature_mapping.get(selected_feature)
        
        if not feature_key:
            self.gui.log_status("❌ Vui lòng chọn feature từ dropdown!")
            return
        
        added_count = 0
        for device_item in selected_items:
            if self.add_device_to_feature(device_item, feature_key, show_log=False):
                added_count += 1
        
        if added_count > 0:
            self.gui.log_status(f"✅ Đã thêm {added_count} device(s) vào {selected_feature}")
        else:
            self.gui.log_status("⚠️ Không có device nào được thêm (có thể đã tồn tại trong feature)")
    
    def add_selected_to_feature(self, feature_key):
        """Thêm tất cả devices đã chọn vào feature cụ thể"""
        selected_items = self.gui.device_tree.selection()
        if not selected_items:
            self.gui.log_status("⚠️ Vui lòng chọn ít nhất 1 device trước!")
            return
        
        added_count = 0
        for device_item in selected_items:
            if self.add_device_to_feature(device_item, feature_key, show_log=False):
                added_count += 1
        
        if added_count > 0:
            self.gui.log_status(f"✅ Đã thêm {added_count} device(s) vào {feature_key}")
        else:
            self.gui.log_status("⚠️ Không có device nào được thêm (có thể đã tồn tại trong feature)")
