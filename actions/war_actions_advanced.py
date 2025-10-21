"""
Advanced War Actions - Xử lý logic cho Advanced Rally với boss selection
"""
import time
import cv2
import numpy as np
import os
from utils.adb_utils import take_screenshot, tap_screen, swipe_down, swipe_up, get_screen_size

def get_boss_image_path(boss_name, language="en"):
    """Get path to boss image"""
    return f"images/{language}/buttons/rally_advance_boss/{boss_name}.JPG"

def get_button_image_path(button_name, language="en"):
    """Get path to button image"""
    return f"images/{language}/buttons/{button_name}.JPG"

def find_all_boss_positions(selected_bosses, device_id):
    """
    Tìm tất cả vị trí của các boss được chọn trong screenshot hiện tại
    Trả về list các tuple (x, y, width, height, boss_name)
    """
    try:
        import os
        import cv2
        from utils.adb_utils import take_screenshot
        
        print(f"🔍 Tìm tất cả boss trong {len(selected_bosses)} boss được chọn")
        
        # Chụp screenshot
        screenshot_filename = f"current_screen_{device_id.replace(':', '_')}.JPG"
        if not take_screenshot(screenshot_filename, device_id):
            print("❌ Không thể chụp screenshot")
            return []
        
        # Load screenshot
        device_folder = f"images/device_{device_id.replace(':', '_')}"
        screenshot_path = os.path.join(device_folder, screenshot_filename)
        
        if not os.path.exists(screenshot_path):
            print(f"❌ File screenshot không tồn tại: {screenshot_path}")
            return []
        
        screenshot = cv2.imread(screenshot_path)
        if screenshot is None:
            print(f"❌ Không thể đọc screenshot: {screenshot_path}")
            return []
        
        found_bosses = []
        
        # Tìm tất cả boss được chọn trong 1 lần duyệt
        for boss_name in selected_bosses:
            print(f"🔍 Tìm kiếm boss: {boss_name}")
            
            # Lấy đường dẫn ảnh boss
            boss_image_path = get_boss_image_path(boss_name)
            if not os.path.exists(boss_image_path):
                print(f"⚠️ Không tìm thấy ảnh boss: {boss_name}")
                continue
            
            # Load boss template
            boss_template = cv2.imread(boss_image_path)
            if boss_template is None:
                print(f"⚠️ Không thể đọc ảnh boss: {boss_name}")
                continue
            
            # Template matching với threshold thấp để tìm tất cả occurrences
            result = cv2.matchTemplate(screenshot, boss_template, cv2.TM_CCOEFF_NORMED)
            threshold = 0.7  # Threshold cao hơn để tránh lẫn lộn
            
            # Debug: Hiển thị max confidence
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            print(f"🔍 Boss '{boss_name}': Max confidence = {max_val:.3f}, Threshold = {threshold}")
            
            # Tìm tất cả locations
            locations = np.where(result >= threshold)
            locations = list(zip(*locations[::-1]))
            
            # Lọc các locations quá gần nhau (duplicate detection)
            filtered_locations = []
            for loc in locations:
                x, y = loc
                # Kiểm tra xem location này có quá gần với locations đã có không
                too_close = False
                for existing in filtered_locations:
                    if abs(x - existing[0]) < 50 and abs(y - existing[1]) < 50:
                        too_close = True
                        break
                
                if not too_close:
                    h, w = boss_template.shape[:2]
                    # Thêm vào filtered_locations trước
                    filtered_locations.append((x, y, w, h, boss_name))
                    # Thêm boss_name vào tuple
                    found_bosses.append((x, y, w, h, boss_name))
                    print(f"✅ Tìm thấy {boss_name} tại ({x}, {y})")
        
        print(f"📊 Tổng cộng tìm thấy {len(found_bosses)} boss")
        return found_bosses
        
    except Exception as e:
        print(f"❌ Lỗi khi tìm boss: {e}")
        return []


