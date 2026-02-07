import os
import logging

# Supported Extensions
CPP_EXTENSIONS = {'.c', '.cpp', '.h', '.hpp', '.cc', '.cxx', '.hxx'}

def collect_files(repo_root: str):
    """
    Walks the repository and collects all relevant files.
    Returns a list of absolute file paths to analyze.
    """
    file_list = []
    
    for root, dirs, files in os.walk(repo_root):
        # Skip hidden directories (like .git)
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            _, ext = os.path.splitext(file)
            if ext.lower() in CPP_EXTENSIONS or file == 'CODEOWNERS':
                file_list.append(os.path.join(root, file))
                
    logging.debug(f"Found {len(file_list)} files to analyze.")
    return file_list

def is_cpp_file(file_path: str) -> bool:
    """Checks if the file is a C++ source/header file."""
    _, ext = os.path.splitext(file_path)
    return ext.lower() in CPP_EXTENSIONS
