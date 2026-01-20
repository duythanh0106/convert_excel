import os
import pandas as pd
import tempfile
from docx import Document
from docx.shared import Pt
from openpyxl import load_workbook
from typing import Optional

class ExcelProcessorError(Exception):
    pass

def is_cell_empty(value) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    return False

def get_max_used_column(ws) -> int:
    max_used_col = 0
    max_row = ws.max_row or 0

    for row in ws.iter_rows(min_row=1, max_row=max_row):
        last_non_empty = 0
        for idx, cell in enumerate(row, start=1):
            if not is_cell_empty(cell.value):
                last_non_empty = idx
        if last_non_empty > max_used_col:
            max_used_col = last_non_empty

    return max_used_col

def validate_file_exists(file_path: str) -> None:
    if not os.path.exists(file_path):
        raise ExcelProcessorError(f"File không tồn tại: {file_path}")
    if not os.path.isfile(file_path):
        raise ExcelProcessorError(f"Đường dẫn không phải file: {file_path}")

def validate_excel_file(file_path: str) -> None:
    validate_file_exists(file_path)
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == '.xls':
         raise ExcelProcessorError("Hệ thống hiện tại chỉ hỗ trợ file .xlsx (OpenXML). Vui lòng lưu file sang định dạng .xlsx và thử lại.")
         
    if ext not in (".xlsx", ".xls"):
        raise ExcelProcessorError(f"File không phải Excel: {ext}")

    if os.path.getsize(file_path) > 50 * 1024 * 1024:
        raise ExcelProcessorError("File quá lớn (tối đa 50MB)")

def get_sheet_names(file_path: str) -> list[str]:
    validate_excel_file(file_path)
    try:
        wb = load_workbook(file_path, read_only=True, data_only=True)
        names = wb.sheetnames
        wb.close()
        return names
    except Exception as e:
        raise ExcelProcessorError(f"Không thể đọc file Excel: {str(e)}")

def preview_sheet_data(file_path: str, sheet_name: str, num_rows: int = 20) -> dict:
    validate_excel_file(file_path)

    wb = load_workbook(file_path, read_only=True, data_only=True)
    if sheet_name not in wb.sheetnames:
        raise ExcelProcessorError(f"Sheet '{sheet_name}' không tồn tại")

    ws = wb[sheet_name]
    max_row = ws.max_row or 0
    max_used_col = get_max_used_column(ws)

    preview = []
    last_data_row = 0
    preview_limit = 20
    if max_used_col == 0:
        wb.close()
        return {
            "preview": [],
            "total_rows": 0,
            "total_cols": 0,
            "display_rows": 0,
        }

    for row_index, row in enumerate(
        ws.iter_rows(min_row=1, max_row=max_row, max_col=max_used_col),
        start=1
    ):
        values = []
        has_data = False
        for cell in row:
            value = cell.value
            if isinstance(value, str):
                value = value.strip()
            values.append("" if value is None else value)
            if not is_cell_empty(value):
                has_data = True

        if has_data:
            last_data_row = row_index

        if len(preview) < preview_limit:
            preview.append(values)

    wb.close()

    if last_data_row < len(preview):
        preview = preview[:last_data_row]

    return {
        "preview": preview,
        "total_rows": last_data_row,
        "total_cols": max_used_col,
        "display_rows": len(preview),
    }

def get_column_headers(file_path: str, sheet_name: str, header_row: int) -> list[str]:
    validate_excel_file(file_path)

    try:
        def read_headers(data_only: bool) -> list[str]:
            wb = load_workbook(file_path, read_only=True, data_only=data_only)
            try:
                if sheet_name not in wb.sheetnames:
                    raise ExcelProcessorError(f"Sheet '{sheet_name}' không tồn tại")

                ws = wb[sheet_name]

                if ws.max_row and header_row > ws.max_row:
                    raise ExcelProcessorError(
                        f"Dòng header ({header_row}) lớn hơn tổng số dòng ({ws.max_row})"
                    )

                max_used_col = get_max_used_column(ws)
                if max_used_col == 0:
                    return []

                row_generator = ws.iter_rows(
                    min_row=header_row,
                    max_row=header_row,
                    max_col=max_used_col
                )

                try:
                    row_cells = next(row_generator)
                except StopIteration:
                    return []

                headers = []
                for cell in row_cells:
                    value = cell.value
                    if value is None:
                        continue

                    header = str(value).replace("\n", " ").replace("\t", " ").strip()
                    if header == "":
                        continue

                    headers.append(header)

                return headers
            finally:
                wb.close()

        headers = read_headers(data_only=True)
        if not headers:
            headers = read_headers(data_only=False)

        return headers

    except Exception as e:
        if isinstance(e, ExcelProcessorError):
            raise e
        raise ExcelProcessorError(f"Lỗi khi đọc cột: {str(e)}")

