import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import random
from multiprocessing import Manager, Lock
from utils.adb_utils import swipe_up, swipe_down, select_memu_devices, set_device, get_memu_devices

class EVONYAutoSimpleGUI:
    def __init__(self, root):
        self.root = root
        self.root.title('EVONY AUTO - Simple Version (No OpenCV)')
        self.root.geometry('500x400')
        
        # Variables
        self.is_running = False
        self.selected_devices = []
        
        self.create_widgets()
    
    def create_widgets(self):
        # Device selection
        device_frame = ttk.LabelFrame(self.root, text='Chon Device', padding=10)
        device_frame.pack(fill='x', padx=10, pady=5)
        
        self.device_listbox = tk.Listbox(device_frame, height=4)
        self.device_listbox.pack(fill='x', pady=5)
        
        ttk.Button(device_frame, text='Lam moi Device', command=self.refresh_devices).pack(pady=5)
        
        # Control buttons
        control_frame = ttk.LabelFrame(self.root, text='Dieu khien', padding=10)
        control_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(control_frame, text='Start Auto', command=self.start_auto).pack(side='left', padx=5)
        ttk.Button(control_frame, text='Stop Auto', command=self.stop_auto).pack(side='left', padx=5)
        
        # Status
        self.status_label = ttk.Label(self.root, text='San sang')
        self.status_label.pack(pady=10)
        
        # Load devices
        self.refresh_devices()
    
    def refresh_devices(self):
        self.device_listbox.delete(0, tk.END)
        devices = get_memu_devices()
        for device in devices:
            self.device_listbox.insert(tk.END, f'{device[\"name\"]} - {device[\"device_id\"]}')
    
    def start_auto(self):
        if not self.is_running:
            self.is_running = True
            self.status_label.config(text='Dang chay...')
            threading.Thread(target=self.auto_loop, daemon=True).start()
    
    def stop_auto(self):
        self.is_running = False
        self.status_label.config(text='Da dung')
    
    def auto_loop(self):
        while self.is_running:
            try:
                # Simple auto actions
                devices = get_memu_devices()
                for device in devices:
                    if self.is_running:
                        # Swipe up
                        swipe_up(device['device_id'])
                        time.sleep(2)
                        
                        # Swipe down  
                        swipe_down(device['device_id'])
                        time.sleep(2)
                
                time.sleep(5)  # Wait 5 seconds before next cycle
            except Exception as e:
                print(f'Loi: {e}')
                time.sleep(1)

if __name__ == '__main__':
    root = tk.Tk()
    app = EVONYAutoSimpleGUI(root)
    root.mainloop()
