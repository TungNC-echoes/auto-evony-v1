import subprocess
import re
import time

# Biến toàn cục để lưu device đang được sử dụng
current_device = None

def get_memu_devices():
    """Lấy danh sách các thiết bị MEmu đang chạy"""
    try:
        output = subprocess.run("adb devices", shell=True, capture_output=True, text=True).stdout
        memu_devices = []
        for line in output.split('\n')[1:]:  # Bỏ qua dòng đầu tiên
            if line.strip() and "127.0.0.1:" in line:
                device_id = line.split()[0]
                port = device_id.split(':')[1]
                index = int(port) - 21503  # MEmu bắt đầu từ port 21503
                memu_devices.append({
                    'device_id': device_id,
                    'name': f'MEmu_{index}',
                    'index': index
                })
        return sorted(memu_devices, key=lambda x: x['index'])
    except Exception as e:
        print(f"Lỗi khi lấy danh sách MEmu: {e}")
        return []

def select_memu_devices():
    """Hiển thị danh sách MEmu và cho phép người dùng chọn"""
    devices = get_memu_devices()
    if not devices:
        print("Không tìm thấy MEmu nào đang chạy!")
        return []
    
    print("\nDanh sách MEmu đang chạy:")
    for device in devices:
        print(f"{device['index']}. {device['name']} ({device['device_id']})")
    
    choice = input("\nChọn số thứ tự MEmu (Enter để chọn tất cả, các số cách nhau bởi dấu cách, -idx để loại bỏ device): ").strip()
    if not choice:
        return devices
        
    try:
        # Xử lý trường hợp loại bỏ device
        if choice.startswith('-'):
            exclude_index = int(choice[1:])  # Lấy số sau dấu -
            selected_devices = [d for d in devices if d['index'] != exclude_index]
            if len(selected_devices) == len(devices):
                print(f"Không tìm thấy device có index {exclude_index} để loại bỏ!")
            return selected_devices
            
        # Tách các số và chuyển thành list số nguyên
        indices = [int(x.strip()) for x in choice.split()]
        
        # Lọc các thiết bị được chọn
        selected_devices = [d for d in devices if d['index'] in indices]
        
        if not selected_devices:
            print("Không có số thứ tự nào hợp lệ!")
            return []
            
        return selected_devices
        
    except ValueError:
        print("Vui lòng nhập số!")
        return []

def set_device(device_id):
    """Thiết lập thiết bị hiện tại"""
    global current_device
    current_device = device_id

def adb_command(command):
    """Thực hiện lệnh adb và trả về kết quả"""
    try:
        if current_device:
            command = command.replace("adb ", f"adb -s {current_device} ")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        print(f"Lỗi khi thực hiện lệnh ADB: {e}")
        return None


def get_screen_size():
    """Lấy kích thước màn hình thiết bị"""
    try:
        output = adb_command("adb shell wm size")
        match = re.search(r'(\d+)x(\d+)', output)
        if match:
            return int(match.group(1)), int(match.group(2))
        return None
    except Exception as e:
        print(f"Lỗi khi lấy kích thước màn hình: {e}")
        return None


def tap_screen(x, y):
    """Thực hiện tap (chạm) vào màn hình"""
    try:
        adb_command(f"adb shell input tap {x} {y}")
        time.sleep(0.5)
        return True
    except Exception as e:
        print(f"Lỗi khi tap màn hình: {e}")
        return False


def swipe_screen(x1, y1, x2, y2, duration=500):
    """Thực hiện swipe (vuốt) màn hình"""
    try:
        adb_command(f"adb shell input swipe {x1} {y1} {x2} {y2} {duration}")
        time.sleep(1)
        return True
    except Exception as e:
        print(f"Lỗi khi swipe màn hình: {e}")
        return False


