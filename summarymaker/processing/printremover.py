"""
Processor to remove all print statements from file content.
"""

import re
from .baseprocessor import BaseProcessor

class RemovePrintStatementsProcessor(BaseProcessor):
    """
    Removes all print statements from the file content.
    """
    def process(self, content: str, filepath: str) -> str:
        # Regular expression to match print statements
        print_pattern = re.compile(r'print\(.*?\)\s*', re.DOTALL)
        return re.sub(print_pattern, '', content)