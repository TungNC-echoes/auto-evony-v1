import os
import subprocess
import time
import xml.etree.ElementTree as ET
from datetime import datetime
import json
import re

# Thêm thư mục gốc vào PYTHONPATH để có thể import từ utils
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.adb_utils import set_device, adb_command, tap_screen, input_text

# --- Thêm thông tin đăng nhập ---
EMAIL = "bkaprodx@gmail.com"
PASSWORD = "tung1995"

# --- Hàm trợ giúp mới ---
def _get_node_center(node):
    """
    Phân tích thuộc tính 'bounds' của một node để lấy tọa độ tâm.
    Ví dụ bounds: '[50,150][400,250]'
    """
    bounds_str = node.attrib.get('bounds')
    if not bounds_str:
        return None
    
    try:
        # Tách chuỗi thành các số
        coords = re.findall(r'\d+', bounds_str)
        if len(coords) != 4:
            return None
        
        x1, y1, x2, y2 = map(int, coords)
        
        # Tính tọa độ tâm
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        return (center_x, center_y)
    except Exception as e:
        print(f"Lỗi khi phân tích bounds '{bounds_str}': {e}")
        return None

def find_and_click_element(device_id, text=None, resource_id=None, a_class=None):
    """
    Tìm một phần tử trên màn hình và nhấn vào nó.
    Cải tiến: Tìm kiếm không phân biệt chữ hoa/thường, tìm trong cả 'text' và 'content-desc'.
    Thêm chế độ chẩn đoán: Nếu không tìm thấy, in ra tất cả các văn bản đã thấy.
    """
    xml_file = dump_ui_xml(device_id)
    if not xml_file:
        return False

    tree = ET.parse(xml_file)
    root = tree.getroot()
    found_element = False
    
    # Danh sách để lưu lại những gì thấy được để chẩn đoán
    diagnostic_texts = set()

    for node in root.iter('node'):
        node_text = node.attrib.get('text', '')
        node_desc = node.attrib.get('content-desc', '')
        
        # Thêm vào danh sách chẩn đoán nếu có nội dung
        if node_text:
            diagnostic_texts.add(f"text: '{node_text}'")
        if node_desc:
            diagnostic_texts.add(f"content-desc: '{node_desc}'")

        # Cải tiến logic tìm kiếm
        match_by_text = False
        if text:
            search_text = text.lower()
            # Tìm kiếm không phân biệt chữ hoa/thường và kiểm tra sự tồn tại (substring)
            if search_text in node_text.lower() or search_text in node_desc.lower():
                match_by_text = True

        match_by_id = resource_id and node.attrib.get('resource-id', '') == resource_id
        match_by_class = a_class and node.attrib.get('class', '') == a_class

        if match_by_text or match_by_id or match_by_class:
            coords = _get_node_center(node)
            if coords:
                print(f"[{device_id}] Tìm thấy phần tử '{text or resource_id or a_class}' tại tọa độ {coords}. Đang nhấn...")
                tap_screen(coords[0], coords[1])
                found_element = True
                break
    
    os.remove(xml_file) 
    
    if not found_element:
        print(f"[{device_id}] LỖI: Không tìm thấy phần tử nào với tiêu chí: text='{text}', id='{resource_id}', class='{a_class}'")
        print(f"[{device_id}] --- BẮT ĐẦU DỮ LIỆU CHẨN ĐOÁN ---")
        print(f"[{device_id}] Các văn bản tìm thấy trên màn hình:")
        for diag_text in sorted(list(diagnostic_texts)):
            print(f"[{device_id}]   - {diag_text}")
        print(f"[{device_id}] --- KẾT THÚC DỮ LIỆU CHẨN ĐOÁN ---")
        
    return found_element

# --- Các hàm ADB chuyên dụng cho việc lấy dữ liệu từ Chrome ---

