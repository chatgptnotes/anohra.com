# Render CLI Deployment Guide

## Quick Start

Deploy DeepGuard AI to Render using the CLI with one command:

```bash
./deploy-render.sh
```

## Manual Steps

### 1. Install Render CLI

#### macOS
```bash
brew tap render-oss/render
brew install render
```

#### Linux
```bash
curl -fsSL https://render.com/install.sh | bash
```

#### Windows
```bash
# Using Scoop
scoop install render
```

### 2. Authenticate

```bash
render login
```

This will open a browser window to authenticate. Follow the prompts.

### 3. Verify Authentication

```bash
render whoami
```

Should display your Render account email.

### 4. Deploy with Blueprint

From the project root:

```bash
render blueprint launch
```

This will:
- Parse `render.yaml`
- Create both backend and frontend services
- Configure environment variables
- Start deployment

### 5. Monitor Deployment

```bash
# List all services
render services list

# Watch backend deployment
render logs --service deepguard-api --tail

# Watch frontend deployment
render logs --service deepguard-frontend --tail
```

## CLI Commands Reference

### Service Management

```bash
# List all services
render services list

# Get service info
render services get deepguard-api

# Restart service
render services restart deepguard-api

# Scale service (paid plans only)
render services scale deepguard-api --num-instances 2
```

### Logs

```bash
# View recent logs
render logs --service deepguard-api

# Tail logs (follow)
render logs --service deepguard-api --tail

# Filter logs
render logs --service deepguard-api --filter "ERROR"

# Get logs from specific time
render logs --service deepguard-api --since 1h
```

### Environment Variables

```bash
# List env vars
render env list --service deepguard-api

# Set env var
render env set --service deepguard-api SECRET_KEY=your-secret-key

# Delete env var
render env unset --service deepguard-api VARIABLE_NAME
```

### Deployments

```bash
# List deployments
render deploys list --service deepguard-api

# Get deployment details
render deploys get <deploy-id> --service deepguard-api

# Trigger manual deployment
render services deploy deepguard-api
```

### Shell Access

```bash
# Open shell to service (paid plans only)
render shell --service deepguard-api

# Run one-off command
render run --service deepguard-api "python manage.py migrate"
```

## Advanced Deployment

### Deploy Specific Branch

```bash
# Modify render.yaml temporarily
render blueprint launch --branch staging
```

### Deploy with Custom Name

```bash
# Edit service names in render.yaml
# Then deploy
render blueprint launch
```

### Update Existing Services

```bash
# After changing render.yaml
render blueprint sync
```

## Environment Variables Setup

### Generate Secret Key

```bash
# Generate a secure secret key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Set Backend Variables

```bash
render env set --service deepguard-api \
  SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))") \
  ENVIRONMENT=production \
  PYTHON_VERSION=3.11.0
```

### Set Frontend Variables

```bash
render env set --service deepguard-frontend \
  REACT_APP_API_URL=https://deepguard-api.onrender.com \
  REACT_APP_ENV=production
```

## Troubleshooting

### Build Failures

```bash
# Check build logs
render logs --service deepguard-api --filter "build"

# Common issues:
# - Missing dependencies: Check requirements-lite.txt
# - Python version: Ensure PYTHON_VERSION=3.11.0
# - Memory issues: Upgrade to paid plan
```

### Deployment Stuck

```bash
# Check deployment status
render deploys list --service deepguard-api

# Cancel current deployment
render deploys cancel <deploy-id> --service deepguard-api

# Retry
render services deploy deepguard-api
```

### Service Not Responding

```bash
# Check service health
render services get deepguard-api

# View recent errors
render logs --service deepguard-api --filter "ERROR" --tail

# Restart service
render services restart deepguard-api
```

### Authentication Issues

```bash
# Logout
render logout

# Login again
render login

# Verify
render whoami
```

## CI/CD Integration

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Render

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install Render CLI
        run: |
          curl -fsSL https://render.com/install.sh | bash
          echo "$HOME/.render/bin" >> $GITHUB_PATH

      - name: Deploy to Render
        env:
          RENDER_API_KEY: ${{ secrets.RENDER_API_KEY }}
        run: |
          render blueprint sync
```

### Get API Key

```bash
# Generate API key at:
# https://dashboard.render.com/u/settings/api-keys
```

## Monitoring

### Health Checks

```bash
# Check backend health
curl https://deepguard-api.onrender.com/health

# Monitor continuously
watch -n 30 'curl -s https://deepguard-api.onrender.com/health | jq'
```

### Performance Metrics

```bash
# View service metrics in dashboard
# Or use Render API
curl -H "Authorization: Bearer $RENDER_API_KEY" \
  https://api.render.com/v1/services/<service-id>/metrics
```

## Backup & Restore

### Database Backup

```bash
# Connect to service shell
render shell --service deepguard-api

# Backup database
cp deepguard.db /tmp/backup-$(date +%Y%m%d).db

# Download backup (from local machine)
render disk download --service deepguard-api \
  --source /app/deepguard.db \
  --dest ./backups/deepguard-$(date +%Y%m%d).db
```

### Restore Database

```bash
# Upload backup
render disk upload --service deepguard-api \
  --source ./backups/deepguard-20250115.db \
  --dest /app/deepguard.db

# Restart service
render services restart deepguard-api
```

## Cost Management

### Check Usage

```bash
# View current plan
render services get deepguard-api | grep plan

# Monitor bandwidth
# Check in dashboard: https://dashboard.render.com
```

### Upgrade Service

```bash
# Upgrade to Starter plan ($7/month)
# Must be done via dashboard or API
# Dashboard: https://dashboard.render.com
```

## Cleanup

### Delete Services

```bash
# Delete frontend
render services delete deepguard-frontend

# Delete backend
render services delete deepguard-api

# Or delete all via blueprint
render blueprint delete
```

## Best Practices

1. **Use Blueprint:** Always use `render.yaml` for reproducible deployments
2. **Environment Variables:** Never commit secrets, use Render env vars
3. **Health Checks:** Configure health check endpoints
4. **Monitoring:** Set up log alerts for errors
5. **Backups:** Regular database backups (automated with PostgreSQL)
6. **Staging:** Use separate services for staging/production
7. **Secrets:** Rotate SECRET_KEY regularly

## Quick Commands Cheatsheet

```bash
# Deploy
render blueprint launch

# View logs
render logs --service deepguard-api --tail

# Restart
render services restart deepguard-api

# Set env var
render env set --service deepguard-api KEY=value

# Check status
render services list

# Open dashboard
open https://dashboard.render.com

# Get service URL
render services get deepguard-api | grep url
```

## Support

- Render Docs: https://render.com/docs/cli
- CLI Reference: https://render.com/docs/cli-reference
- Community: https://community.render.com
- Status: https://status.render.com

## Next Steps

After successful deployment:

1. ✅ Test all endpoints
2. ✅ Configure custom domain
3. ✅ Set up monitoring alerts
4. ✅ Enable auto-deploy from Git
5. ✅ Configure backups
6. ✅ Review security settings

---

**DeepGuard AI is now deployed on Render! 🚀**

Backend: `https://deepguard-api.onrender.com`
Frontend: `https://deepguard-frontend.onrender.com`
