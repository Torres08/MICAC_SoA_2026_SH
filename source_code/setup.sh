#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CURRENT_USER="$(whoami)"
VENV_PATH="$PROJECT_ROOT/venv"
REQ_FILE="$PROJECT_ROOT/requirements.txt"
ENV_FILE="$PROJECT_ROOT/.env"

SCANNER_WORKDIR="$PROJECT_ROOT/source_code/dependency_reader"
WEBSITE_WORKDIR="$PROJECT_ROOT/source_code/webapp"

SCANNER_SERVICE_PATH="/etc/systemd/system/scanner.service"
WEBSITE_SERVICE_PATH="/etc/systemd/system/website.service"
NGINX_SITE_PATH="/etc/nginx/sites-available/dependency_reader"
NGINX_ENABLED_PATH="/etc/nginx/sites-enabled/dependency_reader"

echo "======================================"
echo " Dependency Reader Setup"
echo "======================================"
echo "Project root : $PROJECT_ROOT"
echo "User         : $CURRENT_USER"
echo

check_path() {
    local path="$1"
    local label="$2"
    if [[ ! -e "$path" ]]; then
        echo "[ERROR] Missing $label: $path"
        exit 1
    fi
}

echo "[INFO] Validating project structure..."
check_path "$SCANNER_WORKDIR" "scanner workdir"
check_path "$WEBSITE_WORKDIR" "website workdir"
check_path "$REQ_FILE" "requirements.txt"
check_path "$SCANNER_WORKDIR/api.py" "scanner api.py"
check_path "$WEBSITE_WORKDIR/app.py" "website app.py"

echo "[INFO] Installing system packages..."
sudo apt update
sudo apt install -y python3 python3-venv python3-pip nginx curl

echo "[INFO] Creating virtual environment..."
if [[ ! -d "$VENV_PATH" ]]; then
    python3 -m venv "$VENV_PATH"
fi

echo "[INFO] Installing Python dependencies..."
# shellcheck disable=SC1091
source "$VENV_PATH/bin/activate"
python -m pip install --upgrade pip
pip install -r "$REQ_FILE"
pip install gunicorn uvicorn python-dotenv

echo "[INFO] Configuring .env..."
if [[ ! -f "$ENV_FILE" ]]; then
    touch "$ENV_FILE"
fi

if grep -q '^GITHUB_TOKEN=' "$ENV_FILE"; then
    echo "[INFO] GITHUB_TOKEN already exists in .env"
else
    read -r -s -p "Enter your GitHub token (leave empty to skip): " GITHUB_TOKEN_INPUT
    echo
    if [[ -n "${GITHUB_TOKEN_INPUT:-}" ]]; then
        echo "GITHUB_TOKEN=$GITHUB_TOKEN_INPUT" >> "$ENV_FILE"
        echo "[INFO] GITHUB_TOKEN saved to .env"
    else
        echo "[INFO] No token provided. Continuing without GitHub token."
    fi
fi

echo "[INFO] Creating scanner.service..."
sudo tee "$SCANNER_SERVICE_PATH" > /dev/null <<EOF
[Unit]
Description=Dependency Reader Scanner API
After=network.target

[Service]
User=$CURRENT_USER
WorkingDirectory=$SCANNER_WORKDIR
Environment=PYTHONPATH=$SCANNER_WORKDIR
ExecStart=$VENV_PATH/bin/uvicorn api:app --host 127.0.0.1 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

echo "[INFO] Creating website.service..."
sudo tee "$WEBSITE_SERVICE_PATH" > /dev/null <<EOF
[Unit]
Description=Dependency Reader Frontend Website
After=network.target

[Service]
User=$CURRENT_USER
WorkingDirectory=$WEBSITE_WORKDIR
ExecStart=$VENV_PATH/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

echo "[INFO] Creating Nginx site config..."
sudo tee "$NGINX_SITE_PATH" > /dev/null <<'EOF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/ {
        rewrite ^/api/(.*)$ /$1 break;
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

echo "[INFO] Enabling Nginx site..."
sudo ln -sf "$NGINX_SITE_PATH" "$NGINX_ENABLED_PATH"
sudo rm -f /etc/nginx/sites-enabled/default

echo "[INFO] Testing Nginx config..."
sudo nginx -t

echo "[INFO] Reloading systemd..."
sudo systemctl daemon-reload

echo "[INFO] Enabling services..."
sudo systemctl enable scanner
sudo systemctl enable website
sudo systemctl enable nginx

echo "[INFO] Restarting services..."
sudo systemctl restart scanner
sudo systemctl restart website
sudo systemctl restart nginx

echo
echo "======================================"
echo " Service Status"
echo "======================================"
sudo systemctl --no-pager --full status scanner | sed -n '1,12p' || true
echo
sudo systemctl --no-pager --full status website | sed -n '1,12p' || true
echo
sudo systemctl --no-pager --full status nginx | sed -n '1,12p' || true

HOST_IP="$(hostname -I | awk '{print $1}')"

echo
echo "======================================"
echo " Setup Complete"
echo "======================================"
echo "Website: http://$HOST_IP/"
echo "API docs: http://$HOST_IP/api/docs"
echo
echo "Useful checks:"
echo "  sudo journalctl -u scanner -f"
echo "  sudo journalctl -u website -f"