# File: excel_processor.py
# Module xử lý Excel và chuyển đổi sang DOCX

import os
import pandas as pd
from docx import Document
from docx.shared import Pt
from openpyxl import load_workbook


class ExcelProcessorError(Exception):
    pass



def validate_file_exists(file_path: str) -> None:
    if not os.path.exists(file_path):
        raise ExcelProcessorError(f"File không tồn tại: {file_path}")
    if not os.path.isfile(file_path):
        raise ExcelProcessorError(f"Đường dẫn không phải file: {file_path}")


def validate_excel_file(file_path: str) -> None:
    validate_file_exists(file_path)

    ext = os.path.splitext(file_path)[1].lower()
    if ext not in (".xlsx", ".xls"):
        raise ExcelProcessorError(f"File không phải Excel: {ext}")

    if os.path.getsize(file_path) > 50 * 1024 * 1024:
        raise ExcelProcessorError("File quá lớn (tối đa 50MB)")



def get_sheet_names(file_path: str) -> list[str]:
    validate_excel_file(file_path)
    wb = load_workbook(file_path, read_only=True, data_only=True)
    names = wb.sheetnames
    wb.close()
    return names


def preview_sheet_data(file_path: str, sheet_name: str, num_rows: int = 10) -> dict:
    """
    Preview = quét TOÀN BỘ sheet, lấy N dòng CÓ DỮ LIỆU đầu tiên.
    KHÔNG dùng header_row, KHÔNG dùng data_start_row.
    """
    validate_excel_file(file_path)

    wb = load_workbook(file_path, read_only=True, data_only=True)
    if sheet_name not in wb.sheetnames:
        raise ExcelProcessorError(f"Sheet '{sheet_name}' không tồn tại")

    ws = wb[sheet_name]
    max_row = ws.max_row or 0

    preview = []
    max_col = 0

    for row in ws.iter_rows(min_row=1, max_row=max_row):
        values = ["" if c.value is None else c.value for c in row]
        if any(v not in ("", None) for v in values):
            preview.append(values)
            max_col = max(max_col, len(values))
        if len(preview) >= num_rows:
            break

    wb.close()

    return {
        "preview": preview,
        "total_rows": max_row,
        "total_cols": max_col,
    }



def get_column_headers(file_path: str, sheet_name: str, header_row: int) -> list[str]:
    validate_excel_file(file_path)

    wb = load_workbook(file_path, read_only=True, data_only=True)
    if sheet_name not in wb.sheetnames:
        raise ExcelProcessorError(f"Sheet '{sheet_name}' không tồn tại")

    ws = wb[sheet_name]
    max_row = ws.max_row or 0

    if header_row < 1 or header_row > max_row:
        wb.close()
        raise ExcelProcessorError(
            f"Dòng header không hợp lệ: {header_row} (1 → {max_row})"
        )

    headers = []
    for cell in ws[header_row]:
        if cell.value is None or str(cell.value).strip() == "":
            headers.append(f"Cột {cell.column}")
        else:
            headers.append(
                str(cell.value).replace("\n", " ").replace("\t", " ").strip()
            )

    wb.close()
    return headers


def convert_excel_to_docx(
    excel_file_path: str,
    output_docx_path: str,
    sheet_name: str,
    selected_columns: list[str],
    header_row: int,
    data_start_row: int,
    data_end_row: int | None = None,
) -> int:
    """
    data_start_row = quyết định của USER
    → backend phải đọc TOÀN BỘ, rồi cắt đúng dòng
    """
    validate_excel_file(excel_file_path)

    if not selected_columns:
        raise ExcelProcessorError("Chưa chọn cột để xuất")

    if data_start_row <= header_row:
        raise ExcelProcessorError("Dòng data phải > dòng header")

    wb = load_workbook(excel_file_path, data_only=True)
    if sheet_name not in wb.sheetnames:
        raise ExcelProcessorError(f"Sheet '{sheet_name}' không tồn tại")

    ws = wb[sheet_name]
    max_row = ws.max_row or 0

    if data_start_row > max_row:
        raise ExcelProcessorError("Dòng bắt đầu data vượt quá sheet")

    df = pd.read_excel(
        excel_file_path,
        sheet_name=sheet_name,
        header=header_row - 1,
    )

    df.columns = (
        df.columns.astype(str)
        .str.replace("\n", " ")
        .str.replace("\t", " ")
        .str.strip()
    )

    missing = [c for c in selected_columns if c not in df.columns]
    if missing:
        raise ExcelProcessorError(f"Không tìm thấy cột: {', '.join(missing)}")

    start_idx = data_start_row - header_row - 1
    end_idx = None
    if data_end_row:
        end_idx = data_end_row - header_row

    df = df.iloc[start_idx:end_idx][selected_columns].reset_index(drop=True)

    if df.empty:
        raise ExcelProcessorError("Không có dữ liệu hợp lệ để xuất")

    # merge cells
    merged_values = {}
    for r in ws.merged_cells.ranges:
        v = ws.cell(r.min_row, r.min_col).value
        for row in range(r.min_row, r.max_row + 1):
            for col in range(r.min_col, r.max_col + 1):
                merged_values[(row, col)] = v

    for i, row in df.iterrows():
        excel_row = data_start_row + i
        for j, col in enumerate(df.columns):
            if pd.isna(row[col]):
                for idx, cell in enumerate(ws[header_row], 1):
                    if str(cell.value).strip() == col:
                        df.iat[i, j] = merged_values.get((excel_row, idx))
                        break

    wb.close()

    # DOCX
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Arial"
    style.font.size = Pt(11)

    for i, row in df.iterrows():
        for col in df.columns:
            val = row[col]
            doc.add_paragraph(f"{col}: {val if pd.notna(val) else 'N/A'}")
        if i < len(df) - 1:
            doc.add_paragraph("-" * 80)

    os.makedirs(os.path.dirname(output_docx_path), exist_ok=True)
    doc.save(output_docx_path)

    return len(df)
