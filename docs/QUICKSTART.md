# 🚀 Quick Start Guide - Universal File Converter

Hướng dẫn bắt đầu nhanh để sử dụng Universal File Converter.

---

## ⚡ 5 Phút Đầu Tiên

### 1. Cài Đặt
```bash
# Clone project
git clone https://github.com/yourcompany/convert-tool.git
cd convert_tool/convert_excel

# Virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
```

### 2. Chạy Server
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

### 3. Truy Cập Ứng Dụng
```
🌐 Web UI:        http://localhost:8080
📚 API Docs:      http://localhost:8080/docs
```

---

## 📊 Workflow 1: Excel → DOCX (5 bước)

### Bước 1: Upload Excel File
```bash
curl -F "file=@employees.xlsx" \
  http://localhost:8080/upload
```

📌 **Lưu ý**: Lấy `filename` từ response

### Bước 2: Xem Trước Dữ Liệu
```bash
curl -X POST http://localhost:8080/api/v1/preview \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "employees_20260120_153045.xlsx",
    "sheet": "Sheet1",
    "num_rows": 10
  }'
```

📌 Kiểm tra data có đúng không

### Bước 3: Lấy Danh Sách Cột
```bash
curl -X POST http://localhost:8080/api/v1/columns \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "employees_20260120_153045.xlsx",
    "sheet": "Sheet1",
    "header_row": 1
  }'
```

### Bước 4: Chọn Cột & Convert
```bash
curl -X POST http://localhost:8080/api/v1/convert/docx \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "employees_20260120_153045.xlsx",
    "sheet": "Sheet1",
    "columns": ["Tên", "Email", "Phòng"],
    "header_row": 1,
    "data_start_row": 2
  }'
```

### Bước 5: Download
```bash
curl -O http://localhost:8080/download/output_employees.docx
```

✅ **Done!** DOCX file đã sẵn sàng

---

## 🌍 Workflow 2: Bất Kỳ File → Markdown (3 bước)

### Bước 1: Upload File
```bash
curl -F "file=@presentation.pptx" \
  http://localhost:8080/upload
```

### Bước 2: Convert Sang Markdown
```bash
curl -X POST http://localhost:8080/api/v2/convert/markdown \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "presentation_20260120_153045.pptx"
  }'
```

### Bước 3: Download
```bash
curl -O http://localhost:8080/download/presentation_converted_1234567890.md
```

✅ **Done!** Markdown file ready

---

## 🎯 Các Loại File Có Thể Convert

### 📄 Documents
```
❌ PDF → ✅ Markdown
❌ DOCX → ✅ Markdown
❌ TXT → ✅ Markdown
```

### 📊 Spreadsheets
```
❌ Excel → ✅ DOCX (Excel Converter)
❌ Excel → ✅ Markdown (Universal Converter)
❌ CSV → ✅ Markdown
```

### 🎞️ Presentations
```
❌ PPTX → ✅ Markdown
❌ PPT → ✅ Markdown
```

### 🖼️ Images
```
❌ PNG, JPG, GIF → ✅ Markdown (with OCR)
❌ WEBP, SVG → ✅ Markdown
```

### 💻 Code & Notebooks
```
❌ IPYNB → ✅ Markdown
❌ PY, R, JS, TS, JAVA → ✅ Markdown
❌ RMD → ✅ Markdown
```

### 🌐 Web
```
❌ HTML → ✅ Markdown
❌ JSON, XML → ✅ Markdown
❌ RSS, EPUB → ✅ Markdown
```

---

## 🐳 Chạy Bằng Docker

### Docker Run
```bash
docker build -t convert-tool:3.0.0 .

docker run -p 8080:8080 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/outputs:/app/outputs \
  -e HOST=0.0.0.0 \
  -e PORT=8080 \
  convert-tool:3.0.0
```

### Docker Compose (Khuyến Nghị)
```bash
docker-compose up -d
```

---

## 📚 Các Endpoints Chính

