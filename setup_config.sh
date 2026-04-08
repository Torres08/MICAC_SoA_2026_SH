#!/bin/bash

set -e

echo "======================================"
echo " Dependency Reader Auto Setup"
echo "======================================"

# --------------------------------------------------
# Ask project path
# --------------------------------------------------
read -p "Enter FULL project root path: " PROJECT_PATH

if [ ! -d "$PROJECT_PATH" ]; then
    echo "[ERROR] Directory does not exist."
    exit 1
fi

cd "$PROJECT_PATH"

PROJECT_NAME="dependency_reader"
SERVICE_NAME="dependency_reader"
USER_NAME=$(whoami)

echo "[INFO] Using user: $USER_NAME"
echo "[INFO] Project path: $PROJECT_PATH"

# --------------------------------------------------
# Install system packages
# --------------------------------------------------
echo "[INFO] Installing system dependencies..."

sudo apt update
sudo apt install -y python3 python3-venv python3-pip nginx

# --------------------------------------------------
# Create virtual environment
# --------------------------------------------------
if [ ! -d "venv" ]; then
    echo "[INFO] Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

echo "[INFO] Upgrading pip..."
pip install --upgrade pip

echo "[INFO] Installing requirements..."
pip install -r requirements.txt

echo "[INFO] Installing gunicorn..."
pip install gunicorn python-dotenv

# --------------------------------------------------
# Create WSGI check
# --------------------------------------------------
if [ ! -f "wsgi.py" ]; then
    echo "[ERROR] wsgi.py not found!"
    exit 1
fi

# --------------------------------------------------
# Create systemd service
# --------------------------------------------------
echo "[INFO] Creating systemd service..."

SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

sudo bash -c "cat > $SERVICE_FILE" <<EOF
[Unit]
Description=Dependency Reader Web App
After=network.target

[Service]
User=${USER_NAME}
WorkingDirectory=${PROJECT_PATH}
ExecStart=${PROJECT_PATH}/venv/bin/gunicorn \
          --workers 3 \
          --bind 127.0.0.1:8000 \
          wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# --------------------------------------------------
# Reload systemd
# --------------------------------------------------
sudo systemctl daemon-reload
sudo systemctl enable ${SERVICE_NAME}

# --------------------------------------------------
# Configure Nginx
# --------------------------------------------------
echo "[INFO] Configuring Nginx..."

NGINX_FILE="/etc/nginx/sites-available/${PROJECT_NAME}"

sudo bash -c "cat > $NGINX_FILE" <<EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;

        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/${PROJECT_NAME} \
            /etc/nginx/sites-enabled/

sudo rm -f /etc/nginx/sites-enabled/default

sudo nginx -t

# --------------------------------------------------
# Start services
# --------------------------------------------------
echo "[INFO] Starting services..."

sudo systemctl restart ${SERVICE_NAME}
sudo systemctl restart nginx

# --------------------------------------------------
# Status check
# --------------------------------------------------
echo "======================================"
echo " Service Status"
echo "======================================"

sudo systemctl status ${SERVICE_NAME} --no-pager

IP=$(hostname -I | awk '{print $1}')

echo ""
echo "======================================"
echo " Deployment Complete"
echo "======================================"
echo "Open browser:"
echo "http://$IP"
echo ""
