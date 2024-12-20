import os
from print import print_directory_contents, print_directory_tree, join_summaries

output_directory = "summaries"

ignore_files = ["printer.py", "transcripts.txt", "package-lock.json"]
ignore_dirs = ["venv", "node_modules", ".git", "summaries", ".idea", "transcripts", "flask_session"]
ignore_extensions = [".pyc"]
full_ignore = ["__pycache__"]

exempt_files = ['Dockerfile']
exempt_extensions = ['.json', '.config', '.config.js', ".env"]

print_directory_contents(".", output_directory, ignore_dirs, full_ignore, ignore_files, ignore_extensions, exempt_files, exempt_extensions)

print_directory_tree(".", output_directory, ignore_dirs, full_ignore)

join_summaries(output_directory)