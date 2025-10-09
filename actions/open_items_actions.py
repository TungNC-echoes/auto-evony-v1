import time
import random
import os
from utils.image_utils import find_and_click_button, check_button_exists
from utils.adb_utils import swipe_down, swipe_up, ensure_evony_running, adb_command
from utils.language_utils import get_image_path


# ===== CONSTANTS =====
# Các nút để mở danh sách items
OPEN_ITEMS_MENU_SEQUENCE = [
    ("open_resource/more", 2),     # Click vào more.JPG, chờ 2 giây
    ("open_resource/things", 1),   # Click vào things.JPG, chờ 1 giây
    ("open_resource/time", 1),     # Click vào time.JPG, chờ 1 giây
    ("open_resource/box", 1)       # Click vào box.JPG, chờ 1 giây
]

# Các nút để mở và sử dụng item
ITEM_ACTION_SEQUENCE = [
    ("open_resource/open", 2),     # Click vào open.JPG, chờ 2 giây
    ("open_resource/use", 2)    # Click vào use.JPG, chờ 1 giây
]

# Thư mục chứa ảnh items
ITEMS_FOLDER = "images/buttons/open_resource/items"


# ===== HELPER FUNCTIONS =====
def click_button_sequence(buttons, device_id=None, sequence_name="buttons"):
    """Thực hiện click chuỗi buttons theo thứ tự"""
    try:
        for button_name, wait_time in buttons:
            if not find_and_click_button(button_name, device_id=device_id, wait_time=wait_time, threshold=0.65):
                print(f"Không thể tìm thấy hoặc click vào nút {button_name}")
                return False
        return True
    except Exception as e:
        print(f"Lỗi trong quá trình click {sequence_name}: {e}")
        return False


def get_all_item_images():
    """Lấy danh sách tất cả ảnh items trong thư mục"""
    try:
        if not os.path.exists(ITEMS_FOLDER):
            print(f"Thư mục {ITEMS_FOLDER} không tồn tại")
            return []
        
        item_images = []
        for filename in os.listdir(ITEMS_FOLDER):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                # Loại bỏ extension để tạo tên button
                name_without_ext = os.path.splitext(filename)[0]
                item_images.append(f"open_resource/items/{name_without_ext}")
        
        print(f"Tìm thấy {len(item_images)} ảnh items: {item_images}")
        return item_images
    except Exception as e:
        print(f"Lỗi khi lấy danh sách ảnh items: {e}")
        return []


def find_all_items_in_screen(item_images, device_id=None, threshold=0.77):
    """Tìm tất cả items có thể trong màn hình hiện tại (parallel detection với multi-location)"""
    try:
        found_items = []
        
        # Chụp screenshot 1 lần duy nhất cho tất cả items
        print("📸 Chụp screenshot 1 lần cho tất cả items...")
        screenshot = get_screenshot_once(device_id)
        if screenshot is None:
            print("❌ Không thể chụp screenshot")
            return []
        
        print(f"🔍 Bắt đầu tìm kiếm {len(item_images)} loại items...")
        
        for item_image in item_images:
            print(f"🔍 Đang tìm item: {item_image}")
            
            # Tìm tất cả vị trí của item này trong screenshot đã chụp
            locations = find_all_locations_in_screenshot(item_image, screenshot, threshold)
            
            for i, location in enumerate(locations):
                # Tạo unique identifier cho mỗi vị trí
                item_with_location = f"{item_image}_pos_{i+1}"
                found_items.append({
                    'name': item_image,
                    'location': location,
                    'unique_id': item_with_location
                })
                print(f"✅ Tìm thấy item: {item_image} tại vị trí {i+1} - {location}")
        
        print(f"📋 Tổng cộng tìm thấy {len(found_items)} items trong màn hình")
        
        # Debug: In ra chi tiết từng item
        for i, item in enumerate(found_items):
            print(f"   Item {i+1}: {item['name']} tại vị trí {item['location']} (ID: {item['unique_id']})")
        
        return found_items
    except Exception as e:
        print(f"❌ Lỗi khi tìm items trong màn hình: {e}")
        return []


