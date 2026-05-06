# Docker Deployment

This directory contains the necessary configuration files to deploy the Dependency Reader stack using Docker Compose.

Self signed with HTTPS instead of HTTP with port 8080 

The stack consists of three services:
1. **Backend:** FastAPI scanner service (`api.py`) running on Python Uvicorn.
2. **Frontend:** Flask web application (`app.py`) running on Gunicorn.
3. **Nginx:** Reverse proxy that routes traffic to the frontend and backend, and handles HTTPS.

## Prerequisites

Before deploying to another computer, ensure the following are installed:
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/) (included in Docker Desktop)
- Make sure ports `8080` and `443` are free.

## Deployment Instructions

1. **Clone the Repository**  
   Copy the entire `micac_soa_2026_sh` project folder to the target computer.

2. **Configure Environment Variables**  
   Create or modify the `.env` file in the root of the project (two folders up from this deployment folder: `../../.env`).
   ```env
   GITHUB_TOKEN=your_github_personal_access_token
   ALLOWED_ORIGINS=http://localhost:8080,https://localhost
   ```
   *(Note: The `GITHUB_TOKEN` is highly recommended to avoid GitHub API rate limits.)*

3. **Navigate to the Deployment Folder**  
   Open a terminal and navigate to this folder:
   ```bash
   cd source_code/deployment
   ```

4. **Generate SSL Certificates (Required for HTTPS)**  
   Since we use HTTPS, you must generate a new self-signed certificate on the target machine:
   ```bash
   mkdir -p certs
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout certs/key.pem -out certs/cert.pem -subj "/CN=localhost"
   ```

5. **Start the Stack**  
   Run the following command to build and start the containers in detached mode:
   ```bash
   docker compose up -build -d
   ```

6. **Access the Application**  
   To find your machine's IP address, run:
   ```bash
   hostname -I | awk '{print $1}'
   ```
   The application will be available securely at that IP address:
   - **Website:** `https://<YOUR_IP_ADDRESS>/`
   - **API Docs:** `https://<YOUR_IP_ADDRESS>/api/docs`
   
   *Note: Because you are using a self-signed certificate, your browser will show a "Not Secure" warning. Click **Advanced -> Proceed (Accept Risk)** to view the page.*

## Useful Commands

- **View Logs:**
  ```bash
  docker compose logs -f
  ```
- **Stop the Stack:**
  ```bash
  docker compose down
  ```
- **Rebuild after Code Changes:**
  ```bash
  docker compose up --build -d
  ```
