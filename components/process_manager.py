"""
Process Manager for EVONY AUTO
Handles all automation processes and task execution
"""

import multiprocessing
import time
from actions.war_actions import join_war_sequence, continue_war_sequence, join_war_sequence_no_general
from utils.adb_utils import set_device
from actions.rally import auto_join_rally, auto_join_advanced_rally_with_boss_selection
from actions.market_actions import auto_buy_meat
from actions.open_items_actions import open_items_sequence, open_items_selective_sequence

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
            # Get troops_count from task for attack_boss
            troops_count = task.get('troops_count', 1000)  # Default fallback
            run_attack_boss_direct_process(device_id, log_queue=log_queue, troops_count=troops_count)
        elif feature_code == "5":
            run_open_items_direct_process(device_id, log_queue=log_queue)
        elif feature_code == "6":
            # Advanced Rally
            selected_bosses = task.get('selected_bosses', [])
            run_advanced_rally_direct_process(device_id, log_queue=log_queue, selected_bosses=selected_bosses)
        elif feature_code == "7":
            # Advanced War
            selected_bosses = task.get('selected_bosses', [])
            run_advanced_war_direct_process(device_id, log_queue=log_queue, selected_bosses=selected_bosses)
        
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


def run_attack_boss_direct_process(device_id, log_queue=None, troops_count=1000):
    """Chạy attack_boss trong process con với vòng lặp vô hạn giống attack_boss.py"""
    try:
        if log_queue:
            log_queue.put(f"👹 Bắt đầu tấn công boss trên device {device_id} với {troops_count} quân")
        
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
                if log_queue:
                    log_queue.put("🔍 Đang gọi get_boss_locations()...")
                bosses = get_boss_locations()
                
                if log_queue:
                    log_queue.put(f"📊 Kết quả get_boss_locations(): {type(bosses)} - {len(bosses) if bosses else 0} boss")
                
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
                    
                    # Thực hiện tấn công các boss đã chọn với troops_count từ UI
                    result = attack_selected_bosses(initial_selection, bosses, start_time, troops_count)
                    
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


def run_open_items_direct_process(device_id, log_queue=None):
    """Chạy open_items trong process con"""
    try:
        if log_queue:
            log_queue.put(f"📦 Bắt đầu auto open items trên device {device_id}")
        
        # Chạy vòng lặp vô hạn để mở items liên tục
        while True:
            try:
                # Thực hiện chuỗi mở items
                if open_items_sequence(device_id):
                    if log_queue:
                        log_queue.put(f"✅ Hoàn thành một lượt mở items trên {device_id}")
                else:
                    if log_queue:
                        log_queue.put(f"⚠️ Không thể mở items trên {device_id}, thử lại sau...")
                
                # Chờ một chút trước khi thử lại
                time.sleep(5)
                
            except Exception as e:
                if log_queue:
                    log_queue.put(f"❌ Lỗi khi mở items trên {device_id}: {e}")
                time.sleep(10)  # Chờ lâu hơn khi có lỗi
                
    except Exception as e:
        if log_queue:
            log_queue.put(f"❌ Lỗi nghiêm trọng khi mở items trên {device_id}: {e}")

def run_advanced_rally_direct_process(device_id, log_queue=None, selected_bosses=None):
    """Chạy Advanced Rally với boss selection trong process con"""
    try:
        if log_queue:
            log_queue.put(f"🎯 Bắt đầu Advanced Rally trên device {device_id}")
            log_queue.put(f"📋 Selected bosses: {selected_bosses}")
            log_queue.put(f"🔍 Debug: selected_bosses type: {type(selected_bosses)}, length: {len(selected_bosses) if selected_bosses else 0}")
        
        # Kiểm tra selected_bosses
        if not selected_bosses:
            if log_queue:
                log_queue.put("⚠️ Không có boss nào được chọn, sử dụng logic Basic Rally")
            # Fallback to Basic Rally if no bosses selected
            from actions.rally import auto_join_rally
            auto_join_rally(device_id, use_general=True)
        else:
            # Gọi function Advanced Rally
            auto_join_advanced_rally_with_boss_selection(device_id, use_general=True, selected_bosses=selected_bosses)
        
        if log_queue:
            log_queue.put(f"✅ Hoàn thành Advanced Rally trên device {device_id}")
    except Exception as e:
        if log_queue:
            log_queue.put(f"❌ Lỗi khi chạy Advanced Rally trên {device_id}: {e}")

def run_advanced_war_direct_process(device_id, log_queue=None, selected_bosses=None):
    """Chạy Advanced War với boss selection trong process con"""
    try:
        if log_queue:
            log_queue.put(f"🎯 Bắt đầu Advanced War trên device {device_id}")
            log_queue.put(f"📋 Selected bosses: {selected_bosses}")
            log_queue.put(f"🔍 Debug: selected_bosses type: {type(selected_bosses)}, length: {len(selected_bosses) if selected_bosses else 0}")
        
        # Kiểm tra selected_bosses
        if not selected_bosses:
            if log_queue:
                log_queue.put("⚠️ Không có boss nào được chọn, sử dụng logic Basic Rally")
            # Fallback to Basic Rally if no bosses selected
            from actions.rally import auto_join_rally
            auto_join_rally(device_id, use_general=False)
        else:
            # Gọi function Advanced Rally (không chọn tướng)
            auto_join_advanced_rally_with_boss_selection(device_id, use_general=False, selected_bosses=selected_bosses)
        
        if log_queue:
            log_queue.put(f"✅ Hoàn thành Advanced War trên device {device_id}")
    except Exception as e:
        if log_queue:
            log_queue.put(f"❌ Lỗi khi chạy Advanced War trên {device_id}: {e}")
