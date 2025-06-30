import os
import time
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.image_utils import check_button_exists, find_and_click_button

def buy_general_sequence(device_id=None):
    """Chuỗi hành động mua tướng cho một vòng lặp"""
    print(f"=== Bắt đầu vòng mua tướng trên device {device_id} ===")
    # 1. Click làm mới
    print(f"Click lam_moi trên device {device_id}...")
    if not find_and_click_button("muatuong/lam_moi", device_id=device_id, wait_time=3, threshold=0.65):
        print(f"Không thể click lam_moi trên device {device_id}")
        return False

    # 2. Kiểm tra có tướng không
    if check_button_exists("muatuong/tuong", device_id=device_id, threshold=0.9):
        print(f"Phát hiện tuong trên device {device_id}. Đang thực hiện tuyển mộ...")
        # Click tướng
        if not find_and_click_button("muatuong/tuong", device_id=device_id, wait_time=3, threshold=0.65):
            print(f"Không thể click tuong trên device {device_id}")
            return False
        # Click tuyển mộ
        if not find_and_click_button("muatuong/tuyen_mo", device_id=device_id, wait_time=3, threshold=0.65):
            print(f"Không thể click tuyen_mo trên device {device_id}")
            return False
        # Click xác nhận
        if not find_and_click_button("muatuong/xac_nhan", device_id=device_id, wait_time=3, threshold=0.65):
            print(f"Không thể click xac_nhan sau tuyển mộ trên device {device_id}")
            return False
        print(f"Đã tuyển mộ tướng thành công trên device {device_id}")
        return True

    # 3. Nếu không có tướng, kiểm tra và xử lý xác nhận (nếu có)
    while check_button_exists("muatuong/xac_nhan", device_id=device_id, threshold=0.6):
        print(f"Phát hiện xac_nhan trên device {device_id}. Đang xác nhận...")
        if not find_and_click_button("muatuong/xac_nhan", device_id=device_id, wait_time=3, threshold=0.65):
            print(f"Không thể click xac_nhan trên device {device_id}")
            return False
        # Sau khi xác nhận, kiểm tra lại có tướng không
        if check_button_exists("muatuong/tuong", device_id=device_id, threshold=0.9):
            print(f"Phát hiện tuong sau xác nhận trên device {device_id}. Đang thực hiện tuyển mộ...")
            if not find_and_click_button("muatuong/tuong", device_id=device_id, wait_time=3, threshold=0.65):
                print(f"Không thể click tuong trên device {device_id}")
                return False
            if not find_and_click_button("muatuong/tuyen_mo", device_id=device_id, wait_time=3, threshold=0.65):
                print(f"Không thể click tuyen_mo trên device {device_id}")
                return False
            if not find_and_click_button("muatuong/xac_nhan", device_id=device_id, wait_time=3, threshold=0.65):
                print(f"Không thể click xac_nhan sau tuyển mộ trên device {device_id}")
                return False
            print(f"Đã tuyển mộ tướng thành công trên device {device_id}")
            return True
        # Nếu chưa có tướng, tiếp tục lặp lại xác nhận (nếu còn)

    # Nếu không có tướng và không còn xác nhận, kết thúc vòng lặp, sẽ quay lại làm mới ở vòng tiếp theo
    print(f"Không phát hiện tướng hoặc xác nhận trên device {device_id}, sẽ thử lại...")
    return True

def auto_buy_general(device_id=None):
    """Bot tự động mua tướng lặp vô hạn"""
    print(f"=== Bắt đầu auto mua tướng trên device {device_id} ===")
    while True:
        try:
            buy_general_sequence(device_id)
            time.sleep(2)  # Chờ 2 giây trước khi lặp lại
        except Exception as e:
            print(f"Lỗi trong quá trình chạy bot trên device {device_id}: {e}")
            time.sleep(5)  # Chờ 5 giây nếu có lỗi
