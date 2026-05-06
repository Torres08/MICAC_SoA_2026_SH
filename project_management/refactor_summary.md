# Ship Happens - Refactor & Security Updates

This document summarizes the recent updates, bug fixes, and security improvements made to the **Ship Happens** supply chain security tool. 

## 1. Docker Deployment & HTTPS
* **What:** Containerized the entire application (Frontend, Backend, and Nginx).
* **Why:** To make the app easy to deploy on any machine with a single command (`docker compose up`). We also added an Nginx reverse proxy to enforce HTTPS security.

## 2. Removed Hardcoded Configuration
* **What** Moved all the magic numbers (scoring weights, penalties, and thresholds) into a new file called `config/heuristic_config.json`.
* **Why:** This makes it much easier to tune the security scoring system without having to edit the Python code directly.

## 3. Filtered Bot Contributors
* **What** Updated the GitHub contributor scanner to ignore automated accounts (like Dependabot).
* **Why:** This ensures the "Bus Factor" (number of maintainers) is accurate and only counts real humans.

## 4. Fixed Score Clustering (Mean vs. Max)
* **What we did:** The tool now calculates two different scores: the "Peak Score" (the single most dangerous package) and the "Weighted Mean Score" (the average health of the whole project).
* **Why:** This gives a much clearer picture of whether a project has one bad dependency or is generally unmaintained across the board.

## 5. Secured the API (Error Handling)
* **What:** Updated the backend API to immediately reject unsupported GitLab URLs. We also masked internal server errors.
* **Why:** Masking errors prevents the website from showing messy Python stack traces to the user, which protects the server from hackers trying to gather technical information.

## 6. Fixed Concurrency Bottlenecks
* **What:** Increased the backend's worker pool limit from 2 to 10.
* **Why:** Since the tool spends a lot of time waiting for GitHub to respond, allowing it to process 10 requests at the same time makes the scanning process significantly faster.

## 7. Eliminated OSV False Positives
* **What:** Updated the vulnerability scanner to look up the *exact version* of a package, rather than just the package name.
* **Why:** Previously, the tool flagged old vulnerabilities that had already been fixed. Now, it only flags vulnerabilities that actually affect the specific version you are using.
