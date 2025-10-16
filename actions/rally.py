import time
from actions.war_actions import join_war_sequence, continue_war_sequence, join_war_sequence_no_general, continue_war_sequence_no_general
from utils.image_utils import check_button_exists, find_and_click_button
from utils.adb_utils import swipe_up, swipe_down, adb_command, tap_screen, take_screenshot

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

def auto_join_advanced_rally_with_boss_selection(device_id=None, use_general=True, selected_bosses=None):
    """
    Advanced Rally Logic:
    1. Tìm tất cả boss được chọn và lưu tọa độ vào mảng
    2. Duyệt từng boss trong mảng:
       - Kiểm tra button "joined" ngay dưới boss
       - Nếu có "joined" → bỏ qua (đã tấn công)
       - Nếu không có "joined" → tìm button "join" ngay dưới boss
       - Nếu có "join" → click join → thực hiện war sequence (bỏ phần tìm join)
       - Nếu không có "join" → bỏ qua (không thể tấn công)
    3. Sau khi duyệt hết boss → scroll để tìm boss mới
    4. Lặp lại
    """
    try:
        if not selected_bosses:
            print("❌ Không có boss nào được chọn")
            return False
        
        war_type = "có chọn tướng" if use_general else "không chọn tướng"
        print(f"🎯 Bắt đầu Advanced Rally ({war_type}) với {len(selected_bosses)} boss: {selected_bosses}")
        
        # Import Advanced War Actions
        from actions.war_actions_advanced import (
            join_advanced_war_sequence, 
            join_advanced_war_sequence_no_general,
            find_all_boss_positions,
            find_join_button_below_boss,
        )
        
        # Thiết lập device
        if device_id:
            from utils.adb_utils import set_device
            set_device(device_id)
            print(f"🔧 Set device to: {device_id}")
        
        # Thoát ra màn hình chính bằng ESC (giống Basic)
        print("🔄 Thoát ra màn hình chính...")
        import time
        from utils.adb_utils import adb_command
        from utils.image_utils import check_button_exists, find_and_click_button
        max_esc_attempts = 5
        for i in range(max_esc_attempts):
            print(f"🔄 ESC lần {i+1}/{max_esc_attempts}")
            adb_command('adb shell input keyevent KEYCODE_ESCAPE')
            time.sleep(2)  # Tăng thời gian chờ để cancel button xuất hiện
            
            # Kiểm tra xem có button cancel không
            if check_button_exists("cancel", device_id=device_id, threshold=0.75):
                print("✅ Tìm thấy button cancel, click để thoát ra màn hình chính")
                if find_and_click_button("cancel", device_id=device_id, threshold=0.75):
                    time.sleep(2)  # Chờ animation
                    print("✅ Đã thoát ra màn hình chính thành công")
                    break  # Ngắt vòng lặp ESC ngay lập tức
                else:
                    print("❌ Không thể click cancel button")
            else:
                print(f"⏳ Chưa tìm thấy cancel button... (lần {i+1}/{max_esc_attempts})")
        
        # Kiểm tra war_button sau khi thoát ra màn hình chính (chờ vô hạn)
        print("🔍 Kiểm tra war_button sau khi thoát ra màn hình chính...")
        war_button_found = False
        war_button_attempts = 0
        
        while not war_button_found:
            if check_button_exists("war_button", device_id=device_id):
                print("✅ Tìm thấy war_button, click để vào màn hình war")
                if find_and_click_button("war_button", device_id=device_id):
                    time.sleep(3)  # Chờ animation
                    war_button_found = True
                else:
                    print("❌ Không thể click war_button")
                    time.sleep(2)
            else:
                war_button_attempts += 1
                print(f"⏳ Chưa tìm thấy war_button... (lần {war_button_attempts}) - Chờ 20s")
                time.sleep(20)  # Chờ 20s trước khi kiểm tra lại
        
        # Biến để theo dõi trạng thái kéo màn hình (giống Basic)
        scroll_up = False
        
        # Vòng lặp chính (giống Basic)
        while True:
            try:
                # Kiểm tra auto_join button (giống Basic)
                from utils.image_utils import check_button_exists, find_and_click_button
                if not check_button_exists("auto_join", device_id=device_id):
                    print("⚠️ Không còn ở trong war screen, có thể bị mất kết nối")
                    print("🔄 Thoát ra màn hình chính và tìm war_button...")
                    
                    # Thoát ra màn hình chính bằng ESC
                    max_esc_attempts = 5
                    for i in range(max_esc_attempts):
                        print(f"🔄 ESC lần {i+1}/{max_esc_attempts}")
                        adb_command('adb shell input keyevent KEYCODE_ESCAPE')
                        time.sleep(2)
                        
                        if check_button_exists("cancel", device_id=device_id, threshold=0.75):
                            print("✅ Tìm thấy button cancel, click để thoát ra màn hình chính")
                            if find_and_click_button("cancel", device_id=device_id, threshold=0.75):
                                time.sleep(2)
                                print("✅ Đã thoát ra màn hình chính thành công")
                                break
                    
                    # Tìm war_button để vào lại war screen
                    print("🔍 Tìm war_button để vào lại war screen...")
                    war_button_found = False
                    
                    while not war_button_found:
                        if check_button_exists("war_button", device_id=device_id):
                            print("✅ Tìm thấy war_button, click để vào màn hình war")
                            if find_and_click_button("war_button", device_id=device_id):
                                time.sleep(3)
                                war_button_found = True
                                print("✅ Đã vào lại war screen")
                            else:
                                print("❌ Không thể click war_button")
                                time.sleep(2)
                        else:
                            print("⏳ Chưa tìm thấy war_button... - Chờ 20s")
                            time.sleep(20)
                    
                    continue
                
                # ADVANCED LOGIC: Tìm và xử lý boss (Cách 2 - đơn giản)
                boss_attacked = False  # Flag để biết có boss nào được tấn công không
                
                # 1. Tìm tất cả boss được chọn
                boss_positions = find_all_boss_positions(selected_bosses, device_id)
                
                # 2. Nếu không có boss nào → cần scroll
                if not boss_positions:
                    print("❌ Không tìm thấy boss nào, sẽ scroll")
                    # Không set boss_attacked = True để cho phép scroll
                else:
                    # 3. Duyệt từng boss
                    for boss_info in boss_positions:
                        boss_x, boss_y, boss_width, boss_height, boss_name = boss_info
                        
                        # 4. Tìm button "join" trong vùng dưới boss
                        print(f"🔍 Xử lý boss: {boss_name} tại ({boss_x}, {boss_y})")
                        print(f"🔍 Tìm kiếm join button cho boss {boss_name}...")
                        join_button_pos = find_join_button_below_boss(boss_x, boss_y, boss_width, boss_height, device_id)
                        
                        # 5. Nếu không có join button → boss đã được join, bỏ qua
                        if not join_button_pos:
                            print(f"✅ Boss {boss_name} đã được join (không có join button), bỏ qua")
                            continue
                        
                        if join_button_pos:
                            join_x, join_y = join_button_pos
                            print(f"🎯 Tìm thấy join button cho {boss_name} tại ({join_x}, {join_y})")
                            
                            # Click join button
                            print(f"🖱️ Đang click join button tại ({join_x}, {join_y}) cho boss {boss_name}")
                            if tap_screen(join_x, join_y):
                                print(f"✅ Đã click join button cho boss {boss_name}")
                                boss_attacked = True  # Set True ngay khi click thành công
                                
                                # 6. Thực hiện war sequence
                                if use_general:
                                    war_success = join_advanced_war_sequence(device_id, selected_bosses)
                                    if war_success:
                                        print("✅ Đã hoàn thành war sequence với tướng")
                                    else:
                                        print("❌ Không thể hoàn thành war sequence với tướng")
                                else:
                                    war_success = join_advanced_war_sequence_no_general(device_id, selected_bosses)
                                    if war_success:
                                        print("✅ Đã hoàn thành war sequence không tướng")
                                    else:
                                        print("❌ Không thể hoàn thành war sequence không tướng")
                                
                                break  # Chỉ tấn công 1 boss mỗi lần
                            else:
                                print(f"❌ Không thể click join button cho boss {boss_name}")
                        else:
                            print(f"❌ Không tìm thấy join button cho boss {boss_name}")
                
                # 7. Nếu không có boss nào được tấn công hoặc không tìm thấy boss → scroll (giống Basic)
                if not boss_attacked or not boss_positions:
                    if scroll_up:
                        print("📱 Kéo màn hình lên...")
                        swipe_up()
                    else:
                        print("📱 Kéo màn hình xuống...")
                        swipe_down()
                    scroll_up = not scroll_up
                    print(f"🔄 Lần scroll tiếp theo sẽ: {'lên' if scroll_up else 'xuống'}")
                    time.sleep(4)  # Chờ màn hình ổn định sau khi scroll
                    
                    # Chụp ảnh mới sau khi scroll để tìm boss mới
                    print("📸 Chụp ảnh mới sau khi scroll...")
                    screenshot_filename = f"current_screen_{device_id.replace(':', '_')}.JPG"
                    if take_screenshot(screenshot_filename, device_id):
                        print("✅ Đã chụp ảnh mới sau scroll")
                    else:
                        print("❌ Không thể chụp ảnh mới sau scroll")
                
            except Exception as e:
                print(f"Lỗi trong quá trình chạy bot: {e}")
                time.sleep(30)
        
    except Exception as e:
        print(f"❌ Lỗi trong auto_join_advanced_rally_with_boss_selection: {e}")
        return False
