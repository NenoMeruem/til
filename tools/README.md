# Google Drive Sync Tool for Obsidian Vault

Công cụ này giúp đồng bộ hóa toàn bộ tài liệu từ Obsidian Vault lên Google Drive, tự động di chuyển toàn bộ hình ảnh đính kèm cục bộ lên thư mục lưu trữ (`backup/`) trên Google Drive và thay đổi liên kết trong file markdown thành các liên kết trực tiếp (direct GDrive CDN links).

## Tính năng
* **Tối ưu dung lượng Git**: Loại bỏ ảnh đính kèm cục bộ sau khi đã đồng bộ lên đám mây thành công.
* **Đồng bộ toàn bộ dự án**: Mirror toàn bộ cấu trúc thư mục tài liệu từ cục bộ lên Google Drive.
* **Hỗ trợ OAuth 2.0 & Service Account**: Tương thích hoàn hảo với tài khoản Google cá nhân (không bị giới hạn dung lượng 0 GB của Service Account).
* **An toàn dữ liệu**: Tự động xác thực các liên kết ảnh hoạt động tốt trên Drive trước khi thực hiện xóa file gốc.

---

## Hướng dẫn cài đặt

### 1. Cài đặt thư viện
Yêu cầu Python 3.8 trở lên. Nên cài đặt thông qua môi trường ảo:

```bash
# Tạo môi trường ảo
python3 -m venv .venv

# Kích hoạt môi trường ảo (macOS/Linux)
source .venv/bin/activate

# Cài đặt các thư viện cần thiết
pip install -r requirements.txt
```

### 2. Cấu hình file `.env`
Tạo file `.env` ở thư mục gốc của dự án (sử dụng `.env.example` làm mẫu):
```env
# ID thư mục gốc của dự án trên Google Drive
GDRIVE_FOLDER_ID=your_gdrive_folder_id

# Đường dẫn đến file client secret JSON (tải từ Google Cloud Console)
GDRIVE_SERVICE_ACCOUNT_KEY=tools/credentials.json

# Đường dẫn lưu trữ Token xác thực sau khi đăng nhập (chỉ dùng cho OAuth)
GDRIVE_TOKEN_PATH=token.json

# Thư mục tài liệu cần quét liên kết ảnh
DOCS_DIR=courses/Claude Code in Action

# Thư mục ảnh cần quét đồng bộ và giải phóng dung lượng
IMAGES_DIR=courses/Claude Code in Action/images
```

---

## Hướng dẫn sử dụng

### 1. Chạy thử nghiệm (Dry-run)
Chế độ chạy thử nghiệm giúp quét dự án, in ra các file ảnh sẽ được đồng bộ và thay đổi mô phỏng mà không làm ảnh hưởng tới dữ liệu thực tế:
```bash
python tools/gdrive_sync.py --dry-run
```

### 2. Chạy đồng bộ thực tế (Manual local run)
Khi chạy lần đầu dưới quyền tài khoản cá nhân, một tab trình duyệt sẽ tự động mở ra yêu cầu đăng nhập và cấp quyền Google Drive. Sau khi hoàn tất, file `token.json` sẽ tự động sinh ra và bạn không cần thực hiện đăng nhập lại vào lần sau.
```bash
python tools/gdrive_sync.py
```

---

## Tích hợp CI/CD (GitHub Actions)

Workflow đã được tạo sẵn tại `.github/workflows/gdrive-sync.yml`. Để chạy tự động:
1. Đăng nhập và xác thực lần đầu trên máy cục bộ để lấy file `token.json`.
2. Truy cập Settings của GitHub Repository > **Secrets and variables > Actions**.
3. Thêm 2 Secrets:
   * **`GDRIVE_SERVICE_ACCOUNT_KEY`**: Nội dung file `credentials.json` (OAuth Client Secrets).
   * **`GDRIVE_TOKEN_JSON`**: Nội dung file `token.json` đã sinh ra sau khi chạy cục bộ.
   * **`GDRIVE_FOLDER_ID`**: ID thư mục Google Drive.
4. Chạy thủ công từ tab **Actions** bất kỳ lúc nào bằng cách chọn workflow và nhập đường dẫn thư mục tài liệu/hình ảnh cần đồng bộ.
