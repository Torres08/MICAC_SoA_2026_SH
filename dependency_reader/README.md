# Dependency Reader
Divide and Conquer

## Objective

Script to:
  1. Accept a public repository link.
  2. Parse dependencies from metadata.
  3. Check packages against known vulnerabilities (OSV API).
  4. Output `output.json` with full dependency + vulnerability report.
  5. Create and API to use it 

## Files
- `app_diagram.drawio`: Workflow diagram.
- `output.json`: Last scan output (auto-generated, not committed).
- `main.py`: CLI script — run this directly to scan a repo.
- `utils.py`: GitHub API fetching + dependency file parsers.
- `vulnerability_checker.py`: OSV API integration + report builder.
- `api.py`: REST API — exposes the scan as HTTP endpoints.


## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file (never committed):
```bash 
GITHUB_TOKEN=ghp_yourtoken      # optional, boosts rate limit 60 → 5000 req/hr
ALLOWED_ORIGINS=http://localhost:3000   # for the API CORS
```

## Usage

### CLI Script
```bash
python main.py
# Enter a public GitHub URL when prompted, e.g. https://github.com/axios/axios
# Saves result to output.json automatically
# -- no save to not save the json 
```

### REST API
```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

| Method | Endpoint  | Description                          |
|--------|-----------|--------------------------------------|
| GET    | `/report` | Returns the last saved `output.json` |
| POST   | `/scan`   | Triggers a new scan for a repo URL   |
| GET    | `/docs`   | Interactive Swagger UI               |

**Example scan via curl:**
```bash
curl -X POST 'http://localhost:8000/scan' \
  -H 'Content-Type: application/json' \
  -d '{"repo_url": "https://github.com/axios/axios"}'
```

## Supported Dependency Files
`requirements.txt`, `package.json`, `Pipfile`, `pyproject.toml`, `poetry.lock`,
`yarn.lock`, `package-lock.json`, `Gemfile`, `go.mod`, `Cargo.toml`

## To-Do List:
- [x] **Create Diagram**: Design the workflow in `app_diagram.drawio`.
- [x] **Read Repository Metadata**: Access and read repository metadata to locate dependency files.
- [x] **Read Dependencies**: Parse the metadata to identify dependencies.
- [x] **Generate Output**: Create `output.json` with the parsed dependencies.
- [x] **Vulnerability Check**: Query OSV API for known CVEs per package.
- [x] **REST API**: Expose the scan as HTTP endpoints for the web UI.

## Notes 

**07-04-2026**
- lets start creating a flowchart: workflow of app
- https://www.lucidchart.com/pages/what-is-a-flowchart-tutorial
- create a venv and version Python 3.13.5 (stable), add gitingore to ingore venv 
- now we can read name, only public repositories 
- logic of the repository extraction 
  - extract repository name + owner 
  - GitHub API URL (this retrieve the data) + get the json
  - https://api.github.com/repos/psf/requests/contents 