import time
import random
from utils.image_utils import find_and_click_button, check_button_exists
from utils.adb_utils import swipe_down, swipe_up, ensure_evony_running


def handle_insufficient_stamina(device_id=None):
    """Xử lý trường hợp không đủ thể lực"""
    try:
        print("Đang xử lý trường hợp không đủ thể lực...")
        
        # Danh sách các nút cần click theo thứ tự
        buttons = [
            ("xac_nhan", 1),          # Nút xác nhận, chờ 1 giây
            ("dung", 1),              # Nút dừng, chờ 1 giây
            ("dung2", 1),             # Nút dừng 2, chờ 1 giây
            ("back", 1),              # Nút back, chờ 1 giây
            ("hanh_quan", 1)          # Nút hành quân, chờ 1 giây
        ]
        
        # Thực hiện click từng nút theo thứ tự
        for button_name, wait_time in buttons:
            if not find_and_click_button(button_name, device_id=device_id, wait_time=wait_time):
                print(f"Không thể tìm thấy hoặc click vào nút {button_name}")
                return False
                
        return True
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
        
        # Danh sách các nút cần click theo thứ tự
        buttons = [
            ("join_button", 2),       # Nút tham gia, chờ 2 giây
            ("doi_quan_san_co", 1),   # Nút đổi quân sân cỏ, chờ 1 giây
            ("chon_tuong", 1),        # Nút chọn tướng, chờ 1 giây
            ("chon", 1),              # Nút chọn, chờ 1 giây
            ("hanh_quan", 1)          # Nút hành quân, chờ 1 giây
        ]
        
        # Thực hiện click từng nút theo thứ tự
        for button_name, wait_time in buttons:
            if not find_and_click_button(button_name, device_id=device_id, wait_time=wait_time):
                print(f"Không thể tìm thấy hoặc click vào nút {button_name}")
                return False
                
        # Kiểm tra xem có nút xác nhận không (trường hợp không đủ thể lực)
        if check_button_exists("xac_nhan", device_id=device_id):
            print("Phát hiện trường hợp không đủ thể lực")
            if handle_insufficient_stamina(device_id):
                print("Đã xử lý xong trường hợp không đủ thể lực")
            else:
                print("Không thể xử lý trường hợp không đủ thể lực")
                return False
                
        return True
    except Exception as e:
        print(f"Lỗi trong quá trình tham gia chiến tranh: {e}")
        return False


def continue_war_sequence(device_id=None):
    """Thực hiện chuỗi hành động từ nút join_button"""
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
        
        # Danh sách các nút cần click theo thứ tự (bắt đầu từ join_button)
        buttons = [
            ("join_button", 2),       # Nút tham gia, chờ 2 giây
            ("doi_quan_san_co", 1),   # Nút đổi quân sân cỏ, chờ 1 giây
            ("chon_tuong", 1),        # Nút chọn tướng, chờ 1 giây
            ("chon", 1),              # Nút chọn, chờ 1 giây
            ("hanh_quan", 1)          # Nút hành quân, chờ 1 giây
        ]
        
        # Thực hiện click từng nút theo thứ tự
        for button_name, wait_time in buttons:
            if not find_and_click_button(button_name, device_id=device_id, wait_time=wait_time):
                print(f"Không thể tìm thấy hoặc click vào nút {button_name}")
                return False
                
        # Kiểm tra xem có nút xác nhận không (trường hợp không đủ thể lực)
        if check_button_exists("xac_nhan", device_id=device_id):
            # print("Phát hiện trường hợp không đủ thể lực")
            if handle_insufficient_stamina(device_id):
                print("Đã xử lý xong trường hợp không đủ thể lực")
            else:
                print("Không thể xử lý trường hợp không đủ thể lực")
                return False
                
        return True
    except Exception as e:
        print(f"Lỗi trong quá trình tiếp tục tham gia chiến tranh: {e}")
        return False