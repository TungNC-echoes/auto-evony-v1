import os
import time
import sys

# Thêm thư mục gốc vào PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.image_utils import find_and_click_button, find_and_click_right_edge, check_button_exists
from utils.adb_utils import adb_command, input_text, cancel_action
from actions.boss_data_manager import save_boss_data
from actions.war_actions import handle_insufficient_stamina

def attack_boss(boss_name, x_coord, y_coord, image_folder, troops_count, start_time=None):
    """Tấn công boss với tên và tọa độ được cung cấp"""
    try:
        # Click vào nút location với tối đa 2 lần thử
        max_retries = 2
        location_retry_count = 0
        
        while location_retry_count < max_retries:
            if find_and_click_button("attack/location", 'none', 0.7):
                break
            else:
                print(f"Không tìm thấy nút location, lần thử {location_retry_count + 1}/{max_retries}")
                location_retry_count += 1
                
                # Kéo màn hình lên 50px
                adb_command('adb shell input swipe 300 300 300 250 100')
                time.sleep(1)
                
        if location_retry_count >= max_retries:
            # Thực hiện ESC và cancel khi đã thử đủ số lần
            cancel_action()
            return False
        
        time.sleep(2)

        # Nhập tọa độ X
        if not find_and_click_right_edge("attack/x"):
            print("Không tìm thấy ô nhập tọa độ X")
            cancel_action()
            return False
            
        time.sleep(2)
        adb_command('adb shell input keyevent KEYCODE_MOVE_END')
        for _ in range(5):
            adb_command('adb shell input keyevent KEYCODE_DEL')
        input_text(x_coord)
        time.sleep(1)
        adb_command('adb shell input keyevent KEYCODE_ENTER')
        time.sleep(2)

        # Nhập tọa độ Y
        if not find_and_click_right_edge("attack/y"):
            print("Không tìm thấy ô nhập tọa độ Y")
            cancel_action()
            return False
            
        time.sleep(2)
        adb_command('adb shell input keyevent KEYCODE_MOVE_END')
        for _ in range(5):
            adb_command('adb shell input keyevent KEYCODE_DEL')
        input_text(y_coord)
        time.sleep(1)
        adb_command('adb shell input keyevent KEYCODE_ENTER')
        time.sleep(2)

        # Click nút tiến hành
        if not find_and_click_button("attack/tien_hanh"):
            return False
            
        time.sleep(3)

        # Tìm và click vào ảnh boss trong thư mục
        if os.path.exists(image_folder):
            for image_file in os.listdir(image_folder):
                if image_file.endswith(('.jpg', '.JPG', '.png', '.PNG')):
                    image_name = os.path.splitext(image_file)[0]
                    if find_and_click_button(f"attack/{boss_name}/{image_name}", 'none', 1, 2, 0.75):
                        print(f"Đã tìm thấy và click vào {boss_name}")
                        result = execute_attack_sequence(start_time, troops_count)  # Truyền số lượng quân
                        if result == "update_required":
                            return "update_required"
                        elif result:
                            return True
                        else:
                            print("Không thể hoàn thành chuỗi tấn công")
                            return False
                    time.sleep(0.5)

        print(f"Không tìm thấy ảnh {boss_name} phù hợp")
        return False

    except Exception as e:
        print(f"Lỗi khi tấn công boss: {e}")
        cancel_action()
        return False

def attack_selected_bosses(selected_groups, bosses, start_time=None):
    """Tấn công các boss đã chọn"""
    boss_types = {
        "Cerberus Cấp Thấp": {
            "folder": "cerberus", 
            "image_path": "images/buttons/attack/cerberus",
            "troops_count": "600000"
        },
        "Pan (Lục QUân)": {
            "folder": "pan_luc_quan", 
            "image_path": "images/buttons/attack/pan_luc_quan",
            "troops_count": "300000"
        },
        "Người đá": {
            "folder": "nguoi_da", 
            "image_path": "images/buttons/attack/nguoi_da",
            "troops_count": "300000"
        },
        "Pan (Viễn Quân)": {
            "folder": "pan_vien_quan", 
            "image_path": "images/buttons/attack/pan_vien_quan",
            "troops_count": "300000"
        },
        "Harp bình thường": {
            "folder": "harp",
            "image_path": "images/buttons/attack/harp",
            "troops_count": "700000"
        },
        "Phù thủy": {
            "folder": "phu_thuy",
            "image_path": "images/buttons/attack/phu_thuy",
            "troops_count": "500000"
            # "threshold": 0.75
        },
        "Nhân Sư": {
            "folder": "nhan_su",
            "image_path": "images/buttons/attack/nhan_su",
            "troops_count": "500000",
            # "threshold": 0.75
        },
        "Rùa Nham thạch": {
            "folder": "rua",
            "image_path": "images/buttons/attack/rua",
            "troops_count": "700000"
        },
        "Ymir": {
            "folder": "ymir",
            "image_path": "images/buttons/attack/ymir",
            "troops_count": "700000",
            # "threshold": 0.75
        },
        "Lãnh chúa": {
            "folder": "lanh_chua",
            "image_path": "images/buttons/attack/lanh_chua",
            "troops_count": "700000",
            # "threshold": 0.75-0.8
        },
        "Hiệp sĩ Cấp thấp Bayard": {
            "folder": "bayard",
            "image_path": "images/buttons/attack/Bayard",
            "troops_count": "700000",
            # "threshold": 0.8
        }
    }
    
    for group in selected_groups:
        boss_name = group[0][1]['name']
        boss_info = next((info for name, info in boss_types.items() if name in boss_name), None)
        
        if boss_info:
            print(f"\nĐang tấn công {boss_name}...")
            for idx, boss in group:
                if not boss.get('attacked', 0):
                    result = attack_boss(boss_info['folder'], 
                                      boss['level']['X'], 
                                      boss['level']['Y'], 
                                      boss_info['image_path'],
                                      boss_info['troops_count'],  # Thêm số lượng quân
                                      start_time)
                    if result == "update_required":
                        return "update_required"
                    elif result:
                        print(f"Tấn công thành công boss tại tọa độ X:{boss['level']['X']}, Y:{boss['level']['Y']}")
                    else:
                        print(f"Không tìm thấy boss tại tọa độ X:{boss['level']['X']}, Y:{boss['level']['Y']}")
                    boss['attacked'] = 1
                    save_boss_data(bosses)
                    time.sleep(1)
        else:
            print(f"Chưa hỗ trợ tấn công loại boss: {boss_name}")