# Hàm chính xử lý boss
def find_all_bosses_and_process(selected_bosses, device_id, use_general=True):
    """
    Tìm tất cả boss và xử lý theo thứ tự
    Lưu tọa độ boss vào mảng với trạng thái attacked
    Xóa mảng boss cũ và tạo mảng mới sau mỗi lần scroll
    """
    try:
        from utils.adb_utils import tap_screen
        import os
        import time
        
        print(f"🔍 Tìm tất cả boss trong {len(selected_bosses)} boss được chọn")
        
        # Xóa mảng boss cũ và tạo mảng mới
        boss_array = []
        print("🗑️ Xóa mảng boss cũ, tạo mảng mới...")
        
        # Tìm tất cả boss được chọn và lưu vào mảng
        boss_positions = find_all_boss_positions(selected_bosses, device_id)
        
        for i, boss_position in enumerate(boss_positions):
            boss_x, boss_y, boss_width, boss_height, boss_name = boss_position
            print(f"✅ Tìm thấy {boss_name} #{i+1} tại ({boss_x}, {boss_y})")
            
            # Lưu vào mảng với trạng thái attacked = 0
            boss_info = {
                'name': boss_name,  # Sử dụng tên boss thực
                'x': boss_x,
                'y': boss_y,
                'width': boss_width,
                'height': boss_height,
                'attacked': 0  # 0 = chưa tấn công, 1 = đã tấn công
            }
            boss_array.append(boss_info)
        
        print(f"📊 Tổng cộng tìm thấy {len(boss_array)} boss")
        
        # Xử lý từng boss trong mảng
        for i, boss_info in enumerate(boss_array):
            print(f"🎯 Xử lý boss {boss_info['name']} #{i+1} tại ({boss_info['x']}, {boss_info['y']})")
            
            # Kiểm tra xem boss đã được join chưa
            if check_boss_joined_status(boss_info['x'], boss_info['y'], boss_info['width'], boss_info['height'], device_id):
                print(f"⏭️ Boss {boss_info['name']} #{i+1} đã được join, đánh dấu đã xử lý")
                boss_info['attacked'] = 1  # Đánh dấu đã xử lý (không cần tấn công nữa)
                continue
            
            # Tìm join button ngay dưới boss
            join_button_pos = find_join_button_below_boss(boss_info['x'], boss_info['y'], boss_info['width'], boss_info['height'], device_id)
            if join_button_pos:
                join_x, join_y = join_button_pos
                print(f"✅ Tìm thấy join button cho boss {boss_info['name']} #{i+1} tại ({join_x}, {join_y})")
                
                # Click vào join button
                print(f"🖱️ Click join button tại ({join_x}, {join_y})")
                if tap_screen(join_x, join_y):
                    print(f"✅ Đã click join button cho boss {boss_info['name']} #{i+1}")
                    boss_info['attacked'] = 1  # Đánh dấu đã tấn công
                    time.sleep(2)  # Chờ animation
                    
                    # Thực hiện war sequence sau khi click join button
                    print("⚔️ Bắt đầu war sequence sau khi click join button...")
                    from actions.war_actions_advanced import join_advanced_war_sequence, join_advanced_war_sequence_no_general

                    # Sử dụng use_general parameter

                    if use_general:
                        if join_advanced_war_sequence(device_id, selected_bosses):
                            print("✅ Đã hoàn thành war sequence với tướng")
                            return True
                        else:
                            print("❌ Không thể hoàn thành war sequence với tướng")
                            return False
                    else:
                        if join_advanced_war_sequence_no_general(device_id, selected_bosses):
                            print("✅ Đã hoàn thành war sequence không tướng")
                            return True
                        else:
                            print("❌ Không thể hoàn thành war sequence không tướng")
                            return False
                else:
                    print(f"❌ Không thể click join button cho boss {boss_info['name']} #{i+1}")
                    # Đánh dấu đã xử lý để không kiểm tra lại boss này
                    boss_info['attacked'] = 1
            else:
                print(f"❌ Không tìm thấy join button cho boss {boss_info['name']} #{i+1}")
                # Đánh dấu đã xử lý để không kiểm tra lại boss này
                boss_info['attacked'] = 1
        
        # Kiểm tra xem còn boss nào chưa tấn công không
        remaining_bosses = [boss for boss in boss_array if boss['attacked'] == 0]
        if remaining_bosses:
            print(f"⚠️ Còn {len(remaining_bosses)} boss chưa thể tấn công")
        else:
            print("✅ Đã xử lý hết tất cả boss có thể tấn công")
        
        # Nếu hết boss hoặc đã attacked hết thì cần scroll và xóa mảng cũ
        if len(boss_array) == 0 or len(remaining_bosses) == 0:
            print("🔄 Hết boss hoặc đã attacked hết, cần scroll và xóa mảng cũ...")
            return "scroll_needed"  # Signal để scroll và tìm boss mới
        
        return False  # Không tìm thấy boss nào có thể tham gia
        
    except Exception as e:
        print(f"❌ Lỗi trong find_all_bosses_and_process: {e}")
        return False

