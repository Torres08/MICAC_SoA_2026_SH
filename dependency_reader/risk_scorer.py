"""
risk_scorer.py 

Implements the "Zombie Packages" logic.
Combines data from the OSV API (CVE checking) and the GitHub API (vitality signs)
to dynamically rank the risk of every dependency in a codebase.

bus factor 
- number of active maintainer 

"""

import json

def calculate_package_risk(package_name: str, version: str, cve_details: list, vitals: dict) -> dict:
    """
    HEURISTIC SCORING LOGIC
    =======================
    This calculates the overall risk score based on the parameters defined in the academic guidelines.
    
    1. Security Risk: Measured by active CVEs from the OSV API.
    2. Maintenance Risk: Measured by vitality metrics from GitHub API.

    Rules implemented below:
    - If cve_count > 0 → Base Risk is HIGH
    - If days_since_last_commit > 365 AND open_issues_count > 50 AND maintainer_count <= 1 → Status is ZOMBIE
    - If is_deprecated is True → Status is ZOMBIE
    - If ZOMBIE AND cve_count > 0 → CRITICAL RISK (Active vulnerabilities with no one to fix them)
    """

    # Extract clean baseline metrics
    cve_count = len(cve_details)
    
    # Handle packages where GitHub enrichment failed
    if "error" in vitals:
        return {
            "package": package_name,
            "version": version,
            "status": "UNKNOWN (Vitality Fetch Failed)",
            "risk_score_100": min(cve_count * 10, 50),  # Fallback score based only on CVEs
            "cve_count": cve_count,
            "metrics": vitals,
            "risk_level": "HIGH" if cve_count > 0 else "LOW",
            "recommendation": "Check manually. Could not retrieve GitHub metadata."
        }

    days_old = vitals.get("days_since_last_commit", 0)
    open_issues = vitals.get("open_issues_count", 0)
    maintainers = vitals.get("maintainer_count", 0)
    is_deprecated = vitals.get("is_deprecated", False)

    # 1. Calculate Numeric Score (0 - 100)
    numeric_score = 0
    if is_deprecated:
        numeric_score = 100
    else:
        # Vulnerabilities: 10 points per CVE (Max 50)
        cve_score = min(cve_count * 10, 50)
        
        # Inactivity: Up to 20 points for 1 year of inactivity
        inactivity_score = min((days_old / 365.0) * 20, 20)
        
        # Bus Factor: 15 points if 1 or 0 maintainers
        bus_score = 15 if maintainers <= 1 else 0
        
        # Neglect: Up to 15 points for >= 50 open issues
        neglect_score = min((open_issues / 50.0) * 15, 15)
        
        numeric_score = int(cve_score + inactivity_score + bus_score + neglect_score)
        numeric_score = min(numeric_score, 100)

    # 2. Determine Zombie Status
    is_zombie = False
    
    if is_deprecated:
        is_zombie = True
    elif (days_old > 365) and (open_issues > 50) and (maintainers <= 1):
        # The Bus factor died and nobody has touched accumulated bugs in a year
        is_zombie = True

    status = "ZOMBIE" if is_zombie else "ALIVE"

    # 3. Calculate Final Risk Level
    if is_zombie and cve_count > 0:
        risk_level = "CRITICAL"
        recommendation = "IMMEDIATE ACTION REQUIRED: Package has vulnerabilities and is completely unmaintained. Replace immediately."
    elif cve_count > 0:
        risk_level = "HIGH"
        recommendation = "Update package to patch known vulnerabilities."
    elif is_zombie:
        risk_level = "MEDIUM"
        recommendation = "Package is dead. Technical debt warning. Plan migration to active alternative."
    else:
        risk_level = "LOW"
        recommendation = "Package is healthy and actively maintained."

    return {
        "package": package_name,
        "version": version,
        "status": status,
        "risk_score_100": numeric_score,
        "cve_count": cve_count,
        "metrics": {
            "days_since_last_commit": days_old,
            "maintainer_count": maintainers,
            "open_issues": open_issues,
            "is_deprecated": is_deprecated,
            "github_repo": vitals.get("github_repo", "Unknown")
        },
        "risk_level": risk_level,
        "recommendation": recommendation
    }


def generate_zombie_report(repository_url: str, scanned_deps: dict, enriched_vitals: dict) -> dict:
    """
    Takes the full scan results (vulnerabilities + vitals) and builds the final JSON report.
    
    scanned_deps: From vulnerability_checker.py (contains {"vulnerability_report": {"vulnerable_packages": [...], "clean_packages": [...]}})
    enriched_vitals: From vitality_enricher.py
    """
    analysis = []
    total_zombies = 0
    total_deps = 0

    report_data = scanned_deps.get("vulnerability_report", {})

    # Process Vulnerable Packages
    for pkg in report_data.get("vulnerable_packages", []):
        name = pkg["package"]
        version = pkg["version"]
        cve_details = pkg["vulnerabilities"]
        vitals = enriched_vitals.get(name, {"error": "Missing info"})
        
        report = calculate_package_risk(name, version, cve_details, vitals)
        if report["status"] == "ZOMBIE":
            total_zombies += 1
        total_deps += 1
        analysis.append(report)

    # Process Clean Packages (No CVEs, but might be Zombies)
    for pkg_name in report_data.get("clean_packages", []):
        name = pkg_name
        version = scanned_deps.get("dependencies", {}).get(name, "unknown")
        cve_details = []  # Empty because clean
        vitals = enriched_vitals.get(name, {"error": "Missing info"})

        report = calculate_package_risk(name, version, cve_details, vitals)
        if report["status"] == "ZOMBIE":
            total_zombies += 1
        total_deps += 1
        analysis.append(report)

    # Sort analysis by Risk (CRITICAL -> HIGH -> MEDIUM -> LOW)
    risk_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    analysis.sort(key=lambda x: risk_order.get(x["risk_level"], 4))

    # Calculate overall repo score (A repository is only as secure as its weakest link)
    repo_score = 0
    if analysis:
        repo_score = max(pkg["risk_score_100"] for pkg in analysis)
        
    if repo_score >= 70:
        repo_status = "DANGEROUS (High probability of supply chain attack)"
    elif repo_score >= 40:
        repo_status = "WARNING (Approaching technical debt limits)"
    else:
        repo_status = "SAFE (Healthy dependency tree)"

    return {
        "repository": repository_url,
        "scan_info": {
            "total_dependencies": total_deps,
            "zombies_found": total_zombies,
            "vulnerable_found": len(report_data.get("vulnerable_packages", [])),
            "repo_risk_score_100": repo_score,
            "repo_status": repo_status
        },
        "analysis": analysis
    }


def save_zombie_report_json(report: dict, filepath: str = "zombie_report.json"):
    """Writes the final output as JSON."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)
    print(f"✓ Zombie report saved directly to '{filepath}'")
