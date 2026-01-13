from flask import Flask, render_template, request, send_file, jsonify
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import os
import socket
import time
import threading

from excel_processor import (
    get_sheet_names,
    preview_sheet_data,
    get_column_headers,
    convert_excel_to_docx,
    ExcelProcessorError
)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024 #max size 50MB
app.config['ALLOWED_EXTENSIONS'] = {'xlsx', 'xls'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)


def allowed_file(filename):
    """Kiểm tra file có được phép upload không"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def cleanup_old_files(folder, max_age_hours=24):
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
                    print(f"Đã xóa file cũ: {filename}")
    except Exception as e:
        print(f"Lỗi khi cleanup: {e}")


def schedule_cleanup():
    """Chạy cleanup định kỳ mỗi giờ"""
    def run_cleanup():
        while True:
            cleanup_old_files(app.config['UPLOAD_FOLDER'], max_age_hours=24)
            cleanup_old_files(app.config['OUTPUT_FOLDER'], max_age_hours=24)
            time.sleep(3600)  
    
    cleanup_thread = threading.Thread(target=run_cleanup, daemon=True)
    cleanup_thread.start()


@app.route('/')
def index():
    """Trang chủ"""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """Upload file Excel và lấy danh sách sheets"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Không tìm thấy file trong request'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Chưa chọn file'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File không hợp lệ. Chỉ chấp nhận .xlsx, .xls'}), 400
        
        # Secure filename và thêm timestamp để tránh trùng
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        original_name = secure_filename(file.filename)
        name, ext = os.path.splitext(original_name)
        filename = f"{name}_{timestamp}{ext}"
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Kiểm tra file size
        file_size = os.path.getsize(filepath)
        if file_size > app.config['MAX_CONTENT_LENGTH']:
            os.remove(filepath)
            return jsonify({'error': f'File quá lớn: {file_size / 1024 / 1024:.1f}MB (max 50MB)'}), 400
        
        sheets = get_sheet_names(filepath)
        
        if not sheets:
            os.remove(filepath)
            return jsonify({'error': 'File Excel không có sheet nào'}), 400
        
        return jsonify({
            'filename': filename,
            'sheets': sheets,
            'file_size': f"{file_size / 1024:.1f} KB"
        })
        
    except ExcelProcessorError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Lỗi không xác định: {str(e)}'}), 500


@app.route('/preview', methods=['POST'])
def preview_sheet():
    """Xem trước dữ liệu của sheet"""
    try:
        data = request.get_json()
        filename = data.get('filename')
        sheet_name = data.get('sheet')
        num_rows = int(data.get('num_rows', 10))
        
        if not filename or not sheet_name:
            return jsonify({'error': 'Thiếu tham số filename hoặc sheet'}), 400
        
        # Giới hạn số dòng preview
        num_rows = min(num_rows, 50)
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        result = preview_sheet_data(filepath, sheet_name, num_rows)
        
        return jsonify(result)
        
    except ExcelProcessorError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Lỗi: {str(e)}'}), 500


@app.route('/get-columns', methods=['POST'])
def get_columns():
    """Lấy danh sách cột sau khi chọn dòng header"""
    try:
        data = request.get_json()
        filename = data.get('filename')
        sheet_name = data.get('sheet')
        header_row = data.get('header_row')
        
        if not filename or not sheet_name or not header_row:
            return jsonify({'error': 'Thiếu tham số bắt buộc'}), 400
        
        header_row = int(header_row)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        headers = get_column_headers(filepath, sheet_name, header_row)
        
        if not headers:
            return jsonify({'error': f'Không tìm thấy header ở dòng {header_row}'}), 400
        
        return jsonify({'columns': headers})
        
    except ExcelProcessorError as e:
        return jsonify({'error': str(e)}), 400
    except ValueError:
        return jsonify({'error': 'Dòng header phải là số nguyên'}), 400
    except Exception as e:
        return jsonify({'error': f'Lỗi: {str(e)}'}), 500


@app.route('/convert', methods=['POST'])
def convert():
    """Chuyển đổi Excel sang DOCX"""
    try:
        data = request.get_json()
        filename = data.get('filename')
        sheet_name = data.get('sheet')
        selected_columns = data.get('columns', [])
        header_row = data.get('header_row')
        data_start_row = data.get('data_start_row')
        data_end_row = data.get('data_end_row')  # Có thể null
        
        # Validation
        if not filename or not sheet_name or not selected_columns or not header_row or not data_start_row:
            return jsonify({'error': 'Thiếu tham số bắt buộc'}), 400
        
        if not isinstance(selected_columns, list) or len(selected_columns) == 0:
            return jsonify({'error': 'Phải chọn ít nhất 1 cột'}), 400
        
        if len(selected_columns) > 100:
            return jsonify({'error': 'Chọn tối đa 100 cột'}), 400
        
        header_row = int(header_row)
        data_start_row = int(data_start_row)
        data_end_row = int(data_end_row) if data_end_row else None
        
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if not os.path.exists(input_path):
            return jsonify({'error': 'File không tồn tại. Vui lòng upload lại'}), 404
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"output_{timestamp}.docx"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        
        row_count = convert_excel_to_docx(
            input_path, 
            output_path, 
            sheet_name, 
            selected_columns, 
            header_row, 
            data_start_row,
            data_end_row
        )
        
        return jsonify({
            'success': True,
            'output_file': output_filename,
            'row_count': row_count,
            'column_count': len(selected_columns),
            'message': f'Đã xuất thành công {row_count} bản ghi với {len(selected_columns)} cột'
        })
        
    except ExcelProcessorError as e:
        return jsonify({'error': str(e)}), 400
    except ValueError as e:
        return jsonify({'error': f'Giá trị không hợp lệ: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Lỗi khi chuyển đổi: {str(e)}'}), 500


@app.route('/download/<filename>')
def download(filename):
    """Download file đã convert"""
    try:
        # Secure filename để tránh path traversal
        filename = secure_filename(filename)
        filepath = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'File không tồn tại'}), 404
        
        return send_file(
            filepath, 
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
    except Exception as e:
        return jsonify({'error': f'Lỗi khi download: {str(e)}'}), 500


@app.errorhandler(413)
def request_entity_too_large(error):
    """Xử lý lỗi file quá lớn"""
    return jsonify({'error': 'File quá lớn. Kích thước tối đa: 50MB'}), 413


@app.errorhandler(500)
def internal_error(error):
    """Xử lý lỗi server"""
    return jsonify({'error': 'Lỗi server nội bộ'}), 500


def get_host_ip():
    """Lấy IP thật của máy host (ưu tiên WiFi/Ethernet, bỏ qua Docker/WSL)"""
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


def print_startup_info():
    """In thông tin khởi động server"""
    local_ip = get_host_ip()
    
    print("")
    print("TRUY CẬP TỪ MÁY NÀY:")
    print(f"   → http://localhost:5000")
    print("")
    print("TRUY CẬP TỪ MÁY KHÁC CÙNG MẠNG:")
    print(f"   → http://{local_ip}:5000")
    print("")


if __name__ == '__main__':
    print_startup_info()
    
    cleanup_old_files(app.config['UPLOAD_FOLDER'], max_age_hours=24)
    cleanup_old_files(app.config['OUTPUT_FOLDER'], max_age_hours=24)
    
    schedule_cleanup()

    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)