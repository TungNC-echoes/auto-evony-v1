import os
import time
import sys

# Thêm thư mục gốc vào PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.image_utils import find_and_click_button, find_and_click_right_edge, check_button_exists
from utils.adb_utils import adb_command, input_text, cancel_action
from utils.language_utils import get_image_path
from actions.boss_data_manager import save_boss_data
from actions.war_actions import handle_insufficient_stamina

def attack_boss(boss_name, x_coord, y_coord, image_folder, troops_count, start_time=None, threshold=0.8, boss_info=None):
    """Tấn công boss với tên và tọa độ được cung cấp"""
    try:
        print(f"🔍 Tìm kiếm: {boss_name} - {image_folder} - X:{x_coord}, Y:{y_coord}")
        
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
        if not find_and_click_right_edge("attack/x", threshold=0.8):
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
        if not find_and_click_right_edge("attack/y", threshold=0.8):
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
        if not find_and_click_button("attack/tien_hanh", threshold=0.8):
            return False
            
        time.sleep(3)

        # Tìm và click vào ảnh boss trong thư mục
        if os.path.exists(image_folder):
            for image_file in os.listdir(image_folder):
                if image_file.endswith(('.jpg', '.JPG', '.png', '.PNG')):
                    image_name = os.path.splitext(image_file)[0]
                    if boss_info and find_and_click_button(f"attack/{boss_info['folder']}/{image_name}", 'none', 1, 2, threshold):
                        print(f"✅ Tìm thấy: {boss_name} - {image_name}")
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

def check_image_folder_exists(image_path):
    """Kiểm tra xem thư mục ảnh có tồn tại không"""
    return os.path.exists(image_path)

def list_boss_support_status(bosses_data):
    """Liệt kê trạng thái hỗ trợ của tất cả các loại boss trong dữ liệu"""
    print("\n" + "="*60)
    print("📊 TRẠNG THÁI HỖ TRỢ CÁC LOẠI BOSS")
    print("="*60)
    
    # Lấy danh sách unique các loại boss
    unique_bosses = {}
    for boss in bosses_data.get('bosses', []):
        boss_name = boss['name']
        if boss_name not in unique_bosses:
            unique_bosses[boss_name] = {
                'count': 1,
                'attacked': boss.get('attacked', 0)
            }
        else:
            unique_bosses[boss_name]['count'] += 1
            if boss.get('attacked', 0):
                unique_bosses[boss_name]['attacked'] += 1
    
    # Kiểm tra trạng thái hỗ trợ cho từng loại boss
    for boss_name, info in unique_bosses.items():
        boss_config = get_boss_config(boss_name)
        
        if boss_config.get('is_fallback', False):
            status_icon = "❌"
            status_text = "BỎ QUA (chưa hỗ trợ)"
        else:
            status_icon = "✅"
            status_text = "SẼ TẤN CÔNG"
        
        folder_status = "📁" if boss_config.get('folder_exists', True) else "❌"
        
        print(f"{status_icon} {boss_name} - {status_text}")
        print(f"   📊 Số lượng: {info['count']} | Đã tấn công: {info['attacked']}")
        print(f"   {folder_status} Thư mục: {boss_config['image_path']}")
        print(f"   🎯 Threshold: {boss_config['threshold']}")
        
        if boss_config.get('is_fallback', False):
            print(f"   ⚠️  Boss này sẽ bị bỏ qua vì chưa được định nghĩa")
        print()
    
    print("="*60)
    print("📝 CHÚ THÍCH:")
    print("✅ = Boss được định nghĩa sẵn - SẼ TẤN CÔNG")
    print("❌ = Boss chưa được định nghĩa - BỎ QUA")
    print("📁 = Thư mục ảnh tồn tại")
    print("❌ = Thư mục ảnh không tồn tại")
    print("="*60)

