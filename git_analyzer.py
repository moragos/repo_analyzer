import os
import subprocess
import time
from typing import Dict, Any, Optional

def get_git_info(file_path: str, repo_root: str) -> Optional[Dict[str, Any]]:
    """Extracts commit count, last author, and staleness info."""
    try:
        # Rel path for git commands
        rel_path = os.path.relpath(file_path, repo_root)
        
        # Get unix timestamp and author name of last commit
        cmd_log = ['git', 'log', '-1', '--format=%ct|%an', rel_path]
        output_log = subprocess.check_output(cmd_log, cwd=repo_root, stderr=subprocess.DEVNULL).decode('utf-8').strip()
        
        if not output_log:
            return None

        timestamp_str, author = output_log.split('|', 1)
        last_modified = float(timestamp_str)
        days_silent = (time.time() - last_modified) / (24 * 3600)

        # Get commit count (all time or since X years? Implementation plan said "integration logic", sticking to general for now)
        # Using 3 years as default derived from staleness script logic usually
        since_date = "3.years.ago" 
        cmd_count = ['git', 'rev-list', '--count', f'--since={since_date}', 'HEAD', '--', rel_path]
        output_count = subprocess.check_output(cmd_count, cwd=repo_root, stderr=subprocess.DEVNULL).decode('utf-8').strip()
        commit_count = int(output_count) if output_count else 0
        
        # Staleness score (0-100), 100 is > 3 years silent
        staleness_score = min(100, (days_silent / (365 * 3)) * 100)

        return {
            "days_silent": round(days_silent, 2),
            "last_author": author,
            "commit_count": commit_count,
            "staleness_score": round(staleness_score, 2),
            "last_modified_ts": last_modified
        }
    except Exception:
        return None

def parse_codeowners(repo_root: str) -> Dict[str, str]:
    """
    Parses CODEOWNERS file to build a map of pattern -> owner.
    Checks .github/CODEOWNERS, .gitlab/CODEOWNERS, or root CODEOWNERS.
    """
    possible_locations = [
        os.path.join(repo_root, "CODEOWNERS"),
        os.path.join(repo_root, ".github", "CODEOWNERS"),
        os.path.join(repo_root, ".gitlab", "CODEOWNERS"),
        os.path.join(repo_root, "docs", "CODEOWNERS"),
    ]
    
    codeowners_file = None
    for loc in possible_locations:
        if os.path.exists(loc):
            codeowners_file = loc
            break
            
    if not codeowners_file:
        return {}
        
    owners_map = {} # Simple list of (pattern, owner) tuples would be better for glob matching
                    # But for now, we'll return a list of rules
    
    rules = []
    
    try:
        with open(codeowners_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                parts = line.split()
                if len(parts) >= 2:
                    pattern = parts[0]
                    owner = parts[1] # First owner only for simplicity
                    rules.append((pattern, owner))
    except Exception:
        pass
        
    return rules

def get_owner(file_path: str, repo_root: str, rules: list) -> str:
    """Matches file path against codeowner rules."""
    # This is a simplified matcher. Real CODEOWNERS uses .gitignore style globbing.
    # We will use fnmatch for basic support.
    import fnmatch
    
    rel_path = os.path.relpath(file_path, repo_root).replace(os.sep, '/')
    
    # Iterate in reverse to find last matching rule (standard precedence)
    for pattern, owner in reversed(rules):
        # Handle "folder/" pattern matching anything inside
        if pattern.endswith('/'):
            if rel_path.startswith(pattern) or rel_path == pattern[:-1]:
                return owner
        # Handle wildcard
        elif fnmatch.fnmatch(rel_path, pattern):
            return owner
            
    return "Unassigned"
