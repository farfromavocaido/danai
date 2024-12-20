import os
from danai import printall

output_directory = "summaries"

ignore_files = ["printer.py", "transcripts.txt", "package-lock.json"]
ignore_dirs = ["venv", "node_modules", ".git", "summaries", ".idea", "transcripts", "flask_session"]
ignore_extensions = [".pyc"]
full_ignore = ["__pycache__"]

exempt_files = ['Dockerfile']
exempt_extensions = ['.json', '.config', '.config.js', ".env"]

printall(os.getcwd(), output_directory, ignore_dirs, full_ignore, ignore_files, ignore_extensions, exempt_files, exempt_extensions)