# Tìm button dưới vị trí boss xuất hiện (hỗ trợ join và joined)
def find_button_position_advanced(button_image_path, device_id=None, threshold = 0.75):
    """
    Tìm vị trí button với threshold 85% cho Advanced Rally
    Không ảnh hưởng đến utils chung
    """
    try:
        from utils.image_utils import get_screenshot_filename
        from utils.adb_utils import take_screenshot
        import os
        
        # Đọc ảnh mẫu
        template = cv2.imread(button_image_path)
        if template is None:
            print(f"Không thể đọc ảnh mẫu: {button_image_path}")
            return None
            
        # Chụp màn hình hiện tại
        screenshot_filename = get_screenshot_filename(device_id)
        take_screenshot(screenshot_filename, device_id)
        
        # Xác định đường dẫn đầy đủ của file screenshot
        if device_id:
            screen_path = os.path.join("images", f"device_{device_id.replace(':', '_')}", screenshot_filename)
        else:
            screen_path = os.path.join("images", screenshot_filename)
            
        screen = cv2.imread(screen_path)
        if screen is None:
            print(f"Không thể đọc ảnh màn hình: {screen_path}")
            return None
            
        # Tìm kiếm template trong ảnh màn hình
        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        # Kiểm tra độ chính xác với threshold 85%
        if max_val >= threshold:
            # Tính toán vị trí và kích thước
            x = max_loc[0]
            y = max_loc[1]
            width = template.shape[1]
            height = template.shape[0]
            
            return (x, y, width, height)
        
        return None
        
    except Exception as e:
        print(f"Lỗi trong find_button_position_advanced: {e}")
        return None

# Tham gia tấn công boss có chọn tướng
def join_advanced_war_sequence(device_id=None, selected_bosses=None):
    """
    Thực hiện chuỗi hành động tham gia chiến tranh với boss selection
    Dựa trên join_war_sequence() nhưng thay thế find_join_button_with_scroll() bằng find_and_click_boss_join_button()
    """
    try:
        # Join button đã được click trong rally.py, bỏ qua bước này
        print("✅ Join button đã được click, tiếp tục war sequence...")

        # Thực hiện chuỗi buttons (bỏ qua join_button vì đã click rồi)
        from actions.war_actions import click_button_sequence
        # Sequence bỏ qua join_button vì đã click rồi
        ADVANCED_WAR_BUTTONS_SEQUENCE = [
            ("doi_quan_san_co", 1),   # Nút đổi quân sân cỏ, chờ 1 giây
            ("chon_tuong", 1),        # Nút chọn tướng, chờ 1 giây
            ("chon", 1),              # Nút chọn, chờ 1 giây
            ("hanh_quan", 1)          # Nút hành quân, chờ 1 giây
        ]

        if not click_button_sequence(ADVANCED_WAR_BUTTONS_SEQUENCE, device_id, "advanced war sequence"):
            return False

        # Báo hoàn thành ngay sau khi click hanh_quan
        print("✅ Đã hoàn thành chuỗi hành động tham gia chiến tranh")

        # Kiểm tra và xử lý trường hợp không đủ thể lực (giữ nguyên logic cũ)
        from actions.war_actions import check_and_handle_insufficient_stamina
        stamina_result = check_and_handle_insufficient_stamina(device_id)

        # Nếu không có vấn đề về thể lực, báo hoàn thành
        if stamina_result:
            print("✅ Hoàn thành 1 lượt tham gia chiến tranh thành công")
            return True
        else:
            print("⚠️ Có vấn đề về thể lực nhưng đã xử lý")
            return True

    except Exception as e:
        print(f"❌ Lỗi trong quá trình tham gia advanced war: {e}")
        return False

