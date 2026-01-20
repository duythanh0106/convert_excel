"""
Universal File Converter - Tích hợp Markitdown
Hỗ trợ convert: PDF, DOCX, PPTX, HTML, Images, Excel, CSV, Jupyter, etc.
Tích hợp với UrBox Guideline format
"""

import os
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any
import markitdown
from .excel_processor import (
    convert_excel_to_docx,
    convert_excel_to_markdown,
    ExcelProcessorError
)
from .markdown_formatter import MarkdownFormatter
from .template_processor import (
    GuidelineTemplate,
    TemplateBuilder,
    TemplateVariableInjector,
    TemplateType,
    PredefinedTemplates
)


class UniversalConverterError(Exception):
    """Exception cho Universal Converter"""
    pass


class FileTypeDetector:
    """Detect file type và lấy thông tin file"""
    
    # Supported file extensions với descriptions
    SUPPORTED_FORMATS = {
        # Documents
        '.pdf': 'Portable Document Format',
        '.docx': 'Microsoft Word Document',
        '.doc': 'Microsoft Word Document (Legacy)',
        '.txt': 'Plain Text File',
        '.md': 'Markdown File',
        
        # Spreadsheets
        '.xlsx': 'Microsoft Excel Workbook',
        '.xls': 'Microsoft Excel Workbook (Legacy)',
        '.csv': 'Comma-Separated Values',
        
        # Presentations
        '.pptx': 'Microsoft PowerPoint Presentation',
        '.ppt': 'Microsoft PowerPoint Presentation (Legacy)',
        
        # Data Formats
        '.json': 'JSON Data',
        '.xml': 'XML Data',
        
        # Web
        '.html': 'HyperText Markup Language',
        '.htm': 'HyperText Markup Language',
        
        # Images
        '.png': 'Portable Network Graphics',
        '.jpg': 'JPEG Image',
        '.jpeg': 'JPEG Image',
        '.gif': 'Graphics Interchange Format',
        '.bmp': 'Bitmap Image',
        '.webp': 'WebP Image',
        '.svg': 'Scalable Vector Graphics',
        
        # Code & Notebooks
        '.ipynb': 'Jupyter Notebook',
        '.py': 'Python Source Code',
        '.r': 'R Source Code',
        '.rmd': 'R Markdown',
        '.js': 'JavaScript Source Code',
        '.ts': 'TypeScript Source Code',
        '.java': 'Java Source Code',
        '.cpp': 'C++ Source Code',
        '.c': 'C Source Code',
        
        # Archives & Others
        '.msg': 'Outlook Message',
        '.epub': 'EPUB eBook',
        '.rss': 'RSS Feed',
    }
    
    MARKITDOWN_SUPPORTED = {
        '.pdf', '.docx', '.doc', '.txt', '.md',
        '.xlsx', '.xls', '.csv',
        '.pptx', '.ppt',
        '.json', '.xml',
        '.html', '.htm',
        '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp',
        '.ipynb',
        '.py', '.r', '.rmd', '.js', '.ts', '.java', '.cpp', '.c',
        '.msg', '.epub', '.rss'
    }
    
    EXCEL_SPECIFIC = {'.xlsx', '.xls'}

    @staticmethod
    def detect(file_path: str) -> Dict[str, Any]:
        """Detect file type và trả về thông tin"""
        ext = Path(file_path).suffix.lower()
        
        if not os.path.exists(file_path):
            raise UniversalConverterError(f"File không tồn tại: {file_path}")
        
        if ext not in FileTypeDetector.SUPPORTED_FORMATS:
            supported = ', '.join(sorted(FileTypeDetector.SUPPORTED_FORMATS.keys()))
            raise UniversalConverterError(
                f"Định dạng {ext} không được hỗ trợ.\n"
                f"Các định dạng hỗ trợ: {supported}"
            )
        
        file_size = os.path.getsize(file_path)
        
        return {
            'ext': ext,
            'name': Path(file_path).name,
            'description': FileTypeDetector.SUPPORTED_FORMATS[ext],
            'size': file_size,
            'is_excel': ext in FileTypeDetector.EXCEL_SPECIFIC,
            'is_markitdown_supported': ext in FileTypeDetector.MARKITDOWN_SUPPORTED,
        }


