# 📋 UrBox Guideline Template System

Hệ thống template theo guideline UrBox để tối ưu hóa AI KB processing.

---

## 🎯 Mục Đích

Chuyển đổi các file (Excel, PDF, Word, etc.) sang **Markdown format được optimize cho AI** theo guideline UrBox:
- ✅ **In đậm** Actors, Actions, Objects
- ✅ **Quote** Identifiers, ID, File names
- ✅ **Cấu trúc 5 phần** (A-B-C-D-E) cho mỗi loại tài liệu
- ✅ Chuyển bảng thành danh sách
- ✅ Support custom templates với biến

---

## 📊 Cấu Trúc Template (5 Phần)

### Cho File Excel/CSV:
```
A. Tài Liệu Gốc      → Link nguồn
B. Summary Overview  → Tóm tắt 3-5 dòng
C. Key Metrics       → Thống kê quan trọng
D. Insights          → Nhận xét, điểm đặc biệt
E. Structured Output → Dữ liệu chi tiết (key: value)
```

### Cho File Word/Document:
```
A. Tài Liệu Gốc      → Link nguồn
B. Summary Overview  → Tóm tắt mục đích
C. Key Points        → 5-10 điểm chính
D. Deep Summary      → Phân tích chi tiết
E. Readability Opt.  → Nội dung gốc được trình bày lại
```

### Cho Quy Trình/SOP:
```
A. Tài Liệu Gốc      → Link nguồn
B. Summary Overview  → Tóm tắt quy trình
C. Key Points        → Điểm quan trọng
D. Process Steps     → Từng bước chi tiết
E. Readiness Opt.    → Nội dung gốc
```

---

## 🔧 Modules

### 1. `markdown_formatter.py`
Format văn bản theo guideline:

```python
from markdown_formatter import MarkdownFormatter

formatter = MarkdownFormatter()

# Format text
text = "Nhân sự gửi Offer Letter cho ứng viên"
formatted = formatter.format_text(text)
# Output: **Nhân sự** gửi **Offer Letter** cho ứng viên

# Extract entities
entities = formatter.extract_entities(text)
# Output: {'actors': ['Nhân sự'], 'objects': ['Offer Letter'], ...}

# Convert table to list
table_data = [
    {'Tên': 'A', 'Email': 'a@example.com'},
    {'Tên': 'B', 'Email': 'b@example.com'}
]
list_format = formatter.format_table_to_list(table_data)
```

### 2. `template_processor.py`
Xây dựng template và inject biến:

```python
from template_processor import (
    TemplateBuilder,
    TemplateType,
    TemplateVariableInjector,
    PredefinedTemplates
)

# Option 1: Dùng TemplateBuilder
builder = TemplateBuilder(TemplateType.EXCEL_LIST)
result = (builder
    .set_source("https://docs.google.com/...")
    .set_summary("Tài liệu này là...")
    .set_metrics({"Tổng số": "100"})
    .set_insights("Nhận xét...")
    .set_content("Dữ liệu chi tiết...")
    .build()
)

# Option 2: Dùng custom template + injector
template = """
# <TITLE>
<CONTENT>
"""

injector = TemplateVariableInjector()
result = injector.inject(template, {
    'TITLE': 'Tiêu đề',
    'CONTENT': 'Nội dung'
})
```

### 3. `universal_converter.py`
Convert file với guideline:

```python
from universal_converter import UniversalConverter
from template_processor import TemplateType

converter = UniversalConverter()

# Convert with guideline
result = converter.convert_with_guideline(
    file_path='document.pdf',
    template_type=TemplateType.WORD_DOCUMENT,
    template_data={
        'source_url': 'https://...',
        'summary': 'Tóm tắt...',
        'key_points': ['Point 1', 'Point 2']
    },
    output_path='output.md'
)

# Convert with custom template
result = converter.convert_with_custom_template(
    file_path='data.xlsx',
    template='# <TITLE>\n<MAIN_CONTENT>',
    variables={'TITLE': 'My Data'},
    output_path='output.md'
)
```

---

## 🌐 API Endpoints (v2)

### 1. Convert with Guideline
```http
POST /api/v2/convert/guideline
Content-Type: application/json

{
  "filename": "document.pdf",
  "template_type": "word_document",
  "source_url": "https://...",
  "summary": "Tóm tắt tài liệu...",
  "key_points": ["Point 1", "Point 2"],
  "insights": "Nhận xét...",
  "deep_summary": "Chi tiết..."
}
```

### 2. Convert with Custom Template
```http
POST /api/v2/convert/custom-template
Content-Type: application/json

{
  "filename": "file.pdf",
  "template": "# <TITLE>\n\n<CONTENT>",
  "variables": {
    "TITLE": "Tiêu đề tài liệu"
  }
}
```

### 3. Get Predefined Templates
```http
GET /api/v2/templates
```

