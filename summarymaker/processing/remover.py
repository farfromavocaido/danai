"""
Processor to remove comments from various file types.
"""

import re
from .baseprocessor import BaseProcessor

class RemoveCommentsProcessor(BaseProcessor):
    """
    Removes comments from various file types.
    """
    def __init__(self, extensions):
        self.extensions = extensions

    def process(self, content: str, filepath: str) -> str:
        ext = filepath.split('.')[-1]
        if ext in self.extensions:
            if ext == 'py':
                return self._remove_python_comments(content)
            elif ext == 'js':
                return self._remove_js_comments(content)
            elif ext == 'css':
                return self._remove_css_comments(content)
            elif ext == 'html':
                return self._remove_html_comments(content)
            elif ext in ['rb', 'erb']:
                return self._remove_ruby_comments(content)
            else:
                return self._remove_general_comments(content)
        return content

    def _remove_python_comments(self, content: str) -> str:
        lines = content.split("\n")
        new_lines = []
        for line in lines:
            if line.strip().startswith("#"):
                continue
            new_lines.append(line)
        return "\n".join(new_lines)

    def _remove_js_comments(self, content: str) -> str:
        # Remove single-line and multi-line comments
        content = re.sub(r'//.*', '', content)
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        return content

    def _remove_css_comments(self, content: str) -> str:
        # Remove multi-line comments
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        return content

    def _remove_html_comments(self, content: str) -> str:
        # Remove HTML comments
        content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
        return content

    def _remove_ruby_comments(self, content: str) -> str:
        # Remove single-line comments
        lines = content.split("\n")
        new_lines = []
        for line in lines:
            if line.strip().startswith("#"):
                continue
            new_lines.append(line)
        return "\n".join(new_lines)

    def _remove_general_comments(self, content: str) -> str:
        # Remove lines that start with a '#' or '//'
        lines = content.split("\n")
        new_lines = []
        for line in lines:
            if line.strip().startswith("#") or line.strip().startswith("//"):
                continue
            new_lines.append(line)
        return "\n".join(new_lines)