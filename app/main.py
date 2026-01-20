from fastapi import FastAPI, UploadFile, File, HTTPException, Request, Body
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import os
import time
import threading
from datetime import datetime
import socket
import ipaddress
from starlette.middleware.sessions import SessionMiddleware
from .auth_oidc import (
    login_page,
    login_google,
    auth_callback_google,
    login_keycloak,
    auth_callback_keycloak,
    logout,
)

from .excel_processor import (
    get_sheet_names,
    preview_sheet_data,
    get_column_headers,
    convert_excel_to_docx,
    convert_excel_to_markdown,
    ExcelProcessorError
)

from .universal_converter import (
    UniversalConverter,
    FileTypeDetector,
    BatchConverter,
    UniversalConverterError,
    get_conversion_formats
)

from .markdown_formatter import MarkdownFormatter
from .template_processor import (
    TemplateBuilder,
    TemplateType,
    TemplateVariableInjector,
    PredefinedTemplates
)

import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Excel to DOCX Converter",
    description="Convert Excel spreadsheets to formatted Word documents with intelligent column selection",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Set up templates - adjust path based on where main.py is running from
import os
templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
templates = Jinja2Templates(directory=templates_dir)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "change-this-secret"),
    same_site="lax",
    https_only=False,  
)

# ===== AUTH ROUTES =====
app.add_api_route(
    "/login",
    login_page,
    methods=["GET"],
    include_in_schema=False,
    name="login_page",
)

app.add_api_route(
    "/auth/login/google",
    login_google,
    methods=["GET"],
    include_in_schema=False,
)

app.add_api_route(
    "/auth/callback/google",
    auth_callback_google,
    methods=["GET"],
    include_in_schema=False,
    name="auth_callback_google",
)

app.add_api_route(
    "/auth/login/keycloak",
    login_keycloak,
    methods=["GET"],
    include_in_schema=False,
)

app.add_api_route(
    "/auth/callback/keycloak",
    auth_callback_keycloak,
    methods=["GET"],
    include_in_schema=False,
    name="auth_callback_keycloak",
)

app.add_api_route(
    "/logout",
    logout,
    methods=["GET"],
    include_in_schema=False,
)

UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
OUTPUT_FOLDER = os.getenv('OUTPUT_FOLDER', 'outputs')
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 50 * 1024 * 1024))
ALLOWED_EXTENSIONS = set(os.getenv('ALLOWED_EXTENSIONS', '.xlsx').split(','))
CLEANUP_HOURS = int(os.getenv('CLEANUP_HOURS', 24))


class PreviewRequest(BaseModel):
    filename: str = Field(..., description="Tên file đã upload")
    sheet: str = Field(..., description="Tên sheet cần xem")
    num_rows: int = Field(10, ge=1, le=50, description="Số dòng preview (1-50)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "filename": "data_20240114_153045.xlsx",
                "sheet": "Sheet1",
                "num_rows": 10
            }
        }


class ColumnsRequest(BaseModel):
    filename: str = Field(..., description="Tên file đã upload")
    sheet: str = Field(..., description="Tên sheet")
    header_row: int = Field(..., ge=1, description="Dòng chứa header (≥1)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "filename": "data_20240114_153045.xlsx",
                "sheet": "Sheet1",
                "header_row": 2
            }
        }


class ConvertRequest(BaseModel):
    filename: str = Field(..., description="Tên file Excel")
    sheet: str = Field(..., description="Tên sheet")
    columns: List[str] = Field(..., min_length=1, max_length=100, description="Danh sách cột (1-100)")
    header_row: int = Field(..., ge=1, description="Dòng chứa header")
    data_start_row: int = Field(..., ge=2, description="Dòng bắt đầu data")
    data_end_row: Optional[int] = Field(None, description="Dòng kết thúc (null = hết sheet)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "filename": "data_20240114_153045.xlsx",
                "sheet": "Sheet1",
                "columns": ["Tên", "Email", "SĐT"],
                "header_row": 2,
                "data_start_row": 3,
                "data_end_row": 100
            }
        }


