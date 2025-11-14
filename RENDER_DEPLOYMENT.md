# Deploy DeepGuard AI to Render

This guide will help you deploy both the backend and frontend to Render.

## Prerequisites

- GitHub account with repository: `https://github.com/chatgptnotes/anohra.com.git`
- Render account (free): https://render.com

## Deployment Steps

### Option 1: Automatic Deployment (Blueprint)

1. **Go to Render Dashboard**
   - Visit https://dashboard.render.com

2. **Create New Blueprint**
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Select repository: `chatgptnotes/anohra.com`
   - Render will automatically detect `render.yaml`
   - Click "Apply"

3. **Wait for Deployment**
   - Backend will deploy first (takes 3-5 minutes)
   - Frontend will deploy after backend (takes 2-3 minutes)

4. **Get Your URLs**
   - Backend: `https://deepguard-api.onrender.com`
   - Frontend: `https://deepguard-frontend.onrender.com`

### Option 2: Manual Deployment

#### Step 1: Deploy Backend

1. **Create Web Service**
   - Go to Render Dashboard
   - Click "New +" → "Web Service"
   - Connect GitHub repository
   - Select repository: `chatgptnotes/anohra.com`

2. **Configure Backend**
   ```
   Name: deepguard-api
   Region: Oregon (US West)
   Branch: main
   Root Directory: backend
   Runtime: Python 3
   Build Command: pip install -r requirements-lite.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   Plan: Free
   ```

3. **Environment Variables**
   Add these in the "Environment" section:
   ```
   SECRET_KEY=<click "Generate" to auto-generate>
   ENVIRONMENT=production
   PYTHON_VERSION=3.11.0
   ```

4. **Advanced Settings**
   - Health Check Path: `/health`
   - Auto-Deploy: Yes

5. **Deploy**
   - Click "Create Web Service"
   - Wait 3-5 minutes for deployment
   - Note your backend URL: `https://deepguard-api.onrender.com`

#### Step 2: Deploy Frontend

1. **Create Static Site**
   - Go to Render Dashboard
   - Click "New +" → "Static Site"
   - Connect same GitHub repository

2. **Configure Frontend**
   ```
   Name: deepguard-frontend
   Region: Oregon (US West)
   Branch: main
   Root Directory: frontend
   Build Command: npm install && npm run build
   Publish Directory: build
   Plan: Free
   ```

3. **Environment Variables**
   ```
   REACT_APP_API_URL=https://deepguard-api.onrender.com
   REACT_APP_ENV=production
   ```

4. **Deploy**
   - Click "Create Static Site"
   - Wait 2-3 minutes for deployment
   - Your site will be live at: `https://deepguard-frontend.onrender.com`

## Post-Deployment Configuration

### Update Backend CORS

After frontend is deployed, update backend CORS:

1. Go to backend service in Render
2. Add environment variable:
   ```
   CORS_ORIGINS=https://deepguard-frontend.onrender.com
   ```
3. The service will automatically redeploy

### Custom Domain (Optional)

#### For Frontend:
1. Go to frontend service → Settings → Custom Domain
2. Add your domain: `deepguard.yourdomain.com`
3. Update DNS records as instructed by Render

#### For Backend:
1. Go to backend service → Settings → Custom Domain
2. Add your API domain: `api.deepguard.yourdomain.com`
3. Update DNS records
4. Update frontend env var: `REACT_APP_API_URL=https://api.deepguard.yourdomain.com`

## Testing Deployment

### Test Backend

```bash
# Health check
curl https://deepguard-api.onrender.com/health

# API info
curl https://deepguard-api.onrender.com/

# Test image upload (after creating account)
curl -X POST https://deepguard-api.onrender.com/api/analyze/image \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@test-image.jpg"
```

### Test Frontend

1. Visit: `https://deepguard-frontend.onrender.com`
2. Try uploading a test image
3. Check if API calls work

## Troubleshooting

### Backend Issues