def convert_excel_to_docx(
    excel_file_path: str,
    output_docx_path: str,
    sheet_name: str,
    selected_columns: list[str],
    header_row: int,
    data_start_row: int,
    data_end_row: int | None = None,
) -> int:
    validate_excel_file(excel_file_path)

    if not selected_columns:
        raise ExcelProcessorError("Chưa chọn cột để xuất")

    if data_start_row <= header_row:
        raise ExcelProcessorError("Dòng data phải > dòng header")

    try:
        df = pd.read_excel(
            excel_file_path,
            sheet_name=sheet_name,
            header=header_row - 1,
            dtype=str
        )
    except Exception as e:
         raise ExcelProcessorError(f"Lỗi đọc dữ liệu Excel: {str(e)}")

    df.columns = (
        df.columns.astype(str)
        .str.replace("\n", " ")
        .str.replace("\t", " ")
        .str.strip()
    )
    
    missing = [c for c in selected_columns if c not in df.columns]
    if missing:
        raise ExcelProcessorError(f"Không tìm thấy các cột sau: {', '.join(missing)}")

    start_idx = data_start_row - header_row - 1
    end_idx = None
    if data_end_row:
        end_idx = data_end_row - header_row

    if start_idx < 0: start_idx = 0

    df_subset = df.iloc[start_idx:end_idx].copy()
    
    df_final = df_subset[selected_columns].reset_index(drop=True)
    
    df_final = df_final.fillna("")

    df_final = df_final.replace(r'^\s*$', pd.NA, regex=True).ffill()
    
    df_final = df_final.fillna("")

    if df_final.empty:
        raise ExcelProcessorError("Không có dữ liệu nào trong khoảng dòng đã chọn")

    try:
        doc = Document()
        style = doc.styles["Normal"]
        style.font.name = "Arial"
        style.font.size = Pt(11)

        total_rows = len(df_final)

        for idx, (_, row) in enumerate(df_final.iterrows()):
            p = doc.add_paragraph()

            for col in selected_columns:
                val = str(row[col]).strip()

                run_header = p.add_run(f"{col}: ")
                run_header.bold = True
                p.add_run(f"{val}\n")

            if idx < total_rows - 1:
                doc.add_paragraph("-" * 50)


        os.makedirs(os.path.dirname(output_docx_path), exist_ok=True)
        doc.save(output_docx_path)

        return total_rows

    except Exception as e:
        raise ExcelProcessorError(f"Lỗi khi ghi file DOCX: {str(e)}")