def get_screenshot_once(device_id=None):
    """Chụp screenshot 1 lần duy nhất và trả về ảnh"""
    try:
        import cv2
        from utils.adb_utils import take_screenshot
        from utils.image_utils import get_screenshot_filename
        
        # Chụp screenshot
        screenshot_filename = get_screenshot_filename(device_id)
        take_screenshot(screenshot_filename, device_id)
        
        # Xác định đường dẫn đầy đủ của file screenshot
        if device_id:
            screen_path = os.path.join("images", f"device_{device_id.replace(':', '_')}", screenshot_filename)
        else:
            screen_path = os.path.join("images", screenshot_filename)
        
        # Load screenshot
        screenshot = cv2.imread(screen_path)
        if screenshot is None:
            print(f"❌ Không thể đọc screenshot: {screen_path}")
            return None
        
        print(f"✅ Đã chụp screenshot thành công: {screen_path}")
        return screenshot
    except Exception as e:
        print(f"❌ Lỗi khi chụp screenshot: {e}")
        return None


def find_all_locations_in_screenshot(item_image, screenshot, threshold=0.8):
    """Tìm tất cả vị trí của một loại item trong screenshot đã có"""
    try:
        import cv2
        import numpy as np
        
        # Load template image using language-aware path
        template_path = get_image_path(f"buttons/{item_image}")
        # Try different extensions
        if not os.path.exists(f"{template_path}.JPG"):
            if not os.path.exists(f"{template_path}.jpg"):
                print(f"❌ Không tìm thấy template: {template_path}")
                return []
            else:
                template_path = f"{template_path}.jpg"
        else:
            template_path = f"{template_path}.JPG"
        
        template = cv2.imread(template_path)
        if template is None:
            print(f"❌ Không thể load template: {template_path}")
            return []
        
        # Template matching
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        locations = np.where(result >= threshold)
        
        print(f"📊 Tìm thấy {len(locations[0])} vị trí khả năng cho {item_image}")
        
        # Debug: In ra tất cả vị trí trước khi lọc
        if len(locations[0]) > 0:
            print(f"🔍 Tất cả vị trí trước khi lọc:")
            for i, pt in enumerate(zip(*locations[::-1])):
                x, y = pt
                confidence = result[y, x]
                print(f"   Vị trí {i+1}: ({x}, {y}) - confidence: {confidence:.3f}")
        
        # Lọc các vị trí gần nhau (tránh duplicate)
        filtered_locations = []
        min_distance = 10  # Giảm khoảng cách để không bỏ sót items gần nhau
        
        # Sắp xếp theo độ chính xác (từ cao xuống thấp)
        all_locations = []
        for pt in zip(*locations[::-1]):
            x, y = pt
            confidence = result[y, x]  # Lấy độ chính xác tại vị trí này
            all_locations.append((x, y, confidence))
        
        # Sắp xếp theo confidence giảm dần
        all_locations.sort(key=lambda x: x[2], reverse=True)
        
        for x, y, confidence in all_locations:
            # Kiểm tra xem vị trí này có quá gần với các vị trí đã có không
            too_close = False
            for existing_pt in filtered_locations:
                if abs(x - existing_pt[0]) < min_distance and abs(y - existing_pt[1]) < min_distance:
                    too_close = True
                    print(f"⚠️ Bỏ qua vị trí ({x}, {y}) vì quá gần với ({existing_pt[0]}, {existing_pt[1]})")
                    break
            
            if not too_close:
                filtered_locations.append((x, y))
                print(f"✅ Thêm vị trí: ({x}, {y}) với confidence: {confidence:.3f}")
        
        print(f"✅ Lọc được {len(filtered_locations)} vị trí cuối cùng cho {item_image}")
        return filtered_locations
    except Exception as e:
        print(f"❌ Lỗi khi tìm vị trí của item {item_image}: {e}")
        return []




