#!/usr/bin/env bash
# Render build script for backend

set -o errexit

# Install dependencies
pip install --upgrade pip
pip install -r requirements-lite.txt

# Create necessary directories
mkdir -p uploads

echo "Backend build completed successfully!"
