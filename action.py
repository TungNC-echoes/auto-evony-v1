import time
import subprocess
import random
import re
from PIL import Image
import numpy as np
import cv2
import os


# Hàm để thực hiện lệnh adb
def adb_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        print(f"Lỗi khi thực hiện lệnh ADB: {e}")
        return None


# Hàm để lấy kích thước màn hình thiết bị    
def get_screen_size():
    try:
        output = adb_command("adb shell wm size")
        match = re.search(r'(\d+)x(\d+)', output)
        if match:
            return int(match.group(1)), int(match.group(2))
        return None
    except Exception as e:
        print(f"Lỗi khi lấy kích thước màn hình: {e}")
        return None


# Hàm thực hiện tap (chạm) vào màn hình
def tap_screen(x, y):
    try:
        adb_command(f"adb shell input tap {x} {y}")
        time.sleep(0.5)
        return True
    except Exception as e:
        print(f"Lỗi khi tap màn hình: {e}")
        return False


# Hàm thực hiện swipe (vuốt) màn hình
def swipe_screen(x1, y1, x2, y2, duration=500):
    try:
        adb_command(f"adb shell input swipe {x1} {y1} {x2} {y2} {duration}")
        time.sleep(1)
        return True
    except Exception as e:
        print(f"Lỗi khi swipe màn hình: {e}")
        return False


# Hàm chụp màn hình và lưu vào file
def take_screenshot(filename="screenshot.JPG"):
    try:
        adb_command(f"adb shell screencap -p /sdcard/{filename}")
        adb_command(f"adb pull /sdcard/{filename} ./images/{filename}")
        return True
    except Exception as e:
        print(f"Lỗi khi chụp màn hình: {e}")
        return False


# Hàm kiểm tra màu sắc tại một điểm trên màn hình
def check_color(x, y, expected_color):
    try:
        # Chụp màn hình
        take_screenshot("temp.JPG")
        # Sử dụng thư viện PIL để kiểm tra màu sắc
        img = Image.open(f"./images/temp.JPG")
        pixel = img.getpixel((x, y))
        return pixel == expected_color
    except Exception as e:
        print(f"Lỗi khi kiểm tra màu sắc: {e}")
        return False


# Hàm chọn quân
def select_troops(troop_type, quantity):
    try:
        print(f"Đang chọn {quantity} {troop_type}...")
        # Lấy kích thước màn hình
        screen_width, screen_height = get_screen_size()
        if not screen_width or not screen_height:
            return False

        # Tap vào nút chọn quân (tùy chỉnh tọa độ theo vị trí thực tế)
        troop_button_x = screen_width * 0.3  # Thay đổi theo vị trí thực tế
        troop_button_y = screen_height * 0.4  # Thay đổi theo vị trí thực tế
        tap_screen(troop_button_x, troop_button_y)
        time.sleep(1)

        # Tap vào ô nhập số lượng
        quantity_input_x = screen_width * 0.5
        quantity_input_y = screen_height * 0.5
        tap_screen(quantity_input_x, quantity_input_y)
        time.sleep(0.5)

        # Nhập số lượng quân
        adb_command(f"adb shell input text {quantity}")
        time.sleep(0.5)

        # Tap vào nút xác nhận
        confirm_button_x = screen_width * 0.7
        confirm_button_y = screen_height * 0.6
        tap_screen(confirm_button_x, confirm_button_y)
        return True
    except Exception as e:
        print(f"Lỗi khi chọn quân: {e}")
        return False


# Hàm gửi quân đi đánh
def send_troops(target_coordinates):
    try:
        print(f"Đang gửi quân đến tọa độ {target_coordinates}...")
        screen_width, screen_height = get_screen_size()
        if not screen_width or not screen_height:
            return False

        # Tap vào nút gửi quân
        send_button_x = screen_width * 0.8
        send_button_y = screen_height * 0.8
        tap_screen(send_button_x, send_button_y)
        time.sleep(1)

        # Tap vào ô nhập tọa độ
        coordinate_input_x = screen_width * 0.5
        coordinate_input_y = screen_height * 0.5
        tap_screen(coordinate_input_x, coordinate_input_y)
        time.sleep(0.5)

        # Nhập tọa độ
        adb_command(f"adb shell input text {target_coordinates}")
        time.sleep(0.5)

        # Tap vào nút xác nhận gửi quân
        confirm_send_x = screen_width * 0.7
        confirm_send_y = screen_height * 0.6
        tap_screen(confirm_send_x, confirm_send_y)
        return True
    except Exception as e:
        print(f"Lỗi khi gửi quân: {e}")
        return False