# Tham gia tấn công boss không chọn tướng
def join_advanced_war_sequence_no_general(device_id=None, selected_bosses=None):
    """
    Thực hiện chuỗi hành động tham gia chiến tranh với boss selection (không chọn tướng)
    """
    try:
        # Join button đã được click trong rally.py, bỏ qua bước này
        print("✅ Join button đã được click, tiếp tục war sequence...")
        
        # Thực hiện chuỗi buttons (không chọn tướng, bỏ qua join_button vì đã click rồi)
        from actions.war_actions import click_button_sequence
        # Sequence bỏ qua join_button vì đã click rồi
        ADVANCED_WAR_BUTTONS_SEQUENCE_NO_GENERAL = [
            ("doi_quan_san_co", 1),   # Nút đổi quân sân cỏ, chờ 1 giây
            ("hanh_quan", 1)          # Nút hành quân, chờ 1 giây
        ]
        
        if not click_button_sequence(ADVANCED_WAR_BUTTONS_SEQUENCE_NO_GENERAL, device_id, "advanced war sequence no general"):
            return False
        
        # Báo hoàn thành ngay sau khi click hanh_quan
        print("✅ Đã hoàn thành chuỗi hành động tham gia chiến tranh (không chọn tướng)")
        
        # Kiểm tra và xử lý trường hợp không đủ thể lực
        from actions.war_actions import check_and_handle_insufficient_stamina
        stamina_result = check_and_handle_insufficient_stamina(device_id)
        
        # Nếu không có vấn đề về thể lực, báo hoàn thành
        if stamina_result:
            print("✅ Hoàn thành 1 lượt tham gia chiến tranh thành công (không chọn tướng)")
            return True
        else:
            print("⚠️ Có vấn đề về thể lực nhưng đã xử lý")
            return True
        
    except Exception as e:
        print(f"❌ Lỗi trong quá trình tham gia advanced war (no general): {e}")
        return False

