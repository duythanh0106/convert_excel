"""
Template Processor - Xử lý template theo guideline UrBox
Hỗ trợ cấu trúc 5 phần: A. Source | B. Summary | C. Metrics/Key Points | D. Insights/Deep Summary | E. Structured Output
"""

from typing import Dict, Optional, List, Any
from enum import Enum
from .markdown_formatter import MarkdownFormatter


class TemplateType(Enum):
    """Loại template"""
    EXCEL_LIST = "excel_list"          # Cho file Excel/CSV
    WORD_DOCUMENT = "word_document"    # Cho file Word/Document
    PROCESS = "process"                # Cho quy trình (SOP)
    POLICY = "policy"                  # Cho chính sách


class GuidelineTemplate:
    """Template theo guideline UrBox - 5 phần"""
    
    def __init__(self, template_type: TemplateType = TemplateType.EXCEL_LIST):
        self.template_type = template_type
        self.formatter = MarkdownFormatter()
        self.sections = {}
    
    def build_excel_template(
        self,
        source_url: Optional[str] = None,
        summary: str = "",
        metrics: Dict[str, Any] = None,
        insights: str = "",
        structured_content: str = ""
    ) -> str:
        """
        Xây dựng template cho file Excel/CSV theo 5 phần
        
        A. Tài liệu gốc
        B. Summary Overview
        C. Key Metrics
        D. Insights
        E. Structured Output
        """
        
        result = []
        
        # A. Tài liệu gốc
        if source_url:
            result.append("## A. Tài Liệu Gốc\n")
            result.append(f"**Nguồn:** {source_url}\n")
        
        # B. Summary Overview
        if summary:
            result.append("## B. Summary Overview\n")
            formatted_summary = self.formatter.format_text(summary)
            result.append(f"{formatted_summary}\n")
        
        # C. Key Metrics
        if metrics:
            result.append("## C. Key Metrics\n")
            for key, value in metrics.items():
                result.append(f"- **{key}:** {value}")
            result.append("")
        
        # D. Insights
        if insights:
            result.append("## D. Insights\n")
            formatted_insights = self.formatter.format_text(insights)
            result.append(f"{formatted_insights}\n")
        
        # E. Structured Output
        if structured_content:
            result.append("## E. Structured Output\n")
            formatted_content = self.formatter.format_text(structured_content)
            result.append(formatted_content)
        
        return '\n'.join(result)
    
    def build_document_template(
        self,
        source_url: Optional[str] = None,
        summary: str = "",
        key_points: List[str] = None,
        deep_summary: str = "",
        content: str = ""
    ) -> str:
        """
        Xây dựng template cho file Word/Document theo 5 phần
        
        A. Tài liệu gốc
        B. Summary Overview
        C. Key Points
        D. Deep Summary
        E. Readability Optimized
        """
        
        result = []
        
        # A. Tài liệu gốc
        if source_url:
            result.append("## A. Tài Liệu Gốc\n")
            result.append(f"**Nguồn:** {source_url}\n")
        
        # B. Summary Overview
        if summary:
            result.append("## B. Summary Overview\n")
            formatted_summary = self.formatter.format_text(summary)
            result.append(f"{formatted_summary}\n")
        
        # C. Key Points
        if key_points:
            result.append("## C. Key Points\n")
            for point in key_points:
                formatted_point = self.formatter.format_text(point)
                result.append(f"- {formatted_point}")
            result.append("")
        
        # D. Deep Summary
        if deep_summary:
            result.append("## D. Deep Summary\n")
            formatted_deep = self.formatter.format_text(deep_summary)
            result.append(f"{formatted_deep}\n")
        
        # E. Readability Optimized
        if content:
            result.append("## E. Readability Optimized\n")
            formatted_content = self.formatter.format_text(content)
            result.append(formatted_content)
        
        return '\n'.join(result)
    
    def build_process_template(
        self,
        source_url: Optional[str] = None,
        summary: str = "",
        key_points: List[str] = None,
        steps: List[Dict[str, Any]] = None,
        content: str = ""
    ) -> str:
        """
        Xây dựng template cho quy trình/SOP
        
        A. Tài liệu gốc
        B. Summary Overview
        C. Key Points
        D. Chi tiết Quy trình
        E. Readability Optimized
        """
        
        result = []
        
        # A. Tài liệu gốc
        if source_url:
            result.append("## A. Tài Liệu Gốc\n")
            result.append(f"**Nguồn:** {source_url}\n")
        
        # B. Summary
        if summary:
            result.append("## B. Summary Overview\n")
            formatted_summary = self.formatter.format_text(summary)
            result.append(f"{formatted_summary}\n")
        
        # C. Key Points
        if key_points:
            result.append("## C. Key Points\n")
            for point in key_points:
                formatted_point = self.formatter.format_text(point)
                result.append(f"- {formatted_point}")
            result.append("")
        
        # D. Chi tiết Quy trình
        if steps:
            result.append("## D. Chi Tiết Quy Trình\n")
            for step in steps:
                step_num = step.get('step', '')
                content = step.get('content', '')
                sub_items = step.get('sub_items', [])
                
                formatted_content = self.formatter.format_text(content)
                result.append(f"**Bước {step_num}:** {formatted_content}")
                
                if sub_items:
                    for item in sub_items:
                        formatted_item = self.formatter.format_text(item)
                        result.append(f"- {formatted_item}")
                
                result.append("")
        
        # E. Full content
        if content:
            result.append("## E. Readability Optimized\n")
            formatted_content = self.formatter.format_text(content)
            result.append(formatted_content)
        
        return '\n'.join(result)


