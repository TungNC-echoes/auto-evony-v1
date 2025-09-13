# EVONY Auto - Multi Device Manager

## 📋 Mô tả
Ứng dụng tự động hóa cho game EVONY với khả năng quản lý nhiều thiết bị MEmu đồng thời.

## 🚀 Tính năng
- ✅ Auto tham gia Rally
- ✅ Auto mua thịt
- ✅ Auto tham gia War (không chọn tướng)
- ✅ Auto tấn công Boss
- ✅ Hỗ trợ nhiều thiết bị MEmu
- ✅ Giao diện GUI thân thiện
- ✅ Tích hợp sẵn ADB (không cần cài đặt thêm)

## 📦 Cài đặt và Build

### Yêu cầu hệ thống
- Windows 10/11
- Python 3.8+ (chỉ cần khi build, không cần khi chạy executable)

### Build từ source code
1. Clone repository
2. Chạy script build tự động:
   `ash
   python build.py
   `
3. File executable sẽ được tạo trong thư mục dist/EVONY_Auto.exe

### Chạy ứng dụng
1. Copy file EVONY_Auto.exe sang máy đích
2. Chạy trực tiếp file .exe (không cần cài Python hay ADB)
3. Đảm bảo MEmu đang chạy và kết nối ADB

## 🎮 Hướng dẫn sử dụng

### Chuẩn bị
1. Mở MEmu và đăng nhập game EVONY
2. Đảm bảo ADB debugging được bật
3. Chạy ứng dụng EVONY Auto

### Sử dụng
1. Chọn thiết bị MEmu muốn sử dụng
2. Chọn tính năng muốn chạy tự động
3. Nhấn Start để bắt đầu

## 📁 Cấu trúc project
`
auto-evony-v1/
├── main3_gui.py          # File chính với GUI
├── actions/              # Các hành động tự động
├── components/           # Các component UI
├── utils/                # Utilities (ADB, Image processing)
├── images/               # Hình ảnh template
├── adb_tools/            # ADB Platform Tools
├── requirements.txt      # Dependencies
├── build.py             # Script build tự động
└── download_adb.py      # Script tải ADB
`

## 🔧 Troubleshooting

### Lỗi không tìm thấy MEmu
- Đảm bảo MEmu đang chạy
- Kiểm tra ADB connection: db devices
- Restart MEmu nếu cần

### Lỗi không tìm thấy button
- Kiểm tra độ phân giải màn hình
- Cập nhật template images nếu cần
- Đảm bảo game đang ở đúng màn hình

### Lỗi ADB
- Ứng dụng đã tích hợp sẵn ADB
- Nếu vẫn lỗi, thử cài ADB system-wide

## 📝 Changelog
- v1.0: Phiên bản đầu tiên với GUI
- v1.1: Tích hợp ADB, hỗ trợ multi-device
- v1.2: Tối ưu hóa build process

## 👨‍💻 Tác giả
TungNC

## 📄 License
MIT License