**Build Failed:**
- Check build logs in Render dashboard
- Verify `requirements-lite.txt` is correct
- Make sure Python version is 3.11

**Service Crashes:**
```bash
# Check logs
# Go to backend service → Logs tab
```

**Database Errors:**
- SQLite files persist between deploys on Render
- For production, consider upgrading to PostgreSQL

### Frontend Issues

**Build Failed:**
- Check Node.js version (Render uses latest LTS)
- Verify `package.json` is correct
- Clear build cache in Render

**API Connection Errors:**
- Verify `REACT_APP_API_URL` is correct
- Check CORS settings on backend
- Inspect browser console for errors

### Common Issues

**"Module not found" errors:**
- Ensure all dependencies are in `requirements-lite.txt`
- Check for typos in import statements

**CORS errors:**
- Add frontend URL to backend CORS_ORIGINS
- Redeploy backend after adding env var

**Slow first request:**
- Render free tier spins down after 15 min of inactivity
- First request may take 30-60 seconds to spin up
- Consider upgrading to paid plan for always-on service

## Monitoring

### Health Checks

Render automatically monitors your services:
- Backend: Pings `/health` every 5 minutes
- If health check fails, service will restart

### Logs

View logs in real-time:
1. Go to service in Render dashboard
2. Click "Logs" tab
3. See live application logs

### Metrics

View service metrics:
1. Go to service in Render dashboard
2. Click "Metrics" tab
3. See CPU, memory, request metrics

## Upgrading from Free Tier

### Benefits of Paid Plans

**Starter Plan ($7/month per service):**
- Always-on (no spin down)
- Custom domains included
- More CPU/RAM
- Better performance

**Standard Plan ($25/month per service):**
- Even more resources
- Horizontal scaling
- Priority support

### When to Upgrade

Consider upgrading when:
- Users complain about slow initial load (spin-up time)
- Need consistent performance
- Want custom domain without delays
- Processing large files frequently

## Backup Strategy

### Database Backups

For SQLite (free tier):
```bash
# Backup command (run manually)
# Download database file from Render disk
```

For PostgreSQL (recommended for production):
1. Upgrade database to Render PostgreSQL
2. Automatic daily backups included
3. Point-in-time recovery available

### Configuration Backups

All configuration is in Git:
- Environment variables backed up in Render
- Infrastructure as code in `render.yaml`

## Performance Optimization

### Backend

1. **Enable caching:**
   - Add Redis for session storage
   - Cache detection results

2. **Optimize detection:**
   - Process smaller frame samples for videos
   - Use async processing

3. **Database:**
   - Migrate from SQLite to PostgreSQL
   - Add indexes to frequently queried fields

### Frontend

1. **Code splitting:**
   - Already enabled in Create React App

2. **Image optimization:**
   - Compress images before upload
   - Use WebP format

3. **CDN:**
   - Render includes CDN for static sites
   - No additional configuration needed

## Cost Estimate

**Free Tier (Perfect for testing):**
- Backend: Free (750 hours/month)
- Frontend: Free (100GB bandwidth)
- Total: $0/month

**Production Setup:**
- Backend Starter: $7/month
- Frontend (free): $0/month
- PostgreSQL: $7/month (optional)
- Total: $7-14/month

## Support

### Render Support
- Documentation: https://render.com/docs
- Community: https://community.render.com
- Status: https://status.render.com

### DeepGuard AI Issues
- GitHub: https://github.com/chatgptnotes/anohra.com/issues

## Next Steps After Deployment

1. ✅ Test all features
2. ✅ Set up monitoring
3. ✅ Add custom domain
4. ✅ Enable SSL (automatic on Render)
5. ✅ Set up database backups
6. ✅ Configure alerts
7. ✅ Share with users!

---

**Your DeepGuard AI is now live on Render! 🚀**

Backend: `https://deepguard-api.onrender.com`
Frontend: `https://deepguard-frontend.onrender.com`
