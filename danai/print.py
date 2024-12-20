import os
from . import tokencount_file
import mimetypes


def is_binary_file(file_path, exempt_files, exempt_extensions):
    if os.path.basename(file_path) in exempt_files:
        return False
    if any(file_path.endswith(ext) for ext in exempt_extensions):
        return False
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type is None:
        return True  # If we can't guess the type, assume it's binary
    return not mime_type.startswith('text')

# Function to print the directory contents while ignoring certain directories, files, extensions, and binary/non-readable files
def print_directory_contents(directory, output_dir, ignore_dirs, full_ignore, ignore_files, ignore_extensions, exempt_files, exempt_extensions):
    output_path = os.path.join(output_dir, 'summary.md')
    with open(output_path , 'w') as f:
        # Walk through the directory
        for root, dirs, files in os.walk(directory):
            # Modify dirs in-place to exclude ignored directories globally
            dirs[:] = [d for d in dirs if d not in full_ignore]
            dirs[:] = [d for d in dirs if d not in ignore_dirs]

            # Loop through each file in the current directory
            for name in files:
                # Skip files in ignore_files list or those with ignored extensions
                if name in ignore_files or any(name.endswith(ext) for ext in ignore_extensions):
                    continue

                # Get the full file path
                file_path = os.path.join(root, name)

                # Skip binary files and non-readable files
                if is_binary_file(file_path, exempt_files=exempt_files, exempt_extensions=exempt_extensions) or not os.access(file_path, os.R_OK):
                    continue

                # Write the file name and its contents to summary.md
                f.write(f'## {file_path}\n\n```\n')
                with open(file_path, 'r') as file:
                    tokens = tokencount_file(file_path)
                    print(f'{tokens} tokens in {file_path}')
                    f.write(file.read())
                f.write('\n```\n')
    total_tokens = tokencount_file(output_path)
    print(f'Total tokens in directory: {total_tokens}')
        

def generate_directory_tree(directory, ignore_dirs, full_ignore, prefix="", is_last=True):
    tree = []
    
    # Walk through the directory
    for root, dirs, files in os.walk(directory):
        # Sort dirs and files for consistent output
        dirs[:] = [d for d in dirs if d not in full_ignore]
        dirs[:] = sorted(dirs)
        file_count = len(files)
        dir_count = len(dirs)

        # Loop through each directory in the current level
        for i, d in enumerate(dirs):
            dir_path = os.path.join(root, d)
            is_last_dir = (i == dir_count - 1) and (file_count == 0)

            # Check if the directory is in the ignore list
            if d in ignore_dirs:
                # Include the directory in the tree but omit its contents
                tree.append(f'{prefix}{"└── " if is_last_dir else "├── "}{d}')
                tree.append(f'{prefix}    ├── //contents omitted//')
            else:
                # Include the directory and continue traversing
                tree.append(f'{prefix}{"└── " if is_last_dir else "├── "}{d}/')
                # Recurse into the directory
                tree += generate_directory_tree(os.path.join(root, d), ignore_dirs, full_ignore, prefix + ("    " if is_last_dir else "│   "), is_last_dir)

        # Loop through each file in the current directory
        sorted_files = sorted(files)
        for j, name in enumerate(sorted_files):
            is_last_file = (j == file_count - 1)
            tree.append(f'{prefix}{"└── " if is_last_file else "├── "}{name}')
        
        break  # Stop walking deeper into the directory (handle each directory individually in recursion)
    
    return tree

# Function to print the directory tree in standard format
def print_directory_tree(directory, output_dir, ignore_dirs, full_ignore):
    tree = generate_directory_tree(directory, ignore_dirs, full_ignore)
    with open(f'{output_dir}/tree.md', 'w') as f:
        f.write(f"{directory}/\n")
        f.write("\n".join(tree))
        f.write("\n")


def join_summaries(output_directory):
    open(os.path.join(output_directory, "full_summary.md"), 'w').close()
    open(os.path.join(output_directory, "tree.md"), 'w').close()
    open(os.path.join(output_directory, "summary.md"), 'w').close()
    with open(os.path.join(output_directory, "full_summary.md"), "a") as f:
        f.write("# Directory Tree\n\n")
        with open(os.path.join(output_directory, "tree.md")) as tree_file:
            f.write(tree_file.read())
        f.write("\n\n# Directory Contents\n\n")
        with open(os.path.join(output_directory, "summary.md")) as contents_file:
            f.write(contents_file.read())