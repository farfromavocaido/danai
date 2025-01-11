# danai/summarymaker/output/summary_generator.py
"""
Generates a file summarising the contents of included files.
"""

import os
from typing import List
from ..config import SummaryConfig
from ..filtering.filters import FileInfo

class SummaryGenerator:
    @staticmethod
    def generate(config: SummaryConfig, included_files: List[FileInfo]) -> None:
        """
        Writes out a 'summary.md' (or whichever name you prefer)
        containing the processed contents of each file.
        """
        output_file = os.path.join(config.output_path, "summary.md")
        os.makedirs(config.output_path, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("# Directory Contents\n\n")

            # Sort files by path for consistent output
            sorted_files = sorted(included_files, key=lambda x: x.path)
            for fi in sorted_files:
                folder = os.path.dirname(fi.path)
                if _contains_partially_ignored(folder, config):
                    # Skip summarising partially-ignored directories
                    continue

                # Skip empty files if config says so
                if config.exclude_empty_files_from_summary and not fi.processed_content.strip():
                    continue

                rel_file = _make_rel_path(fi.path, config)
                f.write(f"## {rel_file}\n\n")
                f.write("```\n")
                f.write(fi.processed_content)
                f.write("\n```\n\n")

def _make_rel_path(path: str, config: SummaryConfig) -> str:
    """
    Convert an absolute path to something relative
    to any of the base directories, if possible.
    """
    for base_dir in config.base_directories:
        try:
            rel = os.path.relpath(path, base_dir)
            if not rel.startswith(".."):
                return rel
        except ValueError:
            continue
    return path

def _contains_partially_ignored(folder_path: str, config: SummaryConfig) -> bool:
    """
    Check if any of the partially_ignored_dirs appear in this folder's path segments.
    """
    parts = folder_path.split(os.sep)
    for p in parts:
        if p in config.partially_ignored_dirs:
            return True
    return False