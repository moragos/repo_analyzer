import re
import os

def parse_cpp_file(file_path: str):
    """
    Parses a C++ file to extract metrics.
    Returns a dictionary with:
    - loc: Lines of Code (non-empty)
    - includes: List of included files
    - classes: List of class/struct names
    """
    metrics = {
        "loc": 0,
        "includes": [],
        "classes": []
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            
        metrics["loc"] = len([line for line in lines if line.strip()])
        
        content = "".join(lines)
        
        # Regex for Includes
        # Matches #include <...> or #include "..."
        include_pattern = re.compile(r'^\s*#\s*include\s+["<](.*?)[">]', re.MULTILINE)
        metrics["includes"] = include_pattern.findall(content)
        
        # Regex for Classes and Structs
        # Simplified parser: looks for "class Name" or "struct Name"
        # This is not a full C++ parser so it might miss complex cases or have false positives
        class_pattern = re.compile(r'\b(class|struct)\s+([A-Za-z0-9_]+)\s*(?:final|:\s*[^{]+)?\s*\{')
        matches = class_pattern.findall(content)
        metrics["classes"] = [m[1] for m in matches]
        
    except Exception as e:
        # In case of read errors, just return 0s but maybe log it?
        # For now, we assume caller handles exceptions or we just return partial data
        pass
        
    return metrics
