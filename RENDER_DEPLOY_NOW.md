# Deploy DeepGuard AI to Render NOW 🚀

## Option 1: Web Dashboard (Blueprint - RECOMMENDED)

This is the easiest way since you have `render.yaml` configured.

### Steps:

1. **Open Render Dashboard**
   ```
   https://dashboard.render.com/select-repo?type=blueprint
   ```

2. **Connect GitHub Repository**
   - Click "Connect account" if not connected
   - Authorize Render to access your GitHub
   - Select repository: `chatgptnotes/anohra.com`

3. **Deploy Blueprint**
   - Render will automatically detect `render.yaml`
   - Review the services:
     - `deepguard-api` (Backend)
     - `deepguard-frontend` (Frontend)
   - Click "Apply"

4. **Wait for Deployment** (5-10 minutes)
   - Backend deploys first
   - Frontend deploys after backend is ready
   - You'll see real-time logs

5. **Get Your URLs**
   - Backend: `https://deepguard-api.onrender.com`
   - Frontend: `https://deepguard-frontend.onrender.com`

## Option 2: Manual Web Deployment

If blueprint doesn't work, deploy manually:

### Deploy Backend First:

1. Go to: https://dashboard.render.com/create?type=web
2. Connect repository: `chatgptnotes/anohra.com`
3. Configure:
   ```
   Name: deepguard-api
   Region: Oregon (US West)
   Branch: main
   Root Directory: backend
   Runtime: Python 3
   Build Command: pip install -r requirements-lite.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   Instance Type: Free
   ```

4. Environment Variables (click "Advanced"):
   ```
   SECRET_KEY = [Click "Generate" button]
   ENVIRONMENT = production
   PYTHON_VERSION = 3.11.0
   ```

5. Advanced Settings:
   ```
   Health Check Path: /health
   Auto-Deploy: Yes
   ```

6. Click "Create Web Service"

7. **Wait 3-5 minutes** for backend to deploy

8. **Copy backend URL**: `https://deepguard-api.onrender.com`

### Deploy Frontend Next:

1. Go to: https://dashboard.render.com/create?type=static
2. Connect same repository
3. Configure:
   ```
   Name: deepguard-frontend
   Region: Oregon (US West)
   Branch: main
   Root Directory: frontend
   Build Command: npm install && npm run build
   Publish Directory: build
   ```

4. Environment Variables:
   ```
   REACT_APP_API_URL = https://deepguard-api.onrender.com
   REACT_APP_ENV = production
   ```

5. Click "Create Static Site"

6. **Wait 2-3 minutes** for frontend to deploy

## After Deployment

### Test Backend

```bash
# Health check
curl https://deepguard-api.onrender.com/health

# Should return:
# {"status":"healthy","timestamp":"..."}

# API info
curl https://deepguard-api.onrender.com/

# Should return:
# {"name":"DeepGuard AI","version":"1.0.0",...}
```

### Test Frontend

1. Visit: `https://deepguard-frontend.onrender.com`
2. You should see the DeepGuard AI interface
3. Try uploading a test image

### Register First User

```bash
# Register via API
curl -X POST https://deepguard-api.onrender.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your@email.com",
    "password": "yourpassword",
    "full_name": "Your Name"
  }'

# Login
curl -X POST https://deepguard-api.onrender.com/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d 'username=your@email.com&password=yourpassword'

# Save the access_token from response
```

### Test Image Analysis

```bash
# Upload and analyze image (replace TOKEN with your access token)
curl -X POST https://deepguard-api.onrender.com/api/analyze/image \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "file=@path/to/test-image.jpg"
```

## Troubleshooting

### Build Failed

**Backend:**
- Check build logs in Render dashboard
- Common fix: Ensure PYTHON_VERSION=3.11.0 is set
- Verify requirements-lite.txt is correct

**Frontend:**
- Check Node.js version (auto-detected)
- Clear build cache: Settings → Build & Deploy → Clear Build Cache
- Check if all dependencies are in package.json

### Service Not Starting

**Backend:**
1. Check logs: Dashboard → deepguard-api → Logs
2. Look for errors in startup
3. Common issues:
   - Missing environment variables
   - Port binding (should use $PORT)
   - Import errors

**Frontend:**
1. Check build output
2. Ensure REACT_APP_API_URL is set correctly
3. Verify build succeeded

### CORS Errors

If frontend can't connect to backend:

1. Go to backend service
2. Add environment variable:
   ```
   CORS_ORIGINS=https://deepguard-frontend.onrender.com
   ```
3. Save (will auto-redeploy)

### Slow First Request

- Render free tier spins down after 15 min of inactivity
- First request may take 30-60 seconds to wake up
- This is normal for free tier
- Upgrade to Starter ($7/mo) for always-on

## View Deployment Status

### In Dashboard

1. Go to: https://dashboard.render.com
2. See all services
3. Click on service name for details
4. View logs, metrics, deployments

### Monitor Logs

**Backend:**
```bash
render logs --service deepguard-api --tail -o text
```

**Frontend:**
```bash
render logs --service deepguard-frontend --tail -o text
```

## Update Backend CORS After Frontend Deploys

Once frontend is deployed:

1. Go to backend service settings
2. Add environment variable:
   ```
   CORS_ORIGINS=https://deepguard-frontend.onrender.com,http://localhost:3000
   ```
3. Service will auto-redeploy

## Custom Domain (Optional)

### For Frontend:
1. Go to frontend service → Settings
2. Click "Add Custom Domain"
3. Enter: `deepguard.yourdomain.com`
4. Add CNAME record to your DNS:
   ```
   CNAME deepguard -> deepguard-frontend.onrender.com
   ```

### For Backend:
1. Go to backend service → Settings
2. Click "Add Custom Domain"
3. Enter: `api.deepguard.yourdomain.com`
4. Add CNAME record:
   ```
   CNAME api.deepguard -> deepguard-api.onrender.com
   ```
5. Update frontend env var:
   ```
   REACT_APP_API_URL=https://api.deepguard.yourdomain.com
   ```

## Expected URLs After Deployment

**Backend API:**
- URL: `https://deepguard-api.onrender.com`
- Health: `https://deepguard-api.onrender.com/health`
- Docs: `https://deepguard-api.onrender.com/docs`
- API: `https://deepguard-api.onrender.com/api/*`

**Frontend:**
- URL: `https://deepguard-frontend.onrender.com`
- Uses backend API for all analysis

## Next Steps After Successful Deployment

1. ✅ Test all features (upload image/video/audio)
2. ✅ Create your first user account
3. ✅ Test authentication flow
4. ✅ Configure custom domain (optional)
5. ✅ Set up monitoring alerts
6. ✅ Share with users!

## Support

- Render Status: https://status.render.com
- Render Docs: https://render.com/docs
- GitHub Issues: https://github.com/chatgptnotes/anohra.com/issues

---

## Quick Start Commands

```bash
# Test backend health
curl https://deepguard-api.onrender.com/health

# Test API
curl https://deepguard-api.onrender.com/

# Open frontend
open https://deepguard-frontend.onrender.com

# View logs (if CLI is setup)
render logs --service deepguard-api --tail
```

**🎉 Your DeepGuard AI will be live in 5-10 minutes!**
