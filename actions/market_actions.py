import time
import sys
import os

# Thêm thư mục gốc vào sys.path để có thể import từ utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.image_utils import check_button_exists, find_and_click_button, find_and_click_bottom_edge

# Lấy đường dẫn tuyệt đối đến thư mục gốc
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def is_in_black_market(device_id=None):
    """Kiểm tra xem đã ở trong chợ đen chưa"""
    try:
        print("Đang kiểm tra xem có ở trong chợ đen không...")
        if check_button_exists("market/cho_den", device_id=device_id):
            print("Đã xác nhận đang ở trong chợ đen")
            return True
        else:
            print("Không ở trong chợ đen")
            return False
    except Exception as e:
        print(f"Lỗi khi kiểm tra chợ đen: {e}")
        return False

def check_and_enter_black_market(device_id=None):
    """Kiểm tra và đảm bảo đang ở trong chợ đen"""
    if not is_in_black_market(device_id):
        print("Không ở trong chợ đen, thoát sự kiện...")
        return False
    return True

def find_and_buy_meat(device_id=None):
    """Tìm và mua thịt trong chợ đen"""
    try:
        print("Đang tìm kiếm thịt trong chợ đen...")
        has_bought = False
        
        # Thử click trực tiếp vào cạnh dưới thịt 10
        if find_and_click_bottom_edge("market/thit_10", device_id=device_id, wait_time=1):
            print("Đã click vào cạnh dưới thịt 10")
            # time.sleep(1)
            if find_and_click_button("market/xac_nhan", device_id=device_id, wait_time=1, max_retries=1):
                print("Đã xác nhận mua thịt 10")
                # time.sleep(1)
                has_bought = True
                    
        # Nếu không mua được thịt 10, thử với thịt 1
        if not has_bought:
            if find_and_click_bottom_edge("market/thit_1", device_id=device_id, wait_time=1):
                print("Đã click vào cạnh dưới thịt 1")
                # time.sleep(1)
                if find_and_click_button("market/xac_nhan", device_id=device_id, wait_time=1, max_retries=1):
                    print("Đã xác nhận mua thịt 1")
                    has_bought = True
                else:
                    print("Không tìm thấy nút xác nhận cho thịt 1")
            else:
                print("Không thể click vào cạnh dưới thịt 1")
                
        if not has_bought:
            print("Không tìm thấy hoặc không thể mua thịt 1 hoặc thịt 10")
            return False
            
        return has_bought
    except Exception as e:
        print(f"Lỗi trong quá trình tìm và mua thịt: {e}")
        return False

def refresh_market(device_id=None):
    """Refresh chợ đen"""
    try:
        print("Đang refresh chợ đen...")
        if find_and_click_button("market/refresh", device_id=device_id, wait_time=0.5):
            print("Đã refresh chợ đen thành công")
            time.sleep(2)
            return True
        else:
            print("Không thể refresh chợ đen")
            return False
    except Exception as e:
        print(f"Lỗi khi refresh chợ đen: {e}")
        return False

def auto_buy_meat(device_id=None):
    """Auto mua thịt trong chợ đen"""
    try:
        # print("Bắt đầu quá trình tự động mua thịt...")
        
        while True:
            try:
                if not check_and_enter_black_market(device_id):
                    # print("Không ở trong chợ đen, thoát chương trình...")
                    break
                    
                if find_and_buy_meat(device_id):
                    print("Đã mua thịt thành công")
                else:
                    print("Không thể mua thịt, thử refresh...")
                    
                if refresh_market(device_id):
                    print("Đã refresh, tiếp tục tìm kiếm thịt...")
                else:
                    print("Không thể refresh, thử lại sau 5 giây...")
                    time.sleep(5)
                    
            except Exception as e:
                print(f"Lỗi trong quá trình tự động mua thịt: {e}")
                print("Thử lại sau 5 giây...")
                time.sleep(5)
    except Exception as e:
        print(f"Lỗi khi auto mua thịt: {e}")
        return False


if __name__ == "__main__":
    print("Bắt đầu kiểm tra chợ đen...")
    print("=" * 50)
    
    # Kiểm tra xem có ở trong chợ đen không
    result = is_in_black_market()
    print(f"Kết quả kiểm tra: {'Đang ở trong chợ đen' if result else 'Không ở trong chợ đen'}")
    
    print("=" * 50)
    print("Kiểm tra và đảm bảo đang ở trong chợ đen...")
    
    # Kiểm tra và đảm bảo đang ở trong chợ đen
    if check_and_enter_black_market():
        print("Đã xác nhận đang ở trong chợ đen, bắt đầu quá trình mua thịt...")
        auto_buy_meat()
    else:
        print("Không ở trong chợ đen, kết thúc chương trình")
    
    print("=" * 50)
    print("Kết thúc chương trình")