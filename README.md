# MICAC_SoA_2026_SH
### Project Name: Ship Happens
### Authors and Acknowledgment
- Ariana Sofia Domingues Vaz Silva Alves
- Greivin Sanchez Garita
- Juan Luis Torres Ramos

## Project Overview
The primary objective of this framework is to mitigate risks within the Software Supply Chain by identifying "Zombie Packages". These are defined as dependencies that, despite having no documented vulnerabilities (CVEs), have been abandoned by their maintainers. These "stale" components represent a critical security blind spot, as they are unlikely to receive patches for future exploits.

To address this, the system implements a risk heuristic that evaluates every dependency on a scale of 0 to 100. This score determines if a package has reached a "zombie state" based on four safety pillars:

* **Vulnerability Exposure:** Cross-referencing with the OSV (Open Source Vulnerability) database.
* **Maintenance Vitality:** Detection of project stagnation through commit frequency analysis.
* **Maintenance Redundancy:** Calculating the "Bus Factor" to identify dependencies reliant on a single point of failure.
* **Community Health:** Assessing issue neglect as a lead indicator of package abandonment.

A dependency is formally classified as a Zombie Package if it exceeds the 100-point risk threshold or carries an explicit deprecation flag. Consequently, the final repository grade (**Safe**, **Warning**, or **Dangerous**) is dictated by the highest risk score found within its dependency tree.

## Repository Structure
The repository is organized into the following areas:

### Source Code
* `dependency_reader/`: Core backend analysis engine.
* `webapp/`: Frontend interface for data visualization.

### Project Management
* `Docs/Workflow.md`: Documentation of Git protocols and team collaboration standards.
* `Docs/Meeting_minutes.md`: Chronological record of project sessions and decisions.

### Documentation
The report for this project is maintained and updated via Overleaf [here](https://www.overleaf.com/1311323137tcwpffgfycgw#b24c23).