def execute_attack_sequence(start_time=None, troops_count="300000"):
    """Thực hiện chuỗi hành động tấn công sau khi chọn boss"""
    try:
        # Kiểm tra thời gian nếu được cung cấp
        if start_time and time.time() - start_time >= 1800:  # 30 phút = 1800 giây
            print("\nĐã đủ 30 phút, cần cập nhật lại vị trí boss...")
            return "update_required"
            
        time.sleep(2)  # Chờ sau khi click vào boss

        # Click các nút đầu tiên
        initial_buttons = [
            "attack/attack",
            "attack/war"
        ]

        # Click lần lượt các nút đầu tiên
        for button in initial_buttons:
            if not find_and_click_button(button):
                print(f"Không thể click vào nút {button}")
                return False
            time.sleep(2)

        # Kiểm tra và xử lý trường hợp bị giới hạn đội quân
        max_retries = 7  # Số lần thử lại tối đa
        retry_count = 0
        
        while retry_count < max_retries:
            # Click nút 5minutes và kiểm tra doi_quan_san_co
            if not find_and_click_button("attack/5minutes", 'none', 1):
                print("Không thể click vào nút 5minutes")
                return False
            time.sleep(2)

            # Kiểm tra nút doi_quan_san_co
            if check_button_exists("doi_quan_san_co", 'none', 0.95):
                if find_and_click_button("doi_quan_san_co"):
                    # Nếu click thành công, tiếp tục chuỗi hành động
                    remaining_buttons = [
                        "chon_tuong",
                        "chon",
                        "attack/nhap_quan"
                    ]
                    
                    # Click lần lượt các nút còn lại
                    for button in remaining_buttons:
                        if not find_and_click_button(button, 'none', 1, 1, 0.8):
                            print(f"Không thể click vào nút {button}")
                            return False
                        time.sleep(2)

                    # Nhập số lượng quân và hoàn thành tấn công
                    adb_command('adb shell input keyevent KEYCODE_DEL')
                    adb_command(f'adb shell input text "{troops_count}"')
                    # time.sleep(1)
                    adb_command('adb shell input keyevent KEYCODE_ENTER')
                    time.sleep(1)

                    # Click nút hành quân
                    if not find_and_click_button("hanh_quan", 'none', 1, 1, 0.7):
                        print("Không thể click vào nút hành quân")
                        # Thêm kiểm tra thể lực ở đây
                        if check_button_exists("xac_nhan"):
                            print("Phát hiện trường hợp không đủ thể lực")
                            if handle_insufficient_stamina():
                                print("Đã xử lý xong trường hợp không đủ thể lực")
                                # Thử click lại nút hành quân
                                if find_and_click_button("hanh_quan", 'none', 1, 2, 0.7):
                                    return True
                            else:
                                print("Không thể xử lý trường hợp không đủ thể lực")
                        return False
                        
                    # Kiểm tra xem có nút xác nhận không (trường hợp không đủ thể lực)
                    time.sleep(2)  # Chờ để xem có hiện thông báo không
                    if check_button_exists("xac_nhan"):
                        print("Phát hiện trường hợp không đủ thể lực")
                        if handle_insufficient_stamina():
                            print("Đã xử lý xong trường hợp không đủ thể lực")
                        else:
                            print("Không thể xử lý trường hợp không đủ thể lực")
                            return False

                    print("Hoàn thành một lượt tấn công")      
                    return True
            else:
                print(f"Lần {retry_count + 1}: Không thấy nút doi_quan_san_co, đợi 30s và thử lại...")
                time.sleep(30)  # Đợi
                retry_count += 1
                if retry_count >= max_retries:
                    print(f"Đã thử {max_retries} lần không thành công")
                    return False
                continue

        print("Đã hết số lần thử lại, không thể hoàn thành tấn công")
        return False

    except Exception as e:
        print(f"Lỗi trong quá trình thực hiện tấn công: {e}")
        return False
