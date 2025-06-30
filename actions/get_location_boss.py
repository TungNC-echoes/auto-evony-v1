from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import json
from datetime import datetime

# Thông tin đăng nhập
EMAIL = "bkaprodx@gmail.com"
PASSWORD = "tung1995"

def login_iscout():
    """Thực hiện đăng nhập vào iscout.club"""
    driver = None
    try:
        # Khởi động trình duyệt
        driver = webdriver.Chrome()
        wait = WebDriverWait(driver, 20)
        
        # Truy cập trang đăng nhập
        print("Đang truy cập trang đăng nhập...")
        driver.get("https://www.iscout.club/vi/login")
        time.sleep(5)  # Chờ trang load xong

        # Điền email
        print("Đang nhập email...")
        email_field = wait.until(EC.presence_of_element_located((By.ID, "email")))
        email_field.clear()
        email_field.send_keys(EMAIL)

        # Điền mật khẩu
        print("Đang nhập mật khẩu...")
        password_field = wait.until(EC.presence_of_element_located((By.ID, "password")))
        password_field.clear()
        password_field.send_keys(PASSWORD)

        # Click nút đăng nhập
        print("Đang click nút đăng nhập...")
        login_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(), 'Đăng nhập')]")
        ))
        login_button.click()

        # Xử lý verify human nếu xuất hiện
        try:
            print("Đang kiểm tra verify human...")
            verify_checkbox = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".cb-lb input[type='checkbox']"))
            )

            print("Phát hiện verify human, đang click vào checkbox...")
            driver.execute_script("arguments[0].click();", verify_checkbox)
            time.sleep(2)

            # Chờ tối đa 30s cho tới khi chuyển hướng tới dashboard
            WebDriverWait(driver, 30).until(
                EC.url_contains("dashboard")
            )
            print("Xác thực verify human thành công!")
        except Exception as e:
            print("Không có verify human hoặc đã qua bước này, tiếp tục...")

        return driver

    except Exception as e:
        print(f"Lỗi trong quá trình đăng nhập: {e}")
        if driver:
            driver.quit()
        return None

def get_boss_locations(port=9014, max_retries=3):
    """Lấy thông tin vị trí boss từ web và trả về dạng list"""
    driver = None
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # Thiết lập để kết nối với Chrome đang mở
            chrome_options = Options()
            chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
            
            # Kết nối với Chrome đang mở
            driver = webdriver.Chrome(options=chrome_options)
            wait = WebDriverWait(driver, 20)
            boss_list = []
            
            # Kiểm tra xem đã ở trang dashboard chưa
            current_url = driver.current_url
            if "dashboard" not in current_url:
                print("Đang chuyển đến trang dashboard...")
                driver.get("https://www.iscout.club/vi/dashboard")
            # else:
            #     print("Đang refresh trang dashboard...")
            #     driver.refresh()
                
            # # Chờ 10 giây để trang load hoàn tất và các filter được áp dụng
            # print("Chờ 10 giây để trang load hoàn tất...")
            # time.sleep(10)

            # Chờ và tìm bảng boss
            print("Đang tìm thông tin boss...")
            table = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table tbody")))
            rows = table.find_elements(By.TAG_NAME, "tr")
            
            for row in rows:
                cols = row.find_elements(By.TAG_NAME, "td")
                if cols:
                    # Xử lý level string thành object
                    level_text = cols[2].text if len(cols) > 2 else ""
                    level_info = {}
                    
                    # Tách và xử lý thông tin tọa độ
                    if level_text:
                        lines = level_text.split('\n')
                        for line in lines:
                            if ':' in line:
                                key, value = line.split(':', 1)
                                key = key.strip()
                                value = value.strip()
                                if key in ['S', 'X', 'Y']:
                                    level_info[key] = value
                    
                    boss_info = {
                        "name": cols[0].text,
                        "coordinates": cols[1].text,
                        "level": level_info,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "attacked": 0  # Thêm trường attacked với giá trị mặc định là 0
                    }
                    boss_list.append(boss_info)
                    print(f"Đã thêm boss: {boss_info['name']} tại {boss_info['coordinates']}")
            
            return boss_list

        except Exception as e:
            retry_count += 1
            print(f"Lỗi trong lần thử {retry_count}: {e}")
            if retry_count < max_retries:
                print(f"Đang thử lại sau 5 giây...")
                time.sleep(5)
            else:
                print("Đã hết số lần thử lại")
        finally:
            if driver:
                driver.quit()
    
    return []

def save_to_json(boss_list, filename="boss_locations.json", device_id=None):
    """Lưu danh sách boss vào file JSON"""
    try:
        # Tạo tên file với device_id nếu được cung cấp
        if device_id:
            filename = f"boss_locations_{device_id.replace(':', '_')}.json"
            
        # Tạo dictionary chứa thông tin theo format yêu cầu
        data = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "boss_count": len(boss_list),
            "bosses": boss_list
        }
        
        # Lưu vào file JSON với encoding utf-8 và indent
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
        print(f"Đã lưu thông tin {len(boss_list)} boss vào file {filename}")
        return True
    except Exception as e:
        print(f"Lỗi khi lưu file JSON: {e}")
        return False

def main():
    print("="*50)
    print("CHƯƠNG TRÌNH LẤY THÔNG TIN VỊ TRÝ BOSS")
    print("="*50)
    
    try:
        # Lấy thông tin boss với số lần thử tối đa là 3
        boss_list = get_boss_locations(max_retries=3)
        
        if boss_list:
            # Lưu vào file JSON
            if save_to_json(boss_list):
                print("\nĐã hoàn thành việc lưu thông tin boss!")
            else:
                print("\nKhông thể lưu thông tin boss vào file JSON!")
        else:
            print("\nKhông tìm thấy thông tin boss nào!")
            
    except KeyboardInterrupt:
        print("\nNgười dùng đã dừng chương trình")
    except Exception as e:
        print(f"\nLỗi không mong muốn: {e}")
    
    print("="*50)
    print("Kết thúc chương trình")

if __name__ == "__main__":
    main()
