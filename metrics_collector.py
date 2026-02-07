import os
import logging
try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, desc=None):
        return iterable

import scan_repo
import cpp_parser
import git_analyzer
import external_metrics

def collect_metrics_for_repo(repo_root: str, debug: bool = False):
    """
    Main function to scan repo and collect all metrics.
    Returns a flat list of file artifacts with metrics.
    """
    files = scan_repo.collect_files(repo_root)
    code_owner_rules = git_analyzer.parse_codeowners(repo_root)
    
    analyzed_files = []
    
    # Progress bar setup
    iterator = tqdm(files, desc="Analyzing files") if not debug else files
    
    for file_path in iterator:
        try:
            # 1. Basic Info
            size = os.path.getsize(file_path)
            
            # 2. Static Analysis
            cpp_metrics = cpp_parser.parse_cpp_file(file_path)
            
            # 3. Git Info
            git_info = git_analyzer.get_git_info(file_path, repo_root)
            if not git_info:
                # Default values if git info retrieval fails
                git_info = {
                    "days_silent": 0, "last_author": "Unknown", 
                    "commit_count": 0, "staleness_score": 0, "last_modified_ts": 0
                }
                
            # 4. Code Owner
            owner = git_analyzer.get_owner(file_path, repo_root, code_owner_rules)
            
            # 5. External Metrics
            ext_metrics = external_metrics.get_all_external_metrics(file_path)
            
            # Combine all
            file_data = {
                "name": os.path.basename(file_path),
                "path": file_path,
                "rel_path": os.path.relpath(file_path, repo_root),
                "type": "file",
                "size": size,
                "loc": cpp_metrics["loc"],
                "classes": cpp_metrics["classes"],
                "includes": cpp_metrics["includes"],
                "owner": owner,
                "git": git_info,
                "external": ext_metrics,
                # Placeholders for "Included By" (calculated later if needed, or simplistic approach)
                "included_by": [] 
            }
            analyzed_files.append(file_data)
            
        except Exception as e:
            logging.error(f"Failed to analyze {file_path}: {e}")
            
    # Post-processing: Calculate 'Included By'
    # Build map of Header -> [Files including it]
    # This is rough because C++ includes can be ambiguous (path relative vs absolute)
    include_map = {}
    
    # First pass: Index all files by name (simple assumption) AND relative path
    file_map = {f["name"]: f["rel_path"] for f in analyzed_files}
    
    for f in analyzed_files:
        for inc in f["includes"]:
            # Clean up include path (remove < > " ")
            inc_name = os.path.basename(inc)
            if inc_name not in include_map:
                include_map[inc_name] = []
            include_map[inc_name].append(f["rel_path"])
            
    # Assign 'Included By'
    for f in analyzed_files:
        fname = f["name"]
        if fname in include_map:
            f["included_by"] = include_map[fname]
            
    return analyzed_files

def aggregate_metrics_for_dashboard(analyzed_files: list, repo_root: str):
    """
    Converts flat file list into a nested folder structure with aggregated metrics.
    Stores full system paths for file linking.
    """
    root = {
        "name": "Root",
        "type": "folder",
        "path": ".",
        "full_path": repo_root,
        "children": {},  # Use dict for easy lookup during construction
        "metrics": _empty_metrics()
    }
    
    for file_data in analyzed_files:
        parts = file_data["rel_path"].split(os.sep)
        current = root
        
        # Traverse/Create folders
        current_abs_path = repo_root
        for i, part in enumerate(parts[:-1]):
            current_abs_path = os.path.join(current_abs_path, part)
            if part not in current["children"]:
                current["children"][part] = {
                    "name": part,
                    "type": "folder",
                    "path": os.path.join(current["path"], part) if current["path"] != "." else part,
                    "full_path": current_abs_path,
                    "children": {},
                    "metrics": _empty_metrics()
                }
            current = current["children"][part]
            
        # Add file
        filename = parts[-1]
        # Flatten metrics for the node
        file_node = {
            "name": filename,
            "type": "file",
            "path": file_data["rel_path"],
            "full_path": file_data["path"],
            "metrics": {
                "loc": file_data["loc"],
                "size": file_data["size"],
                "classes": len(file_data["classes"]),
                "classes_list": file_data["classes"],
                "includes": len(file_data["includes"]),
                "includes_list": file_data["includes"],
                "included_by": len(file_data["included_by"]),
                "included_by_list": file_data["included_by"],
                "owner": file_data["owner"],
                "staleness": file_data["git"]["staleness_score"],
                "last_author": file_data["git"]["last_author"],
                "commit_count": file_data["git"]["commit_count"],
                "misra_crit": file_data["external"]["misra_critical"],
                "misra_med": file_data["external"]["misra_medium"],
                "coverage": file_data["external"]["coverage"],
                 # Add other external metrics if needed aggregated
            }
        }
        current["children"][filename] = file_node

    # Recursive Aggregation
    _aggregate_recursive(root)
    
    # Convert 'children' dicts to lists for JSON
    _convert_children_to_list(root)
    
    # Pass the root children as the result (or the root itself)
    return root

