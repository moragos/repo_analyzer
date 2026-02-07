# C++ Repository Analyzer & Dashboard

A Python-based tool to analyze C++ repositories, collecting code metrics, git staleness instights, and code ownership data. The results are visualized in an interactive, browsable HTML dashboard.

## Features

- **Code Metrics**: Lines of Code (LOC), File Size, Number of Classes, Includes, and "Included By" counts.
- **Git Integration**:
  - Staleness Score: Identifies code that hasn't been touched in a long time.
  - Ownership: Parses `CODEOWNERS` files to assign ownership to files/folders.
  - Last Author & Commit Counts.
- **Interactive Dashboard**:
  - TreeGrid layout for browsing the repository structure.
  - Collapsible panels for navigation and details.
  - Searchable/Sortable data (via the UI structure).
  - Open files directly from the dashboard.
- **Extensible**: Placeholders for external metrics like MISRA violations and Code Coverage.

## Screenshot

(Add a screenshot of your dashboard here)
![Dashboard Screenshot](path/to/screenshot.png)

## Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/repo_analyzer.git
    cd repo_analyzer
    ```
2.  **Requirements**:
    - Python 3.6+
    - `tqdm` (optional, for progress bars)

    **Using Pip:**
    ```bash
    pip install tqdm
    ```

    **Using Conda:**
    ```bash
    conda env create -f environment.yml
    conda activate repo_analyzer
    ```

## Usage

Run the analyzer on a local C++ repository:

```bash
python analyzer_main.py /path/to/cpp_repo --output dashboard_data.json
```

**Arguments:**
- `path`: Path to the root of the C++ repository to analyze.
- `-o`, `--output`: Path to the output JSON file (default: `dashboard_data.json`).
- `--debug`: Enable debug logging.

## Visualization

1.  Open `metrics_dashboard.html` in a modern web browser.
2.  Click the **Load JSON** (folder icon) button in the left sidebar.
3.  Select the generated `dashboard_data.json` file.
4.  Browse the tree, click rows to see details, and right-click files to copy paths.

## Architecture

The tool is composed of several modular Python scripts and a frontend dashboard.

### Data Flow Diagram

![Data Flow Diagram](https://mermaid.ink/img/Z3JhcGggVEQKICAgIEFbIlVzZXIiXSAtLT58IlJ1bnMgU2NyaXB0InwgQlsiYW5hbHl6ZXJfbWFpbi5weSJdCiAgICBCIC0tPnwiU2NhbnMifCBDeyJGaWxlIFN5c3RlbSJ9CiAgICBDIC0tPnwiUmVhZHMgRmlsZXMvQ09ERU9XTkVSUyJ8IERbInNjYW5fcmVwby5weSAmIGdpdF9hbmFseXplci5weSJdCiAgICBDIC0tPnwiUGFyc2VzIEMrKyJ8IEVbImNwcF9wYXJzZXIucHkiXQogICAgRCAtLT4gR1sibWV0cmljc19jb2xsZWN0b3IucHkiXQogICAgRSAtLT4gRwogICAgRyAtLT58IkZldGNoIEV4dGVybmFsIE1ldHJpY3MifCBGWyJleHRlcm5hbF9tZXRyaWNzLnB5Il0KICAgIEYgLS0-IEcKICAgIEcgLS0-fCJBZ2dyZWdhdGVzIEZvbGRlcnMifCBIWyJEYXRhIFN0cnVjdHVyZSJdCiAgICBIIC0tPnwiR2VuZXJhdGVzInwgSVsiZGFzaGJvYXJkX2RhdGEuanNvbiJdCiAgICBJIC0tPiBKWyJtZXRyaWNzX2Rhc2hib2FyZC5odG1sIl0KICAgIEogLS0-fCJEaXNwbGF5cyJ8IEtbIkJyb3dzZXIgVUkgKFRyZWVHcmlkKSJd)

### Class/Module Overview

![Class Diagram](https://mermaid.ink/img/Y2xhc3NEaWFncmFtCiAgICBjbGFzcyBBbmFseXplck1haW4gewogICAgICAgICttYWluKCkKICAgICAgICArcGFyc2VfYXJncygpCiAgICAgICAgK3NldHVwX2xvZ2dpbmcoKQogICAgfQogICAgY2xhc3MgTWV0cmljc0NvbGxlY3RvciB7CiAgICAgICAgK2NvbGxlY3RfZmlsZV9tZXRyaWNzKGZpbGVfcGF0aCk6IEZpbGVOb2RlCiAgICAgICAgK2FnZ3JlZ2F0ZV9mb2xkZXJfbWV0cmljcyhmb2xkZXJfbm9kZSk6IEZvbGRlck5vZGUKICAgIH0KICAgIGNsYXNzIEV4dGVybmFsTWV0cmljc0ludGVyZmFjZSB7CiAgICAgICAgPDxpbnRlcmZhY2U-PgogICAgICAgICtnZXRfYWxsX21ldHJpY3MoZmlsZV9wYXRoKTogRGljdAogICAgfQogICAgY2xhc3MgR2l0QW5hbHl6ZXIgewogICAgICAgICtnZXRfZ2l0X2luZm8oZmlsZV9wYXRoKTogRGljdAogICAgICAgICtwYXJzZV9jb2Rlb3duZXJzKHJlcG9fcm9vdCk6IERpY3QKICAgICAgICArZ2V0X293bmVyKGZpbGVfcGF0aCk6IFN0cmluZwogICAgfQogICAgY2xhc3MgQ3BwUGFyc2VyIHsKICAgICAgICArcGFyc2VfZmlsZShmaWxlX3BhdGgpOiBEaWN0CiAgICB9CiAgICBBbmFseXplck1haW4gLS0-IE1ldHJpY3NDb2xsZWN0b3IKICAgIE1ldHJpY3NDb2xsZWN0b3IgLS0-IENwcFBhcnNlcgogICAgTWV0cmljc0NvbGxlY3RvciAtLT4gR2l0QW5hbHl6ZXIKICAgIE1ldHJpY3NDb2xsZWN0b3IgLS0-IEV4dGVybmFsTWV0cmljc0ludGVyZmFjZQ==)

- **`analyzer_main.py`**: Entry point. Handles CLI arguments and orchestration.
- **`scan_repo.py`**: File system scanner. Identifies C++ files.
- **`cpp_parser.py`**: Static analysis. Uses Regex to count classes, includes, and LOC.
- **`git_analyzer.py`**: Git interactions. Uses `git log` for history and parses `CODEOWNERS`.
- **`metrics_collector.py`**: Data aggregation. Combines all metrics into a single tree structure.
- **`dashboard_generator.py`**: JSON output generation.
- **`metrics_dashboard.html`**: The frontend. A standalone HTML file that visualizes the JSON data.

## Running Tests

To run the unit tests:

```bash
python -m unittest discover tests
```