### 4. Format Text
```http
POST /api/v2/format/text
Content-Type: application/json

{
  "text": "Nhân sự gửi Offer Letter..."
}
```

### 5. Format Table to List
```http
POST /api/v2/format/table
Content-Type: application/json

{
  "table_data": [
    {"Tên": "A", "Email": "a@example.com"},
    {"Tên": "B", "Email": "b@example.com"}
  ]
}
```

---

## 💡 Ví Dụ Sử Dụng

### Example 1: Format Text
```bash
curl -X POST http://localhost:8080/api/v2/format/text \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Kế toán phê duyệt hợp đồng số HĐ_2025_001"
  }'

# Response:
# Formatted: **Kế toán** **phê duyệt** **hợp đồng** số > HĐ_2025_001
# Entities: 
#   actors: ['Kế toán']
#   actions: ['phê duyệt']
#   objects: ['hợp đồng']
#   identifiers: ['HĐ_2025_001']
```

### Example 2: Convert Excel with Guideline
```bash
# 1. Upload file
curl -F "file=@data.xlsx" http://localhost:8080/upload

# 2. Convert with guideline
curl -X POST http://localhost:8080/api/v2/convert/guideline \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "data_20250120_153045.xlsx",
    "template_type": "excel_list",
    "source_url": "https://docs.google.com/spreadsheets/...",
    "summary": "Danh sách Merchant E-voucher phân loại theo nhóm ngành hàng",
    "insights": "Có 3 merchant chưa cập nhật thông tin"
  }'

# 3. Download
curl -O http://localhost:8080/download/data_guideline_1234567890.md
```

### Example 3: Custom Template
```bash
# 1. Upload
curl -F "file=@document.pdf" http://localhost:8080/upload

# 2. Lấy template mẫu
curl http://localhost:8080/api/v2/templates

# 3. Convert with custom template
curl -X POST http://localhost:8080/api/v2/convert/custom-template \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "document_20250120_153045.pdf",
    "template": "# <TITLE>\n\n**Ngày:** <DATE>\n\n<MAIN_CONTENT>",
    "variables": {
      "TITLE": "Báo Cáo Tháng 1/2025",
      "DATE": "2025-01-20"
    }
  }'
```

---

## 🎨 Guideline Rules

### Actors (In Đậm)
**Người thực hiện hành động:**
- Phòng ban: Kế toán, Nhân sự, IT, Partnership
- Chức danh: Manager, Team Lead, Director
- Đối tượng: Ứng viên, Khách hàng, Hệ thống AI

### Actions (In Đậm)
**Hành động, trạng thái:**
- Phê duyệt, Duyệt, Từ chối, Xác nhận
- Gửi, Nhận, Kiểm tra, Hoàn thành
- Đã hoàn thành, Đang treo, Chấp nhận

### Objects (In Đậm)
**Tài liệu, công cụ:**
- Hợp đồng, Biểu mẫu, Báo cáo
- Nút, Màn hình, File
- Offer Letter, Email

### Identifiers (Quote)
**Mã, ID, File names:**
- Mã nhân viên: EMP_001
- Mã hợp đồng: HĐ_2025_001
- Email: contact@company.com
- URL: https://example.com
- File path: /uploads/data.xlsx

### Variables (Template)
**Biến cần điền:**
- Format: `<VARIABLE_NAME>`
- Ví dụ: `<SỐ_HỢP_ĐỒNG>`, `<NGÀY_KÝ>`, `<TÊN_NGƯỜI_DÙNG>`

---

## 📝 Output Examples

### Input (Excel):
```
| Merchant | Email | Status |
|----------|-------|--------|
| Starbucks | sb@example.com | Active |
| McDonald's | mc@example.com | Inactive |
```

### Output (Guideline):
```markdown
## E. Structured Output

Tên Merchant: Starbucks
Email: sb@example.com
Trạng thái: **Active**

---

Tên Merchant: McDonald's
Email: mc@example.com
Trạng thái: Inactive
```

---

## 🚀 Next Steps

1. **Test với file thực:**
   - Quăng Excel, PDF, Word lên
   - Xem output được format thế nào

2. **Customize:**
   - Điều chỉnh ACTORS, ACTIONS, OBJECTS list
   - Thêm patterns riêng cho company

3. **Integration:**
   - Tích hợp vào Knowledge Base system
   - Sử dụng output cho RAG pipeline

---

## 📚 File References

- `markdown_formatter.py` - 330 lines, phần chính format logic
- `template_processor.py` - 280 lines, xây dựng template
- `universal_converter.py` - Cập nhật với 2 method mới
- `main.py` - Thêm 6 endpoints v2 mới
- `guideline_examples.py` - 350+ dòng ví dụ

---

## 💬 Support

Các câu hỏi hoặc vấn đề? Xem:
- `/api/v2/templates` - Các template mẫu
- `/api/v2/formats` - Các format hỗ trợ
- `/api/v2/info` - Thông tin chi tiết
- Swagger UI: http://localhost:8080/docs