def allowed_file(filename: str) -> bool:
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS


def cleanup_old_files(folder: str, max_age_hours: int = 24):
    try:
        now = time.time()
        max_age_seconds = max_age_hours * 3600
        
        for filename in os.listdir(folder):
            filepath = os.path.join(folder, filename)
            if os.path.isfile(filepath):
                file_age = now - os.path.getmtime(filepath)
                if file_age > max_age_seconds:
                    os.remove(filepath)
                    print(f"✓ Đã xóa file cũ: {filename}")
    except Exception as e:
        print(f"✗ Lỗi khi cleanup: {e}")


def schedule_cleanup():
    def run_cleanup():
        while True:
            cleanup_old_files(UPLOAD_FOLDER, max_age_hours=24)
            cleanup_old_files(OUTPUT_FOLDER, max_age_hours=24)
            time.sleep(3600)
    
    cleanup_thread = threading.Thread(target=run_cleanup, daemon=True)
    cleanup_thread.start()


def get_host_ip() -> str:
    def is_public_ipv4(ip: str) -> bool:
        try:
            a = ipaddress.ip_address(ip)
            return (
                a.version == 4
                and not a.is_loopback
                and not a.is_private
                and not a.is_link_local
                and not a.is_reserved
                and not a.is_multicast
            )
        except ValueError:
            return False

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.2)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()

        if local_ip and local_ip != "127.0.0.1":
            return local_ip
    except Exception:
        pass

    try:
        hostname = socket.gethostname()
        addrs = socket.getaddrinfo(hostname, None, socket.AF_INET)

        for addr in addrs:
            sockaddr = addr[4]
            if isinstance(sockaddr, tuple) and len(sockaddr) >= 1 and isinstance(sockaddr[0], str):
                ip = sockaddr[0]
                if is_public_ipv4(ip):
                    return ip

        for addr in addrs:
            sockaddr = addr[4]
            if isinstance(sockaddr, tuple) and len(sockaddr) >= 1 and isinstance(sockaddr[0], str):
                ip = sockaddr[0]
                if ip and ip != "127.0.0.1":
                    return ip
    except Exception:
        pass

    return "localhost"


@app.get('/', response_class=HTMLResponse, include_in_schema=False)
async def index(request: Request):
    if "user" not in request.session:
        return RedirectResponse("/login")

    return templates.TemplateResponse("index.html", {"request": request})


@app.post('/upload', tags=["Excel Processing"])
async def upload_file(file: UploadFile = File(...)):
    """
    **Parameters:**
    - **file**: File Excel (.xlsx tối đa 50MB)
    
    **Returns:**
    - `filename`: Tên file đã lưu (có timestamp)
    - `sheets`: Danh sách sheet trong file
    - `file_size`: Kích thước file (KB)
    
    **Errors:**
    - `400`: File không hợp lệ hoặc quá lớn
    - `500`: Lỗi server
    """
    try:
        if not file.filename:
            raise HTTPException(400, 'Chưa chọn file')
        
        if not allowed_file(file.filename):
            raise HTTPException(
                400, 
                'File không hợp lệ. Chỉ chấp nhận .xlsx'
            )
        
        contents = await file.read()
        file_size = len(contents)
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                400, 
                f'File quá lớn: {file_size / 1024 / 1024:.1f}MB (max 50MB)'
            )
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name, ext = os.path.splitext(file.filename)
        clean_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_'))
        filename = f"{clean_name}_{timestamp}{ext}"
        
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        with open(filepath, 'wb') as f:
            f.write(contents)
        
        sheets = get_sheet_names(filepath)
        
        if not sheets:
            os.remove(filepath)
            raise HTTPException(400, 'File Excel không có sheet nào')
        
        return {
            'filename': filename,
            'sheets': sheets,
            'file_size': f"{file_size / 1024:.1f} KB"
        }
        
    except ExcelProcessorError as e:
        raise HTTPException(400, str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f'Lỗi không xác định: {str(e)}')


