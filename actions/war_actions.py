import time
import random
from utils.image_utils import find_and_click_button, check_button_exists
from utils.adb_utils import swipe_down, swipe_up, ensure_evony_running


# ===== CONSTANTS =====
WAR_BUTTONS_SEQUENCE = [
    ("join_button", 2),       # Nút tham gia, chờ 2 giây
    ("doi_quan_san_co", 1),   # Nút đổi quân sân cỏ, chờ 1 giây
    ("chon_tuong", 1),        # Nút chọn tướng, chờ 1 giây
    ("chon", 1),              # Nút chọn, chờ 1 giây
    ("hanh_quan", 1)          # Nút hành quân, chờ 1 giây
]

WAR_BUTTONS_SEQUENCE_NO_GENERAL = [
    ("join_button", 2),       # Nút tham gia, chờ 2 giây
    ("doi_quan_san_co", 1),   # Nút đổi quân sân cỏ, chờ 1 giây
    ("hanh_quan", 1)          # Nút hành quân, chờ 1 giây
]

INSUFFICIENT_STAMINA_BUTTONS = [
    ("xac_nhan", 1),          # Nút xác nhận, chờ 1 giây
    ("dung", 1),              # Nút dừng, chờ 1 giây
    ("dung2", 1),             # Nút dừng 2, chờ 1 giây
    ("back", 1),              # Nút back, chờ 1 giây
    ("hanh_quan", 1)          # Nút hành quân, chờ 1 giây
]


# ===== HELPER FUNCTIONS =====
def click_button_sequence(buttons, device_id=None, sequence_name="buttons"):
    """Thực hiện click chuỗi buttons theo thứ tự"""
    try:
        for button_name, wait_time in buttons:
            if not find_and_click_button(button_name, device_id=device_id, wait_time=wait_time):
                print(f"Không thể tìm thấy hoặc click vào nút {button_name}")
                return False
        return True
    except Exception as e:
        print(f"Lỗi trong quá trình click {sequence_name}: {e}")
        return False


def find_join_button_with_scroll(device_id=None):
    """Tìm nút join_button bằng cách scroll xuống/lên nếu cần"""
    try:
        # Kéo màn hình xuống để kiểm tra các cuộc chiến tranh
        if swipe_down():
            # Kiểm tra xem có nút join_button không sau khi kéo xuống
            if not check_button_exists("join_button", device_id=device_id):
                # print("Không tìm thấy nút tham gia sau khi kéo xuống, kéo lên lại...")
                swipe_up()
                # Kiểm tra lại nút join_button ở vị trí ban đầu
                if not check_button_exists("join_button", device_id=device_id):
                    # print("Không tìm thấy nút tham gia ở vị trí ban đầu")
                    return False
        return True
    except Exception as e:
        print(f"Lỗi khi tìm nút join_button: {e}")
        return False


def check_and_handle_insufficient_stamina(device_id=None):
    """Kiểm tra và xử lý trường hợp không đủ thể lực"""
    try:
        if check_button_exists("xac_nhan", device_id=device_id):
            print("Phát hiện trường hợp không đủ thể lực")
            if handle_insufficient_stamina(device_id):
                print("Đã xử lý xong trường hợp không đủ thể lực")
                return True
            else:
                print("Không thể xử lý trường hợp không đủ thể lực")
                return False
        return True
    except Exception as e:
        print(f"Lỗi khi kiểm tra thể lực: {e}")
        return False


# ===== MAIN FUNCTIONS =====
def handle_insufficient_stamina(device_id=None):
    """Xử lý trường hợp không đủ thể lực"""
    try:
        print("Đang xử lý trường hợp không đủ thể lực...")
        return click_button_sequence(INSUFFICIENT_STAMINA_BUTTONS, device_id, "insufficient stamina")
    except Exception as e:
        print(f"Lỗi trong quá trình xử lý không đủ thể lực: {e}")
        return False


def join_war_sequence(device_id=None):
    """Thực hiện chuỗi hành động tham gia chiến tranh"""
    try:
        # Click vào nút chiến tranh
        if not find_and_click_button("war_button", device_id=device_id, wait_time=2):
            # print("Không thể tìm thấy hoặc click vào nút chiến tranh")
            return False
            
        # Tìm nút join_button
        if not find_join_button_with_scroll(device_id):
            return False
        
        # Thực hiện chuỗi buttons
        if not click_button_sequence(WAR_BUTTONS_SEQUENCE, device_id, "war sequence"):
            return False
                
        # Kiểm tra và xử lý trường hợp không đủ thể lực
        return check_and_handle_insufficient_stamina(device_id)
        
    except Exception as e:
        print(f"Lỗi trong quá trình tham gia chiến tranh: {e}")
        return False


def continue_war_sequence(device_id=None):
    """Thực hiện chuỗi hành động từ nút join_button"""
    try:
        # Tìm nút join_button
        if not find_join_button_with_scroll(device_id):
            return False
        
        # Thực hiện chuỗi buttons
        if not click_button_sequence(WAR_BUTTONS_SEQUENCE, device_id, "war sequence"):
            return False
                
        # Kiểm tra và xử lý trường hợp không đủ thể lực
        return check_and_handle_insufficient_stamina(device_id)
        
    except Exception as e:
        print(f"Lỗi trong quá trình tiếp tục tham gia chiến tranh: {e}")
        return False


def join_war_sequence_no_general(device_id=None):
    """Thực hiện chuỗi hành động tham gia chiến tranh (không chọn tướng)"""
    try:
        # Click vào nút chiến tranh
        if not find_and_click_button("war_button", device_id=device_id, wait_time=2):
            # print("Không thể tìm thấy hoặc click vào nút chiến tranh")
            return False
            
        # Tìm nút join_button
        if not find_join_button_with_scroll(device_id):
            return False
        
        # Thực hiện chuỗi buttons (không có chọn tướng)
        if not click_button_sequence(WAR_BUTTONS_SEQUENCE_NO_GENERAL, device_id, "war sequence no general"):
            return False
                
        # Kiểm tra và xử lý trường hợp không đủ thể lực
        return check_and_handle_insufficient_stamina(device_id)
        
    except Exception as e:
        print(f"Lỗi trong quá trình tham gia chiến tranh (không chọn tướng): {e}")
        return False


def continue_war_sequence_no_general(device_id=None):
    """Thực hiện chuỗi hành động từ nút join_button (không chọn tướng)"""
    try:
        # Tìm nút join_button
        if not find_join_button_with_scroll(device_id):
            return False
        
        # Thực hiện chuỗi buttons (không có chọn tướng)
        if not click_button_sequence(WAR_BUTTONS_SEQUENCE_NO_GENERAL, device_id, "war sequence no general"):
            return False
                
        # Kiểm tra và xử lý trường hợp không đủ thể lực
        return check_and_handle_insufficient_stamina(device_id)
        
    except Exception as e:
        print(f"Lỗi trong quá trình tiếp tục tham gia chiến tranh (không chọn tướng): {e}")
        return False