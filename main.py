import time
import random
from multiprocessing import Process, Manager, Lock
from actions.war_actions import join_war_sequence, continue_war_sequence, join_war_sequence_no_general
from utils.image_utils import check_button_exists, find_and_click_button
from utils.adb_utils import swipe_up, swipe_down, select_memu_devices, set_device
from actions.rally import auto_join_rally
from actions.market_actions import auto_buy_meat

# Import cho attack boss
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from actions.user_interface import get_boss_selection, display_boss_list
from actions.get_location_boss import get_boss_locations, save_to_json
from actions.boss_data_manager import load_boss_data, group_bosses_by_name
from actions.boss_attacker import attack_selected_bosses


def show_feature_menu():
    """Hiển thị menu chọn tính năng"""
    print("\nChọn tính năng muốn sử dụng:")
    print("1. Auto tham gia Rally")
    print("2. Auto mua thịt")
    print("3. Auto tham gia War (không chọn tướng)")
    print("4. Auto tấn công Boss")
    return input("Nhập số tương ứng với tính năng (1-4): ").strip()


def run_attack_boss_for_device(device_id):
    """Chạy attack_boss cho một device cụ thể"""
    try:
        # Thiết lập device
        set_device(device_id)

        print(f"Bắt đầu tấn công boss trên device {device_id}")

        # Bước 1: Cập nhật vị trí boss từ thiết bị
        print(
            f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Đang cập nhật vị trí boss từ thiết bị {device_id}...")
        bosses = get_boss_locations()

        if not bosses:
            print("Không tìm thấy thông tin boss!")
            return

        # Lưu thông tin boss vào file
        if not save_to_json(bosses, device_id=device_id):
            print("Không thể lưu thông tin boss vào file!")
            return

        # Bước 2: Tự động chọn tất cả boss (tránh input trong multi-process)
        boss_groups = group_bosses_by_name(bosses)
        initial_selection = []

        # Chọn tất cả boss có sẵn
        for boss_name, boss_group in boss_groups.items():
            initial_selection.append(boss_group)

        if not initial_selection:
            print("Không có boss nào để tấn công!")
            return

        print(f"Đã tự động chọn {len(initial_selection)} loại boss để tấn công")

        # Bước 3: Bắt đầu vòng lặp tấn công
        start_time = time.time()
        while True:
            # Kiểm tra số boss chưa tấn công và hiển thị thông tin
            unattacked_count = sum(1 for group in initial_selection
                                   for _, boss in group
                                   if not boss.get('attacked', 0))

            remaining_time = int(1800 - (time.time() - start_time))  # 30 phút = 1800 giây
            print(f"\nCòn {unattacked_count} boss chưa tấn công")
            print(f"Thời gian còn lại: {remaining_time} giây")

            # Thực hiện tấn công các boss đã chọn
            result = attack_selected_bosses(initial_selection, bosses, start_time)

            # Kiểm tra kết quả
            if result == "update_required" or remaining_time <= 0:
                print("\nĐã đủ 30 phút, kết thúc tấn công boss...")
                break  # Thoát vòng lặp tấn công
            elif unattacked_count == 0:
                print("\nĐã hết boss, kết thúc tấn công boss...")
                break  # Thoát vòng lặp tấn công

            time.sleep(1)

    except Exception as e:
        print(f"Lỗi khi tấn công boss trên {device_id}: {e}")


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
                auto_join_rally(device['device_id'], use_general=True)  # Sử dụng rally với cờ có chọn tướng
            elif feature_choice == "2":
                print(f"Bắt đầu auto mua thịt trên {device['name']}...")
                auto_buy_meat(device['device_id'])  # Thêm device_id
            elif feature_choice == "3":
                print(f"Bắt đầu auto tham gia War (không chọn tướng) trên {device['name']}...")
                auto_join_rally(device['device_id'], use_general=False)  # Sử dụng rally với cờ không chọn tướng
            elif feature_choice == "4":
                print(f"Bắt đầu auto tấn công Boss trên {device['name']}...")
                run_attack_boss_for_device(device['device_id'])

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
                print(
                    f"Không ở trong chợ đen trên {device['name']}, đang thử vào lại... (Lần {retry_count}/{max_retries})")
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
            if choice in ["1", "2", "3", "4"]:
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