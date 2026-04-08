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
    https://github.com/boto/boto3
    https://github.com/axios/axios
    https://github.com/gin-gonic/gin
    https://github.com/ansible/ansible

now check if they're deprecated - vulnerability checker 
- OSV API (Open Source Vulnerabilities)  https://osv.dev 

Authentication (Optional but Recommended):
    The app reads from the GitHub API. Without a token, GitHub limits your IP
    to 60 requests per hour. By providing a Personal Access Token (with NO scopes
    selected) via the `.env` file, the limit is boosted to 5,000 requests per hour.
    
    Setup your token in dependency_reader/.env:
    GITHUB_TOKEN=ghp_yourtokenhere
"""

import sys
from utils import (
    get_repository_link,
    fetch_repository_metadata,
    parse_dependencies,
    display_dependencies,
    generate_output,
)
from vulnerability_checker import check_vulnerabilities


def main() -> None:
    print("\n=== Dependency Reader ===\n")

    # Check flags
    save_json = "--no-save" not in sys.argv

    # Step 1 — get & validate repository link
    repo_link = get_repository_link()
    if not repo_link:
        sys.exit(1)

    # Step 2 — fetch root-level file listing
    metadata = fetch_repository_metadata(repo_link)
    if metadata is None:
        print("[ERR] Could not retrieve repository metadata. Exiting.")
        sys.exit(1)

    # Step 3 — parse dependencies
    result = parse_dependencies(metadata)
    if result is None:
        print("No dependencies to display.")
        sys.exit(0)

    # Step 4 — display in terminal
    display_dependencies(result)

    # Step 5 — check vulnerabilities via OSV API
    result = check_vulnerabilities(result)

    # Step 6 — save to JSON
    if save_json and result:
        generate_output(result)
    elif not save_json:
        print("\n(output.json skipped — --no-save flag set)\n")


if __name__ == "__main__":
    main()