def convert_excel_to_markdown(
    excel_file_path: str,
    output_md_path: str,
    sheet_name: str,
    selected_columns: list[str],
    header_row: int,
    data_start_row: int,
    data_end_row: int | None = None,
) -> int:
    validate_excel_file(excel_file_path)

    if not selected_columns:
        raise ExcelProcessorError("Chưa chọn cột để xuất")

    if data_start_row <= header_row:
        raise ExcelProcessorError("Dòng data phải > dòng header")

    try:
        df = pd.read_excel(
            excel_file_path,
            sheet_name=sheet_name,
            header=header_row - 1,
            dtype=str
        )
    except Exception as e:
        raise ExcelProcessorError(f"Lỗi đọc dữ liệu Excel: {str(e)}")

    df.columns = (
        df.columns.astype(str)
        .str.replace("\n", " ")
        .str.replace("\t", " ")
        .str.strip()
    )

    missing = [c for c in selected_columns if c not in df.columns]
    if missing:
        raise ExcelProcessorError(f"Không tìm thấy các cột sau: {', '.join(missing)}")

    start_idx = data_start_row - header_row - 1
    end_idx = None
    if data_end_row:
        end_idx = data_end_row - header_row

    if start_idx < 0:
        start_idx = 0

    df_subset = df.iloc[start_idx:end_idx].copy()
    df_final = df_subset[selected_columns].reset_index(drop=True)
    df_final = df_final.fillna("")
    df_final = df_final.replace(r'^\s*$', pd.NA, regex=True).ffill()
    df_final = df_final.fillna("")

    if df_final.empty:
        raise ExcelProcessorError("Không có dữ liệu nào trong khoảng dòng đã chọn")

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as temp_file:
            temp_path = temp_file.name

        df_final.to_excel(temp_path, index=False)

        try:
            from markitdown import MarkItDown
        except Exception:
            raise ExcelProcessorError(
                "Chưa cài markitdown"
            )

        md = MarkItDown()
        result = md.convert(temp_path)
        markdown_text = getattr(result, "text_content", None)
        if markdown_text is None:
            markdown_text = str(result)

        os.makedirs(os.path.dirname(output_md_path), exist_ok=True)
        with open(output_md_path, "w", encoding="utf-8") as f:
            f.write(markdown_text)

        return len(df_final)
    except ExcelProcessorError:
        raise
    except Exception as e:
        raise ExcelProcessorError(f"Lỗi khi tạo Markdown: {str(e)}")
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


class ClassicExcelProcessor:
    def get_sheet_names(self, file_path: str) -> list[str]:
        return get_sheet_names(file_path)

    def preview_sheet_data(self, file_path: str, sheet_name: str, num_rows: int = 20) -> dict:
        return preview_sheet_data(file_path, sheet_name, num_rows)

    def get_column_headers(self, file_path: str, sheet_name: str, header_row: int) -> list[str]:
        return get_column_headers(file_path, sheet_name, header_row)

    def convert_excel_to_docx(
        self,
        excel_file_path: str,
        output_docx_path: str,
        sheet_name: str,
        selected_columns: list[str],
        header_row: int,
        data_start_row: int,
        data_end_row: int | None = None,
    ) -> int:
        return convert_excel_to_docx(
            excel_file_path,
            output_docx_path,
            sheet_name,
            selected_columns,
            header_row,
            data_start_row,
            data_end_row,
        )

    def convert_excel_to_markdown(
        self,
        excel_file_path: str,
        output_md_path: str,
        sheet_name: str,
        selected_columns: list[str],
        header_row: int,
        data_start_row: int,
        data_end_row: int | None = None,
    ) -> int:
        return convert_excel_to_markdown(
            excel_file_path,
            output_md_path,
            sheet_name,
            selected_columns,
            header_row,
            data_start_row,
            data_end_row,
        )


class UniversalFileProcessor:
    def __init__(self, max_file_size: int = 100 * 1024 * 1024) -> None:
        self.max_file_size = max_file_size
        self._converter = None
        self._converter_error: Optional[Exception] = None
        try:
            from markitdown import MarkItDown
            self._converter = MarkItDown()
        except Exception as exc:
            self._converter_error = exc

    def validate_file(self, file_path: str) -> None:
        validate_file_exists(file_path)
        file_size = os.path.getsize(file_path)
        if file_size > self.max_file_size:
            size_mb = file_size / (1024 * 1024)
            max_mb = self.max_file_size / (1024 * 1024)
            raise ExcelProcessorError(
                f"File quá lớn ({size_mb:.2f}MB). Tối đa: {max_mb:.0f}MB"
            )

    def convert_to_markdown(self, file_path: str, output_path: Optional[str] = None) -> str:
        if self._converter is None:
            detail = str(self._converter_error) if self._converter_error else "markitdown"
            raise ExcelProcessorError(f"Chưa cài markitdown: {detail}")

        self.validate_file(file_path)
        try:
            result = self._converter.convert(file_path)
            markdown_text = getattr(result, "text_content", None)
            if markdown_text is None:
                markdown_text = str(result)

            if output_path:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(markdown_text)

            return markdown_text
        except ExcelProcessorError:
            raise
        except Exception as e:
            raise ExcelProcessorError(f"Lỗi khi convert sang Markdown: {str(e)}")
