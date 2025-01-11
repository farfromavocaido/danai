# danai/summarymaker/processing/truncator.py
"""
Extended processor: truncates content based on extension-specific line limits,
an optional default, and a list of exceptions.
"""

import os
from typing import Optional, Dict, List
from .baseprocessor import BaseProcessor

class TruncateProcessor(BaseProcessor):
    """
    Truncates file content based on:
      1. Extension-specific line limits (via 'rules' dict).
      2. An optional 'default' line limit for extensions not in 'rules'.
      3. A list of 'exceptions' that should never be truncated.

    Usage Example:
        config.processors = [
            TruncateProcessor(
                rules={".txt": 10, ".json": 500},
                default=100,  # anything else truncated at 100 lines
                exceptions=["requirements.txt"]  # full file never truncated
            )
        ]
    """

    def __init__(
        self,
        rules: Dict[str, int],
        default: Optional[int] = None,
        exceptions: Optional[List[str]] = None
    ):
        """
        :param rules: A dict mapping file extensions (e.g. ".txt") to max line count.
        :param default: A line limit to apply if the extension isn't in rules (None => no limit).
        :param exceptions: A list of filenames or paths to NEVER truncate 
                           (matching absolute path or just basename).
        """
        self.rules = rules
        self.default = default
        self.exceptions = exceptions or []

    def process(self, content: str, filepath: str) -> str:
        # If the file is an exception, skip truncation
        if self._is_exception(filepath):
            return content

        # Extract extension
        _, ext = os.path.splitext(filepath)
        ext = ext.lower()

        # Figure out the line limit for this extension
        if ext in self.rules:
            limit = self.rules[ext]
        else:
            limit = self.default

        # If limit is None, we do not truncate this file
        if limit is None:
            return content

        lines = content.split("\n")
        if len(lines) > limit:
            truncated = lines[:limit]
            truncated.append("... [CONTENT TRUNCATED] ...")
            return "\n".join(truncated)
        return content

    def _is_exception(self, filepath: str) -> bool:
        """
        Check if 'filepath' matches any item in 'self.exceptions'.
        We'll check both absolute path and the basename for a match.
        """
        abspath = os.path.abspath(filepath)
        basename = os.path.basename(abspath)
        for ex in self.exceptions:
            # normalise it
            ex_abs = os.path.abspath(ex)
            if abspath == ex_abs or basename == ex or basename == os.path.basename(ex_abs):
                return True
        return False