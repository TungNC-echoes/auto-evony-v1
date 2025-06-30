import sys
import os
import time
from multiprocessing import Process, Manager, Lock

# Thêm thư mục gốc vào PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from actions.buy_general_actions import auto_buy_general
from utils.adb_utils import select_memu_devices, set_device


def run_feature_with_retry(device, device_lock):
    """Chạy tính năng với cơ chế thử lại liên tục"""
    max_retries = 1  # Số lần thử lại tối đa cho mỗi lỗi
    retry_count = 0
    
    while True:  # Vòng lặp vô hạn để tiếp tục chạy
        try:
            with device_lock:
                set_device(device['device_id'])
            
            print(f"Bắt đầu auto mua tướng trên {device['name']}...")
            auto_buy_general(device['device_id'])
                
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
            else:
                print(f"Lỗi khác trên {device['name']}, đang thử lại... (Lần {retry_count}/{max_retries})")
                time.sleep(2)
                continue


def run_feature_for_device(device, device_lock):
    """Chạy tính năng cho một thiết bị cụ thể"""
    try:
        print(f"\nBắt đầu chạy trên {device['name']}...")
        run_feature_with_retry(device, device_lock)
    except Exception as e:
        print(f"Lỗi nghiêm trọng khi chạy trên {device['name']}: {e}")


def main():
    """Hàm chính của chương trình"""
    print("="*50)
    print("CHƯƠNG TRÌNH TỰ ĐỘNG MUA TƯỚNG")
    print("="*50)
    
    try:
        # Chọn giả lập
        devices = select_memu_devices()
        if not devices:
            print("Không có giả lập nào được chọn, kết thúc chương trình.")
            return

        print("\nDanh sách thiết bị được chọn:")
        for device in devices:
            print(f"- {device['name']} ({device['device_id']})")

        print(f"\nBắt đầu chạy trên {len(devices)} thiết bị...")
        
        # Tạo lock cho mỗi thiết bị
        manager = Manager()
        device_locks = {device['device_id']: manager.Lock() for device in devices}
        
        # Tạo và khởi chạy các process
        processes = []
        for device in devices:
            process = Process(
                target=run_feature_for_device,
                args=(device, device_locks[device['device_id']])
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