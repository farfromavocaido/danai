# danai/summarymaker/config.py
"""
Defines configuration objects and defaults for the summarymaker.
"""

import os
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class SummaryConfig:
    """
    Configuration for controlling which files/folders to include or ignore,
    plus which processors to apply, and output preferences.
    """

    # Allow one or multiple base directories for the main summarising scope
    base_directories: List[str] = field(
        default_factory=lambda: [os.getcwd()]
    )

    # Optional separate scope for the directory tree. If None or empty, we use base_directories
    tree_directories: Optional[List[str]] = None

    fully_ignored_dirs: List[str] = field(default_factory=lambda: ["__pycache__", ".git", ".idea"])
    partially_ignored_dirs: List[str] = field(default_factory=lambda: ["venv", "node_modules"])
    ignored_file_extensions: List[str] = field(default_factory=lambda: [".pyc", ".exe"])
    allowed_file_extensions: List[str] = field(default_factory=lambda: [".env", ".toml", ".json", ".config"])
    ignored_files: List[str] = field(default_factory=lambda: [".DS_Store"])
    include_file_extensions: List[str] = field(default_factory=list)

    processors: List[object] = field(default_factory=list)
    generate_tree: bool = True
    generate_summarydoc: bool = True
    exclude_empty_files_from_summary: bool = False
    output_path: str = "summaries"