import sys
import os
import time
from datetime import datetime

# Thêm thư mục gốc vào PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from actions.user_interface import main, get_boss_selection, display_boss_list
from actions.get_location_boss import get_boss_locations, save_to_json # Code cũ, tạm thời vô hiệu hóa
# from actions.get_location_boss_device import get_boss_locations_from_device, save_to_json
from actions.boss_data_manager import load_boss_data, group_bosses_by_name
from actions.boss_attacker import attack_selected_bosses
from utils.adb_utils import select_memu_devices, set_device

def auto_update_and_attack():
    print("="*50)
    print("CHƯƠNG TRÌNH TỰ ĐỘNG TẤN CÔNG BOSS")
    print("="*50)
    
    # Chọn thiết bị MEmu
    devices = select_memu_devices()
    if not devices:
        print("Không có giả lập nào được chọn, kết thúc chương trình.")
        return
        
    print("\nDanh sách thiết bị được chọn:")
    for device in devices:
        print(f"- {device['name']} ({device['device_id']})")
    
    # Thiết lập device đầu tiên làm device mặc định để lấy thông tin boss
    main_device_id = devices[0]['device_id']
    set_device(main_device_id)
    
    # Lưu danh sách tên boss được chọn ban đầu
    selected_boss_names = set()
    initial_selection = None
    
    while True:  # Vòng lặp chính để cập nhật boss
        try:
            # Bước 1: Cập nhật vị trí boss từ thiết bị
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Đang cập nhật vị trí boss từ thiết bị {main_device_id}...")
            bosses = get_boss_locations() # Code cũ
            # bosses = get_boss_locations_from_device(main_device_id) # Code mới
            if bosses is None: # Hàm mới trả về None nếu có lỗi
                print("Lỗi khi lấy thông tin boss từ thiết bị. Thử lại sau 60 giây.")
                time.sleep(60)
                continue
            if not bosses:
                print("Không tìm thấy thông tin boss! Thử lại sau 60 giây.")
                time.sleep(60)
                continue
                
            # Lưu thông tin boss vào file
            if not save_to_json(bosses, device_id=main_device_id): # Truyền device_id để lưu file riêng
                print("Không thể lưu thông tin boss vào file!")
                time.sleep(60)
                continue
            
            # Bước 2: Xử lý lựa chọn boss
            if not selected_boss_names:  # Nếu chưa có lựa chọn ban đầu
                boss_groups = display_boss_list(bosses)
                initial_selection = get_boss_selection(boss_groups)
                
                if initial_selection is None:  # Người dùng chọn thoát
                    return
                    
                # Lưu lại tên các boss được chọn
                for group in initial_selection:
                    boss_name = group[0][1]['name']  # Lấy tên từ boss đầu tiên trong nhóm
                    selected_boss_names.add(boss_name)
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
                print(f"\nCòn {unattacked_count} boss chưa tấn công")
                print(f"Thời gian còn lại: {remaining_time} giây")
                
                # Thực hiện tấn công các boss đã chọn
                result = attack_selected_bosses(initial_selection, bosses, start_time)
                
                # Kiểm tra kết quả
                if result == "update_required" or remaining_time <= 0:
                    print("\nĐã đủ 30 phút, cập nhật lại vị trí boss...")
                    break  # Thoát vòng lặp tấn công để cập nhật boss
                elif unattacked_count == 0:
                    print("\nĐã hết boss, cập nhật lại vị trí boss...")
                    break  # Thoát vòng lặp tấn công để cập nhật boss
                
                time.sleep(1)
            
        except KeyboardInterrupt:
            print("\nĐã dừng chương trình.")
            break
        except Exception as e:
            print(f"\nLỗi: {e}")
            print("Thử lại sau 1 phút...")
            time.sleep(60)

if __name__ == "__main__":
    auto_update_and_attack()