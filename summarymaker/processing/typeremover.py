# danai/summarymaker/processing/typeremover.py
"""
Processor to remove all typing hints (docstrings) from file content.
"""

import re
from .baseprocessor import BaseProcessor

class RemoveTypingHintsProcessor(BaseProcessor):
    """
    Removes all typing hints (docstrings) from the file content.
    """
    def process(self, content: str, filepath: str) -> str:
        # Regular expression to match docstrings
        docstring_pattern = re.compile(r'""".*?"""', re.DOTALL)
        return re.sub(docstring_pattern, '', content)