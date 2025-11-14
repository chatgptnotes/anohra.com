#!/bin/bash

echo "🚀 DeepGuard AI - Render CLI Deployment"
echo "========================================"
echo ""

# Check if render CLI is installed
if ! command -v render &> /dev/null; then
    echo "❌ Render CLI not found!"
    echo ""
    echo "📦 Installing Render CLI..."
    echo ""

    # Install Render CLI
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        brew tap render-oss/render
        brew install render
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        curl -fsSL https://render.com/install.sh | bash
    else
        echo "Please install Render CLI manually:"
        echo "https://render.com/docs/cli"
        exit 1
    fi

    echo "✅ Render CLI installed!"
    echo ""
fi

# Check if user is logged in
echo "🔐 Checking Render authentication..."
if ! render whoami &> /dev/null; then
    echo "❌ Not logged in to Render"
    echo ""
    echo "Please run: render login"
    echo "Then run this script again."
    exit 1
fi

echo "✅ Authenticated as: $(render whoami)"
echo ""

# Deploy using Blueprint
echo "📋 Deploying with Blueprint (render.yaml)..."
echo ""

# Check if render.yaml exists
if [ ! -f "render.yaml" ]; then
    echo "❌ render.yaml not found!"
    exit 1
fi

# Deploy
render blueprint launch

echo ""
echo "🎉 Deployment initiated!"
echo ""
echo "📊 Check deployment status:"
echo "   render services list"
echo ""
echo "📝 View logs:"
echo "   render logs --service deepguard-api"
echo "   render logs --service deepguard-frontend"
echo ""
echo "🌐 Your services will be available at:"
echo "   Backend:  https://deepguard-api.onrender.com"
echo "   Frontend: https://deepguard-frontend.onrender.com"
echo ""
echo "⏳ Deployment typically takes 5-10 minutes"
echo "   Check status at: https://dashboard.render.com"
echo ""
