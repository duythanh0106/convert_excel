import os
from pathlib import Path
from typing import Optional, Dict, Any
from .processor import (
    ClassicExcelProcessor,
    UniversalFileProcessor,
    ExcelProcessorError
)
from .markdown_formatter import MarkdownFormatter
from .template_processor import (
    TemplateBuilder,
    TemplateVariableInjector,
    TemplateType
)


class UniversalConverterError(Exception):
    pass


class FileTypeDetector:
    SUPPORTED_FORMATS = {
        # Documents
        '.pdf': 'Portable Document Format',
        '.docx': 'Microsoft Word Document',
        '.pptx': 'Microsoft PowerPoint Presentation',
        '.xlsx': 'Microsoft Excel Workbook',
        
        # Images
        '.png': 'Portable Network Graphics',
        '.jpg': 'JPEG Image',
        
        # Audio
        '.mp3': 'MP3 Audio',
        '.wav': 'WAV Audio',
        '.m4a': 'M4A Audio',
        '.aac': 'AAC Audio',
        '.flac': 'FLAC Audio',
        '.ogg': 'OGG Audio',
        
        # Web
        '.html': 'HyperText Markup Language',
        
        # Data Formats
        '.csv': 'Comma-Separated Values',
        '.json': 'JSON Data',
        '.xml': 'XML Data',
        
        # Archives
        '.zip': 'ZIP Archive',
    }
    
    MARKITDOWN_SUPPORTED = set(SUPPORTED_FORMATS.keys())
    
    EXCEL_SPECIFIC = {'.xlsx'}

    @staticmethod
    def detect(file_path: str) -> Dict[str, Any]:
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
    def __init__(self, max_file_size: int = 100 * 1024 * 1024):
        self.max_file_size = max_file_size
        self.formatter = MarkdownFormatter()
        self.template_injector = TemplateVariableInjector()
        self.classic_processor = ClassicExcelProcessor()
        self.universal_processor = UniversalFileProcessor(max_file_size=max_file_size)
    
    def validate_file(self, file_path: str) -> None:
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
            return self.universal_processor.convert_to_markdown(file_path, output_path)
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
    ) -> int:
        try:
            return self.classic_processor.convert_excel_to_docx(
                file_path,
                output_path,
                sheet_name,
                columns,
                header_row,
                data_start_row
            )
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
    ) -> int:
        try:
            if output_path is None:
                raise UniversalConverterError("output_path is required for Markdown table output")

            return self.classic_processor.convert_excel_to_markdown(
                file_path,
                output_path,
                sheet_name,
                columns,
                header_row,
                data_start_row
            )
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
            raw_markdown = self.universal_processor.convert_to_markdown(file_path)
            formatted_markdown = self.formatter.format_text(raw_markdown)

            template_data = template_data or {}
            builder = TemplateBuilder(template_type)
            builder.set_content(formatted_markdown)
            
            for key, value in template_data.items():
                if hasattr(builder, f'set_{key}'):
                    getattr(builder, f'set_{key}')(value)
            
            result_markdown = builder.build()
            
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
            raw_markdown = self.universal_processor.convert_to_markdown(file_path)
            formatted_markdown = self.formatter.format_text(raw_markdown)
            
            template_vars = variables or {}
            template_vars['MAIN_CONTENT'] = formatted_markdown
            result_markdown = self.template_injector.inject(template, template_vars)
            
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
        return FileTypeDetector.SUPPORTED_FORMATS
    
    def get_supported_extensions(self) -> list:
        return sorted(list(FileTypeDetector.SUPPORTED_FORMATS.keys()))


class BatchConverter:
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
        
        for filename in os.listdir(input_dir):
            file_path = os.path.join(input_dir, filename)
            
            if not os.path.isfile(file_path):
                continue
            
            ext = Path(file_path).suffix.lower()
            if extensions and ext not in extensions:
                continue
            
            results['total'] += 1
            
            try:
                output_filename = Path(filename).stem + '.md'
                output_path = os.path.join(output_dir, output_filename)
                
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


def get_conversion_formats(file_ext: str) -> list:
    """
    Lấy danh sách format có thể convert tới từ một file type
    
    Args:
        file_ext: Extension của input file
    
    Returns:
        List các output formats
    """
    ext = file_ext.lower()
    formats = ['markdown']
    if ext in {'.xlsx', '.xls'}:
        formats.extend(['docx', 'markdown_table'])
    
    return formats
