
import sys
from dependency_reader.utils import (
    get_repository_link,
    fetch_repository_metadata,
    parse_dependencies,
    generate_output,
)
from dependency_reader.vulnerability_checker import check_vulnerabilities, _get_ecosystem
from dependency_reader.vitality_enricher import enrich_all_packages
from dependency_reader.risk_scorer import generate_zombie_report, save_zombie_report_json

### Previous main function (before refactor to run web):  
def main() -> None:
    print("\n=== Dependency Reader & Zombie Scanner ===\n")

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

    # Step 5 — check vulnerabilities via OSV API (Phase 1)
    scan_result = check_vulnerabilities(result)

    # Step 6 — save output.json
    if save_json and scan_result:
        generate_output(scan_result)

    # Step 7 — enrich with GitHub Vitality Metrics (Phase 2)
    ecosystem = _get_ecosystem(result["source_file"])
    vitals_map = enrich_all_packages(result["dependencies"], ecosystem)

    # Step 8 — generate Zombie Report
    report = generate_zombie_report(repo_link, scan_result, vitals_map)

    # Display a quick summary of Zombies
    zombies_count = report["scan_info"]["zombies_found"]
    vulnerabilities_count = report["scan_info"]["vulnerable_found"]
    repo_score = report["scan_info"]["repo_risk_score_100"]
    repo_status = report["scan_info"]["repo_status"]

    # Print Metrics for EVERY package FIRST
    all_packages = report.get("analysis", [])
    if all_packages:
        print(f"  \n  [PACKAGE VITALITY METRICS]")
        print(f"  * Risk Score = CVEs (up to 50) + Inactivity (up to 20) + Bus Factor (up to 15) + Neglect (up to 15)")
        print(f"  ───────────────────────────────────────────────────")
        for pkg in all_packages:
            m = pkg["metrics"]
            dep_msg = " (DEPRECATED)" if m.get("is_deprecated") else ""
            zomb_msg = " [ZOMBIE!]" if pkg.get("status") == "ZOMBIE" else ""
            
            print(f"  {pkg['package']}{dep_msg}{zomb_msg}")
            print(f"    Days since last commit : {m.get('days_since_last_commit', 'Error')}")
            print(f"    Open issues            : {m.get('open_issues', 'Error')}")
            print(f"    Maintainers (Bus Fact) : {m.get('maintainer_count', 'Error')}")
            print(f"    Risk Score             : {pkg.get('risk_score_100', 0)} / 100")
            print()

    # Display a quick summary of Zombies
    print(f"  ───────────────────────────────────────────────────")
    print(f"  Zombie Scan Complete")
    print(f"  ───────────────────────────────────────────────────")
    print(f"  Vulnerable Packages found: {vulnerabilities_count}")
    print(f"  Zombie (Unmaintained) Packages found: {zombies_count}")
    print(f"  ───────────────────────────────────────────────────")
    print(f"  OVERALL REPOSITORY SECURITY SCORE : {repo_score} / 100")
    print(f"  STATUS                            : {repo_status}")
    print(f"  ───────────────────────────────────────────────────")

    print(f"  Risk Score Formula (0-100):")
    print(f"  CVEs (up to 50) + Inactivity (up to 20) +")
    print(f"  Bus Factor (up to 15) + Issue Neglect (up to 15)")
    print(f"  ───────────────────────────────────────────────────\n")

    # Step 9 — save zombie_report.json
    if save_json:
        save_zombie_report_json(report)
    else:
        print("\n(Reports skipped — --no-save flag set)\n")


if __name__ == "__main__":
    main()