"""
Guideline Template Processor - Usage Examples
Ví dụ cách sử dụng template processor theo UrBox Guideline
"""

from markdown_formatter import MarkdownFormatter, bold, quote, variable, create_step
from template_processor import (
    TemplateBuilder, 
    TemplateType, 
    GuidelineTemplate,
    TemplateVariableInjector,
    PredefinedTemplates
)
from universal_converter import UniversalConverter


# ===== EXAMPLE 1: Format text theo Guideline =====
def example_1_format_text():
    """Format văn bản theo guideline UrBox"""
    print("=" * 60)
    print("EXAMPLE 1: Format Text Theo Guideline")
    print("=" * 60)
    
    formatter = MarkdownFormatter()
    
    # Văn bản gốc
    original_text = """
    Sau khi Nhân sự gửi Offer Letter, ứng viên phải bấm Xác nhận trong 24h.
    Nếu không xác nhận, hệ thống AI sẽ gửi nhắc nhở.
    Mã ứng viên: HR_APP_2025_001.
    Email: candidate@example.com
    """
    
    # Format theo guideline
    formatted = formatter.format_text(original_text)
    
    print("\n📝 ORIGINAL TEXT:")
    print(original_text)
    
    print("\n✅ FORMATTED TEXT (Theo Guideline):")
    print(formatted)
    
    print("\n📊 EXTRACTED ENTITIES:")
    entities = formatter.extract_entities(original_text)
    for entity_type, values in entities.items():
        if values:
            print(f"  {entity_type}: {values}")


# ===== EXAMPLE 2: Build Excel Template =====
def example_2_excel_template():
    """Xây dựng template cho file Excel/CSV"""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Excel Template")
    print("=" * 60)
    
    builder = TemplateBuilder(TemplateType.EXCEL_LIST)
    
    result = (builder
        .set_source("https://docs.google.com/spreadsheets/...")
        .set_summary(
            "Tài liệu này cung cấp danh sách các Merchant E-voucher, "
            "phân loại theo nhóm ngành hàng để hiển thị trên App UrBox."
        )
        .set_metrics({
            "Tổng số dòng": "50 merchants",
            "Tổng loại ngành": "12 categories",
            "Merchant hoạt động": "45 merchants",
            "Merchant ngừng": "5 merchants"
        })
        .set_insights(
            "Có 3 Merchant chưa cập nhật thông tin trong 30 ngày. "
            "Cần kiểm tra và gửi yêu cầu cập nhật."
        )
        .set_content(
            """Tên Merchant: Starbucks Vietnam
Email: contact@starbucks.vn
Số điện thoại: 0912345678
Nhóm ngành: Thức uống & Cafe
Trạng thái: Hoạt động

---

Tên Merchant: Pizza Hut Vietnam
Email: partner@pizzahut.vn
Số điện thoại: 0987654321
Nhóm ngành: Thức ăn nhanh
Trạng thái: Hoạt động"""
        )
        .build()
    )
    
    print("\n📄 GENERATED TEMPLATE:")
    print(result)


# ===== EXAMPLE 3: Build Document Template =====
def example_3_document_template():
    """Xây dựng template cho file Word/Document"""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Document Template")
    print("=" * 60)
    
    builder = TemplateBuilder(TemplateType.WORD_DOCUMENT)
    
    result = (builder
        .set_source("https://docs.google.com/document/...")
        .set_summary(
            "Chính sách này quy định các quyền lợi, phúc lợi và chế độ "
            "lương thưởng cho toàn bộ nhân viên của công ty UrBox, "
            "hiệu lực từ ngày 01/01/2025."
        )
        .set_key_points([
            "Lương cơ bản: Từ 8 triệu đến 20 triệu/tháng tùy vị trí",
            "Thưởng hiệu quả: Từ 5% đến 20% lương cơ bản",
            "BHXH: Công ty đóng 18.5%, nhân viên đóng 10.5%",
            "Phép năm: 12 ngày/năm + 3 ngày không lý do",
            "Chế độ OT: Tối đa 40 giờ/tháng, trả công gấp 1.5 lần"
        ])
        .set_deep_summary(
            """**Bối cảnh:**
Chính sách này được ban hành nhằm đảm bảo sự công bằng, minh bạch 
và nhất quán trong quản lý nhân sự tại UrBox.

**Phạm vi áp dụng:**
Toàn bộ nhân viên chính thức (Full-time) và thử việc (Probation) của công ty.

**Các con số quan trọng:**
- Mức lương tối thiểu: 8,000,000 VND
- Tỷ lệ BHXH: 18.5% (công ty) + 10.5% (nhân viên) = 29%
- Phép năm tối thiểu: 12 ngày
- OT tối đa: 40 giờ/tháng"""
        )
        .set_content(
            """## I. LƯƠNG VÀ THƯỞNG

### 1. Lương cơ bản

**Lương cơ bản** được xác định dựa trên vị trí công việc, 
kinh nghiệm và năng lực của nhân viên.

Mức lương:
- Junior: 8-10 triệu
- Senior: 12-15 triệu  
- Lead: 15-18 triệu
- Manager: 18-20 triệu

### 2. Thưởng Hiệu Quả Làm Việc (THQLVT)

Tính toán: **THQLVT = Lương cơ bản × Tỷ lệ thưởng**

Tỷ lệ thưởng:
- Đạt yêu cầu: 5-10%
- Vượt yêu cầu: 10-15%
- Xuất sắc: 15-20%"""
        )
        .build()
    )
    
    print("\n📄 GENERATED DOCUMENT TEMPLATE:")
    print(result[:500] + "...\n(Hiển thị 500 ký tự đầu)")


