import os
import pandas as pd
from excel_processor import preview_sheet_data, convert_excel_to_docx

# --- CẤU HÌNH ---
# Thay tên file này bằng tên file thật của bạn đang nằm trong thư mục uploads/
# Nếu bạn để file ở cùng thư mục code thì chỉ cần ghi tên file
TEST_FILE = r"D:\Urbox\Convert_Excel\uploads\FINAL_DANH_SACH_MC_URBOX_PRT_quan_ly_20260114_041447_20260114_161654.xlsx"  # <--- SỬA TÊN FILE TẠI ĐÂY
SHEET_NAME = "Số outlets theo Brand_17.07.202"                            # <--- SỬA TÊN SHEET TẠI ĐÂY

def test_preview():
    print("\n" + "="*50)
    print("TEST 1: PREVIEW DATA (Kiểm tra dòng trống)")
    print("="*50)
    
    try:
        # Giả sử mình muốn xem 5 dòng đầu
        result = preview_sheet_data(TEST_FILE, SHEET_NAME, num_rows=5)
        
        print(f"Tổng số dòng trong file: {result['total_rows']}")
        print(f"Số dòng lấy ra: {len(result['preview'])}")
        print("-" * 30)
        
        # In ra từng dòng kèm số thứ tự để kiểm tra
        # Dòng 1 trong Excel (index 0) nên là dòng trống nếu file bạn có dòng trống
        for i, row in enumerate(result['preview']):
            print(f"Dòng {i+1}: {row}")
            
    except Exception as e:
        print(f"LỖI PREVIEW: {e}")

def test_convert():
    print("\n" + "="*50)
    print("TEST 2: CONVERT WORD (Kiểm tra Merged Cells)")
    print("="*50)
    
    OUTPUT_DOC = r"D:\Urbox\Convert_Exceltest_output.docx"
    
    # Giả lập tham số user gửi lên
    # Bạn thay đổi 'columns' cho khớp với file của bạn
    params = {
        "excel_file_path": TEST_FILE,
        "output_docx_path": OUTPUT_DOC,
        "sheet_name": SHEET_NAME,
        "selected_columns": ["Ngành hàng", "Tên thương hiệu"], # <--- SỬA TÊN CỘT CẦN TEST
        "header_row": 2,       # Giả sử header ở dòng 2
        "data_start_row": 3,   # Data bắt đầu dòng 3
        "data_end_row": 10     # Lấy thử vài dòng
    }
    
    try:
        count = convert_excel_to_docx(**params)
        print(f"✅ Đã xuất thành công {count} bản ghi ra file '{OUTPUT_DOC}'")
        print("👉 Hãy mở file word ra kiểm tra xem cột 'Ngành hàng' có dữ liệu ở các dòng dưới không.")
    except Exception as e:
        print(f"❌ LỖI CONVERT: {e}")

if __name__ == "__main__":
    if not os.path.exists(TEST_FILE):
        print(f"❌ Không tìm thấy file: {TEST_FILE}")
        print("Vui lòng sửa đường dẫn TEST_FILE trong code test.py")
    else:
        test_preview()
        test_convert()