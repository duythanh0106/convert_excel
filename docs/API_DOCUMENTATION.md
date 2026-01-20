# API Documentation - Universal File Converter v3.0.0

> Ứng dụng chuyển đổi file toàn năng hỗ trợ 30+ định dạng file

## 📋 Mục Lục

- [Tổng Quan](#tổng-quan)
- [API v1 - Excel Converter](#api-v1---excel-converter)
- [API v2 - Universal Converter](#api-v2---universal-converter)
- [Authentication](#authentication)
- [Error Handling](#error-handling)
- [Examples](#examples)

---

## Tổng Quan

### Base URL
```
http://localhost:8080
```

### API Versions
- **v1**: Excel to DOCX/Markdown chuyên biệt
- **v2**: Universal converter cho 30+ file types

---

## API v1 - Excel Converter

### 1. Upload File
```
POST /upload
Content-Type: multipart/form-data

Parameters:
- file: (binary) File Excel (.xlsx)

Response:
{
  "success": true,
  "message": "Upload thành công",
  "filename": "data_20260120_153045.xlsx",
  "size": 12345,
  "timestamp": "2026-01-20T15:30:45"
}
```

### 2. Lấy Danh Sách Sheet
```
POST /api/v1/sheets
Content-Type: application/json

Body:
{
  "filename": "data_20260120_153045.xlsx"
}

Response:
{
  "success": true,
  "sheets": ["Sheet1", "Sheet2", "Summary"],
  "default_sheet": "Sheet1"
}
```

### 3. Xem Trước Dữ Liệu
```
POST /api/v1/preview
Content-Type: application/json

Body:
{
  "filename": "data_20260120_153045.xlsx",
  "sheet": "Sheet1",
  "num_rows": 10
}

Response:
{
  "success": true,
  "preview": [
    ["Tên", "Email", "Phòng"],
    ["Nguyễn Văn A", "a@company.com", "IT"],
    ...
  ],
  "total_rows": 100,
  "total_cols": 3,
  "display_rows": 10
}
```

### 4. Lấy Danh Sách Cột
```
POST /api/v1/columns
Content-Type: application/json

Body:
{
  "filename": "data_20260120_153045.xlsx",
  "sheet": "Sheet1",
  "header_row": 1
}

Response:
{
  "success": true,
  "columns": [
    {"index": 1, "name": "Tên"},
    {"index": 2, "name": "Email"},
    {"index": 3, "name": "Phòng"}
  ]
}
```

### 5. Convert Excel to DOCX
```
POST /api/v1/convert/docx
Content-Type: application/json

Body:
{
  "filename": "data_20260120_153045.xlsx",
  "sheet": "Sheet1",
  "columns": ["Tên", "Email", "Phòng"],
  "header_row": 1,
  "data_start_row": 2,
  "output_format": "docx",
  "custom_title": "Danh Sách Nhân Viên"
}

Response:
{
  "success": true,
  "message": "Convert thành công",
  "output_filename": "data_20260120_153045.docx",
  "file_size": 45678,
  "download_url": "/download/data_20260120_153045.docx"
}
```

### 6. Convert Excel to Markdown Table
```
POST /api/v1/convert/markdown
Content-Type: application/json

Body:
{
  "filename": "data_20260120_153045.xlsx",
  "sheet": "Sheet1",
  "columns": ["Tên", "Email", "Phòng"],
  "header_row": 1,
  "data_start_row": 2
}

Response:
{
  "success": true,
  "markdown_content": "| Tên | Email | Phòng |\n|---|---|---|\n...",
  "file_saved": "output_markdown_1234567890.md",
  "download_url": "/download/output_markdown_1234567890.md"
}
```

---

## API v2 - Universal Converter

### 1. Lấy Danh Sách Định Dạng Hỗ Trợ
```
GET /api/v2/formats

Response:
{
  "supported_extensions": [
    ".csv", ".docx", ".epub", ".gif", ".html", ".ipynb", 
    ".jpg", ".json", ".md", ".pdf", ".png", ".pptx", 
    ".py", ".r", ".rmd", ".txt", ".xlsx", ...
  ],
  "supported_formats": {
    ".pdf": "Portable Document Format",
    ".docx": "Microsoft Word Document",
    ".xlsx": "Microsoft Excel Workbook",
    ...
  }
}
```

### 2. Detect File Type
```
POST /api/v2/detect
Content-Type: application/json

Body:
{
  "filename": "document.pdf"
}

Response:
{
  "success": true,
  "file": {
    "ext": ".pdf",
    "name": "document.pdf",
    "description": "Portable Document Format",
    "size": 1024000,
    "is_excel": false,
    "is_markitdown_supported": true
  },
  "available_conversions": ["markdown"]
}
```

### 3. Convert Bất Kỳ File Nào Sang Markdown
```
POST /api/v2/convert/markdown
Content-Type: application/json

Body:
{
  "filename": "presentation.pptx",
  "output_format": "markdown"
}

Response:
{
  "success": true,
  "markdown_content": "# Slide 1\n\nContent here...",
  "full_content_length": 5432,
  "file_saved": "presentation_converted_1234567890.md",
  "download_url": "/download/presentation_converted_1234567890.md"
}
```

### 4. Batch Convert Thư Mục
```
POST /api/v2/batch/convert
Content-Type: application/json

Body:
{
  "input_dir": "uploads",
  "extensions": [".pdf", ".docx", ".xlsx"]
}

Response:
{
  "success": true,
  "conversion_results": {
    "total": 10,
    "success": 9,
    "failed": 1,
    "files": [
      {
        "input": "file1.pdf",
        "output": "file1.md",
        "status": "success"
      },
      {
        "input": "file2.pdf",
        "output": null,
        "status": "failed",
        "error": "File quá lớn"
      }
    ]
  }
}
```

### 5. Lấy Thông Tin Universal Converter
```
GET /api/v2/info

Response:
{
  "name": "Universal File Converter",
  "version": "1.0.0",
  "description": "Convert nhiều loại file sang Markdown hoặc định dạng khác",
  "capabilities": {
    "documents": ["PDF", "DOCX", "TXT", "MD"],
    "spreadsheets": ["XLSX", "XLS", "CSV"],
    "presentations": ["PPTX", "PPT"],
    "images": ["PNG", "JPG", "GIF", "BMP", "WEBP", "SVG"],
    "code": ["IPYNB", "PY", "R", "RMD", "JS", "TS", "JAVA", "CPP"],
    "archives": ["MSG", "EPUB"]
  },
  "powered_by": "Markitdown"
}
```

---

## System Endpoints

### Health Check
```
GET /health

Response:
{
  "status": "healthy",
  "timestamp": "2026-01-20T15:30:45.123456",
  "version": "3.0.0"
}
```

### App Info
```
GET /info

Response:
{
  "app_name": "Universal File Converter",
  "version": "3.0.0",
  "framework": "FastAPI",
  "max_file_size": "100MB",
  "modules": {
    "excel_converter": {...},
    "universal_converter": {...}
  }
}
```

### Download File
```
GET /download/{filename}

Supported Content-Types:
- application/vnd.openxmlformats-officedocument.wordprocessingml.document (.docx)
- text/markdown (.md)
- application/octet-stream (others)
```

---

## Authentication

Nếu cấu hình OIDC (Google OAuth hoặc Keycloak):

```
GET /login                           # Trang login
GET /auth/login/google               # Login với Google
GET /auth/callback/google            # Google callback
GET /auth/login/keycloak             # Login với Keycloak
GET /auth/callback/keycloak          # Keycloak callback
GET /logout                          # Logout
```

---

## Error Handling

### HTTP Status Codes
- `200 OK`: Request thành công
- `400 Bad Request`: Input không hợp lệ
- `401 Unauthorized`: Chưa authenticate
- `404 Not Found`: Resource không tồn tại
- `413 Payload Too Large`: File quá lớn
- `500 Internal Server Error`: Server error

### Error Response Format
```json
{
  "detail": "Mô tả lỗi chi tiết",
  "error_code": "ERROR_CODE",
  "timestamp": "2026-01-20T15:30:45"
}
```

### Thường Gặp Errors
```
❌ "File không tồn tại"
   → Kiểm tra filename, file có được upload?

❌ "Định dạng không được hỗ trợ"
   → Xem danh sách ở /api/v2/formats

❌ "File quá lớn (tối đa 100MB)"
   → Giảm kích thước file

❌ "Sheet 'Sheet1' không tồn tại"
   → Xem danh sách sheets từ /api/v1/sheets

❌ "Cột không tìm thấy"
   → Kiểm tra tên cột từ /api/v1/columns
```

---

## Examples

### Example 1: Excel to DOCX Workflow
```bash
# 1. Upload file
curl -F "file=@data.xlsx" http://localhost:8080/upload

# 2. Lấy sheets
curl -X POST http://localhost:8080/api/v1/sheets \
  -H "Content-Type: application/json" \
  -d '{"filename": "data_20260120_153045.xlsx"}'

# 3. Preview data
curl -X POST http://localhost:8080/api/v1/preview \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "data_20260120_153045.xlsx",
    "sheet": "Sheet1",
    "num_rows": 10
  }'

# 4. Get columns
curl -X POST http://localhost:8080/api/v1/columns \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "data_20260120_153045.xlsx",
    "sheet": "Sheet1",
    "header_row": 1
  }'

# 5. Convert to DOCX
curl -X POST http://localhost:8080/api/v1/convert/docx \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "data_20260120_153045.xlsx",
    "sheet": "Sheet1",
    "columns": ["Tên", "Email", "Phòng"],
    "header_row": 1,
    "data_start_row": 2
  }'

# 6. Download file
curl -O http://localhost:8080/download/output.docx
```

### Example 2: Convert PDF to Markdown
```bash
# 1. Upload PDF
curl -F "file=@document.pdf" http://localhost:8080/upload

# 2. Detect file type
curl -X POST http://localhost:8080/api/v2/detect \
  -H "Content-Type: application/json" \
  -d '{"filename": "document_20260120_153045.pdf"}'

# 3. Convert to Markdown
curl -X POST http://localhost:8080/api/v2/convert/markdown \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "document_20260120_153045.pdf",
    "output_format": "markdown"
  }'

# 4. Download
curl -O http://localhost:8080/download/document_converted_1234567890.md
```

### Example 3: Batch Convert Directory
```bash
# Convert tất cả PDF files trong uploads folder
curl -X POST http://localhost:8080/api/v2/batch/convert \
  -H "Content-Type: application/json" \
  -d '{
    "input_dir": "uploads",
    "extensions": [".pdf"]
  }'
```

---

## Rate Limiting

Hiện tại không có rate limiting, nhưng sẽ được thêm vào production:
- Max 100 requests/minute/IP
- Max file size: 100MB
- Max concurrent uploads: 5

---

## Changelog

### v3.0.0 (Current)
- ✅ Tích hợp Markitdown Universal Converter
- ✅ Hỗ trợ 30+ loại file
- ✅ Batch conversion
- ✅ Vietnamese documentation

### v2.0.0
- ✅ Excel to DOCX converter
- ✅ Excel to Markdown table
- ✅ OIDC authentication

### v1.0.0
- ✅ Basic Excel converter

---

## Support

📧 Email: support@company.com
📚 Docs: http://localhost:8080/docs
🐛 Issues: GitHub Issues
💬 Discord: [Discord Server]