def get_boss_config(boss_name, troops_count=500000):
    """Lấy cấu hình cho boss dựa trên tên, với fallback cho các boss chưa được định nghĩa cụ thể"""
    
    # Dictionary chính cho các boss đã được định nghĩa cụ thể
    specific_boss_types = {
        "Aglaope": {
            "folder": "aglaope",
            "image_path": get_image_path("buttons/attack/aglaope/"),
            "troops_count": str(troops_count),
            "threshold": 0.7
        },
        "Cerberus Cấp Thấp": {
            "folder": "cerberus", 
            "image_path": get_image_path("buttons/attack/cerberus/"),
            "troops_count": str(troops_count),
            "threshold": 0.7
        },
        "Cerberus Cấp Trung": {
            "folder": "cerberus",
            "image_path": get_image_path("buttons/attack/cerberus/"),
            "troops_count": str(troops_count),
            "threshold": 0.7
        },
        "Cerberus Cấp Cao": {
            "folder": "cerberus",
            "image_path": get_image_path("buttons/attack/cerberus/"),
            "troops_count": str(troops_count),
            "threshold": 0.7
        },
        "Kỵ Sĩ Gugler Thường": {
            "folder": "gugler_knight",
            "image_path": get_image_path("buttons/attack/gugler_knight/"),
            "troops_count": str(troops_count),
            "threshold": 0.8
        },
        "Pan (Lục QUân)": {
            "folder": "pan_luc_quan", 
            "image_path": get_image_path("buttons/attack/pan_luc_quan/"),
            "troops_count": str(troops_count),
            "threshold": 0.7
        },
        "Người đá": {
            "folder": "nguoi_da", 
            "image_path": get_image_path("buttons/attack/nguoi_da/"),
            "troops_count": str(troops_count),
            "threshold": 0.8
        },
        "Pan (Viễn Quân)": {
            "folder": "pan_vien_quan", 
            "image_path": get_image_path("buttons/attack/pan_vien_quan/"),
            "troops_count": str(troops_count),
            "threshold": 0.7
        },
        "Pan (Lục Quân)": {
            "folder": "pan_luc_quan",
            "image_path": get_image_path("buttons/attack/pan_luc_quan/"),
            "troops_count": str(troops_count),
            "threshold": 0.7
        },
        "Pan (Kỵ Binh)": {
            "folder": "pan_ky_binh",
            "image_path": get_image_path("buttons/attack/pan_ky_binh/"),
            "troops_count": str(troops_count),
            "threshold": 0.7
        },
        "Harp bình thường": {
            "folder": "harp",
            "image_path": get_image_path("buttons/attack/harp/"),
            "troops_count": str(troops_count),
            "threshold": 0.7
        },
        "Phù thủy": {
            "folder": "phu_thuy",
            "image_path": get_image_path("buttons/attack/phu_thuy/"),
            "troops_count": str(troops_count),
            "threshold": 0.7
        },
        "Nhân Sư": {
            "folder": "nhan_su",
            "image_path": get_image_path("buttons/attack/nhan_su/"),
            "troops_count": str(troops_count),
            "threshold": 0.75
        },
        "Rùa Nham thạch": {
            "folder": "rua",
            "image_path": get_image_path("buttons/attack/rua/"),
            "troops_count": str(troops_count),
            "threshold": 0.7
        },
        "(Trùm quái vật) Fafnir": {
            "folder": "fafnir",
            "image_path": get_image_path("buttons/attack/fafnir/"),
            "troops_count": str(troops_count),
            "threshold": 0.7
        },
        "Quái vật Khổng lồ": {
            "folder": "titan",
            "image_path": get_image_path("buttons/attack/fafnir/"),
            "troops_count": str(troops_count),
            "threshold": 0.8
        },
        "Phượng hoàng": {
            "folder": "phonix",
            "image_path": get_image_path("buttons/attack/fafnir/"),
            "troops_count": str(troops_count),
            "threshold": 0.7
        },
        "Ymir": {
            "folder": "ymir",
            "image_path": get_image_path("buttons/attack/ymir/"),
            "troops_count": str(troops_count),
            "threshold": 0.8
        },
        "Lãnh chúa": {
            "folder": "lanh_chua",
            "image_path": get_image_path("buttons/attack/lanh_chua/"),
            "troops_count": str(troops_count),
            "threshold": 0.75
        },
        "Hiệp sĩ Cấp thấp Bayard": {
            "folder": "bayard",
            "image_path": get_image_path("buttons/attack/bayard/"),
            "troops_count": str(troops_count),
            "threshold": 0.8
        },
        "Hiệp sĩ Cấp cao Bayar": {
            "folder": "bayard",
            "image_path": get_image_path("buttons/attack/bayard/"),
            "troops_count": str(troops_count),
            "threshold": 0.8
        },
        "Hiệp Sĩ Bayar Hoàn Hảo": {
            "folder": "bayard",
            "image_path": get_image_path("buttons/attack/bayard/"),
            "troops_count": str(troops_count),
            "threshold": 0.8
        },
        "Normal Serpopard": {
            "folder": "serpopard",
            "image_path": get_image_path("buttons/attack/serpopard/"),
            "troops_count": str(troops_count),
            "threshold": 0.9
        },
        "Rắn Nhiều Đầu Cấp thấp": {
            "folder": "hydra",
            "image_path": get_image_path("buttons/attack/hydra/"),
            "troops_count": str(troops_count),
            "threshold": 0.85
        },
        "Rắn Nhiều Đầu Cấp trung": {
            "folder": "hydra",
            "image_path": get_image_path("buttons/attack/hydra/"),
            "troops_count": str(troops_count),
            "threshold": 0.85
        },
        "Rắn Nhiều Đầu Cấp cao": {
            "folder": "hydra",
            "image_path": get_image_path("buttons/attack/hydra/"),
            "troops_count": str(troops_count),
            "threshold": 0.85
        },
        "Quái vật Bí ngô": {
            "folder": "pumpkin",
            "image_path": get_image_path("buttons/attack/pumpkin/"),
            "troops_count": str(troops_count),
            "threshold": 0.9
        },
        "Nian Cấp cao": {
            "folder": "nian",
            "image_path": get_image_path("buttons/attack/nian/"),
            "troops_count": str(troops_count),
            "threshold": 0.75
        },
        "Niên Thú Huyền Thoại": {
            "folder": "nian",
            "image_path": get_image_path("buttons/attack/nian/"),
            "troops_count": str(troops_count),
            "threshold": 0.75
        },
        "Nasu Thường": {
            "folder": "nasu",
            "image_path": get_image_path("buttons/attack/nasu/"),
            "troops_count": str(troops_count),
            "threshold": 0.75
        }
    }
    
    # Kiểm tra xem boss có được định nghĩa cụ thể không
    if boss_name in specific_boss_types:
        config = specific_boss_types[boss_name].copy()
        config['is_fallback'] = False  # Đánh dấu đây là boss đã định nghĩa sẵn
        config['folder_exists'] = check_image_folder_exists(config['image_path'])
        return config
    
    # Fallback: Tạo cấu hình động dựa trên tên boss
    # Loại bỏ các ký tự đặc biệt và tạo folder name
    clean_name = boss_name.replace("(", "").replace(")", "").replace(" ", "_").lower()
    clean_name = clean_name.replace("trùm_quái_vật_", "").replace("trùm_", "")
    
    # Tạo đường dẫn ảnh dựa trên tên đã làm sạch
    image_path = get_image_path(f"buttons/attack/{clean_name}")
    
    # Kiểm tra xem thư mục ảnh có tồn tại không
    folder_exists = check_image_folder_exists(image_path)
    
    config = {
        "folder": clean_name,
        "image_path": image_path,
        "troops_count": str(troops_count),
        "threshold": 0.7,  # Threshold mặc định
        "folder_exists": folder_exists,
        "is_fallback": True  # Đánh dấu đây là cấu hình fallback
    }
    
    if not folder_exists:
        print(f"⚠️  Cảnh báo: Thư mục ảnh không tồn tại: {image_path}")
        print(f"   Boss '{boss_name}' sẽ sử dụng cấu hình fallback")
        print(f"   Vui lòng tạo thư mục và thêm ảnh boss vào: {image_path}")
    
    return config

