# danai/summarymaker/processing/baseprocessor.py
"""
Defines the base processor interface or class for transforming file contents.
"""

from abc import ABC, abstractmethod

class BaseProcessor(ABC):
    """
    Abstract base class for file content processors.
    Each processor can modify or filter the text in a file.
    """
    @abstractmethod
    def process(self, content: str, filepath: str) -> str:
        """
        Takes in the file content and returns transformed content.
        """
        pass