# danai/summarymaker/sample_configs.py
"""
Example 'presets' for different use cases.
You can import these to quickly configure the summarymaker.
"""

import os
from .config import SummaryConfig
from .processing import RemoveHashCommentsProcessor, TruncateProcessor

def get_dev_config() -> SummaryConfig:
    """
    Example config: only include .py files, remove # comments,
    and truncate after 300 lines. Ignores the usual suspect dirs.
    """
    return SummaryConfig(
        base_directories=[os.getcwd()],
        fully_ignored_dirs=["__pycache__", ".git", ".idea"],
        partially_ignored_dirs=["venv", "node_modules"],
        ignored_file_extensions=[],
        allowed_file_extensions=[".env", ".toml", ".json", ".config"],
        ignored_files=[".DS_Store"],
        only_include=[".py"],  # only .py
        processors=[
            RemoveHashCommentsProcessor(),
            TruncateProcessor(max_lines=300),
        ],
        generate_tree=True,
        generate_summarydoc=True,
        exclude_empty_files_from_summary=True,
        output_path="summaries_dev"
    )

def get_blueprint_config() -> SummaryConfig:
    """
    Example config: show all files except .pyc, but skip removing comments.
    """
    return SummaryConfig(
        base_directories=["/path/to/blueprints"],
        fully_ignored_dirs=["__pycache__", ".git", ".idea"],
        partially_ignored_dirs=["venv", "node_modules"],
        ignored_file_extensions=[".pyc"],
        allowed_file_extensions=[".env", ".toml", ".json", ".config"],
        ignored_files=[".DS_Store"],
        only_include=[],  # empty => include everything
        processors=[],  # no special transformations
        generate_tree=True,
        generate_summarydoc=True,
        exclude_empty_files_from_summary=False,
        output_path="summaries_blueprints"
    )