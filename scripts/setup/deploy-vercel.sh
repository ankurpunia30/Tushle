#!/bin/bash

# 🚀 Vercel Deployment Script for Tushle AI Dashboard

echo "🎯 Preparing Tushle AI Dashboard for Vercel deployment..."
echo "======================================================"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "PROJECT_STRUCTURE.md" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

print_status "Step 1: Building frontend for production..."
cd frontend
npm install
npm run build
cd ..
print_success "Frontend built successfully"

print_status "Step 2: Verifying Vercel configuration..."
if [ ! -f "vercel.json" ]; then
    echo "❌ vercel.json not found"
    exit 1
fi

if [ ! -f "api/index.py" ]; then
    echo "❌ api/index.py not found"
    exit 1
fi

if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found"
    exit 1
fi

print_success "Vercel configuration verified"

print_status "Step 3: Checking environment variables..."
if [ ! -f "frontend/.env.production" ]; then
    print_warning "frontend/.env.production not found - creating template"
    echo "VITE_API_URL=https://your-vercel-url.vercel.app/api" > frontend/.env.production
fi

print_status "Step 4: Git preparation..."
git add .
git status

print_success "🎉 Project ready for Vercel deployment!"
echo ""
echo "📋 Next steps:"
echo "1. Push to GitHub: git commit -m 'Deploy to Vercel' && git push"
echo "2. Connect to Vercel: https://vercel.com/dashboard"
echo "3. Set environment variables in Vercel dashboard:"
echo "   - GROQ_API_KEY=your_groq_api_key"
echo "   - SECRET_KEY=your_secret_key"
echo "   - DATABASE_URL=your_database_url"
echo ""
echo "📚 Full deployment guide: docs/guides/vercel-deploy.md"
echo ""
echo "🚀 Happy deploying!"