@app.post('/preview', tags=["Excel Processing"])
async def preview_sheet(data: PreviewRequest):
    """
    **Parameters:**
    - **filename**: Tên file đã upload
    - **sheet**: Tên sheet cần xem
    - **num_rows**: Số dòng preview (1-50, mặc định 10)
    
    **Returns:**
    - `preview`: Mảng 2D chứa dữ liệu preview
    - `total_rows`: Tổng số dòng trong sheet
    - `total_cols`: Tổng số cột
    """
    try:
        filepath = os.path.join(UPLOAD_FOLDER, data.filename)
        
        if not os.path.exists(filepath):
            raise HTTPException(404, 'File không tồn tại. Vui lòng upload lại')
        
        result = preview_sheet_data(filepath, data.sheet, data.num_rows)
        return result
        
    except ExcelProcessorError as e:
        raise HTTPException(400, str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f'Lỗi: {str(e)}')


@app.post('/get-columns', tags=["Excel Processing"])
async def get_columns(data: ColumnsRequest):
    """
    **Parameters:**
    - **filename**: Tên file đã upload
    - **sheet**: Tên sheet
    - **header_row**: Số thứ tự dòng chứa header (bắt đầu từ 1)
    
    **Returns:**
    - `columns`: Danh sách tên cột
    """
    try:
        filepath = os.path.join(UPLOAD_FOLDER, data.filename)
        
        if not os.path.exists(filepath):
            raise HTTPException(404, 'File không tồn tại. Vui lòng upload lại')
        
        headers = get_column_headers(filepath, data.sheet, data.header_row)
        
        if not headers:
            raise HTTPException(
                400, 
                f'Không tìm thấy header ở dòng {data.header_row}'
            )
        
        return {'columns': headers}
        
    except ExcelProcessorError as e:
        raise HTTPException(400, str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f'Lỗi: {str(e)}')


@app.post('/convert', tags=["Conversion"])
async def convert(data: ConvertRequest):
    """    
    **Parameters:**
    - **filename**: Tên file Excel đã upload
    - **sheet**: Tên sheet cần convert
    - **columns**: Danh sách tên cột cần xuất (1-100 cột)
    - **header_row**: Dòng chứa header (≥1)
    - **data_start_row**: Dòng bắt đầu data (≥2)
    - **data_end_row**: Dòng kết thúc (optional, null = đến cuối sheet)
    
    **Returns:**
    - `success`: true
    - `output_file`: Tên file DOCX đã tạo
    - `row_count`: Số dòng đã xuất
    - `column_count`: Số cột đã xuất
    - `message`: Thông báo kết quả
    
    **Errors:**
    - `400`: Tham số không hợp lệ
    - `404`: File không tồn tại
    - `500`: Lỗi khi convert
    """
    try:
        if data.data_start_row <= data.header_row:
            raise HTTPException(
                400, 
                'Dòng bắt đầu data phải lớn hơn dòng header'
            )
        
        if data.data_end_row and data.data_end_row < data.data_start_row:
            raise HTTPException(
                400, 
                'Dòng kết thúc phải lớn hơn hoặc bằng dòng bắt đầu'
            )
        
        input_path = os.path.join(UPLOAD_FOLDER, data.filename)
        
        if not os.path.exists(input_path):
            raise HTTPException(404, 'File không tồn tại. Vui lòng upload lại')
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"output_{timestamp}.docx"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        row_count = convert_excel_to_docx(
            input_path, 
            output_path, 
            data.sheet, 
            data.columns, 
            data.header_row, 
            data.data_start_row,
            data.data_end_row
        )
        
        return {
            'success': True,
            'output_file': output_filename,
            'row_count': row_count,
            'column_count': len(data.columns),
            'message': f'Đã xuất thành công {row_count} bản ghi với {len(data.columns)} cột'
        }
        
    except ExcelProcessorError as e:
        raise HTTPException(400, str(e))
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(400, f'Giá trị không hợp lệ: {str(e)}')
    except Exception as e:
        raise HTTPException(500, f'Lỗi khi chuyển đổi: {str(e)}')