def open_chrome_with_url(device_id, url):
    """
    Mở trình duyệt Chrome trên thiết bị và điều hướng đến URL được chỉ định.
    """
    print(f"[{device_id}] Đang mở Chrome với URL: {url}")
    set_device(device_id)
    # Lệnh 'am start' sẽ mở activity của Chrome. 
    # '-a android.intent.action.VIEW' chỉ định hành động là xem một nội dung.
    # '-d {url}' cung cấp dữ liệu (URL) cho hành động đó.
    result = adb_command(f"adb shell am start -a android.intent.action.VIEW -d {url}")
    if "Error" in str(result):
        print(f"[{device_id}] Lỗi khi mở Chrome: {result}")
        return False
    print(f"[{device_id}] Đã gửi lệnh mở Chrome thành công.")
    time.sleep(10) # Chờ 10 giây để trang web có thời gian tải
    return True

def dump_ui_xml(device_id, local_path="."):
    """
    Chụp cấu trúc UI hiện tại của màn hình và lưu vào một file XML.
    Kéo file XML đó về máy tính.
    """
    print(f"[{device_id}] Đang chụp cấu trúc UI (dumping UI)...")
    set_device(device_id)
    
    # Tên file XML trên thiết bị và trên máy tính
    device_xml_path = "/sdcard/window_dump.xml"
    local_xml_file = os.path.join(local_path, f"window_dump_{device_id.replace(':', '_')}.xml")

    # Chạy uiautomator dump
    adb_command(f"adb shell uiautomator dump {device_xml_path}")
    
    # Thêm độ trễ 2 giây để đảm bảo file được tạo xong trên thiết bị
    print(f"[{device_id}] Chờ 2 giây để thiết bị tạo file dump...")
    time.sleep(2)

    # Kéo file về máy tính
    adb_command(f"adb pull {device_xml_path} {local_xml_file}")

    # Xóa file trên thiết bị để dọn dẹp
    adb_command(f"adb shell rm {device_xml_path}")

    if os.path.exists(local_xml_file):
        print(f"[{device_id}] Đã lưu cấu trúc UI vào file: {local_xml_file}")
        return local_xml_file
    else:
        print(f"[{device_id}] Lỗi: Không thể kéo file UI dump về máy tính.")
        return None

def perform_login_on_device(device_id):
    """
    Thực hiện quy trình đăng nhập tự động trên thiết bị.
    """
    print(f"[{device_id}] Bắt đầu quy trình đăng nhập tự động...")
    set_device(device_id)

    # 1. Mở trang đăng nhập
    login_url = "https://www.iscout.club/vi/login"
    if not open_chrome_with_url(device_id, login_url):
        return False
    
    print(f"[{device_id}] Đã ở trang đăng nhập. Chờ 5 giây để ổn định.")
    time.sleep(20)

    # 2. Tìm ô email (dựa vào class) và nhập email
    # Giả định ô nhập liệu là 'android.widget.EditText'
    print(f"[{device_id}] Tìm ô Email và nhập...")
    # Chúng ta sẽ tìm ô EditText đầu tiên, giả định đó là ô email
    if not find_and_click_element(device_id, a_class="android.widget.EditText"):
        print(f"[{device_id}] Lỗi: Không tìm thấy ô để nhập email.")
        return False
    time.sleep(1)
    input_text(EMAIL)
    time.sleep(1)

    # 3. Chuyển sang ô mật khẩu bằng phím TAB và nhập
    print(f"[{device_id}] Chuyển sang ô mật khẩu bằng phím Tab...")
    adb_command("adb shell input keyevent KEYCODE_TAB")
    time.sleep(1)

    print(f"[{device_id}] Nhập mật khẩu...")
    input_text(PASSWORD)
    time.sleep(1)

    # 4. Tìm và nhấn nút đăng nhập (dựa vào text)
    print(f"[{device_id}] Tìm và nhấn nút 'Đăng nhập'...")
    if not find_and_click_element(device_id, text="Đăng nhập"):
       print(f"[{device_id}] Lỗi: Không tìm thấy nút 'Đăng nhập'.")
       return False
    
    # ... (code chờ và xác thực sau đăng nhập không đổi) ...
    print(f"[{device_id}] Chờ 15 giây để vào dashboard...")
    time.sleep(15)
    
    # Kiểm tra lại xem đã vào được dashboard chưa
    print(f"[{device_id}] Kiểm tra lại kết quả đăng nhập...")
    xml_check_file = dump_ui_xml(device_id)
    if xml_check_file:
        with open(xml_check_file, 'r', encoding='utf-8') as f:
            content = f.read()
        os.remove(xml_check_file)
        if "Dashboard" in content or "Bored" in content:
            print(f"[{device_id}] Đăng nhập thành công!")
            return True
        else:
            print(f"[{device_id}] Đăng nhập thất bại.")
            # Xử lý verify human nếu có
            if find_and_click_element(device_id, resource_id="cf-chl-widget-s3rzj"): # ID này chỉ là ví dụ
                 print(f"[{device_id}] Đã nhấn vào checkbox 'Verify Human'. Chờ và thử lại...")
                 time.sleep(10)
                 return True # Trả về True để vòng lặp chính thử lại việc lấy dữ liệu
            return False
    return False

