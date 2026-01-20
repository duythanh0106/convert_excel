# Changelog

Tất cả các thay đổi đáng chú ý của dự án này sẽ được tài liệu trong file này.

Format dựa trên [Keep a Changelog](https://keepachangelog.com/vi-VN/).

---

## [3.0.0] - 2026-01-20

### 🎉 Thêm
- ✨ **Universal File Converter** - Module mới tích hợp Markitdown
  - Hỗ trợ 30+ loại file (PDF, DOCX, PPTX, Images, Code, Notebooks, etc.)
  - Convert bất kỳ file nào sang Markdown format
  - Batch conversion (chuyển đổi hàng loạt)
  - File type detection tự động
  
- 🆕 **API v2** - Bộ endpoints mới cho Universal Converter
  - `GET /api/v2/formats` - Lấy danh sách định dạng hỗ trợ
  - `POST /api/v2/detect` - Detect loại file
  - `POST /api/v2/convert/markdown` - Convert file sang Markdown
  - `POST /api/v2/batch/convert` - Batch conversion
  - `GET /api/v2/info` - Thông tin Universal Converter

- 📚 **Tài Liệu Mới**
  - API_DOCUMENTATION.md - Tài liệu API chi tiết (150+ dòng)
  - Universal converter examples và use cases
  - Supported formats documentation

- 🔧 **Cấu Hình**
  - Cập nhật requirements.txt: thêm markitdown==0.1.5b1
  - Tích hợp với main.py imports

- 🎨 **Giao Diện Cải Tiến**
  - Startup message hiển thị tất cả modules
  - Danh sách supported formats rõ ràng

### 📝 Thay Đổi
- 📋 **README.md** - Rewrite toàn bộ tài liệu tiếng Việt
  - Đổi tiêu đề từ "Excel to DOCX Converter" → "Universal File Converter"
  - Cập nhật mô tả các tính năng mới
  - Thêm mermaid diagrams cho kiến trúc
  - Thêm supported formats list

- ⚙️ **main.py** - Cập nhật FastAPI app
  - Imports thêm universal_converter modules
  - Thêm 5 endpoints v2 mới
  - Cập nhật app.get('/info') để bao gồm modules mới
  - Cập nhật startup event message

- 🔐 **Version Bump**
  - Cập nhật version: 2.0.0 → 3.0.0
  - App name: "Excel to DOCX Converter" → "Universal File Converter"

### 🔄 Refactor
- ❌ Không có refactor lớn (backward compatible)

### 🐛 Sửa Lỗi
- ❌ Không có lỗi sửa

### 🚀 Hiệu Suất
- ❌ Không có thay đổi hiệu suất

### 🔒 Bảo Mật
- ✅ Universal converter validate file size và extension

### 🧪 Tests
- ❌ Chưa có unit tests (sẽ thêm vào v3.1.0)

---

## [2.0.0] - 2025-12-15

### 🎉 Thêm
- ✨ Excel to DOCX converter chính
- 🔐 OIDC authentication (Google OAuth, Keycloak)
- 📄 Excel to Markdown table conversion
- 🐳 Docker support
- 📚 Comprehensive README documentation

### 📝 Thay Đổi
- Cập nhật UI/UX
- Tối ưu hóa Excel processing

### 🐛 Sửa Lỗi
- Fix: Column detection cho merged cells
- Fix: Large file handling

---

## [1.0.0] - 2025-11-01

### 🎉 Thêm
- ✨ Initial release - Basic Excel converter
- 📤 File upload functionality
- 👁️ Data preview
- 🔄 Basic Excel to DOCX conversion

---

## 🔮 Lộ Trình Tương Lai (Roadmap)

### v3.1.0 (Tháng 2 - 2026)
- [ ] Unit tests cho universal converter
- [ ] Integration tests
- [ ] Performance optimization
- [ ] Support cho cloud storage (S3, GCS, Azure Blob)

### v3.2.0 (Tháng 3 - 2026)
- [ ] Web UI improvements
- [ ] Dark mode support
- [ ] Drag-and-drop upload
- [ ] File size visualization

### v4.0.0 (Tháng 6 - 2026)
- [ ] Microservices architecture
- [ ] Message queue (Celery + Redis)
- [ ] Async job processing
- [ ] Database support (PostgreSQL)
- [ ] API versioning improvements

---

## 📞 Support

Nếu bạn tìm thấy vấn đề hoặc có đề xuất:
- 🐛 [GitHub Issues](https://github.com/yourrepo/convert-tool/issues)
- 💬 [Discussions](https://github.com/yourrepo/convert-tool/discussions)
- 📧 support@company.com

---

## 📄 Quy Ước

- `[ADDED]` cho tính năng mới
- `[CHANGED]` cho thay đổi trong chức năng hiện tại
- `[DEPRECATED]` cho tính năng sẽ bị xóa
- `[REMOVED]` cho tính năng đã xóa
- `[FIXED]` cho sửa lỗi
- `[SECURITY]` cho cập nhật bảo mật

---

## Phiên Bản Hiện Tại

**Latest**: [3.0.0]
**Released**: 2026-01-20
