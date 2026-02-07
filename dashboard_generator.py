import json
import os

def generate_dashboard_json(aggregated_data: dict, output_path: str):
    """
    Writes the aggregated data structure to a JSON file.
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(aggregated_data, f, indent=2)
            
    except Exception as e:
        raise IOError(f"Failed to write dashboard data to {output_path}: {e}")