def attack_selected_bosses(selected_groups, bosses, start_time=None, troops_count=500000):
    """Tấn công các boss đã chọn với troops_count từ UI"""
    
    for group in selected_groups:
        boss_name = group[0][1]['name']
        # Sử dụng hàm get_boss_config mới để lấy cấu hình cho boss
        boss_info = get_boss_config(boss_name, troops_count)
        
        # Kiểm tra xem boss có được định nghĩa sẵn không
        if boss_info.get('is_fallback', False):
            # Boss chưa được định nghĩa - bỏ qua và hiện cảnh báo
            print(f"\n⚠️  BỎ QUA BOSS CHƯA ĐƯỢC HỖ TRỢ: {boss_name}")
            print(f"   Tọa độ: {group[0][1]['level']['X']},{group[0][1]['level']['Y']}")
            print(f"   Boss này chưa được định nghĩa trong danh sách hỗ trợ")
            print(f"   Vui lòng thêm cấu hình cho boss này trong specific_boss_types")
            print(f"   Hoặc tạo thư mục ảnh: {boss_info['image_path']}")
            continue  # Bỏ qua boss này, chuyển sang boss tiếp theo
        
        # Boss đã được định nghĩa sẵn - tiến hành tấn công
        print(f"\n🎯 {boss_name} - {boss_info['folder']} - Tọa độ: {group[0][1]['level']['X']},{group[0][1]['level']['Y']}")
        print(f"📁 Đường dẫn ảnh: {boss_info['image_path']}")
        print(f"🎯 Threshold: {boss_info['threshold']}")
        print(f"✅ Sử dụng cấu hình được định nghĩa sẵn")
        
        for idx, boss in group:
            if not boss.get('attacked', 0):
                result = attack_boss(boss_info['folder'], 
                                  boss['level']['X'], 
                                  boss['level']['Y'], 
                                  boss_info['image_path'],
                                  boss_info['troops_count'],
                                  start_time,
                                  boss_info.get('threshold', 0.7),
                                  boss_info)
                if result == "update_required":
                    return "update_required"
                elif result:
                    print(f"✅ Thành công: {boss_name} - {boss_info['folder']} - X:{boss['level']['X']}, Y:{boss['level']['Y']}")
                else:
                    print(f"❌ Thất bại: {boss_name} - {boss_info['folder']} - X:{boss['level']['X']}, Y:{boss['level']['Y']}")
                boss['attacked'] = 1
                save_boss_data(bosses)
                time.sleep(1)

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
            if not find_and_click_button(button, threshold=0.85):
                print(f"Không thể click vào nút {button}")
                return False
            time.sleep(2)

        # Kiểm tra và xử lý trường hợp bị giới hạn đội quân
        max_retries = 7  # Số lần thử lại tối đa
        retry_count = 0
        
        while retry_count < max_retries:
            # Click nút 5minutes và kiểm tra doi_quan_san_co
            if not find_and_click_button("attack/5minutes", 'none', 1, threshold=0.85):
                print("Không thể click vào nút 5minutes")
                return False
            time.sleep(2)

            # Kiểm tra nút doi_quan_san_co
            if check_button_exists("doi_quan_san_co", 'none', 0.85):
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
