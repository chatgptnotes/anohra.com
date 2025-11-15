#!/bin/bash

echo "🔍 Checking DeepGuard AI Render Deployment Status"
echo "=================================================="
echo ""

# Check Backend
echo "📡 Testing Backend API..."
backend_status=$(curl -s -o /dev/null -w "%{http_code}" https://deepguard-api.onrender.com/health)

if [ "$backend_status" = "200" ]; then
    echo "✅ Backend is LIVE (Status: $backend_status)"
    echo "   URL: https://deepguard-api.onrender.com"

    # Get health check response
    echo ""
    echo "   Health Check Response:"
    curl -s https://deepguard-api.onrender.com/health | python3 -m json.tool
else
    echo "❌ Backend is DOWN (Status: $backend_status)"
    echo "   Check logs at: https://dashboard.render.com"
fi

echo ""
echo "---"
echo ""

# Check Frontend
echo "🌐 Testing Frontend..."
frontend_status=$(curl -s -o /dev/null -w "%{http_code}" https://deepguard-frontend.onrender.com)

if [ "$frontend_status" = "200" ]; then
    echo "✅ Frontend is LIVE (Status: $frontend_status)"
    echo "   URL: https://deepguard-frontend.onrender.com"
else
    echo "❌ Frontend is DOWN or NOT READY (Status: $frontend_status)"
    echo "   This usually means:"
    echo "   1. Build is still in progress (wait 2-3 minutes)"
    echo "   2. Build failed (check logs)"
    echo "   3. Static files not found (verify build directory)"
    echo ""
    echo "   Check status at: https://dashboard.render.com"
fi

echo ""
echo "=================================================="
echo ""
echo "🔗 Quick Links:"
echo "   Dashboard: https://dashboard.render.com"
echo "   Backend Service: https://dashboard.render.com/web/deepguard-api"
echo "   Frontend Service: https://dashboard.render.com/static/deepguard-frontend"
echo ""
