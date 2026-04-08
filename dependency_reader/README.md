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

**08-04-2026**
- Added OSV API vulnerability checker (parallel fetch with ThreadPoolExecutor)
- Added REST API with FastAPI: GET /report, POST /scan
- GitHub token via .env to raise rate limit 60 → 5000 req/hr
- output.json now includes full vulnerability_report section
- No need for Libraries.io — GitHub API + PyPI/npm registry APIs cover all vitality data

---

## Phase 2 — Zombie Package Detection

**Goal:** Identify *Zombie Packages* — dependencies that are alive but unmaintained, making them high-risk supply chain attack vectors.

**APIs used (no new keys needed):**
- GitHub API (already integrated) → last commit, contributor count, open issues, archived flag
- PyPI: `https://pypi.org/pypi/{package}/json` → maps package name to GitHub repo
- npm: `https://registry.npmjs.org/{package}` → same, for JS packages

**Heuristic Risk Scoring:**
The final risk score combines two dimensions:
1. **Security Risk** (CVEs from OSV API)
2. **Maintenance Risk** (Vitality signs: Is it still alive?)

Example Heuristic Logic:
```
IF cve_count > 0 → Base Risk is HIGH
IF days_since_last_commit > 365
   AND open_issues / closed_issues > 0.5
   AND contributors <= 1
   → Package is a ZOMBIE
IF ZOMBIE and cve_count > 0 → CRITICAL RISK (Active vulnerabilities with no one to fix them)
```

**Divide & Conquer:**

| Component | File | Owner | Status |
|---|---|---|---|
| A — Repository Ingestor | `utils.py` | Student A | ✅ Done |
| B — Vitality Enricher | `vitality_enricher.py` | Student B | ✅ Done |
| C — Risk Scorer | `risk_scorer.py` | Student C | ✅ Done |

**References:**
- *On the Decay of Open-Source Software*
- *The Open Source Sustainability Crisis* (XZ Utils, Log4j)
- *Technical Lag in Software Ecosystems*

---

## Phase 2 — To-Do List

### Component A — Repository Ingestor
- [x] Parse dependency files from GitHub URL
- [x] Support 10+ dependency formats
- [ ] Extend to support GitLab URLs

### Component B — Vitality Enricher (`vitality_enricher.py`)
- [x] For each package: resolve GitHub repo via PyPI/npm registry API
- [x] Fetch last commit date, contributor count, open/closed issues, archived flag
- [x] Return structured vitality dict per package

### Component C — Risk Scorer (`risk_scorer.py`)
- [x] Define zombie thresholds (inactivity, neglect ratio, bus factor)
- [x] Combine vitality data + OSV CVE count → risk score + status
- [x] Generate `zombie_report.json`
- [ ] Add `POST /zombie-scan` endpoint to `api.py`
- [ ] Update `app_diagram.drawio` to include Phase 2 flow

---

## Current Issues

> Track what is actively being worked on.

- [x] ~~`vitality_enricher.py` — Is this package still alive and maintained? It takes a package name (e.g. express, requests) and returns its vital signs.~~
- [x] ~~`risk_scorer.py` — define and implement zombie scoring logic~~
- [ ] `POST /zombie-scan` — new API endpoint that runs full Phase 2 pipeline


---

## Phase 2 — Zombie Package Detection

**Goal:** Extend the tool into a **Tool-as-a-Service** that identifies *Zombie Packages* — dependencies that are functionally alive but dead in terms of maintenance, making them high-risk supply chain attack vectors.

**What we already have (reuse):**
- ✅ Repository Ingestor → `utils.py` (parses dependency files)
- ✅ CVE / Vulnerability data → `vulnerability_checker.py` (OSV API)
- ✅ REST API → `api.py` (FastAPI)

**What we need to add (Divide & Conquer):**

### Component A — Repository Ingestor ✅ (done)
> Owner: Student A

Already implemented in `utils.py`.
- Takes a GitHub URL → extracts package names + versions
- No changes needed

---

### Component B — Vitality Enricher (NEW → `vitality_enricher.py`)
> Owner: Student B

Queries the **GITHUB API** (free key) for each package.

Collects "Vital Signs":
- `days_since_last_commit` — inactivity indicator
- `maintainer_count` — bus factor indicator
- `is_deprecated` — explicit deprecation flag
- `open_issues_count` / `closed_issues_count` — neglect ratio
- `sourcerank` — Github.io pre-calculated health score

API reference: https://libraries.io/api

---

### Component C — Risk Scorer & JSON Generator (NEW → `risk_scorer.py`)
> Owner: Student C

Implements the **Zombie Logic** combining vitality data + existing CVE data:

```
if days_since_last_commit > 365
   AND open_issues / closed_issues > 0.5
   AND maintainer_count <= 1
   → status: ZOMBIE, risk_level: HIGH
```

Produces the final `zombie_report.json`:
```json
{
  "repository": "https://github.com/example/project",
  "scan_info": { "total_dependencies": 12, "zombies_found": 1 },
  "analysis": [
    {
      "package": "old-http-client",
      "version": "2.1.0",
      "status": "ZOMBIE",
      "cve_count": 3,
      "metrics": {
        "days_since_last_commit": 940,
        "maintainer_count": 1,
        "is_deprecated": true
      },
      "risk_level": "HIGH",
      "recommendation": "Replace with actively maintained alternative."
    }
  ]
}
```

---

## Phase 2 — To-Do List

### Component A — Repository Ingestor
- [x] Parse dependency files from GitHub URL
- [x] Support 10+ dependency formats
- [ ] Extend to support GitLab URLs

### Component B — Vitality Enricher
- [ ] Get Libraries.io API key and add `LIBRARIES_IO_KEY` to `.env`
- [ ] Create `vitality_enricher.py`
- [ ] For each package: fetch last commit date, maintainer count, deprecated flag, issue counts, sourcerank
- [ ] Return structured dict per package

### Component C — Risk Scorer
- [ ] Create `risk_scorer.py`
- [ ] Define zombie thresholds (inactivity, neglect ratio, bus factor)
- [ ] Combine vitality data + OSV CVE count into a single risk score
- [ ] Generate `zombie_report.json`
- [ ] Add `POST /zombie-scan` endpoint to `api.py`
- [ ] Update `app_diagram.drawio` to include Phase 2 flow

### References
- *On the Decay of Open-Source Software* — software aging as a security liability
- *The Open Source Sustainability Crisis* — bus factor and abandoned packages (XZ Utils, Log4j)
- *Technical Lag in Software Ecosystems* — projects stuck on old unmaintained versions


**08-04-2026**