@app.post('/convert-markdown', tags=["Conversion"])
async def convert_markdown(data: ConvertRequest):
    try:
        if data.data_start_row <= data.header_row:
            raise HTTPException(
                400,
                'Dòng bắt đầu data phải lớn hơn dòng header'
            )

        if data.data_end_row and data.data_end_row < data.data_start_row:
            raise HTTPException(
                400,
                'Dòng kết thúc phải lớn hơn hoặc bằng dòng bắt đầu'
            )

        input_path = os.path.join(UPLOAD_FOLDER, data.filename)

        if not os.path.exists(input_path):
            raise HTTPException(404, 'File không tồn tại. Vui lòng upload lại')

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"output_{timestamp}.md"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)

        row_count = convert_excel_to_markdown(
            input_path,
            output_path,
            data.sheet,
            data.columns,
            data.header_row,
            data.data_start_row,
            data.data_end_row
        )

        return {
            'success': True,
            'output_file': output_filename,
            'row_count': row_count,
            'column_count': len(data.columns),
            'message': f'Đã xuất Markdown thành công {row_count} bản ghi với {len(data.columns)} cột'
        }

    except ExcelProcessorError as e:
        raise HTTPException(400, str(e))
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(400, f'Giá trị không hợp lệ: {str(e)}')
    except Exception as e:
        raise HTTPException(500, f'Lỗi khi chuyển đổi: {str(e)}')

@app.get('/download/{filename}', tags=["Download"])
async def download(filename: str):
    """
    **Parameters:**
    - **filename**: Tên file cần tải
    
    **Returns:**
    - File DOCX
    
    **Errors:**
    - `404`: File không tồn tại
    """
    try:
        filename = os.path.basename(filename)
        filepath = os.path.join(OUTPUT_FOLDER, filename)
        
        if not os.path.exists(filepath):
            raise HTTPException(404, 'File không tồn tại')
        
        ext = os.path.splitext(filename)[1].lower()
        if ext == ".md":
            media_type = "text/markdown; charset=utf-8"
        else:
            media_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'

        return FileResponse(
            filepath,
            filename=filename,
            media_type=media_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f'Lỗi khi download: {str(e)}')


# ===== UNIVERSAL CONVERTER ENDPOINTS =====

universal_converter = UniversalConverter(max_file_size=MAX_FILE_SIZE)


class UniversalUploadRequest(BaseModel):
    filename: str = Field(..., description="Tên file đã upload")
    output_format: str = Field(default="markdown", description="Output format (markdown, docx, etc.)")


@app.get('/api/v2/formats', tags=["Universal Converter"])
async def get_supported_formats():
    """Lấy danh sách các định dạng file được hỗ trợ"""
    return {
        'supported_extensions': sorted(universal_converter.get_supported_extensions()),
        'supported_formats': universal_converter.get_supported_formats(),
        'description': 'Hỗ trợ convert từ và sang Markdown'
    }


@app.post('/api/v2/detect', tags=["Universal Converter"])
async def detect_file_type(request: UniversalUploadRequest):
    """
    Detect loại file và lấy thông tin chi tiết
    
    Returns:
        - ext: File extension
        - description: File type description
        - size: File size in bytes
        - is_excel: Có phải Excel file không
        - is_markitdown_supported: Có hỗ trợ convert không
    """
    try:
        upload_path = os.path.join(UPLOAD_FOLDER, request.filename)
        file_info = FileTypeDetector.detect(upload_path)
        
        return {
            'success': True,
            'file': file_info,
            'available_conversions': get_conversion_formats(file_info['ext'])
        }
    except UniversalConverterError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, f'Lỗi detect file: {str(e)}')