def process_found_items(found_items, device_id=None):
    """Xử lý tuần tự các items đã tìm thấy (với multi-location support)"""
    try:
        items_processed = 0
        total_items = len(found_items)
        
        print(f"📋 Bắt đầu xử lý {total_items} items...")
        
        for i, item_data in enumerate(found_items):
            item_name = item_data['name']
            item_location = item_data['location']
            unique_id = item_data['unique_id']
            
            print(f"🔄 [{i+1}/{total_items}] Đang xử lý item: {item_name} tại vị trí {item_location} (ID: {unique_id})")
            
            # Click vào item tại vị trí cụ thể
            if click_item_at_location(item_name, item_location, device_id):
                print(f"✅ Đã click vào item: {item_name} tại vị trí {item_location}")
                
                # Click open và use
                if click_button_sequence(ITEM_ACTION_SEQUENCE, device_id, "item action"):
                    print(f"✅ Đã mở và sử dụng item: {item_name} tại vị trí {item_location}")
                    items_processed += 1
                    
                    # Chờ tài nguyên load
                    print("⏳ Chờ tài nguyên load...")
                    time.sleep(2)
                    
                    # Nhấn ESC để đóng dialog
                    press_escape()
                    time.sleep(0.5)
                else:
                    print(f"❌ Không thể mở/sử dụng item: {item_name} tại vị trí {item_location}")
            else:
                print(f"❌ Không thể click vào item: {item_name} tại vị trí {item_location}")
        
        print(f"📊 Hoàn thành xử lý: {items_processed}/{total_items} items thành công")
        return items_processed
    except Exception as e:
        print(f"❌ Lỗi khi xử lý items: {e}")
        return 0


def click_item_at_location(item_name, location, device_id=None):
    """Click vào item tại vị trí cụ thể"""
    try:
        x, y = location
        # Click trực tiếp tại tọa độ
        adb_command(f'adb shell input tap {x} {y}')
        time.sleep(0.3)
        return True
    except Exception as e:
        print(f"❌ Lỗi khi click tại vị trí {location}: {e}")
        return False


def scroll_down_small():
    """Kéo màn hình xuống 150px (tối ưu cho parallel detection)"""
    try:
        adb_command('adb shell input swipe 300 300 300 150 100')
        time.sleep(1)
        return True
    except Exception as e:
        print(f"Lỗi khi kéo màn hình xuống: {e}")
        return False


def press_escape():
    """Nhấn phím ESC"""
    try:
        adb_command('adb shell input keyevent KEYCODE_ESCAPE')
        time.sleep(0.5)
        return True
    except Exception as e:
        print(f"Lỗi khi nhấn ESC: {e}")
        return False


def ensure_outside_screen():
    """Đảm bảo đang ở ngoài cùng màn hình bằng cách ESC cho đến khi thấy cancel button"""
    try:
        attempt = 0
        while True:
            attempt += 1
            if check_button_exists("cancel", device_id=None, threshold=0.7):
                print("✅ Đã ở ngoài cùng màn hình (thấy cancel button)")
                # Click vào cancel để đảm bảo ở ngoài cùng
                if find_and_click_button("cancel", device_id=None, wait_time=1, threshold=0.8):
                    print("✅ Đã click cancel, hoàn thành quá trình về ngoài cùng")
                    return True
                else:
                    print("⚠️ Không thể click cancel, tiếp tục ESC...")
            
            print(f"🔄 Lần {attempt}: Nhấn ESC để về ngoài cùng màn hình...")
            press_escape()
            time.sleep(1)
        
    except Exception as e:
        print(f"❌ Lỗi khi đảm bảo ở ngoài cùng màn hình: {e}")
        return False


def check_in_chest_screen():
    """Kiểm tra xem có đang trong màn hình mở item không"""
    try:
        return check_button_exists("open_resource/in_chest", device_id=None, threshold=0.8)
    except Exception as e:
        print(f"❌ Lỗi khi kiểm tra màn hình in_chest: {e}")
        return False


