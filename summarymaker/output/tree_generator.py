# danai/summarymaker/output/tree_generator.py
"""
Generates a 'pretty' ASCII directory tree representation, saving it to tree.md.

Supports:
- Fully ignored directories (excluded entirely).
- Partially ignored directories (included but marked as '# contents omitted').
"""

import os
from typing import List, Dict, Set
from ..config import SummaryConfig
from ..filtering.filters import FileInfo

class TreeGenerator:
    @staticmethod
    def generate(config: SummaryConfig, included_files: List[FileInfo]) -> None:
        """
        Build a textual ASCII representation of the directory tree, ignoring
        fully_ignored_dirs and marking partially_ignored_dirs as omitted.
        If config.tree_directories is provided and non-empty, we scope the tree
        to those directories only. Otherwise, we use config.base_directories.

        Saves the output to 'tree.md' inside config.output_path.
        """
        output_file = os.path.join(config.output_path, "tree.md")
        os.makedirs(config.output_path, exist_ok=True)

        # Determine the directories to walk for the tree
        if config.tree_directories and len(config.tree_directories) > 0:
            top_scope = config.tree_directories
        else:
            top_scope = config.base_directories

        # Build the dir_map from scratch for the tree
        dir_map = {}  # type: Dict[str, Dict[str, Set[str]]]

        def ensure_dir_in_map(d: str):
            if d not in dir_map:
                dir_map[d] = {"subdirs": set(), "files": set()}

        # Walk each top-scope directory
        for base_dir in top_scope:
            for root, dirs, files in os.walk(base_dir):
                root_abs = os.path.abspath(root)

                # Skip if any segment is fully ignored
                if _is_tree_ignored(root_abs, config):
                    dirs[:] = []  # don't descend further
                    continue

                ensure_dir_in_map(root_abs)

                filtered_dirs = []
                for d in dirs:
                    subdir_abs = os.path.abspath(os.path.join(root_abs, d))

                    # If fully ignored, skip
                    if _is_tree_ignored(subdir_abs, config):
                        continue

                    # If partially ignored, add a special marker to the subdir list
                    if _contains_partially_ignored(subdir_abs, config):
                        dir_map[root_abs]["subdirs"].add(f"{d}/ # contents omitted")
                        # we do NOT descend into it
                        continue

                    # Otherwise, keep it and ensure it’s in the map
                    filtered_dirs.append(d)
                    ensure_dir_in_map(subdir_abs)
                    dir_map[root_abs]["subdirs"].add(d)

                # Modify in-place so os.walk won't descend into partially ignored or fully ignored
                dirs[:] = filtered_dirs

                # Add files to the map
                for f in files:
                    dir_map[root_abs]["files"].add(f)

        # Generate the tree lines
        lines = ["# Directory Tree\n"]

        for top_dir in top_scope:
            top_abs = os.path.abspath(top_dir)
            lines.append(f"{top_abs}/")

            if top_abs not in dir_map:
                lines.append("")  # blank line
                continue

            subdirs_sorted = sorted(dir_map[top_abs]["subdirs"])
            files_sorted = sorted(dir_map[top_abs]["files"])
            items = subdirs_sorted + files_sorted

            for idx, item in enumerate(items):
                is_last = (idx == len(items) - 1)

                # If we previously appended "dir # contents omitted", treat it as a special "directory" label
                # but do NOT expand it further
                if item.endswith("# contents omitted"):
                    prefix_char = "└── " if is_last else "├── "
                    lines.append(prefix_char + item)
                    continue

                path_item = os.path.join(top_abs, item)
                if os.path.isdir(path_item):
                    prefix_char = ""  # we'll manage prefix in recursion
                    lines += _build_ascii_tree(
                        config, path_item, prefix="", is_last=is_last, dir_map=dir_map
                    )
                else:
                    prefix_char = "└── " if is_last else "├── "
                    lines.append(prefix_char + item)
            lines.append("")

        # Write out
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")


def _build_ascii_tree(
    config: SummaryConfig,
    current_path: str,
    prefix: str,
    is_last: bool,
    dir_map: Dict[str, Dict[str, Set[str]]]
) -> List[str]:
    """
    Recursively build lines for current_path in an ASCII tree style.
    """
    lines = []
    current_name = os.path.basename(current_path)

    branch_prefix = "└── " if is_last else "├── "
    lines.append(prefix + branch_prefix + current_name)

    # If partially ignored, show # contents omitted (though we already handle that above)
    if _contains_partially_ignored(current_path, config):
        lines.append(prefix + ("    " if is_last else "│   ") + "# contents omitted")
        return lines

    sub_prefix = prefix + ("    " if is_last else "│   ")

    # If not in dir_map, no subdirectories or files
    if current_path not in dir_map:
        return lines

    subdirs_sorted = sorted(dir_map[current_path]["subdirs"])
    files_sorted = sorted(dir_map[current_path]["files"])
    items = subdirs_sorted + files_sorted

    for idx, item in enumerate(items):
        path_item = os.path.join(current_path, item)
        last_item = (idx == len(items) - 1)

        if item.endswith("# contents omitted"):
            # Already flagged as partial
            file_prefix = sub_prefix + ("└── " if last_item else "├── ")
            lines.append(file_prefix + item)
            continue

        if os.path.isdir(path_item):
            lines += _build_ascii_tree(config, path_item, sub_prefix, last_item, dir_map)
        else:
            file_prefix = sub_prefix + ("└── " if last_item else "├── ")
            lines.append(file_prefix + item)

    return lines


def _is_tree_ignored(path: str, config: SummaryConfig) -> bool:
    """
    Return True if any path segment is in fully_ignored_dirs.
    E.g., if path = /Users/.../project/0_projectmanagement
    and '0_projectmanagement' is in fully_ignored_dirs, skip it entirely.
    """
    parts = os.path.normpath(path).split(os.sep)
    # e.g. ["Users", "aidan...", "Documents", "...", "0_projectmanagement"]
    for segment in parts:
        if segment in config.fully_ignored_dirs:
            return True
    return False


def _contains_partially_ignored(folder_path: str, config: SummaryConfig) -> bool:
    """
    Return True if the final segment of folder_path is in partially_ignored_dirs.
    i.e., we show the folder but omit contents.
    """
    folder_name = os.path.basename(os.path.normpath(folder_path))
    return folder_name in config.partially_ignored_dirs