@app.post('/api/v2/convert/markdown', tags=["Universal Converter"])
async def convert_to_markdown(request: UniversalUploadRequest):
    """
    Convert bất kỳ file type nào sang Markdown
    
    Args:
        filename: Tên file đã upload
        output_format: Format output (mặc định: markdown)
    
    Returns:
        - success: True/False
        - markdown_content: Nội dung Markdown
        - file_saved: Tên file output
    """
    try:
        input_path = os.path.join(UPLOAD_FOLDER, request.filename)
        
        if not os.path.exists(input_path):
            raise HTTPException(404, f'File không tồn tại: {request.filename}')
        
        # Tạo output filename
        base_name = os.path.splitext(request.filename)[0]
        output_filename = f"{base_name}_converted_{int(time.time())}.md"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        # Convert
        markdown_content = universal_converter.convert_to_markdown(input_path, output_path)
        
        return {
            'success': True,
            'markdown_content': markdown_content[:1000] + '...' if len(markdown_content) > 1000 else markdown_content,
            'full_content_length': len(markdown_content),
            'file_saved': output_filename,
            'download_url': f'/download/{output_filename}'
        }
    
    except UniversalConverterError as e:
        raise HTTPException(400, str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f'Lỗi convert sang Markdown: {str(e)}')


@app.post('/api/v2/batch/convert', tags=["Universal Converter"])
async def batch_convert(request: BaseModel):
    """
    Convert toàn bộ files trong một thư mục
    
    Args:
        input_dir: Input directory
        extensions: List extensions cần convert (optional)
    
    Returns:
        Kết quả convert từng file
    """
    try:
        # Request body
        batch_converter = BatchConverter()
        
        # Tạm thời convert từ uploads folder
        results = batch_converter.convert_directory(
            UPLOAD_FOLDER,
            OUTPUT_FOLDER
        )
        
        return {
            'success': True,
            'conversion_results': results
        }
    
    except UniversalConverterError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, f'Lỗi batch convert: {str(e)}')


# ===== GUIDELINE TEMPLATE ENDPOINTS =====

class GuidelineConvertRequest(BaseModel):
    filename: str = Field(..., description="Tên file đã upload")
    template_type: str = Field(default="excel_list", description="Loại template: excel_list, word_document, process, policy")
    source_url: Optional[str] = Field(None, description="URL tài liệu gốc")
    summary: Optional[str] = Field(None, description="Tóm tắt nội dung")
    key_points: Optional[List[str]] = Field(None, description="Các điểm chính")
    insights: Optional[str] = Field(None, description="Insights/Nhận xét")
    deep_summary: Optional[str] = Field(None, description="Deep summary chi tiết")


class CustomTemplateConvertRequest(BaseModel):
    filename: str = Field(..., description="Tên file đã upload")
    template: str = Field(..., description="Custom template với placeholders <VARIABLE_NAME>")
    variables: Optional[dict] = Field(None, description="Dict biến để inject")