# --- Hàm phân tích dữ liệu ---

def parse_boss_from_xml(xml_file_path):
    """
    Phân tích file XML từ UI dump để trích xuất thông tin boss.
    
    LƯU Ý QUAN TRỌNG:
    Hàm này được viết dựa trên GIẢ ĐỊNH về cấu trúc của trang iscout.club.
    Cấu trúc thực tế có thể khác. Chúng ta sẽ cần điều chỉnh lại sau khi có file XML mẫu.
    
    Giả định:
    - Mỗi boss nằm trong một 'node' cha.
    - Thông tin (tên, tọa độ, level) là các 'node' con có thuộc tính 'text'.
    """
    if not os.path.exists(xml_file_path):
        print(f"Lỗi: File XML không tồn tại tại đường dẫn: {xml_file_path}")
        return []

    print(f"Đang phân tích file: {xml_file_path}")
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    boss_list = []

    # --- PHẦN CẦN ĐIỀU CHỈNH SAU KHI CÓ FILE XML THỰC TẾ ---
    # Đoạn code dưới đây là ví dụ dựa trên giả định.
    
    # Giả định 1: Tìm tất cả các node có thuộc tính 'content-desc' (mô tả nội dung)
    # Đây là một cách phổ biến để tìm các phần tử có thể tương tác.
    # Chúng ta cần tìm một mẫu chung cho các hàng (row) trong bảng boss.
    # Ví dụ: có thể tất cả các node chứa thông tin boss đều có resource-id là "com.android.chrome:id/boss_row"
    # Hoặc chúng ta có thể phải lặp qua tất cả các node và tìm các node có text khớp với mẫu tọa độ.

    for node in root.iter('node'):
        # Giả định 2: Tọa độ boss luôn có dạng "K: Tọa độ"
        node_text = node.attrib.get('text', '')
        if re.match(r'^\d+:\d+$', node_text): # Giả định tọa độ có dạng XXX:YYY
             # Nếu tìm thấy một node có text là tọa độ, ta giả định các node "anh em" của nó
             # sẽ chứa thông tin còn lại (tên, level). Logic này rất phức tạp và cần file XML thực tế.
             
             # Code ví dụ (sẽ không chạy đúng):
             # parent_node = ... # Cần tìm node cha
             # boss_name = parent_node.find("./node[@resource-id='boss_name_id']").attrib['text']
             # level = parent_node.find("./node[@resource-id='boss_level_id']").attrib['text']
             
            boss_info = {
                "name": "TÊN BOSS (Cần điều chỉnh parser)",
                "coordinates": node_text,
                "level": "LEVEL (Cần điều chỉnh parser)",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "attacked": 0
            }
            boss_list.append(boss_info)
            print(f"Đã tìm thấy một mục có thể là boss tại: {node_text}")

    if not boss_list:
        print("CẢNH BÁO: Không tìm thấy thông tin boss nào từ file XML. Hàm 'parse_boss_from_xml' cần được điều chỉnh lại cho phù hợp với cấu trúc file XML thực tế của bạn.")
        
    return boss_list


# --- Hàm điều phối chính ---