def _empty_metrics():
    return {
        "loc": 0, "size": 0, "classes": 0, "includes": 0, "included_by": 0,
        "misra_crit": 0, "misra_med": 0, "staleness": 0, # Avg?
        "coverage": 0.0 # Avg?
    }

def _aggregate_recursive(node):
    if node["type"] == "file":
        return node["metrics"]
    
    # It's a folder
    total_loc = 0
    total_size = 0
    total_classes = 0
    total_includes = 0
    total_included_by = 0
    total_misra_crit = 0
    total_misra_med = 0
    
    staleness_sum = 0
    coverage_sum = 0
    count = 0
    
    # We also keep ownership if uniform, or "Mixed"
    owners = set()
    
    for child in node["children"].values():
        start_node_type = child.get("type", "file") # safety
        child_metrics = _aggregate_recursive(child)
        
        total_loc += child_metrics.get("loc", 0)
        total_size += child_metrics.get("size", 0)
        total_classes += child_metrics.get("classes", 0)
        total_includes += child_metrics.get("includes", 0)
        total_included_by += child_metrics.get("included_by", 0)
        total_misra_crit += child_metrics.get("misra_crit", 0)
        total_misra_med += child_metrics.get("misra_med", 0)
        
        staleness_sum += child_metrics.get("staleness", 0)
        coverage_sum += child_metrics.get("coverage", 0)
        
        if "owner" in child_metrics:
            owners.add(child_metrics["owner"])
        elif "owner" in child: # File node stores it at root of obj, Folder in metrics? No wait.
             # File node: 
             # file_node["metrics"]... no owner there in my code above?
             # Ah, I put owner in metrics for file_node in loop above. Yes.
             pass
             
        # For folders, owner might be in metrics
        if "owner" in child_metrics and child_metrics["owner"] != "Mixed":
             owners.add(child_metrics["owner"])
             
        count += 1
        
    node["metrics"]["loc"] = total_loc
    node["metrics"]["size"] = total_size
    node["metrics"]["classes"] = total_classes
    node["metrics"]["includes"] = total_includes
    node["metrics"]["included_by"] = total_included_by
    node["metrics"]["misra_crit"] = total_misra_crit
    node["metrics"]["misra_med"] = total_misra_med
    
    if count > 0:
        node["metrics"]["staleness"] = round(staleness_sum / count, 2)
        node["metrics"]["coverage"] = round(coverage_sum / count, 2)
        
    # Owner Logic for Folder
    # If all children have same owner, folder has that owner.
    # If mixed, "Mixed".
    # Need to check file nodes specifically too.
    # Actually, let's simplify:
    # If I see "owner" in child_metrics, I use it.
    
    # Wait, file_node has "owner" inside "metrics" dict in my code above:
    # "owner": file_data["owner"], INSIDE "metrics" key?
    # Yes: node["metrics"] = { ... "owner": ... }
    
    unique_owners = set()
    for child in node["children"].values():
         m = child["metrics"]
         if "owner" in m:
             unique_owners.add(m["owner"])
             
    if len(unique_owners) == 1:
        node["metrics"]["owner"] = list(unique_owners)[0]
    elif len(unique_owners) > 1:
        node["metrics"]["owner"] = "Mixed"
    else:
        node["metrics"]["owner"] = "Unassigned"

    return node["metrics"]

def _convert_children_to_list(node):
    if "children" in node and isinstance(node["children"], dict):
        # Convert dict to list
        children_list = list(node["children"].values())
        # Sort by name (folders first? or mixed?)
        # Let's sort folders first, then files
        children_list.sort(key=lambda x: (x["type"] != "folder", x["name"]))
        node["children"] = children_list
        
        for child in children_list:
            _convert_children_to_list(child)
