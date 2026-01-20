"""
Markdown Formatter - Áp dụng UrBox Guideline
Tự động định dạng markdown output theo guideline AI KB
"""

import re
from typing import List, Dict, Optional, Tuple
from enum import Enum


class ContentType(Enum):
    """Loại nội dung cần format"""
    ACTOR = "actor"              # Phòng ban, chức danh
    ACTION = "action"            # Hành động, trạng thái
    OBJECT = "object"            # Tài liệu, công cụ
    IDENTIFIER = "identifier"    # Mã, ID, File names
    VARIABLE = "variable"        # Biến template


class MarkdownFormatter:
    """Formatter theo guideline UrBox"""
    
    # Từ điển nhận diện Actors (Phòng ban, chức danh)
    ACTORS = {
        'actors': [
            'kế toán', 'nhân sự', 'it', 'truyền thông', 'partnership',
            'kinh doanh', 'ban giám đốc', 'khách hàng', 'ứng viên',
            'nhân viên', 'operation', 'marketing', 'sales', 'support',
            'admin', 'manager', 'team lead', 'phòng', 'bộ phận',
            'hệ thống ai', 'urbox', 'merchant', 'partner'
        ]
    }
    
    # Từ điển nhận diện Actions (Động từ hành động)
    ACTIONS = {
        'actions': [
            'phê duyệt', 'duyệt', 'từ chối', 'gửi', 'nhận', 'kiểm tra',
            'xác nhận', 'hoàn thành', 'bắt đầu', 'kết thúc', 'cập nhật',
            'xóa', 'sửa', 'tạo', 'lưu', 'tải', 'tải lên', 'tải xuống',
            'đã hoàn thành', 'đang treo', 'chấp nhận', 'từ chối',
            'gửi yêu cầu', 'bấm', 'nhấp', 'truy cập', 'điền',
            'submit', 'approve', 'reject', 'confirm', 'cancel'
        ]
    }
    
    # Từ điển nhận diện Objects (Tài liệu, công cụ)
    OBJECTS = {
        'objects': [
            'biên bản đối soát', 'hợp đồng', 'biểu mẫu', 'file',
            'báo cáo', 'nút', 'màn hình', 'offer letter', 'email',
            'thông báo', 'form', 'button', 'screen', 'document',
            'report', 'contract', 'application', 'system', 'database'
        ]
    }
    
    # Pattern cho mã định danh
    ID_PATTERNS = [
        r'\b[A-Z]{1,5}_[A-Z0-9_]{2,}\b',  # HĐ_URBOX_001
        r'\bHD\s*\d{3,}\b',                # HĐ 001
        r'\b[A-Z]{2,}\s*\d{3,}\b',         # ID 123
        r'\b\d{9,}\b',                      # Mã số dài
    ]
    
    def __init__(self):
        self.variable_pattern = r'<[A-Z_]+>'  # <VARIABLE_NAME>
    
    def format_text(self, text: str) -> str:
        """
        Định dạng text theo guideline UrBox
        
        Args:
            text: Văn bản gốc
        
        Returns:
            Văn bản được format
        """
        # Thứ tự áp dụng format rất quan trọng!
        
        # 1. Format variables trước (có độ ưu tiên cao nhất)
        text = self._format_variables(text)
        
        # 2. Format actors/actions/objects
        text = self._format_actors(text)
        text = self._format_actions(text)
        text = self._format_objects(text)
        
        # 3. Format identifiers (ID, file names)
        text = self._format_identifiers(text)
        
        # 4. Format cấu trúc (Bước X, Nếu-Thì)
        text = self._format_structure(text)
        
        return text
    
    def _format_variables(self, text: str) -> str:
        """Format biến template: <VARIABLE_NAME>"""
        # Giữ nguyên format <VARIABLE_NAME>, chỉ thêm quote nếu cần
        pattern = r'(<[A-Z_]+>)'
        
        def replace_var(match):
            var = match.group(1)
            # Thêm line break nếu variable đứng một mình trên dòng
            return f"\n> {var}\n"
        
        # Chỉ format nếu variable không nằm trong câu
        lines = text.split('\n')
        formatted_lines = []
        
        for line in lines:
            if re.match(r'^\s*<[A-Z_]+>\s*$', line):
                formatted_lines.append(f"> {line.strip()}")
            else:
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    def _format_actors(self, text: str) -> str:
        """In đậm các Actors (Phòng ban, chức danh)"""
        for actor in self.ACTORS['actors']:
            # Tìm kiếm không phân biệt hoa/thường, từ nguyên
            pattern = r'\b' + actor + r'\b'
            replacement = f'**{actor.title()}**' if actor.islower() else f'**{actor}**'
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def _format_actions(self, text: str) -> str:
        """In đậm các Actions (Hành động, trạng thái)"""
        for action in self.ACTIONS['actions']:
            pattern = r'\b' + action + r'\b'
            replacement = f'**{action.title()}**' if action.islower() else f'**{action}**'
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def _format_objects(self, text: str) -> str:
        """In đậm các Objects (Tài liệu, công cụ)"""
        for obj in self.OBJECTS['objects']:
            pattern = r'\b' + obj + r'\b'
            replacement = f'**{obj.title()}**' if obj.islower() else f'**{obj}**'
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def _format_identifiers(self, text: str) -> str:
        """Format mã định danh thành Quote format"""
        lines = text.split('\n')
        formatted_lines = []
        
        for line in lines:
            # Kiểm tra nếu dòng chỉ chứa ID/code
            if self._is_identifier_line(line):
                formatted_lines.append(f"> {line.strip()}")
            else:
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    def _is_identifier_line(self, line: str) -> bool:
        """Kiểm tra nếu dòng là identifier"""
        # Nếu có email, URL, hoặc mã
        if re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', line):
            return True
        
        if re.search(r'https?://', line):
            return True
        
        for pattern in self.ID_PATTERNS:
            if re.search(pattern, line):
                return True
        
        return False
    
    def _format_structure(self, text: str) -> str:
        """Format cấu trúc: Bước X, Nếu-Thì"""
        # Tăng emphasis cho "Bước X:"
        text = re.sub(
            r'^(Bước\s+\d+:)',
            r'**\1**',
            text,
            flags=re.MULTILINE
        )
        
        # Tăng emphasis cho "Trường hợp X:"
        text = re.sub(
            r'^(Trường\s+hợp\s+\d+.*?:)',
            r'**\1**',
            text,
            flags=re.MULTILINE | re.IGNORECASE
        )
        
        # Format "Nếu-Thì"
        text = re.sub(
            r'(Nếu\s+.+?\s+thì)',
            r'**\1**',
            text,
            flags=re.IGNORECASE
        )
        
        return text
    
    def format_table_to_list(self, table_data: List[Dict[str, str]]) -> str:
        """
        Chuyển bảng sang format danh sách
        
        Args:
            table_data: List các dict (mỗi row là 1 dict)
        
        Returns:
            Markdown format danh sách
        """
        if not table_data:
            return ""
        
        result = []
        
        for idx, row in enumerate(table_data):
            # Mỗi hàng thành một khối
            for key, value in row.items():
                # Format key (tên cột)
                formatted_key = key.strip()
                # Format value
                formatted_value = value.strip() if value else "N/A"
                
                result.append(f"{formatted_key}: {formatted_value}")
            
            # Thêm separator giữa các hàng
            if idx < len(table_data) - 1:
                result.append("\n---\n")
        
        return '\n'.join(result)
    
    def add_bold(self, text: str, term: str) -> str:
        """
        Thêm bold cho một từ cụ thể
        
        Args:
            text: Văn bản gốc
            term: Từ cần bold
        
        Returns:
            Văn bản với bold
        """
        pattern = r'\b' + re.escape(term) + r'\b'
        return re.sub(pattern, f'**{term}**', text, flags=re.IGNORECASE)
    
    def add_quote(self, text: str) -> str:
        """Chuyển đoạn thành Quote format"""
        lines = text.split('\n')
        quoted = '\n'.join(f"> {line}" if line.strip() else "" for line in lines)
        return quoted
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Trích xuất các entity từ text
        
        Returns:
            Dict chứa actors, actions, objects tìm được
        """
        entities = {
            'actors': [],
            'actions': [],
            'objects': [],
            'identifiers': []
        }
        
        # Tìm actors
        for actor in self.ACTORS['actors']:
            pattern = r'\b' + actor + r'\b'
            if re.search(pattern, text, re.IGNORECASE):
                entities['actors'].append(actor)
        
        # Tìm actions
        for action in self.ACTIONS['actions']:
            pattern = r'\b' + action + r'\b'
            if re.search(pattern, text, re.IGNORECASE):
                entities['actions'].append(action)
        
        # Tìm objects
        for obj in self.OBJECTS['objects']:
            pattern = r'\b' + obj + r'\b'
            if re.search(pattern, text, re.IGNORECASE):
                entities['objects'].append(obj)
        
        # Tìm identifiers
        for pattern in self.ID_PATTERNS:
            matches = re.findall(pattern, text)
            entities['identifiers'].extend(matches)
        
        # Remove duplicates
        for key in entities:
            entities[key] = list(set(entities[key]))
        
        return entities


# Utility functions
def bold(text: str) -> str:
    """Shortcut để in đậm"""
    return f"**{text}**"


def quote(text: str) -> str:
    """Shortcut để quote"""
    return f"> {text}"


def variable(name: str) -> str:
    """Tạo biến template"""
    return f"<{name.upper()}>"


def create_section(title: str, content: str) -> str:
    """Tạo section trong markdown"""
    return f"\n## {title}\n\n{content}\n"


def create_step(step_num: int, content: str, sub_items: Optional[List[str]] = None) -> str:
    """Tạo step trong quy trình"""
    result = f"**Bước {step_num}:** {content}\n"
    
    if sub_items:
        for item in sub_items:
            result += f"- {item}\n"
    
    return result
