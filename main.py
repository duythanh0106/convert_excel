from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import os
import time
import threading
from datetime import datetime
import socket

from excel_processor import (
    get_sheet_names,
    preview_sheet_data,
    get_column_headers,
    convert_excel_to_docx,
    ExcelProcessorError
)


app = FastAPI(
    title="Excel to DOCX Converter",
    description="Convert Excel spreadsheets to formatted Word documents with intelligent column selection",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware (nếu cần gọi API từ domain khác)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# CONFIGURATION
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration from environment
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
OUTPUT_FOLDER = os.getenv('OUTPUT_FOLDER', 'outputs')
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 50 * 1024 * 1024))
ALLOWED_EXTENSIONS = set(os.getenv('ALLOWED_EXTENSIONS', '.xlsx,.xls').split(','))
CLEANUP_HOURS = int(os.getenv('CLEANUP_HOURS', 24))


# REQUEST MODELS
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
    """Kiểm tra file có được phép upload không"""
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS


def cleanup_old_files(folder: str, max_age_hours: int = 24):
    """Xóa file cũ hơn max_age_hours"""
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
    """Chạy cleanup định kỳ mỗi giờ"""
    def run_cleanup():
        while True:
            cleanup_old_files(UPLOAD_FOLDER, max_age_hours=24)
            cleanup_old_files(OUTPUT_FOLDER, max_age_hours=24)
            time.sleep(3600)
    
    cleanup_thread = threading.Thread(target=run_cleanup, daemon=True)
    cleanup_thread.start()


def get_host_ip():
    """Lấy IP thật của máy host"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.1)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        
        if not local_ip.startswith(('172.', '10.0.0.')):
            return local_ip
    except Exception:
        pass
    
    try:
        hostname = socket.gethostname()
        addrs = socket.getaddrinfo(hostname, None, socket.AF_INET)
        
        for addr in addrs:
            ip = addr[4][0]
            if not ip.startswith(('127.', '172.', '169.', '10.0.0.')):
                return ip
        
        for addr in addrs:
            ip = addr[4][0]
            if not ip.startswith('127.'):
                return ip
    except Exception:
        pass
    
    return "localhost"


@app.get('/', response_class=HTMLResponse, include_in_schema=False)
async def index():
    """
    Trang chủ - Giao diện web converter
    """
    try:
        with open('templates/index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise HTTPException(404, "File index.html không tồn tại")


@app.post('/upload', tags=["Excel Processing"])
async def upload_file(file: UploadFile = File(...)):
    """
    📤 Upload file Excel và lấy danh sách sheets
    
    **Parameters:**
    - **file**: File Excel (.xlsx hoặc .xls, tối đa 50MB)
    
    **Returns:**
    - `filename`: Tên file đã lưu (có timestamp)
    - `sheets`: Danh sách sheet trong file
    - `file_size`: Kích thước file (KB)
    
    **Errors:**
    - `400`: File không hợp lệ hoặc quá lớn
    - `500`: Lỗi server
    """
    try:
        # Validate filename
        if not file.filename:
            raise HTTPException(400, 'Chưa chọn file')
        
        if not allowed_file(file.filename):
            raise HTTPException(
                400, 
                'File không hợp lệ. Chỉ chấp nhận .xlsx, .xls'
            )
        
        contents = await file.read()
        file_size = len(contents)
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                400, 
                f'File quá lớn: {file_size / 1024 / 1024:.1f}MB (max 50MB)'
            )
        
        # Tạo filename với timestamp để tránh trùng
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name, ext = os.path.splitext(file.filename)
        clean_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_'))
        filename = f"{clean_name}_{timestamp}{ext}"
        
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        # Lưu file
        with open(filepath, 'wb') as f:
            f.write(contents)
        
        # Lấy danh sách sheets
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
    👁️ Xem trước dữ liệu của sheet
    
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
    📋 Lấy danh sách cột sau khi chọn dòng header
    
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
    🔄 Chuyển đổi Excel sang DOCX
    
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
        # Validation
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
        
        # Convert (blocking operation - có thể cải tiến thành async)
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


@app.get('/download/{filename}', tags=["Download"])
async def download(filename: str):
    """
    ⬇️ Download file DOCX đã convert
    
    **Parameters:**
    - **filename**: Tên file cần tải (vd: output_20240114_153045.docx)
    
    **Returns:**
    - File DOCX
    
    **Errors:**
    - `404`: File không tồn tại
    """
    try:
        # Security: chỉ cho phép tên file, không cho phép path
        filename = os.path.basename(filename)
        filepath = os.path.join(OUTPUT_FOLDER, filename)
        
        if not os.path.exists(filepath):
            raise HTTPException(404, 'File không tồn tại')
        
        return FileResponse(
            filepath, 
            filename=filename,
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f'Lỗi khi download: {str(e)}')



@app.get('/health', tags=["System"])
async def health_check():
    """
    ❤️ Health check endpoint
    """
    return {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0'
    }


@app.get('/info', tags=["System"])
async def info():
    """
    ℹ️ Thông tin hệ thống
    """
    return {
        'app_name': 'Excel to DOCX Converter',
        'version': '2.0.0',
        'framework': 'FastAPI',
        'max_file_size': f'{MAX_FILE_SIZE / 1024 / 1024:.0f}MB',
        'allowed_formats': list(ALLOWED_EXTENSIONS),
        'endpoints': {
            'web_ui': '/',
            'api_docs': '/docs',
            'redoc': '/redoc'
        }
    }



@app.on_event("startup")
async def startup_event():
    """Chạy khi app khởi động"""
    local_ip = get_host_ip()
    
    print("\n" + "="*70)
    print("EXCEL TO DOCX CONVERTER - FastAPI v2.0.0")
    print("="*70)
    print("\nTRUY CẬP TỪ MÁY NÀY:")
    print(f"   → http://localhost:8080")
    print("\nTRUY CẬP TỪ MÁY KHÁC CÙNG MẠNG:")
    print(f"   → http://{local_ip}:8080")
    print("\nAPI DOCUMENTATION:")
    print(f"   → http://localhost:8080/docs (Swagger UI)")
    print(f"   → http://localhost:8080/redoc (ReDoc)")
    print("\n" + "="*70 + "\n")
    
    print("🧹 Đang dọn dẹp files cũ...")
    cleanup_old_files(UPLOAD_FOLDER, max_age_hours=24)
    cleanup_old_files(OUTPUT_FOLDER, max_age_hours=24)
    
    print("Đã lên lịch cleanup tự động mỗi giờ\n")
    schedule_cleanup()


@app.on_event("shutdown")
async def shutdown_event():
    """Chạy khi app tắt"""
    print("\n👋 Shutting down Excel to DOCX Converter...\n")
