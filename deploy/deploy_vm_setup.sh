#!/bin/bash
set -e

APP_DIR="$HOME/book_catalog_stage2"

sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip nginx

python3 -m venv "$APP_DIR/venv"
source "$APP_DIR/venv/bin/activate"
pip install -r "$APP_DIR/requirements.txt"
python "$APP_DIR/init_db.py"

sed "s|\$USER|$USER|g" "$APP_DIR/deploy/bookcatalog.service" | sudo tee /etc/systemd/system/bookcatalog.service > /dev/null
sudo cp "$APP_DIR/deploy/nginx_bookcatalog.conf" /etc/nginx/sites-available/bookcatalog
sudo ln -sf /etc/nginx/sites-available/bookcatalog /etc/nginx/sites-enabled/bookcatalog
sudo rm -f /etc/nginx/sites-enabled/default

sudo systemctl daemon-reload
sudo systemctl enable bookcatalog
sudo systemctl restart bookcatalog
sudo nginx -t
sudo systemctl restart nginx
