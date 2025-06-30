import time
import random
from multiprocessing import Process, Manager, Lock
from actions.war_actions import join_war_sequence, continue_war_sequence
from utils.image_utils import check_button_exists, find_and_click_button
from utils.adb_utils import swipe_up, swipe_down, select_memu_devices, set_device
from actions.rally import auto_join_rally
from actions.market_actions import auto_buy_meat

def show_feature_menu():
    """Hiển thị menu chọn tính năng"""
    print("\nChọn tính năng muốn sử dụng:")
    print("1. Auto tham gia Rally")
    print("2. Auto mua thịt")
    return input("Nhập số tương ứng với tính năng (1-2): ").strip()

def run_feature_with_retry(device, feature_choice, device_lock):
    """Chạy tính năng với cơ chế thử lại liên tục"""
    max_retries = 3  # Số lần thử lại tối đa cho mỗi lỗi
    retry_count = 0
    
    while True:  # Vòng lặp vô hạn để tiếp tục chạy
        try:
            with device_lock:
                set_device(device['device_id'])
            
            if feature_choice == "1":
                print(f"Bắt đầu auto tham gia Rally trên {device['name']}...")
                auto_join_rally(device['device_id'])  # Thêm device_id
            elif feature_choice == "2":
                print(f"Bắt đầu auto mua thịt trên {device['name']}...")
                auto_buy_meat(device['device_id'])  # Thêm device_id
                
            # Reset số lần thử lại khi thành công
            retry_count = 0
                
        except Exception as e:
            print(f"Lỗi trên {device['name']}: {e}")
            retry_count += 1
            
            if retry_count >= max_retries:
                print(f"Đã thử lại {max_retries} lần không thành công, đợi thêm thời gian...")
                time.sleep(30)  # Đợi lâu hơn sau nhiều lần thất bại
                retry_count = 0  # Reset counter
                continue
            
            if "libpng error" in str(e):
                print(f"Lỗi đọc ảnh trên {device['name']}, đang thử lại... (Lần {retry_count}/{max_retries})")
                time.sleep(5)  # Chờ lâu hơn cho lỗi đọc ảnh
                continue
                
            elif "Không ở trong chợ đen" in str(e):
                print(f"Không ở trong chợ đen trên {device['name']}, đang thử vào lại... (Lần {retry_count}/{max_retries})")
                time.sleep(3)
                continue
                
            else:
                print(f"Lỗi khác trên {device['name']}, đang thử lại... (Lần {retry_count}/{max_retries})")
                time.sleep(2)
                continue

def run_feature_for_device(device, feature_choice, device_lock):
    """Chạy tính năng cho một thiết bị cụ thể"""
    try:
        print(f"\nBắt đầu chạy trên {device['name']}...")
        run_feature_with_retry(device, feature_choice, device_lock)
    except Exception as e:
        print(f"Lỗi nghiêm trọng khi chạy trên {device['name']}: {e}")

def main():
    """Hàm chính của chương trình"""
    print("Chào mừng đến với EVONY AUTO!")
    
    try:
        # Chọn giả lập
        devices = select_memu_devices()
        if not devices:
            print("Không có giả lập nào được chọn, kết thúc chương trình.")
            return

        print("\nDanh sách thiết bị được chọn:")
        for device in devices:
            print(f"- {device['name']} ({device['device_id']})")

        # Chọn tính năng một lần duy nhất
        while True:
            choice = show_feature_menu()
            if choice in ["1", "2"]:
                break
            print("Lựa chọn không hợp lệ, vui lòng chọn lại!")

        print(f"\nBắt đầu chạy trên {len(devices)} thiết bị...")
        
        # Tạo lock cho mỗi thiết bị
        manager = Manager()
        device_locks = {device['device_id']: manager.Lock() for device in devices}
        
        # Tạo và khởi chạy các process
        processes = []
        for device in devices:
            process = Process(
                target=run_feature_for_device,
                args=(device, choice, device_locks[device['device_id']])
            )
            processes.append(process)
            process.start()
        
        # Chờ tất cả các process hoàn thành
        for process in processes:
            process.join()
            
    except KeyboardInterrupt:
        print("\nĐã nhận được tín hiệu dừng chương trình...")
        # Kết thúc tất cả các process
        for process in processes:
            if process.is_alive():
                process.terminate()
    except Exception as e:
        print(f"Lỗi không mong muốn: {e}")

if __name__ == "__main__":
    main()  # Bắt đầu chạy bot tự động
    # auto_join_rally()  # Dòng này gây ra việc chạy thêm một lần nữa