import os
from aiutils import print_directory_contents, print_directory_tree, tokencount_file

ignore_files = ["printer.py"]
ignore_dirs = ["__pycache__", "venv", "node_modules", ".git"]
ignore_extensions = [".pyc"]
output_directory = "summaries"

print_directory_contents(".", output_directory, ignore_dirs, ignore_files, ignore_extensions)

print_directory_tree(".", output_directory, ignore_dirs)