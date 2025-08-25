"""
Process Manager for EVONY AUTO
Handles all automation processes and task execution
"""

import multiprocessing
import time
from actions.war_actions import join_war_sequence, continue_war_sequence, join_war_sequence_no_general
from utils.adb_utils import set_device
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
    """Chạy attack_boss trong process con với vòng lặp vô hạn giống attack_boss.py"""
    try:
        if log_queue:
            log_queue.put(f"👹 Bắt đầu tấn công boss trên device {device_id}")
        
        # Import hàm từ get_location_boss (file cũ, an toàn)
        from actions.get_location_boss import get_boss_locations, save_to_json
        
        # Lưu danh sách tên boss được chọn ban đầu
        selected_boss_names = set()
        initial_selection = None
        
        while True:  # Vòng lặp chính để cập nhật boss (vô hạn)
            try:
                # Bước 1: Cập nhật vị trí boss từ thiết bị
                if log_queue:
                    log_queue.put(f"📡 Đang cập nhật vị trí boss từ thiết bị {device_id}...")
                
                # Sử dụng hàm từ get_location_boss (file cũ, an toàn)
                bosses = get_boss_locations()
                
                if not bosses:
                    if log_queue:
                        log_queue.put("❌ Không tìm thấy thông tin boss! Thử lại sau 60 giây.")
                    time.sleep(60)
                    continue
                    
                # Lưu thông tin boss vào file
                if not save_to_json(bosses, device_id=device_id):
                    if log_queue:
                        log_queue.put("❌ Không thể lưu thông tin boss vào file!")
                    time.sleep(60)
                    continue
                
                # Bước 2: Xử lý lựa chọn boss
                if not selected_boss_names:  # Nếu chưa có lựa chọn ban đầu
                    # Tự động chọn tất cả boss có sẵn
                    boss_groups = group_bosses_by_name(bosses)
                    initial_selection = []
                    
                    for boss_name, boss_group in boss_groups.items():
                        initial_selection.append(boss_group)
                        selected_boss_names.add(boss_name)
                    
                    if not initial_selection:
                        if log_queue:
                            log_queue.put("❌ Không có boss nào để tấn công!")
                        time.sleep(60)
                        continue
                    
                    if log_queue:
                        log_queue.put(f"✅ Đã tự động chọn {len(initial_selection)} loại boss để tấn công")
                else:  # Đã có lựa chọn trước đó, tạo lại initial_selection từ dữ liệu boss mới
                    boss_groups = group_bosses_by_name(bosses)
                    initial_selection = []
                    for name in selected_boss_names:
                        if name in boss_groups:
                            initial_selection.append(boss_groups[name])
                
                # Bước 3: Bắt đầu vòng lặp tấn công
                start_time = time.time()
                while True:
                    # Kiểm tra số boss chưa tấn công và hiển thị thông tin
                    unattacked_count = sum(1 for group in initial_selection
                                         for _, boss in group
                                         if not boss.get('attacked', 0))
                    
                    remaining_time = int(1800 - (time.time() - start_time))  # 30 phút = 1800 giây
                    if log_queue:
                        log_queue.put(f"⏱️ Còn {unattacked_count} boss, thời gian: {remaining_time}s")
                    
                    # Thực hiện tấn công các boss đã chọn
                    result = attack_selected_bosses(initial_selection, bosses, start_time)
                    
                    # Kiểm tra kết quả
                    if result == "update_required" or remaining_time <= 0:
                        if log_queue:
                            log_queue.put("⏰ Đã đủ 30 phút, cập nhật lại vị trí boss...")
                        break  # Thoát vòng lặp tấn công để cập nhật boss
                    elif unattacked_count == 0:
                        if log_queue:
                            log_queue.put("🎯 Đã hết boss, cập nhật lại vị trí boss...")
                        break  # Thoát vòng lặp tấn công để cập nhật boss
                    
                    time.sleep(1)
                
            except Exception as e:
                if log_queue:
                    log_queue.put(f"❌ Lỗi: {e}")
                    log_queue.put("Thử lại sau 1 phút...")
                time.sleep(60)
                 
    except Exception as e:
        if log_queue:
            log_queue.put(f"❌ Lỗi nghiêm trọng khi tấn công boss trên {device_id}: {e}")
