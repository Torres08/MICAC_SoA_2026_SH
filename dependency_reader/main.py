"""
Dependency Reader — main entry point.

Usage:
    python main.py [--no-save]

Flags:
    --no-save   Print dependencies to the terminal only (skip output.json).

Workflow:
    1. Prompt for a public repository URL
    2. Validate it (format + public visibility via GitHub API)
    3. Fetch the repository's root file listing
    4. Locate and parse the first supported dependency file
    5. Display results in the terminal
    6. Optionally save to output.json

Supported dependency files (checked in this order):
    requirements.txt, package.json, Pipfile, pyproject.toml,
    poetry.lock, yarn.lock, package-lock.json, Gemfile, go.mod, Cargo.toml

Setup:
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    python main.py

Try:
    python main.py --no-save
    https://github.com/boto/boto3 0 
    https://github.com/axios/axios 100
    https://github.com/gin-gonic/gin 100 
    https://github.com/ansible/ansible 83 

now check if they're deprecated - vulnerability checker 
- OSV API (Open Source Vulnerabilities)  https://osv.dev 

Authentication (Optional but Recommended):
    The app reads from the GitHub API. Without a token, GitHub limits your IP
    to 60 requests per hour. By providing a Personal Access Token (with NO scopes
    selected) via the `.env` file, the limit is boosted to 5,000 requests per hour.
    
    Setup your token in .env:
    GITHUB_TOKEN=ghp_yourtokenhere
"""

import sys
from utils import (
    get_repository_link,
    fetch_repository_metadata,
    parse_dependencies,
    generate_output,
)
from vulnerability_checker import check_vulnerabilities, _get_ecosystem
from vitality_enricher import enrich_all_packages
from risk_scorer import generate_zombie_report, save_zombie_report_json

def run_analysis(repo_link: str, save: bool = True):
    """
    Core analysis engine usable by CLI and Web API.
    Returns the zombie report dictionary.
    """

    # Step 2 — fetch repository metadata
    metadata = fetch_repository_metadata(repo_link)
    if metadata is None:
        raise Exception("Could not retrieve repository metadata")

    # Step 3 — parse dependencies
    result = parse_dependencies(metadata)
    if result is None:
        raise Exception("No dependencies found")

    # Step 4 — vulnerability scan
    scan_result = check_vulnerabilities(result)

    if save and scan_result:
        generate_output(scan_result)

    # Step 5 — vitality enrichment
    ecosystem = _get_ecosystem(result["source_file"])
    vitals_map = enrich_all_packages(result["dependencies"], ecosystem)

    # Step 6 — zombie report
    report = generate_zombie_report(repo_link, scan_result, vitals_map)

    if save:
        save_zombie_report_json(report)

    return report
  
def main() -> None:
    print("\n=== Dependency Reader & Zombie Scanner ===\n")

    save = "--no-save" not in sys.argv

    repo_link = get_repository_link()
    if not repo_link:
        sys.exit(1)
    try:
        report = run_analysis(repo_link, save=save)
    except Exception as e:
        print(f"[ERR] {e}")
        sys.exit(1)

    print("\nScan completed successfully.\n")

if __name__ == "__main__":
    main()

