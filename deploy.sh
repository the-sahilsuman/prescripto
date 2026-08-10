#!/bin/bash
set -euo pipefail

DOMAIN1="user.thesahilsuman.online"
FRONTEND="http://13.127.151.21:5173"
DOMAIN2="admin.thesahilsuman.online"
ADMIN="http://13.127.151.21:5174"
EMAIL="sahilsuman890@gmail.com"

if ! command -v nginx >/dev/null 2>&1; then
    sudo apt install nginx -y
fi

sudo systemctl enable nginx
sudo systemctl start nginx
if systemctl is-active --quiet nginx; then
    echo "Nginx is Running..."
else
    echo "Ngnix not Running.... and Exiting..."
    exit 1
fi
   

sudo tee /etc/nginx/sites-available/prescripto > /dev/null <<EOF
server {
    listen 80;
    server_name $DOMAIN1;

    location / {
        proxy_pass $FRONTEND;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}

server {
    listen 80;
    server_name $DOMAIN2;

    location / {
        proxy_pass $ADMIN;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF

echo "🔗 Enabling Nginx config..."
sudo ln -sf /etc/nginx/sites-available/prescripto /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

echo "✅ Testing Nginx..."
sudo nginx -t

echo "🔄 Reloading Nginx..."
sudo systemctl reload nginx

if ! command -v certbot &> /dev/null; then
    echo "Installing Certbot..."
    sudo apt install -y certbot python3-certbot-nginx
fi

echo "🔒 Generating SSL certificates..."
sudo /usr/bin/certbot --nginx \
    -d $DOMAIN1 \
    -d $DOMAIN2 \
    --non-interactive \
    --agree-tos \
    -m $EMAIL \
    --redirect
    
    echo "🔄 Testing auto-renew..."
    sudo certbot renew --dry-run


echo "https://$DOMAIN1"
echo "https://$DOMAIN2"