def swipe_down():
    """Kéo màn hình xuống để kiểm tra các cuộc chiến tranh"""
    try:
        screen_width, screen_height = get_screen_size()
        if not screen_width or not screen_height:
            return False
            
        # Tính toán vị trí vuốt
        start_x = screen_width // 2
        start_y = screen_height * 0.7  # Bắt đầu từ 70% chiều cao màn hình
        end_x = screen_width // 2
        end_y = screen_height * 0.3    # Kết thúc ở 30% chiều cao màn hình
        
        # Thực hiện vuốt
        if swipe_screen(start_x, start_y, end_x, end_y):
            print("Đã kéo màn hình xuống để kiểm tra các cuộc chiến tranh")
            time.sleep(1)  # Chờ màn hình ổn định
            return True
        return False
    except Exception as e:
        print(f"Lỗi khi kéo màn hình xuống: {e}")
        return False


def swipe_up():
    """Kéo màn hình lên để trở về vị trí ban đầu"""
    try:
        screen_width, screen_height = get_screen_size()
        if not screen_width or not screen_height:
            return False
            
        # Tính toán vị trí vuốt (ngược lại với swipe_down)
        start_x = screen_width // 2
        start_y = screen_height * 0.3  # Bắt đầu từ 30% chiều cao màn hình
        end_x = screen_width // 2
        end_y = screen_height * 0.7    # Kết thúc ở 70% chiều cao màn hình
        
        # Thực hiện vuốt
        if swipe_screen(start_x, start_y, end_x, end_y):
            print("Đã kéo màn hình lên để trở về vị trí ban đầu")
            time.sleep(1)  # Chờ màn hình ổn định
            return True
        return False
    except Exception as e:
        print(f"Lỗi khi kéo màn hình lên: {e}")
        return False


import os

def take_screenshot(filename="screenshot.JPG", device_id=None):
    """Chụp màn hình và lưu vào file"""
    try:
        # Đảm bảo thư mục images tồn tại
        os.makedirs("images", exist_ok=True)
        
        # Tạo tên file với device_id
        if device_id:
            # Tạo thư mục cho device
            device_folder = os.path.join("images", f"device_{device_id.replace(':', '_')}")
            os.makedirs(device_folder, exist_ok=True)
            full_path = os.path.join(device_folder, filename)
        else:
            full_path = os.path.join("images", filename)
            
        # Chụp màn hình và pull về máy tính
        adb_command(f"adb shell screencap -p /sdcard/{filename}")
        adb_command(f"adb pull /sdcard/{filename} {full_path}")
        
        # Xóa file tạm trên thiết bị
        adb_command(f"adb shell rm /sdcard/{filename}")
        
        return True
    except Exception as e:
        print(f"Lỗi khi chụp màn hình: {e}")
        return False

def input_text(text):
    """Nhập text vào trường đang focus"""
    try:
        adb_command(f'adb shell input text "{text}"')
        time.sleep(0.5)
        return True
    except Exception as e:
        print(f"Lỗi khi nhập text: {e}")
        return False


def cancel_action():
    """Hủy thao tác hiện tại bằng cách nhấn ESC và nút cancel"""
    try:
        adb_command('adb shell input keyevent KEYCODE_ESCAPE')
        time.sleep(1)
        from utils.image_utils import find_and_click_button
        if find_and_click_button("cancel"):
            print("Đã nhấn hủy thành công")
        time.sleep(2)
        return True
    except Exception as e:
        print(f"Lỗi khi hủy thao tác: {e}")
        return False


def is_evony_running():
    """Kiểm tra xem game Evony có đang chạy không"""
    try:
        # Chỉ kiểm tra process của Evony bằng ps
        result = adb_command('adb shell ps | grep com.topgamesinc.evony')
        return bool(result and 'com.topgamesinc.evony' in result)
    except Exception as e:
        print(f"Lỗi khi kiểm tra trạng thái Evony: {e}")
        return False

def ensure_evony_running():
    """Đảm bảo game Evony đang chạy, khởi động lại nếu cần"""
    if not is_evony_running():
        print("Không tìm thấy game Evony đang chạy, đang khởi động...")
        adb_command('adb shell monkey -p com.topgamesinc.evony -c android.intent.category.LAUNCHER 1')
        time.sleep(50)  # Đợi game khởi động
    return True