# Tìm button joined dưới boss, nếu có thì update status attacked = 1
def check_boss_joined_status(boss_x, boss_y, boss_width, boss_height, device_id):
    """
    Kiểm tra xem boss đã được join chưa bằng cách tìm button "joined" ngay dưới boss
    """
    try:
        import os
        import cv2
        from utils.adb_utils import take_screenshot
        # find_button_position_advanced được định nghĩa trong file này
        
        # Chụp screenshot
        screenshot_filename = f"current_screen_{device_id.replace(':', '_')}.JPG"
        if not take_screenshot(screenshot_filename, device_id):
            print("❌ Không thể chụp screenshot")
            return False
        
        # Load screenshot
        device_folder = f"images/device_{device_id.replace(':', '_')}"
        screenshot_path = os.path.join(device_folder, screenshot_filename)
        
        if not os.path.exists(screenshot_path):
            print(f"❌ File screenshot không tồn tại: {screenshot_path}")
            return False
        
        screenshot = cv2.imread(screenshot_path)
        if screenshot is None:
            print(f"❌ Không thể đọc screenshot: {screenshot_path}")
            return False
        
        # Tìm button "joined" trong vùng ngay dưới boss
        search_region = get_search_region_below_boss(boss_x, boss_y, boss_width, boss_height, screenshot)
        if search_region is None:
            return False
        
        # Tìm button "joined" trong vùng tìm kiếm
        joined_button_path = get_button_image_path("joined_button")
        if not os.path.exists(joined_button_path):
            print("⚠️ Không tìm thấy ảnh joined_button")
            return False
        
        # Tìm button "joined" trong vùng tìm kiếm (giống find_join_button_below_boss)
        joined_template = cv2.imread(joined_button_path)
        if joined_template is None:
            print("⚠️ Không thể đọc ảnh joined_button")
            return False
        
        # Template matching trong vùng tìm kiếm
        result = cv2.matchTemplate(search_region, joined_template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= 0.75:
            print(f"✅ Tìm thấy joined button, boss đã được join (độ chính xác: {max_val:.2f})")
            return True
        else:
            print(f"❌ Không tìm thấy joined button, boss chưa được join (độ chính xác cao nhất: {max_val:.2f})")
            return False
        
    except Exception as e:
        print(f"❌ Lỗi trong check_boss_joined_status: {e}")
        return False

# Tìm button join dưới boss
def find_join_button_below_boss(boss_x, boss_y, boss_width, boss_height, device_id):
    """
    Tìm button "join" ngay dưới boss
    Trả về (x, y) nếu tìm thấy, None nếu không tìm thấy
    """
    try:
        import os
        import cv2
        from utils.adb_utils import take_screenshot
        # find_button_position_advanced được định nghĩa trong file này
        
        # Chụp screenshot
        screenshot_filename = f"current_screen_{device_id.replace(':', '_')}.JPG"
        if not take_screenshot(screenshot_filename, device_id):
            print("❌ Không thể chụp screenshot")
            return None
        
        # Load screenshot
        device_folder = f"images/device_{device_id.replace(':', '_')}"
        screenshot_path = os.path.join(device_folder, screenshot_filename)
        
        if not os.path.exists(screenshot_path):
            print(f"❌ File screenshot không tồn tại: {screenshot_path}")
            return None
        
        screenshot = cv2.imread(screenshot_path)
        if screenshot is None:
            print(f"❌ Không thể đọc screenshot: {screenshot_path}")
            return None
        
        # Tìm button "join" trong vùng ngay dưới boss
        search_region = get_search_region_below_boss(boss_x, boss_y, boss_width, boss_height, screenshot)
        if search_region is None:
            return None
        
        # Tìm button "join" trong vùng tìm kiếm
        join_button_path = get_button_image_path("join_button")
        if not os.path.exists(join_button_path):
            print("⚠️ Không tìm thấy ảnh join_button")
            return None
        
        # Tìm button "join" trong vùng tìm kiếm
        join_template = cv2.imread(join_button_path)
        if join_template is None:
            print("⚠️ Không thể đọc ảnh join_button")
            return None
        
        # Template matching trong vùng tìm kiếm
        result = cv2.matchTemplate(search_region, join_template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= 0.75:
            # Tính toán tọa độ thực trên màn hình
            actual_x = boss_x + max_loc[0]
            actual_y = boss_y + boss_height + max_loc[1]
            print(f"✅ Tìm thấy join button tại ({actual_x}, {actual_y}) với độ chính xác {max_val:.2f}")
            return (actual_x, actual_y)
        else:
            print(f"❌ Không tìm thấy join button (độ chính xác cao nhất: {max_val:.2f})")
            return None
        
    except Exception as e:
        print(f"❌ Lỗi trong find_join_button_below_boss: {e}")
        return None

# Khoanh vùng phần tìm kiếm joined và join
def get_search_region_below_boss(boss_x, boss_y, boss_width, boss_height, screenshot):
    """
    Lấy vùng tìm kiếm ngay dưới boss
    """
    try:
        # Tính toán vùng tìm kiếm ngay dưới boss
        search_x = max(0, boss_x - 50)  # Mở rộng 50px về 2 bên
        search_y = boss_y + boss_height  # Bắt đầu từ dưới boss
        search_width = min(boss_width + 100, screenshot.shape[1] - search_x)  # Mở rộng 100px
        search_height = min(200, screenshot.shape[0] - search_y)  # Tìm trong 200px dưới boss
        
        # Kiểm tra vùng tìm kiếm có hợp lệ không
        if search_width <= 0 or search_height <= 0:
            print("❌ Vùng tìm kiếm không hợp lệ")
            return None
        
        # Cắt vùng tìm kiếm từ screenshot
        search_region = screenshot[search_y:search_y + search_height, search_x:search_x + search_width]
        
        if search_region.size == 0:
            print("❌ Vùng tìm kiếm rỗng")
            return None
        
        print(f"🔍 Vùng tìm kiếm: ({search_x}, {search_y}) - ({search_width}x{search_height})")
        return search_region
        
    except Exception as e:
        print(f"❌ Lỗi trong get_search_region_below_boss: {e}")
        return None