class UniversalConverter:
    """Main converter class - tích hợp Excel processor + Markitdown + Guideline Format"""
    
    def __init__(self, max_file_size: int = 100 * 1024 * 1024):
        self.max_file_size = max_file_size
        try:
            # Try new markitdown API
            self.markitdown_converter = markitdown.MarkItDown()
        except (AttributeError, TypeError):
            # Fallback for different markitdown versions
            self.markitdown_converter = None
        self.formatter = MarkdownFormatter()
        self.template_injector = TemplateVariableInjector()
    
    def validate_file(self, file_path: str) -> None:
        """Validate file trước convert"""
        if not os.path.exists(file_path):
            raise UniversalConverterError(f"File không tồn tại: {file_path}")
        
        file_size = os.path.getsize(file_path)
        if file_size > self.max_file_size:
            size_mb = file_size / (1024 * 1024)
            max_mb = self.max_file_size / (1024 * 1024)
            raise UniversalConverterError(
                f"File quá lớn ({size_mb:.2f}MB). Tối đa: {max_mb:.0f}MB"
            )
    
    def convert_to_markdown(self, file_path: str, output_path: Optional[str] = None) -> str:
        """
        Convert bất kỳ file type nào sang Markdown
        
        Args:
            file_path: Đường dẫn input file
            output_path: Đường dẫn output file (optional)
        
        Returns:
            Markdown content
        """
        self.validate_file(file_path)
        file_info = FileTypeDetector.detect(file_path)
        
        try:
            # Sử dụng markitdown để convert
            result = self.markitdown_converter.convert(file_path)
            markdown_content = result.text_content
            
            # Lưu output nếu có path
            if output_path:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
            
            return markdown_content
        
        except Exception as e:
            raise UniversalConverterError(
                f"Lỗi convert {file_info['ext']} sang Markdown: {str(e)}"
            )
    
    def convert_excel_to_docx(
        self,
        file_path: str,
        sheet_name: str,
        columns: list,
        header_row: int,
        data_start_row: int,
        output_path: str
    ) -> str:
        """Convert Excel file sang DOCX (specialized handler)"""
        try:
            output = convert_excel_to_docx(
                file_path,
                sheet_name,
                columns,
                header_row,
                data_start_row,
                output_path
            )
            return output
        except ExcelProcessorError as e:
            raise UniversalConverterError(f"Excel conversion error: {str(e)}")
    
    def convert_excel_to_markdown_table(
        self,
        file_path: str,
        sheet_name: str,
        columns: list,
        header_row: int,
        data_start_row: int,
        output_path: Optional[str] = None
    ) -> str:
        """Convert Excel sang Markdown table format"""
        try:
            markdown_content = convert_excel_to_markdown(
                file_path,
                sheet_name,
                columns,
                header_row,
                data_start_row,
                output_path
            )
            return markdown_content
        except ExcelProcessorError as e:
            raise UniversalConverterError(f"Excel to Markdown error: {str(e)}")
    
    def convert_with_guideline(
        self,
        file_path: str,
        template_type: TemplateType = TemplateType.EXCEL_LIST,
        template_data: Optional[Dict[str, Any]] = None,
        output_path: Optional[str] = None
    ) -> str:
        """
        Convert file sang Markdown với UrBox Guideline format
        
        Args:
            file_path: Đường dẫn input file
            template_type: Loại template (EXCEL_LIST, WORD_DOCUMENT, PROCESS, POLICY)
            template_data: Dict chứa dữ liệu cho template
            output_path: Đường dẫn output file
        
        Returns:
            Markdown content theo guideline
        """
        self.validate_file(file_path)
        file_info = FileTypeDetector.detect(file_path)
        
        try:
            # 1. Convert file thô
            raw_markdown = self.markitdown_converter.convert(file_path).text_content
            
            # 2. Format theo guideline
            formatted_markdown = self.formatter.format_text(raw_markdown)
            
            # 3. Tạo template
            template_data = template_data or {}
            builder = TemplateBuilder(template_type)
            
            # Inject raw content vào template
            builder.set_content(formatted_markdown)
            
            # Apply các field khác từ template_data
            for key, value in template_data.items():
                if hasattr(builder, f'set_{key}'):
                    getattr(builder, f'set_{key}')(value)
            
            result_markdown = builder.build()
            
            # 4. Lưu output nếu có path
            if output_path:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(result_markdown)
            
            return result_markdown
        
        except Exception as e:
            raise UniversalConverterError(
                f"Lỗi convert {file_info['ext']} với guideline: {str(e)}"
            )
    
    def convert_with_custom_template(
        self,
        file_path: str,
        template: str,
        variables: Optional[Dict[str, str]] = None,
        output_path: Optional[str] = None
    ) -> str:
        """
        Convert file với custom template
        
        Args:
            file_path: Đường dẫn input file
            template: Template string với placeholders <VARIABLE_NAME>
            variables: Dict biến để inject vào template
            output_path: Đường dẫn output file
        
        Returns:
            Markdown content với template applied
        """
        self.validate_file(file_path)
        
        try:
            # 1. Convert file thô
            raw_markdown = self.markitdown_converter.convert(file_path).text_content
            
            # 2. Format theo guideline
            formatted_markdown = self.formatter.format_text(raw_markdown)
            
            # 3. Inject content vào template
            template_vars = variables or {}
            template_vars['MAIN_CONTENT'] = formatted_markdown
            
            result_markdown = self.template_injector.inject(template, template_vars)
            
            # 4. Lưu output nếu có path
            if output_path:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(result_markdown)
            
            return result_markdown
        
        except Exception as e:
            raise UniversalConverterError(
                f"Lỗi convert với custom template: {str(e)}"
            )
    
    def get_supported_formats(self) -> Dict[str, str]:
        """Lấy danh sách các định dạng được hỗ trợ"""
        return FileTypeDetector.SUPPORTED_FORMATS
    
    def get_supported_extensions(self) -> list:
        """Lấy danh sách extension được hỗ trợ"""
        return sorted(list(FileTypeDetector.SUPPORTED_FORMATS.keys()))


