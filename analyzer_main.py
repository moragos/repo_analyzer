import argparse
import logging
import os
import sys
import time
from datetime import datetime

# Optional tqdm
try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, desc=None):
        if desc:
            logging.info(f"{desc}...")
        return iterable

from metrics_collector import collect_metrics_for_repo, aggregate_metrics_for_dashboard
from dashboard_generator import generate_dashboard_json

def setup_logging(debug_mode: bool):
    """Configures logging for the execution."""
    level = logging.DEBUG if debug_mode else logging.INFO
    format_str = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=level, format=format_str, datefmt='%H:%M:%S')

def main():
    parser = argparse.ArgumentParser(description="Analyze C++ repository for code metrics and staleness.")
    parser.add_argument("path", help="Path to the local git repository")
    parser.add_argument("-o", "--output", default="dashboard_data.json", help="Output JSON filename")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    
    setup_logging(args.debug)
    
    repo_path = os.path.abspath(args.path)
    if not os.path.isdir(repo_path):
        logging.error(f"Invalid repository path: {repo_path}")
        sys.exit(1)
        
    start_time = time.time()
    logging.info(f"Starting analysis of {repo_path}")
    
    try:
        # Step 1: Collect Metrics
        # We pass a progress bar callback or handle tqdm inside
        logging.info("Scanning repository and collecting metrics...")
        repo_data = collect_metrics_for_repo(repo_path, debug=args.debug)
        
        # Step 2: Aggregate Metrics
        logging.info("Aggregating folder metrics...")
        aggregated_data = aggregate_metrics_for_dashboard(repo_data, repo_path)
        
        # Step 3: Generate Dashboard Data
        logging.info("Generating dashboard data...")
        generate_dashboard_json(aggregated_data, args.output)
        
        duration = time.time() - start_time
        logging.info(f"Analysis complete in {duration:.2f} seconds.")
        logging.info(f"Dashboard data written to {args.output}")
        
    except Exception as e:
        logging.error(f"An error occurred during analysis: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
