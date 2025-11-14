# Deployment Guide for DeepGuard AI

## Vercel Deployment

### Prerequisites
- Vercel account (https://vercel.com)
- GitHub repository connected to Vercel
- Vercel CLI installed: `npm install -g vercel`

## Option 1: Deploy Frontend to Vercel

### 1. Deploy Frontend

```bash
cd frontend
vercel
```

Follow the prompts:
- Link to existing project or create new one
- Set framework preset to "Create React App"
- Build command: `npm run build`
- Output directory: `build`

### 2. Set Environment Variables

In Vercel Dashboard → Settings → Environment Variables:
```
REACT_APP_API_URL=https://your-backend-url.com
```

### 3. Deploy

```bash
vercel --prod
```

## Option 2: Deploy Backend Separately

### Backend Deployment Options

#### A. Railway (Recommended for Python/FastAPI)

1. Go to https://railway.app
2. Connect your GitHub repository
3. Select `backend` directory as root
4. Set environment variables:
   ```
   SECRET_KEY=your-secret-key-here
   PORT=8000
   ```
5. Deploy

#### B. Render

1. Go to https://render.com
2. Create new Web Service
3. Connect GitHub repo
4. Settings:
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements-lite.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Environment Variables:
   ```
   SECRET_KEY=your-secret-key-here
   PYTHON_VERSION=3.11
   ```

#### C. Heroku

1. Install Heroku CLI
2. Create `Procfile` in backend directory:
   ```
   web: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
3. Deploy:
   ```bash
   cd backend
   heroku create deepguard-api
   git subtree push --prefix backend heroku main
   ```

#### D. AWS Lambda + API Gateway (Serverless)

1. Install serverless framework
2. Create `serverless.yml`:
   ```yaml
   service: deepguard-api
   provider:
     name: aws
     runtime: python3.11
   functions:
     api:
       handler: main.handler
       events:
         - http: ANY /
         - http: ANY /{proxy+}
   ```
3. Deploy:
   ```bash
   serverless deploy
   ```

## Option 3: Docker Deployment

### 1. Create Backend Dockerfile

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements-lite.txt .
RUN pip install --no-cache-dir -r requirements-lite.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Create Frontend Dockerfile

```dockerfile
# frontend/Dockerfile
FROM node:18-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 3. Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - SECRET_KEY=your-secret-key
    volumes:
      - ./backend/uploads:/app/uploads
      - ./backend/deepguard.db:/app/deepguard.db

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    depends_on:
      - backend
```

### 4. Deploy to Docker Host

```bash
docker-compose up -d
```

## Option 4: VPS Deployment (DigitalOcean, Linode, etc.)

### 1. Setup Server

```bash
# SSH into server
ssh root@your-server-ip

# Install dependencies
apt update
apt install python3 python3-pip nodejs npm nginx -y

# Install PM2
npm install -g pm2
```

### 2. Deploy Backend

```bash
cd /var/www
git clone https://github.com/chatgptnotes/anohra.com.git
cd anohra.com/backend

python3 -m venv venv
source venv/bin/activate
pip install -r requirements-lite.txt

# Start with PM2
pm2 start "uvicorn main:app --host 0.0.0.0 --port 8000" --name deepguard-api
pm2 save
pm2 startup
```

### 3. Deploy Frontend

```bash
cd /var/www/anohra.com/frontend
npm install
npm run build

# Configure Nginx
cat > /etc/nginx/sites-available/deepguard <<EOF
server {
    listen 80;
    server_name your-domain.com;

    location / {
        root /var/www/anohra.com/frontend/build;
        try_files \$uri /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }
}
EOF

ln -s /etc/nginx/sites-available/deepguard /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

### 4. SSL Certificate (Let's Encrypt)

```bash
apt install certbot python3-certbot-nginx -y
certbot --nginx -d your-domain.com
```

## Environment Variables

### Production Environment Variables

**Backend:**
```bash
SECRET_KEY=<generate-strong-random-key>
ENVIRONMENT=production
DATABASE_URL=sqlite:///deepguard.db  # or PostgreSQL URL
CORS_ORIGINS=https://your-frontend-url.com
MAX_FILE_SIZE=52428800  # 50MB
```

**Frontend:**
```bash
REACT_APP_API_URL=https://api.your-domain.com
REACT_APP_ENV=production
```

### Generate Secret Key

```python
import secrets
print(secrets.token_urlsafe(32))
```

## Post-Deployment Checklist

- [ ] Update SECRET_KEY in production
- [ ] Configure CORS origins
- [ ] Set up database backups
- [ ] Enable HTTPS
- [ ] Configure rate limiting
- [ ] Set up monitoring (Sentry, LogRocket)
- [ ] Configure CDN for static assets
- [ ] Set up analytics
- [ ] Test all API endpoints
- [ ] Test file uploads
- [ ] Verify authentication flow
- [ ] Load testing

## Monitoring & Maintenance

### Health Check Endpoint
```bash
curl https://api.your-domain.com/health
```

### Logs
```bash
# PM2
pm2 logs deepguard-api

# Docker
docker-compose logs -f backend

# Systemd
journalctl -u deepguard-api -f
```

### Database Backup

```bash
# SQLite
cp deepguard.db deepguard.db.backup

# Automated backup
echo "0 2 * * * cp /var/www/anohra.com/backend/deepguard.db /backups/deepguard-\$(date +\%Y\%m\%d).db" | crontab -
```

## Troubleshooting

### Backend not starting
- Check logs: `pm2 logs` or `docker logs`
- Verify Python version: `python --version`
- Check dependencies: `pip list`

### CORS errors
- Verify CORS_ORIGINS in backend
- Check API_URL in frontend

### File upload issues
- Check `uploads/` directory permissions
- Verify MAX_FILE_SIZE setting
- Check disk space

## Scaling

### Horizontal Scaling
- Use load balancer (nginx, HAProxy)
- Deploy multiple backend instances
- Share storage (S3, MinIO)
- Use Redis for session storage

### Database
- Migrate from SQLite to PostgreSQL
- Set up read replicas
- Implement caching (Redis)

## Cost Estimation

**Free Tier Options:**
- Vercel (Frontend): Free
- Railway (Backend): Free tier available
- Render (Backend): Free tier with limits

**Paid Options:**
- DigitalOcean Droplet: $6/month
- AWS EC2 t3.micro: ~$8/month
- Heroku Hobby: $7/month

## Support

For deployment issues:
- Check logs first
- Review environment variables
- Test endpoints individually
- Check firewall/security groups

---

**Next Steps:**
1. Choose deployment option
2. Set up environment variables
3. Deploy backend
4. Deploy frontend
5. Configure DNS
6. Enable HTTPS
7. Monitor and maintain
