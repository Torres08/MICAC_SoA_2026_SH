# Dependency Reader
Divide and Conquer

## Objective

Script to:
  1. Accept a public repository link.
  2. Parse dependencies from metadata.
  3. Output `output.json` (dummy data).

## Files
- `app_diagram.drawio`: Workflow diagram.
- `output.json`: Example output.
- `main.py`: Script implementation.

## To-Do List:
- [x] **Create Diagram**: Design the workflow in `app_diagram.drawio`.
- [x] **Read Repository Metadata**: Access and read repository metadata to locate dependency files.
- [ ] **Read Dependencies**: Parse the metadata to identify dependencies.
- [ ] **Generate Output**: Create `output.json` with the parsed dependencies.


## Notes 

- 07-04-2026
- lets start creating a flowchart: workflow of app
- https://www.lucidchart.com/pages/what-is-a-flowchart-tutorial
- create a venv and version Python 3.13.5 (stable), add gitingore to ingore venv 
- now we can read name, only public repositories 
- logic of the repository extraction 
  - extract repository name + owner 
  - GitHub API URL (this retrieve the data) + get the json
  - https://api.github.com/repos/psf/requests/contents 