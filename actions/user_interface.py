import sys
import os

# Thêm thư mục gốc vào PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from actions.boss_data_manager import load_boss_data, display_boss_list, save_boss_data
from actions.boss_attacker import attack_selected_bosses

def get_boss_selection(boss_groups):
    """Nhận input lựa chọn boss từ người dùng"""
    while True:
        try:
            choice = input("\nNhập ID boss muốn tấn công (phân cách bằng dấu phẩy hoặc Enter để chọn tất cả, 'q' để thoát): ").strip()
            
            if choice.lower() == 'q':
                return None
            
            if not choice:  # Nếu người dùng nhấn Enter
                return list(boss_groups.values())  # Trả về tất cả các nhóm boss
            
            # Xử lý input thành list các ID
            selected_ids = [int(id.strip()) for id in choice.split(',')]
            
            # Kiểm tra tính hợp lệ của các ID
            if all(1 <= id <= len(boss_groups) for id in selected_ids):
                # Trả về các nhóm boss được chọn
                selected_groups = [list(boss_groups.values())[id-1] for id in selected_ids]
                return selected_groups
            else:
                print("ID không hợp lệ! Vui lòng nhập lại.")
                
        except ValueError:
            print("Vui lòng nhập ID hợp lệ!")
        except Exception as e:
            print(f"Lỗi: {e}")

def main():
    print("="*50)
    print("CHƯƠNG TRÌNH TẤN CÔNG BOSS")
    print("="*50)
    
    # Đọc dữ liệu boss
    bosses = load_boss_data()
    if not bosses:
        print("Không tìm thấy thông tin boss!")
        return
    
    while True:
        # Đếm số boss chưa tấn công
        unattacked_count = sum(1 for boss in bosses if not boss.get('attacked', 0))
        if unattacked_count == 0:
            print("\nĐã tấn công tất cả các boss!")
            break
            
        print(f"\nCòn {unattacked_count} boss chưa tấn công")
        
        # Hiển thị danh sách boss và nhận lựa chọn
        boss_groups = display_boss_list(bosses)
        selected_groups = get_boss_selection(boss_groups)
        
        if selected_groups is None:  # Người dùng chọn thoát
            break
            
        if selected_groups:
            attack_selected_bosses(selected_groups, bosses)  # Truyền thêm biến bosses

if __name__ == "__main__":
    main()