class TemplateVariableInjector:
    """Inject biến vào template"""
    
    def __init__(self):
        self.variable_pattern = r'<([A-Z_]+)>'
    
    def inject(self, template: str, variables: Dict[str, str]) -> str:
        """
        Inject biến vào template
        
        Args:
            template: Template có chứa <VARIABLE_NAME>
            variables: Dict các biến cần inject
        
        Returns:
            Template sau khi inject
        """
        result = template
        
        for var_name, var_value in variables.items():
            var_placeholder = f"<{var_name.upper()}>"
            result = result.replace(var_placeholder, str(var_value))
        
        return result
    
    def extract_variables(self, template: str) -> List[str]:
        """
        Trích xuất tất cả biến từ template
        
        Returns:
            List các tên biến
        """
        import re
        matches = re.findall(self.variable_pattern, template)
        return list(set(matches))


class TemplateBuilder:
    """Builder pattern cho template tạo dễ dàng"""
    
    def __init__(self, template_type: TemplateType = TemplateType.EXCEL_LIST):
        self.template_type = template_type
        self.template = GuidelineTemplate(template_type)
        self.data = {}
    
    def set_source(self, url: str) -> 'TemplateBuilder':
        """Set nguồn tài liệu"""
        self.data['source_url'] = url
        return self
    
    def set_summary(self, summary: str) -> 'TemplateBuilder':
        """Set summary"""
        self.data['summary'] = summary
        return self
    
    def set_metrics(self, metrics: Dict[str, Any]) -> 'TemplateBuilder':
        """Set metrics (cho Excel)"""
        self.data['metrics'] = metrics
        return self
    
    def set_key_points(self, points: List[str]) -> 'TemplateBuilder':
        """Set key points (cho Document)"""
        self.data['key_points'] = points
        return self
    
    def set_insights(self, insights: str) -> 'TemplateBuilder':
        """Set insights"""
        self.data['insights'] = insights
        return self
    
    def set_deep_summary(self, deep_summary: str) -> 'TemplateBuilder':
        """Set deep summary (cho Document)"""
        self.data['deep_summary'] = deep_summary
        return self
    
    def set_steps(self, steps: List[Dict[str, Any]]) -> 'TemplateBuilder':
        """Set steps (cho Process)"""
        self.data['steps'] = steps
        return self
    
    def set_content(self, content: str) -> 'TemplateBuilder':
        """Set content chính"""
        self.data['content'] = content
        return self
    
    def build(self) -> str:
        """Build template cuối cùng"""
        if self.template_type == TemplateType.EXCEL_LIST:
            return self.template.build_excel_template(**self.data)
        elif self.template_type == TemplateType.WORD_DOCUMENT:
            return self.template.build_document_template(**self.data)
        elif self.template_type == TemplateType.PROCESS:
            return self.template.build_process_template(**self.data)
        else:
            return self.template.build_excel_template(**self.data)


# Predefined templates
class PredefinedTemplates:
    """Các template định sẵn"""
    
    @staticmethod
    def get_excel_template() -> str:
        """Template cho file Excel/CSV"""
        return """## A. Tài Liệu Gốc

**Nguồn:** <SOURCE_URL>

---

## B. Summary Overview

<SUMMARY_CONTENT>

---

## C. Key Metrics

<KEY_METRICS>

---

## D. Insights

<INSIGHTS_CONTENT>

---

## E. Structured Output

<STRUCTURED_CONTENT>
"""
    
    @staticmethod
    def get_document_template() -> str:
        """Template cho file Word/Document"""
        return """## A. Tài Liệu Gốc

**Nguồn:** <SOURCE_URL>

---

## B. Summary Overview

<SUMMARY_CONTENT>

---

## C. Key Points

<KEY_POINTS>

---

## D. Deep Summary

<DEEP_SUMMARY_CONTENT>

---

## E. Readability Optimized

<MAIN_CONTENT>
"""
    
    @staticmethod
    def get_process_template() -> str:
        """Template cho quy trình/SOP"""
        return """## A. Tài Liệu Gốc

**Nguồn:** <SOURCE_URL>

---

## B. Summary Overview

<SUMMARY_CONTENT>

---

## C. Key Points

<KEY_POINTS>

---

## D. Chi Tiết Quy Trình

<PROCESS_STEPS>

---

## E. Readability Optimized

<MAIN_CONTENT>
"""
    
    @staticmethod
    def get_policy_template() -> str:
        """Template cho chính sách"""
        return """## A. Tài Liệu Gốc

**Nguồn:** <SOURCE_URL>

---

## B. Summary Overview

**Hiệu lực:** <EFFECTIVE_DATE>

<SUMMARY_CONTENT>

---

## C. Key Points

<KEY_POINTS>

---

## D. Chi Tiết Chính Sách

<POLICY_DETAILS>

---

## E. Readability Optimized

<MAIN_CONTENT>
"""
