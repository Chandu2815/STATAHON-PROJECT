#!/bin/bash
# Deploy Script for Survey AI on statquery.in
# Run this on your server as: bash deploy-survey-ai.sh

set -e

echo "🚀 Deploying Survey AI Frontend..."

# Step 1: Create directories
echo "📁 Creating directories..."
sudo mkdir -p /var/www/survey-ai/dist

# Step 2: Update NGINX config
echo "⚙️ Updating NGINX configuration..."
sudo tee /etc/nginx/sites-available/statquery > /dev/null << 'EOF'
server {
    listen 80;
    server_name statquery.in;

    # Survey AI Frontend
    location /survey-ai/ {
        alias /var/www/survey-ai/dist/;
        try_files $uri $uri/ /index.html;
        
        location ~ \.(js|css)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
        
        location = /index.html {
            expires -1;
            add_header Cache-Control "no-cache, no-store, must-revalidate";
        }
    }

    # API Proxy
    location /api/ai/ {
        proxy_pass http://127.0.0.1:8002/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/health {
        proxy_pass http://127.0.0.1:8002/health;
    }
}
EOF

# Step 3: Enable site
echo "🔗 Enabling NGINX site..."
sudo ln -sf /etc/nginx/sites-available/statquery /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Step 4: Test NGINX
echo "✅ Testing NGINX configuration..."
sudo nginx -t

# Step 5: Restart NGINX
echo "🔄 Restarting NGINX..."
sudo systemctl restart nginx

# Step 6: Set permissions
echo "🔐 Setting permissions..."
sudo chown -R www-data:www-data /var/www/survey-ai
sudo chmod -R 755 /var/www/survey-ai

echo ""
echo "✅ NGINX configuration updated!"
echo ""
echo "⚠️  NEXT STEP: Deploy the frontend files"
echo ""
echo "From your local machine, run:"
echo "  cd survey-ai-app/frontend"
echo "  npm run build"
echo "  scp -r dist/* user@statquery.in:/var/www/survey-ai/dist/"
echo ""
echo "Then verify:"
echo "  curl http://statquery.in/survey-ai/"
echo "  curl http://statquery.in/api/ai/health"