### Excel Converter (API v1)
| Endpoint | Method | Mô Tả |
|----------|--------|-------|
| `/upload` | POST | Tải Excel file |
| `/api/v1/sheets` | POST | Lấy sheet names |
| `/api/v1/preview` | POST | Xem trước dữ liệu |
| `/api/v1/columns` | POST | Lấy column names |
| `/api/v1/convert/docx` | POST | Convert → DOCX |
| `/api/v1/convert/markdown` | POST | Convert → Markdown |

### Universal Converter (API v2)
| Endpoint | Method | Mô Tả |
|----------|--------|-------|
| `/api/v2/formats` | GET | Danh sách formats |
| `/api/v2/detect` | POST | Detect file type |
| `/api/v2/convert/markdown` | POST | Convert → Markdown |
| `/api/v2/batch/convert` | POST | Batch conversion |
| `/api/v2/info` | GET | Thông tin converter |

### System
| Endpoint | Method | Mô Tả |
|----------|--------|-------|
| `/health` | GET | Health check |
| `/info` | GET | App info |
| `/download/{filename}` | GET | Download file |

---

## 🔧 Cấu Hình Cơ Bản

### .env File
```dotenv
# Server
HOST=0.0.0.0
PORT=8080
FASTAPI_ENV=production

# Security (Generate: python -c "import secrets; print(secrets.token_urlsafe(32))")
SECRET_KEY=your-secret-key-here

# File Settings
UPLOAD_FOLDER=uploads
OUTPUT_FOLDER=outputs
MAX_FILE_SIZE=104857600  # 100MB

# Cleanup (Auto delete old files)
CLEANUP_HOURS=24
CLEANUP_INTERVAL=3600

# Timezone
TZ=Asia/Ho_Chi_Minh
```

---

## 🆘 Troubleshooting

### ❌ "ModuleNotFoundError: No module named 'markitdown'"
```bash
pip install markitdown==0.1.5b1
```

### ❌ "Port 8080 already in use"
```bash
# Sử dụng port khác
uvicorn main:app --port 8081
```

### ❌ "File quá lớn"
```bash
# Tăng MAX_FILE_SIZE trong .env
MAX_FILE_SIZE=209715200  # 200MB
```

### ❌ "Permission denied" (uploads/outputs folder)
```bash
chmod 755 uploads outputs
```

---

## 📊 Performance Tips

1. **Large Files**: Sử dụng Docker với resource limits
   ```bash
   docker run --memory=4g --cpus=2 ...
   ```

2. **Batch Processing**: Sử dụng `/api/v2/batch/convert`

3. **Cleanup**: Set `CLEANUP_HOURS=24` để xóa file cũ tự động

4. **Monitoring**: Kiểm tra `/health` endpoint

---

## 🚀 Production Deployment

### Checklist
- [ ] Update `SECRET_KEY` trong .env
- [ ] Set `FASTAPI_ENV=production`
- [ ] Cấu hình CORS origins
- [ ] Setup backup cho uploads/outputs
- [ ] Enable logging
- [ ] Setup monitoring
- [ ] Configure reverse proxy (Nginx/Apache)

### Nginx Config Example
```nginx
server {
    listen 80;
    server_name convert.company.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Increase upload size limit
    client_max_body_size 100M;
}
```

---

## 📞 Support & Resources

- 📚 **Full Documentation**: [README.md](README.md)
- 📖 **API Docs**: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- 📋 **Changelog**: [CHANGELOG.md](CHANGELOG.md)
- 🐛 **Issues**: GitHub Issues
- 💬 **Discussions**: GitHub Discussions

---

## ✅ Checklist Trước Khi Push

```bash
# 1. Kiểm tra lỗi
python -m py_compile main.py universal_converter.py

# 2. Test APIs
curl http://localhost:8080/health
curl http://localhost:8080/info

# 3. Docker test
docker build -t convert-tool:test .
docker run -p 8081:8080 convert-tool:test

# 4. Commit
git add .
git commit -m "feat: add universal file converter with markitdown integration"

# 5. Tag & Push
git tag -a v3.0.0 -m "Release Universal File Converter v3.0.0"
git push origin main --tags
```

---

Happy Converting! 🎉
