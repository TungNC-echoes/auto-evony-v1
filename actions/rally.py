import time
from actions.war_actions import join_war_sequence, continue_war_sequence, join_war_sequence_no_general, continue_war_sequence_no_general
from utils.image_utils import check_button_exists, find_and_click_button
from utils.adb_utils import swipe_up, swipe_down, adb_command

def auto_join_rally(device_id=None, use_general=True):
    """Hàm chạy bot tự động tham gia chiến tranh"""
    war_type = "có chọn tướng" if use_general else "không chọn tướng"
    print(f"Bắt đầu chạy bot tự động tham gia chiến tranh ({war_type})...")

    # Thực hiện chuỗi hành động tham gia chiến tranh lần đầu
    while True:
        try:
            # Kiểm tra nút back trước
            if check_button_exists("back", device_id=device_id):
                # print("Phát hiện đang ở màn hình chờ, quay lại màn hình chính...")
                if not find_and_click_button("back", device_id=device_id):
                    print("Không thể click vào nút back, thử dùng phím ESC...")
                    if adb_command('adb shell input keyevent KEYCODE_ESCAPE'):
                        print("Đã nhấn ESC thành công")
                    else:
                        print("Không thể thực hiện thao tác quay lại, chờ 30 giây...")
                        time.sleep(30)
                        continue
                time.sleep(2)  # Chờ animation hoàn thành

            # print("Đang thử tham gia chiến tranh...")
            if use_general:
                if join_war_sequence(device_id):
                    # print("Đã hoàn thành chuỗi hành động tham gia chiến tranh lần đầu")
                    break
                else:
                    # print("Không thể hoàn thành chuỗi hành động tham gia chiến tranh lần đầu")
                    # print("Chờ 30 giây trước khi thử lại...")
                    time.sleep(30)
            else:
                if join_war_sequence_no_general(device_id):
                    # print("Đã hoàn thành chuỗi hành động tham gia chiến tranh lần đầu (không chọn tướng)")
                    break
                else:
                    # print("Không thể hoàn thành chuỗi hành động tham gia chiến tranh lần đầu (không chọn tướng)")
                    # print("Chờ 30 giây trước khi thử lại...")
                    time.sleep(30)
        except Exception as e:
            # print(f"Lỗi trong quá trình tham gia chiến tranh lần đầu: {e}")
            # print("Chờ 30 giây trước khi thử lại...")
            time.sleep(30)

    # Biến để theo dõi trạng thái kéo màn hình
    scroll_up = False

    # Vòng lặp chính kiểm tra và tham gia chiến tranh
    while True:
        try:
            # Kiểm tra xem có nút auto_join không (đang ở màn hình chiến tranh)
            if not check_button_exists("auto_join", device_id=device_id):
                # print("Không ở màn hình chiến tranh, kiểm tra trạng thái...")

                # Kiểm tra nút back
                if check_button_exists("back", device_id=device_id):
                    # print("Phát hiện đang ở màn hình chờ, quay lại màn hình chính...")
                    if not find_and_click_button("back", device_id=device_id):
                        # print("Không thể click vào nút back")
                        time.sleep(30)
                        continue
                    time.sleep(2)  # Chờ animation hoàn thành

                # Thực hiện lại chuỗi hành động từ war_button
                if use_general:
                    if join_war_sequence(device_id):
                        print("Đã hoàn thành chuỗi hành động tham gia chiến tranh")
                    else:
                        # print("Không thể hoàn thành chuỗi hành động tham gia chiến tranh")
                        # print("Chờ 30 giây trước khi thử lại...")
                        time.sleep(30)
                else:
                    if join_war_sequence_no_general(device_id):
                        print("Đã hoàn thành chuỗi hành động tham gia chiến tranh (không chọn tướng)")
                    else:
                        # print("Không thể hoàn thành chuỗi hành động tham gia chiến tranh (không chọn tướng)")
                        # print("Chờ 30 giây trước khi thử lại...")
                        time.sleep(30)
                continue

            # Chờ 10 giây trước khi kiểm tra
            print("Chờ 10 giây trước khi kiểm tra...")
            time.sleep(10)

            # Kiểm tra nút tham gia
            if check_button_exists("join_button", device_id=device_id):
                # print("Tìm thấy nút tham gia, bắt đầu tham gia chiến tranh...")
                # Thực hiện chuỗi hành động từ join_button
                if use_general:
                    if continue_war_sequence(device_id):
                        print("Đã hoàn thành chuỗi hành động tham gia chiến tranh")
                    else:
                        print("Không thể hoàn thành chuỗi hành động tham gia chiến tranh")
                else:
                    if continue_war_sequence_no_general(device_id):
                        print("Đã hoàn thành chuỗi hành động tham gia chiến tranh (không chọn tướng)")
                    else:
                        print("Không thể hoàn thành chuỗi hành động tham gia chiến tranh (không chọn tướng)")
            else:
                # Thực hiện kéo màn hình
                if scroll_up:
                    print("Kéo màn hình lên...")
                    swipe_up()
                else:
                    print("Kéo màn hình xuống...")
                    swipe_down()

                # Đảo ngược trạng thái cho lần sau
                scroll_up = not scroll_up

        except Exception as e:
            # print(f"Lỗi trong quá trình chạy bot: {e}")
            # Nếu có lỗi, chờ thêm 30 giây trước khi thử lại
            time.sleep(30)            # Cập nhật tất cả các lời gọi hàm check_button_exists và find_and_click_button
            # bằng cách thêm device_id
            if check_button_exists("rally/join_button", device_id=device_id):
                find_and_click_button("rally/join_button", device_id=device_id)
            print(f"Lỗi khi tham gia rally: {e}")