# ===== EXAMPLE 4: Process/SOP Template =====
def example_4_process_template():
    """Xây dựng template cho quy trình/SOP"""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Process Template")
    print("=" * 60)
    
    builder = TemplateBuilder(TemplateType.PROCESS)
    
    result = (builder
        .set_source("https://docs.google.com/document/...")
        .set_summary("Quy trình đăng ký nhân viên mới (Onboarding)")
        .set_key_points([
            "Kéo dài từ 7-10 ngày",
            "Phòng Nhân sự chịu trách nhiệm điều phối",
            "Cần hoàn thành training văn hóa công ty",
            "Ký hợp đồng lao động bắt buộc"
        ])
        .set_steps([
            {
                'step': 1,
                'content': 'Nhân sự **Lập hồ sơ** nhân viên mới trong hệ thống',
                'sub_items': [
                    'Tạo email công ty',
                    'Cấp tài khoản truy cập hệ thống',
                    'Chuẩn bị workspace'
                ]
            },
            {
                'step': 2,
                'content': 'Nhân sự **Gửi Offer Letter** cho ứng viên',
                'sub_items': [
                    'Chờ ứng viên **Xác nhận** trong 24h',
                    'Nếu không xác nhận: Gửi nhắc nhở sau 12h'
                ]
            },
            {
                'step': 3,
                'content': 'Nhân sự **Ký hợp đồng** lao động',
                'sub_items': [
                    'Chuẩn bị 2 bản hợp đồng',
                    'Chuẩn bị các văn bản khác: BHXH, BHYT, BHTN',
                    'Ký trực tiếp hoặc gửi điện tử'
                ]
            }
        ])
        .build()
    )
    
    print("\n📄 GENERATED PROCESS TEMPLATE:")
    print(result[:600] + "...\n(Hiển thị 600 ký tự đầu)")


# ===== EXAMPLE 5: Custom Template with Variables =====
def example_5_custom_template():
    """Sử dụng custom template với biến"""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Custom Template with Variables")
    print("=" * 60)
    
    # Custom template
    custom_template = """
# <TITLE>

**Ngày ban hành:** <ISSUE_DATE>
**Người soạn:** <AUTHOR_NAME>
**Phòng ban:** <DEPARTMENT>

---

## Mô tả

<SUMMARY>

---

## Chi tiết

<MAIN_CONTENT>

---

## Liên hệ

Email: <CONTACT_EMAIL>
SĐT: <CONTACT_PHONE>
"""
    
    # Biến để inject
    variables = {
        'TITLE': 'Chính sách Làm Việc Từ Xa',
        'ISSUE_DATE': '2025-01-20',
        'AUTHOR_NAME': 'Phòng Nhân Sự',
        'DEPARTMENT': 'HR',
        'SUMMARY': 'Quy định cho phép nhân viên làm việc từ xa tối đa 3 ngày/tuần',
        'CONTACT_EMAIL': 'hr@urbox.vn',
        'CONTACT_PHONE': '02812345678'
    }
    
    injector = TemplateVariableInjector()
    
    result = injector.inject(custom_template, variables)
    
    print("\n🎯 CUSTOM TEMPLATE:")
    print(custom_template)
    
    print("\n✅ AFTER VARIABLE INJECTION:")
    print(result)


# ===== EXAMPLE 6: Format Table to List =====
def example_6_format_table():
    """Convert bảng thành danh sách"""
    print("\n" + "=" * 60)
    print("EXAMPLE 6: Format Table to List")
    print("=" * 60)
    
    # Dữ liệu bảng
    table_data = [
        {
            'Họ và tên': 'Nguyễn Đức Ninh',
            'Email': 'ninh.nd@urbox.vn',
            'SĐT': '0906009618',
            'Vị trí': 'Product Manager'
        },
        {
            'Họ và tên': 'Trương Hải Nam',
            'Email': 'nam.th@urbox.vn',
            'SĐT': '0934445619',
            'Vị trí': 'Backend Developer'
        },
        {
            'Họ và tên': 'Phạm Hồng Hạnh',
            'Email': 'hanh.ph@urbox.vn',
            'SĐT': '0393309830',
            'Vị trí': 'UI/UX Designer'
        }
    ]
    
    formatter = MarkdownFormatter()
    result = formatter.format_table_to_list(table_data)
    
    print("\n📊 FORMATTED LIST:")
    print(result)


# ===== EXAMPLE 7: Convert with Guideline =====
def example_7_convert_with_guideline():
    """Convert file với guideline (requires actual file)"""
    print("\n" + "=" * 60)
    print("EXAMPLE 7: Convert File with Guideline")
    print("=" * 60)
    
    print("""
ĐỂ CHẠY EXAMPLE NÀY:
1. Quăng file lên server
2. Gọi endpoint mới: POST /api/v2/convert/guideline
3. Pass template_type và template_data

CÚ PHÁP:

curl -X POST http://localhost:8080/api/v2/convert/guideline \\
  -H "Content-Type: application/json" \\
  -d '{
    "filename": "document.pdf",
    "template_type": "word_document",
    "template_data": {
      "source_url": "https://...",
      "summary": "Tóm tắt tài liệu...",
      "key_points": ["Point 1", "Point 2"]
    }
  }'
    """)


# ===== Run All Examples =====
if __name__ == "__main__":
    example_1_format_text()
    example_2_excel_template()
    example_3_document_template()
    example_4_process_template()
    example_5_custom_template()
    example_6_format_table()
    example_7_convert_with_guideline()
    
    print("\n" + "=" * 60)
    print("✅ Tất cả examples chạy xong!")
    print("=" * 60)