# ===== MAIN FUNCTIONS =====
def open_items_sequence(device_id=None):
    """Thực hiện chuỗi hành động mở items theo quy trình mới"""
    try:
        print("🔄 Bắt đầu quy trình mở items...")
        
        # Bước 0: Đảm bảo ở ngoài màn hình chính trước khi bắt đầu
        print("📋 Bước 0: Đảm bảo ở ngoài màn hình chính...")
        if not ensure_outside_screen():
            print("❌ Không thể về ngoài màn hình chính")
            return False
        
        # Bước 1: Mở menu items (more -> things -> time -> box)
        print("📋 Bước 1: Mở menu items...")
        if not click_button_sequence(OPEN_ITEMS_MENU_SEQUENCE, device_id, "open items menu"):
            print("❌ Không thể mở menu items")
            return False
        
        # Bước 2: Lấy danh sách tất cả ảnh items
        print("📋 Bước 2: Lấy danh sách ảnh items...")
        item_images = get_all_item_images()
        if not item_images:
            print("❌ Không tìm thấy ảnh items nào")
            return False
        
        # Bước 3: Duyệt và mở tất cả items (Parallel Detection với logic cũ)
        print("📋 Bước 3: Duyệt và mở items với parallel detection...")
        items_processed = 0
        consecutive_empty_scrolls = 0  # Đếm số lần scroll liên tiếp không tìm thấy item
        scroll_count = 0  # Đếm tổng số lần scroll
        
        while True:  # Vòng lặp vô hạn cho đến khi dừng theo điều kiện
            print(f"🔍 Lần scroll {scroll_count + 1}: Quét màn hình để tìm items...")
            
            # Quét 1 lượt tìm tất cả items trong màn hình hiện tại
            found_items = find_all_items_in_screen(item_images, device_id, threshold=0.8)
            
            if found_items:
                print(f"📋 Tìm thấy {len(found_items)} items, bắt đầu xử lý...")
                
                # Xử lý tuần tự các items đã tìm thấy
                items_processed_in_scroll = process_found_items(found_items, device_id)
                items_processed += items_processed_in_scroll
                
                # Reset counter vì tìm thấy items
                consecutive_empty_scrolls = 0
                print(f"✅ Đã xử lý {items_processed_in_scroll} items trong lần scroll {scroll_count + 1}")
            else:
                consecutive_empty_scrolls += 1
                print(f"📋 Không tìm thấy item nào trong lần scroll {scroll_count + 1} (lần liên tiếp: {consecutive_empty_scrolls})")
            
            # Tăng số lần scroll
            scroll_count += 1
            
            # Kiểm tra điều kiện dừng: 3 lần scroll liên tiếp không tìm thấy item
            if consecutive_empty_scrolls >= 3:
                print("📋 Đã kéo xuống 3 lần liên tiếp mà không tìm thấy item nào")
                print("📋 Đang ra ngoài màn hình chính...")
                if ensure_outside_screen():
                    print("✅ Đã về ngoài màn hình chính, kết thúc quy trình")
                else:
                    print("⚠️ Không thể về ngoài màn hình chính, nhưng vẫn kết thúc quy trình")
                break
            
            # Scroll tiếp nếu chưa đạt điều kiện dừng
            # Kiểm tra xem có đang trong màn hình mở item không
            if check_in_chest_screen():
                print("📋 Đang trong màn hình mở item, kéo màn hình xuống...")
                scroll_down_small()
                print("⏳ Chờ màn hình ổn định sau khi scroll...")
                time.sleep(2)  # Chờ 2 giây để màn hình ổn định
            else:
                print("📋 Không trong màn hình mở item, cần vào lại menu items...")
                # Nhấn ESC để đóng menu hiện tại
                press_escape()
                time.sleep(1)
                
                # Vào lại menu items
                if click_button_sequence(OPEN_ITEMS_MENU_SEQUENCE, device_id, "reopen items menu"):
                    print("✅ Đã vào lại menu items")
                    print("⏳ Chờ màn hình ổn định sau khi vào menu...")
                    time.sleep(2)  # Chờ 2 giây để màn hình ổn định
                else:
                    print("❌ Không thể vào lại menu items")
                    break
        
        print(f"✅ Hoàn thành quy trình mở items. Tổng cộng đã xử lý: {items_processed} items")
        return True
        
    except Exception as e:
        print(f"❌ Lỗi trong quá trình mở items: {e}")
        return False


def continue_open_items_sequence(device_id=None):
    """Thực hiện chuỗi hành động mở items (tương tự open_items_sequence)"""
    return open_items_sequence(device_id)


def open_items_selective_sequence(device_id=None):
    """Thực hiện chuỗi hành động mở items có chọn lọc (tương tự open_items_sequence)"""
    return open_items_sequence(device_id)


def continue_open_items_selective_sequence(device_id=None):
    """Thực hiện chuỗi hành động mở items có chọn lọc (tương tự open_items_sequence)"""
    return open_items_sequence(device_id)