@app.post('/api/v2/convert/guideline', tags=["Guideline Template"])
async def convert_with_guideline(request: GuidelineConvertRequest):
    """Convert file sang Markdown với UrBox Guideline format (5-section template)"""
    try:
        input_path = os.path.join(UPLOAD_FOLDER, request.filename)
        
        if not os.path.exists(input_path):
            raise HTTPException(404, f'File không tồn tại: {request.filename}')
        
        template_type_map = {
            'excel_list': TemplateType.EXCEL_LIST,
            'word_document': TemplateType.WORD_DOCUMENT,
            'process': TemplateType.PROCESS,
            'policy': TemplateType.POLICY,
        }
        
        template_type = template_type_map.get(request.template_type, TemplateType.EXCEL_LIST)
        
        template_data = {}
        if request.source_url:
            template_data['source'] = request.source_url
        if request.summary:
            template_data['summary'] = request.summary
        if request.key_points:
            template_data['key_points'] = request.key_points
        if request.insights:
            template_data['insights'] = request.insights
        if request.deep_summary:
            template_data['deep_summary'] = request.deep_summary
        
        base_name = os.path.splitext(request.filename)[0]
        output_filename = f"{base_name}_guideline_{int(time.time())}.md"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        markdown_content = universal_converter.convert_with_guideline(
            input_path,
            template_type=template_type,
            template_data=template_data,
            output_path=output_path
        )
        
        return {
            'success': True,
            'markdown_content': markdown_content[:1000] + '...' if len(markdown_content) > 1000 else markdown_content,
            'full_content_length': len(markdown_content),
            'file_saved': output_filename,
            'download_url': f'/download/{output_filename}'
        }
    
    except UniversalConverterError as e:
        raise HTTPException(400, str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f'Lỗi convert với guideline: {str(e)}')


@app.post('/api/v2/convert/custom-template', tags=["Guideline Template"])
async def convert_with_custom_template(request: CustomTemplateConvertRequest):
    """Convert file với custom template"""
    try:
        input_path = os.path.join(UPLOAD_FOLDER, request.filename)
        
        if not os.path.exists(input_path):
            raise HTTPException(404, f'File không tồn tại: {request.filename}')
        
        base_name = os.path.splitext(request.filename)[0]
        output_filename = f"{base_name}_custom_{int(time.time())}.md"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        markdown_content = universal_converter.convert_with_custom_template(
            input_path,
            template=request.template,
            variables=request.variables,
            output_path=output_path
        )
        
        return {
            'success': True,
            'markdown_content': markdown_content[:1000] + '...' if len(markdown_content) > 1000 else markdown_content,
            'full_content_length': len(markdown_content),
            'file_saved': output_filename,
            'download_url': f'/download/{output_filename}'
        }
    
    except UniversalConverterError as e:
        raise HTTPException(400, str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f'Lỗi convert với custom template: {str(e)}')


@app.get('/api/v2/templates', tags=["Guideline Template"])
async def get_predefined_templates():
    """Lấy danh sách các template định sẵn"""
    return {
        'templates': {
            'excel': PredefinedTemplates.get_excel_template(),
            'document': PredefinedTemplates.get_document_template(),
            'process': PredefinedTemplates.get_process_template(),
            'policy': PredefinedTemplates.get_policy_template()
        }
    }


@app.post('/api/v2/format/text', tags=["Guideline Template"])
async def format_text_guideline(text: str = Body(..., description="Văn bản cần format")):
    """Format văn bản theo UrBox Guideline"""
    try:
        formatter = MarkdownFormatter()
        formatted = formatter.format_text(text)
        entities = formatter.extract_entities(text)
        
        return {
            'success': True,
            'original_text': text,
            'formatted_text': formatted,
            'entities_found': entities
        }
    except Exception as e:
        raise HTTPException(500, f'Lỗi format text: {str(e)}')


@app.post('/api/v2/format/table', tags=["Guideline Template"])
async def format_table_guideline(table_data: List[dict] = Body(..., description="Dữ liệu bảng")):
    """Chuyển bảng sang format danh sách theo guideline"""
    try:
        formatter = MarkdownFormatter()
        formatted = formatter.format_table_to_list(table_data)
        
        return {
            'success': True,
            'original_table': table_data,
            'formatted_list': formatted
        }
    except Exception as e:
        raise HTTPException(500, f'Lỗi format table: {str(e)}')


