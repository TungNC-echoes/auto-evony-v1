import json
from datetime import datetime
from collections import defaultdict

def load_boss_data(filename="boss_locations.json", device_id=None):
    """Đọc dữ liệu boss từ file JSON"""
    try:
        # Xử lý tên file nếu có device_id
        if device_id:
            filename = f"boss_locations_{device_id.replace(':', '_')}.json"
            
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('bosses', [])
    except Exception as e:
        print(f"Lỗi khi đọc file JSON: {e}")
        return []

def save_boss_data(bosses, filename="boss_locations.json", device_id=None):
    """Lưu danh sách boss vào file JSON"""
    try:
        # Xử lý tên file nếu có device_id
        if device_id:
            filename = f"boss_locations_{device_id.replace(':', '_')}.json"
            
        data = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "boss_count": len(bosses),
            "bosses": bosses
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"Lỗi khi lưu file JSON: {e}")
        return False

def group_bosses_by_name(bosses):
    """Gom nhóm các boss theo tên"""
    boss_groups = defaultdict(list)
    for idx, boss in enumerate(bosses):
        boss_groups[boss['name']].append((idx, boss))
    return boss_groups

def display_boss_list(bosses):
    """Hiển thị danh sách boss đã được gom nhóm"""
    print("\n=== DANH SÁCH BOSS ===\n")
    print("ID | Tên Boss | Số lượng")
    print("-" * 50)
    
    boss_groups = group_bosses_by_name(bosses)
    for idx, (name, group) in enumerate(boss_groups.items(), 1):
        print(f"{idx:2d} | {name:30s} | {len(group):2d} con")
    
    return boss_groups