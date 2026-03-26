# Quick Build & Deploy Guide

## One-Command Build
```bash
cd survey-ai-app/frontend && npm run build
```

## Deploy to NGINX
```bash
# Copy build output
sudo cp -r dist/* /path/to/nginx/root/survey-ai/

# Or if using symlink
sudo ln -sf /path/to/survey-ai-app/frontend/dist /var/www/survey-ai
```

## Test Locally
```bash
cd survey-ai-app/frontend

# Development
npm run dev
# → http://localhost:5173

# Production preview
npm run build
npm run preview
# → http://localhost:4173/survey-ai/
```

## Key Files Checklist

- [x] `vite.config.js` - base path: `/survey-ai/`
- [x] `src/App.jsx` - basename: `/survey-ai`
- [x] `src/main.jsx` - imports `./index.css`
- [x] `src/index.css` - has all @tailwind directives
- [x] `src/components/Navbar.jsx` - uses environment variables
- [x] `.env` - development config
- [x] `.env.production` - production config
- [x] `tailwind.config.js` - content patterns correct

## NGINX Config
```nginx
location /survey-ai/ {
    alias /path/to/dist/;
    try_files $uri $uri/ /index.html;
}

location /api/ {
    proxy_pass http://localhost:8001;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}
```

## Verify Build
```bash
# Check dist directory exists
ls -la survey-ai-app/frontend/dist/

# Check index.html
cat survey-ai-app/frontend/dist/index.html | head -20

# Check build size
du -sh survey-ai-app/frontend/dist/
```

## Common Issues & Fixes

| Problem | Solution |
|---------|----------|
| Assets 404 | Check base path in vite.config.js |
| Tailwind not applied | Verify index.css imports and tailwind.config.js |
| Routes broken | Add basename to Router |
| API fails | Check NGINX proxy configuration |
| Page refresh 404 | Add try_files rule in NGINX |

---

**Status**: ✅ Ready to Deploy