@app.get('/api/v2/info', tags=["Universal Converter"])
async def universal_converter_info():
    """Lấy thông tin chi tiết về Universal Converter"""
    return {
        'name': 'Universal File Converter',
        'version': '1.0.0',
        'description': 'Convert nhiều loại file sang Markdown hoặc định dạng khác',
        'capabilities': {
            'documents': ['PDF', 'DOCX', 'TXT', 'MD'],
            'spreadsheets': ['XLSX', 'XLS', 'CSV'],
            'presentations': ['PPTX', 'PPT'],
            'data_formats': ['JSON', 'XML'],
            'web': ['HTML', 'RSS'],
            'images': ['PNG', 'JPG', 'GIF', 'BMP', 'WEBP', 'SVG'],
            'code': ['IPYNB', 'PY', 'R', 'RMD', 'JS', 'TS', 'JAVA', 'CPP'],
            'archives': ['MSG', 'EPUB']
        },
        'powered_by': 'Markitdown'
    }




@app.get('/health', tags=["System"])
async def health_check():
    return {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0'
    }


@app.get('/info', tags=["System"])
async def info():
    return {
        'app_name': 'Universal File Converter',
        'version': '3.0.0',
        'framework': 'FastAPI',
        'description': 'Convert multiple file types (Excel, PDF, Images, Code, etc.) to Markdown and other formats',
        'max_file_size': f'{MAX_FILE_SIZE / 1024 / 1024:.0f}MB',
        'allowed_formats': list(ALLOWED_EXTENSIONS),
        'modules': {
            'excel_converter': {
                'version': '2.0.0',
                'description': 'Specialized Excel to DOCX/Markdown converter'
            },
            'universal_converter': {
                'version': '1.0.0',
                'description': 'Convert any supported file type to Markdown',
                'powered_by': 'Markitdown'
            }
        },
        'endpoints': {
            'web_ui': '/',
            'api_docs': '/docs',
            'redoc': '/redoc',
            'excel_api': '/api/v1',
            'universal_api': '/api/v2'
        }
    }




@app.on_event("startup")
async def startup_event():
    local_ip = get_host_ip()
    
    print("\n" + "="*70)
    print("UNIVERSAL FILE CONVERTER - FastAPI v3.0.0")
    print("="*70)
    print("\n🚀 MODULES:")
    print("   • Excel to DOCX/Markdown Converter")
    print("   • Universal File Converter (Powered by Markitdown)")
    print("\n📁 SUPPORTED FORMATS:")
    print("   • Documents: PDF, DOCX, TXT, MD")
    print("   • Spreadsheets: XLSX, CSV, XLS")
    print("   • Presentations: PPTX, PPT")
    print("   • Images: PNG, JPG, GIF, WEBP")
    print("   • Code: IPYNB, PY, R, RMD, JS, TS, JAVA, CPP")
    print("   • Web: HTML, RSS, XML, JSON")
    print("   • Archives: MSG, EPUB")
    print("\n🌐 TRUY CẬP TỪ MÁY NÀY:")
    print(f"   → http://localhost:8080")
    print("\n🌍 TRUY CẬP TỪ MÁY KHÁC CÙNG MẠNG:")
    print(f"   → http://{local_ip}:8080")
    print("\n📚 API DOCUMENTATION:")
    print(f"   → http://localhost:8080/docs (Swagger UI)")
    print(f"   → http://localhost:8080/redoc (ReDoc)")
    print("\n💡 API VERSIONS:")
    print(f"   → /api/v1/* (Excel Converter Endpoints)")
    print(f"   → /api/v2/* (Universal Converter Endpoints)")
    print("\n" + "="*70 + "\n")
    
    print("Đang dọn dẹp files cũ...")
    cleanup_old_files(UPLOAD_FOLDER, max_age_hours=24)
    cleanup_old_files(OUTPUT_FOLDER, max_age_hours=24)
    
    print("Đã lên lịch cleanup tự động mỗi giờ\n")
    schedule_cleanup()


@app.on_event("shutdown")
async def shutdown_event():
    print("\nShutting down Excel to DOCX Converter...\n")