class BatchConverter:
    """Hỗ trợ convert multiple files"""
    
    def __init__(self):
        self.converter = UniversalConverter()
    
    def convert_directory(
        self,
        input_dir: str,
        output_dir: str,
        extensions: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Convert toàn bộ files trong directory
        
        Args:
            input_dir: Input directory
            output_dir: Output directory
            extensions: List extensions cần convert (None = tất cả)
        
        Returns:
            Kết quả convert
        """
        results = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'files': []
        }
        
        if not os.path.isdir(input_dir):
            raise UniversalConverterError(f"Input directory không tồn tại: {input_dir}")
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Lấy tất cả files
        for filename in os.listdir(input_dir):
            file_path = os.path.join(input_dir, filename)
            
            if not os.path.isfile(file_path):
                continue
            
            ext = Path(file_path).suffix.lower()
            if extensions and ext not in extensions:
                continue
            
            results['total'] += 1
            
            try:
                # Generate output path
                output_filename = Path(filename).stem + '.md'
                output_path = os.path.join(output_dir, output_filename)
                
                # Convert
                self.converter.convert_to_markdown(file_path, output_path)
                
                results['success'] += 1
                results['files'].append({
                    'input': filename,
                    'output': output_filename,
                    'status': 'success'
                })
            
            except Exception as e:
                results['failed'] += 1
                results['files'].append({
                    'input': filename,
                    'output': None,
                    'status': 'failed',
                    'error': str(e)
                })
        
        return results


# Utility functions
def get_conversion_formats(file_ext: str) -> list:
    """
    Lấy danh sách format có thể convert tới từ một file type
    
    Args:
        file_ext: Extension của input file
    
    Returns:
        List các output formats
    """
    ext = file_ext.lower()
    
    # Tất cả files có thể convert sang Markdown
    formats = ['markdown']
    
    # Excel files có thể convert sang DOCX hoặc Markdown table
    if ext in {'.xlsx', '.xls'}:
        formats.extend(['docx', 'markdown_table'])
    
    return formats