def get_boss_locations_from_device(device_id):
    """
    Quy trình hoàn chỉnh để lấy thông tin boss từ một thiết bị cụ thể.
    """
    # *** LOGIC MỚI: KIỂM TRA ĐĂNG NHẬP TRƯỚC ***
    print(f"[{device_id}] Kiểm tra trạng thái đăng nhập...")
    set_device(device_id)
    
    # 1. Mở trang dashboard để kiểm tra
    ISCOUT_URL = "https://www.iscout.club/vi/dashboard"
    if not open_chrome_with_url(device_id, ISCOUT_URL):
        return None 

    # 2. Dump UI để xem đang ở trang nào
    xml_file_check = dump_ui_xml(device_id)
    is_logged_in = False
    if xml_file_check:
        with open(xml_file_check, 'r', encoding='utf-8') as f:
            content = f.read()
        os.remove(xml_file_check)
        # Nếu không thấy chữ "Đăng nhập" thì có lẽ đã đăng nhập rồi
        if "Đăng nhập" not in content and "Login" not in content:
            print(f"[{device_id}] Có vẻ đã đăng nhập. Bắt đầu lấy dữ liệu boss.")
            is_logged_in = True

    if not is_logged_in:
        print(f"[{device_id}] Chưa đăng nhập. Bắt đầu quy trình đăng nhập...")
        if not perform_login_on_device(device_id):
            print(f"[{device_id}] Đăng nhập tự động thất bại.")
            return None # Dừng lại nếu đăng nhập thất bại
    
    # --- Nếu đã đăng nhập thành công, tiếp tục quy trình cũ ---
    
    # 3. Dump UI của trang dashboard
    print(f"[{device_id}] Đang ở trang dashboard, tiến hành dump UI để lấy dữ liệu.")
    xml_file_data = dump_ui_xml(device_id)
    if not xml_file_data:
        return None

    # 4. Phân tích file XML
    boss_list = parse_boss_from_xml(xml_file_data)
    
    # Dọn dẹp file XML sau khi phân tích xong
    try:
        os.remove(xml_file_data)
        print(f"Đã xóa file XML tạm: {xml_file_data}")
    except (OSError, TypeError) as e:
        print(f"Lỗi khi xóa file XML tạm: {e}")

    return boss_list

def save_to_json(boss_list, filename="boss_locations.json", device_id=None):
    """Lưu danh sách boss vào file JSON (Tương tự file cũ)"""
    try:
        if device_id:
            filename = f"boss_locations_{device_id.replace(':', '_')}.json"
        
        data = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "boss_count": len(boss_list),
            "bosses": boss_list
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
        print(f"Đã lưu thông tin {len(boss_list)} boss vào file {filename}")
        return True
    except Exception as e:
        print(f"Lỗi khi lưu file JSON: {e}")
        return False


# --- Khối để chạy kiểm tra ---
if __name__ == "__main__":
    # Đây là phần để bạn có thể chạy file này trực tiếp để kiểm tra.
    # Bạn cần thay thế 'your_device_id' bằng ID thực tế của giả lập bạn muốn kiểm tra.
    
    # Lấy danh sách thiết bị
    from utils.adb_utils import select_memu_devices
    devices = select_memu_devices()
    
    if not devices:
        print("Không có thiết bị nào được chọn. Kết thúc.")
    else:
        # Chạy trên thiết bị đầu tiên được chọn
        test_device_id = devices[0]['device_id']
        print(f"\n--- Bắt đầu kiểm tra trên thiết bị: {test_device_id} ---")
        
        bosses = get_boss_locations_from_device(test_device_id)
        
        if bosses is not None:
            print(f"\n--- Hoàn thành: Lấy được {len(bosses)} thông tin boss ---")
            save_to_json(bosses, device_id=test_device_id)
        else:
            print("\n--- Thất bại: Không lấy được thông tin boss ---")
            
        print("\nQUAN TRỌNG: Hãy mở file XML vừa được tạo (ví dụ: window_dump_127.0.0.1_21503.xml) và gửi nội dung cho tôi để tôi có thể hoàn thiện hàm `parse_boss_from_xml`.") 