# Hàm kiểm tra trạng thái chiến đấu
def check_battle_status():
    try:
        # Chụp màn hình hiện tại
        take_screenshot("battle_status.JPG")
        
        # Kiểm tra các vị trí đặc trưng cho từng trạng thái
        screen_width, screen_height = get_screen_size()
        if not screen_width or not screen_height:
            return "error"

        # Kiểm tra màu sắc tại các vị trí đặc trưng
        victory_color = (255, 255, 0)  # Màu vàng cho chiến thắng
        defeat_color = (255, 0, 0)     # Màu đỏ cho thất bại
        in_progress_color = (0, 255, 0) # Màu xanh cho đang chiến đấu

        # Kiểm tra các vị trí
        if check_color(screen_width * 0.5, screen_height * 0.3, victory_color):
            print("Chiến thắng!")
            return "won"
        elif check_color(screen_width * 0.5, screen_height * 0.3, defeat_color):
            print("Thất bại!")
            return "lost"
        elif check_color(screen_width * 0.5, screen_height * 0.3, in_progress_color):
            print("Đang chiến đấu...")
            return "in_progress"
        return "unknown"
    except Exception as e:
        print(f"Lỗi khi kiểm tra trạng thái chiến đấu: {e}")
        return "error"


# Hàm kéo bản đồ
def scroll_map():
    try:
        screen_width, screen_height = get_screen_size()
        if not screen_width or not screen_height:
            return False

        # Thực hiện swipe từ dưới lên trên
        start_x = screen_width * 0.5
        start_y = screen_height * 0.8
        end_x = screen_width * 0.5
        end_y = screen_height * 0.2
        swipe_screen(start_x, start_y, end_x, end_y)
        return True
    except Exception as e:
        print(f"Lỗi khi kéo bản đồ: {e}")
        return False


# Hàm so sánh hai ảnh để phát hiện sự thay đổi
def compare_images(img1_path, img2_path, threshold=30):
    try:
        img1 = Image.open(img1_path).convert('RGB')
        img2 = Image.open(img2_path).convert('RGB')
        
        # Chuyển đổi sang numpy array
        arr1 = np.array(img1)
        arr2 = np.array(img2)
        
        # Tính toán sự khác biệt
        diff = np.abs(arr1 - arr2)
        mean_diff = np.mean(diff)
        
        return mean_diff < threshold
    except Exception as e:
        print(f"Lỗi khi so sánh ảnh: {e}")
        return False


# Hàm tìm vị trí của nút trên màn hình
def find_button_on_screen(button_image_path, threshold=0.8):
    try:
        # Đọc ảnh mẫu và ảnh màn hình
        template = cv2.imread(button_image_path)
        if template is None:
            print(f"Không thể đọc ảnh mẫu: {button_image_path}")
            return None
            
        # Chụp màn hình hiện tại
        take_screenshot("current_screen.JPG")
        screen = cv2.imread("./images/current_screen.JPG")
        if screen is None:
            print("Không thể đọc ảnh màn hình")
            return None
            
        # Tìm kiếm template trong ảnh màn hình
        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        # Kiểm tra độ chính xác
        if max_val >= threshold:
            # Tính toán tọa độ trung tâm của nút
            h, w = template.shape[:2]
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2
            return (center_x, center_y)
        else:
            print(f"Không tìm thấy nút với độ chính xác đủ cao: {max_val}")
            return None
    except Exception as e:
        print(f"Lỗi khi tìm nút trên màn hình: {e}")
        return None


# Hàm kiểm tra xem hoạt cảnh đã kết thúc chưa
def wait_for_animation_end(timeout=10):
    try:
        print("Đang chờ hoạt cảnh kết thúc...")
        # Chụp ảnh đầu tiên
        take_screenshot("before.JPG")
        time.sleep(1)
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            # Chụp ảnh mới
            take_screenshot("after.JPG")
            
            # So sánh hai ảnh
            if compare_images("./images/before.JPG", "./images/after.JPG"):
                print("Hoạt cảnh đã kết thúc")
                return True
                
            # Cập nhật ảnh trước đó
            take_screenshot("before.JPG")
            time.sleep(0.5)
            
        print("Hết thời gian chờ hoạt cảnh")
        return False
    except Exception as e:
        print(f"Lỗi khi chờ hoạt cảnh: {e}")
        return False


# Hàm tìm và click vào nút
def find_and_click_button(button_name, wait_time=1):
    try:
        print(f"Đang tìm nút {button_name}...")
        # Tìm nút trong thư mục buttons
        button_path = f"./images/buttons/{button_name}.JPG"
        if not os.path.exists(button_path):
            print(f"Không tìm thấy ảnh nút {button_name}")
            return False
            
        # Tìm vị trí nút trên màn hình
        button_pos = find_button_on_screen(button_path)
        if button_pos:
            # Tap vào nút
            if tap_screen(button_pos[0], button_pos[1]):
                print(f"Đã tìm thấy và tap vào nút {button_name}")
                time.sleep(wait_time)  # Chờ sau khi click
                return True
                
        return False
    except Exception as e:
        print(f"Lỗi khi tìm nút {button_name}: {e}")
        return False


