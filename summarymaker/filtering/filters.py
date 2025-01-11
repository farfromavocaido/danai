# danai/summarymaker/filtering/filters.py
"""
Handles logic for including or excluding directories/files.
"""

import os
import mimetypes
from dataclasses import dataclass
from typing import List

from ..config import SummaryConfig

@dataclass
class FileInfo:
    """
    Holds basic information about a file, including its
    final 'processed content' once all transformations are applied.
    """
    path: str
    processed_content: str = ""

def collect_included_files(config: SummaryConfig) -> List[FileInfo]:
    """
    Recursively walk each directory in 'config.base_directories', 
    applying ignore/include logic to figure out which files to keep.
    Returns a list of FileInfo objects for included files.
    """
    included_files: List[FileInfo] = []

    # Ensure output directory doesn't get included
    output_abs = os.path.abspath(config.output_path)

    for base_dir in config.base_directories:
        for root, dirs, files in os.walk(base_dir):
            root_abs = os.path.abspath(root)

            # FULLY-IGNORED directories: remove them from scanning
            dirs[:] = [d for d in dirs if d not in config.fully_ignored_dirs]

            # PARTIALLY-IGNORED directories: we want them to appear in the tree, 
            # but we skip scanning inside. So we remove them from 'dirs'.
            filtered_dirs = []
            for d in dirs:
                if d in config.partially_ignored_dirs:
                    # skip scanning inside
                    # do not add it to filtered_dirs so os.walk doesn't descend
                    pass
                else:
                    filtered_dirs.append(d)
            dirs[:] = filtered_dirs

            # For each file in this folder, decide if we keep it
            for filename in files:
                file_path = os.path.join(root, filename)
                file_ext = os.path.splitext(filename)[1].lower()

                # Exclude anything in the output folder
                if output_abs in os.path.abspath(file_path):
                    continue

                # Check ignore-lists
                if filename in config.ignored_files:
                    continue

                # Skip ignored extensions unless explicitly allowed
                if file_ext in config.ignored_file_extensions:
                    if file_ext not in config.allowed_file_extensions:
                        continue

                # If include_file_extensions is non-empty, skip anything not in that list
                if config.include_file_extensions and file_ext not in config.include_file_extensions:
                    continue

                # Check if file is likely binary (unless exempt)
                if is_binary_file(file_path, config.allowed_file_extensions):
                    if file_ext not in config.allowed_file_extensions:
                        continue

                included_files.append(FileInfo(path=file_path))

    return included_files

def is_binary_file(file_path: str, allowed_extensions: List[str]) -> bool:
    """
    Checks if file is binary using 'mimetypes'. If the extension is
    explicitly exempted, we treat it as non-binary by definition.
    """
    _, ext = os.path.splitext(file_path)
    if ext in allowed_extensions:
        return False

    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type is None:
        # If we cannot guess the type, treat as binary
        return True
    return not mime_type.startswith("text")