# Hàm kiểm tra xem nút có tồn tại trên màn hình không
def check_button_exists(button_name, threshold=0.8):
    try:
        button_path = f"./images/buttons/{button_name}.JPG"
        if not os.path.exists(button_path):
            print(f"Không tìm thấy ảnh nút {button_name}")
            return False
            
        button_pos = find_button_on_screen(button_path, threshold)
        return button_pos is not None
    except Exception as e:
        print(f"Lỗi khi kiểm tra nút {button_name}: {e}")
        return False


# Hàm xử lý trường hợp không đủ thể lực
def handle_insufficient_stamina():
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
            if not find_and_click_button(button_name, wait_time):
                print(f"Không thể tìm thấy hoặc click vào nút {button_name}")
                return False
                
        return True
    except Exception as e:
        print(f"Lỗi trong quá trình xử lý không đủ thể lực: {e}")
        return False


# Hàm thực hiện chuỗi hành động tham gia chiến tranh
def join_war_sequence():
    try:
        # Danh sách các nút cần click theo thứ tự
        buttons = [
            ("war_button", 2),        # Nút chiến tranh, chờ 2 giây
            ("join_button", 2),       # Nút tham gia, chờ 2 giây
            ("doi_quan_san_co", 1),   # Nút đổi quân sân cỏ, chờ 1 giây
            ("chon_tuong", 1),        # Nút chọn tướng, chờ 1 giây
            ("chon", 1),              # Nút chọn, chờ 1 giây
            ("hanh_quan", 1)          # Nút hành quân, chờ 1 giây
        ]
        
        # Thực hiện click từng nút theo thứ tự
        for button_name, wait_time in buttons:
            if not find_and_click_button(button_name, wait_time):
                print(f"Không thể tìm thấy hoặc click vào nút {button_name}")
                return False
                
        # Kiểm tra xem có nút xác nhận không (trường hợp không đủ thể lực)
        if check_button_exists("xac_nhan"):
            print("Phát hiện trường hợp không đủ thể lực")
            if handle_insufficient_stamina():
                print("Đã xử lý xong trường hợp không đủ thể lực")
            else:
                print("Không thể xử lý trường hợp không đủ thể lực")
                return False
                
        return True
    except Exception as e:
        print(f"Lỗi trong quá trình tham gia chiến tranh: {e}")
        return False


# Hàm thực hiện chuỗi hành động từ nút join_button
def continue_war_sequence():
    try:
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
            if not find_and_click_button(button_name, wait_time):
                print(f"Không thể tìm thấy hoặc click vào nút {button_name}")
                return False
                
        # Kiểm tra xem có nút xác nhận không (trường hợp không đủ thể lực)
        if check_button_exists("xac_nhan"):
            print("Phát hiện trường hợp không đủ thể lực")
            if handle_insufficient_stamina():
                print("Đã xử lý xong trường hợp không đủ thể lực")
            else:
                print("Không thể xử lý trường hợp không đủ thể lực")
                return False
                
        return True
    except Exception as e:
        print(f"Lỗi trong quá trình tiếp tục tham gia chiến tranh: {e}")
        return False


# Hàm chạy bot tự động
def auto_join_rally():
    while True:
        print("Bắt đầu chuỗi hành động tham gia chiến tranh...")
        
        # Thực hiện chuỗi hành động tham gia chiến tranh
        if join_war_sequence():
            print("Đã hoàn thành chuỗi hành động tham gia chiến tranh")
            
            # Chờ một khoảng thời gian ngẫu nhiên (3-5 giây)
            wait_time = random.uniform(3, 5)
            print(f"Chờ {wait_time:.2f} giây để kiểm tra nút tham gia...")
            time.sleep(wait_time)
            
            # Kiểm tra xem có nút join_button không
            if check_button_exists("join_button"):
                print("Phát hiện nút tham gia mới, tiếp tục chuỗi hành động...")
                if continue_war_sequence():
                    print("Đã hoàn thành chuỗi hành động tiếp theo")
                else:
                    print("Không thể hoàn thành chuỗi hành động tiếp theo")
        else:
            print("Không thể hoàn thành chuỗi hành động tham gia chiến tranh")
            
        # Chờ một khoảng thời gian trước khi thử lại
        wait_time = random.uniform(30, 60)
        print(f"Chờ {wait_time:.2f} giây trước khi thử lại...")
        time.sleep(wait_time)


if __name__ == "__main__":
    # Bắt đầu chạy bot tự động
    auto_join_rally()
