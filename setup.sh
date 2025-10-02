#!/bin/bash

# 🚀 Tushle AI Automation Dashboard - Complete Setup Script

echo "🎯 Setting up Tushle AI Automation Dashboard..."
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "PROJECT_STRUCTURE.md" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

print_status "Creating project directories..."

# Create necessary directories
mkdir -p backend/data
mkdir -p backend/reports/pdf
mkdir -p frontend/dist
mkdir -p scripts/logs

print_success "Project directories created"

# Backend setup
print_status "Setting up backend environment..."

cd backend

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_warning "Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install -r requirements.txt
print_success "Python dependencies installed"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    print_status "Creating backend .env file..."
    cp .env.example .env
    print_warning "Please update .env file with your configuration"
else
    print_warning "Backend .env file already exists"
fi

# Initialize database
if [ ! -f "data/automation_dashboard.db" ]; then
    print_status "Initializing database..."
    python ../scripts/database/create_simple_dummy_data.py
    print_success "Database initialized with test data"
else
    print_warning "Database already exists"
fi

cd ..

# Frontend setup
print_status "Setting up frontend environment..."

cd frontend

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    print_error "Node.js is required but not installed"
    print_error "Please install Node.js from https://nodejs.org/"
    exit 1
fi

# Install Node dependencies
print_status "Installing Node.js dependencies..."
npm install
print_success "Node.js dependencies installed"

# Create frontend .env file if it doesn't exist
if [ ! -f ".env.production" ]; then
    print_status "Creating frontend .env file..."
    echo "VITE_API_URL=http://localhost:8000" > .env.local
    print_success "Frontend .env file created"
fi

cd ..

# Final setup
print_status "Running final setup checks..."

# Make scripts executable
chmod +x scripts/setup/*.sh

print_success "Setup completed successfully!"
echo ""
echo "🎉 Tushle AI Automation Dashboard is ready!"
echo "==========================================="
echo ""
echo "📋 Next steps:"
echo "1. Update backend/.env with your API keys (especially GROQ_API_KEY)"
echo "2. Start the backend: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "3. Start the frontend: cd frontend && npm run dev"
echo "4. Visit http://localhost:5173 to access the dashboard"
echo ""
echo "📚 Documentation:"
echo "- Project structure: PROJECT_STRUCTURE.md"
echo "- Setup guides: docs/guides/"
echo "- API documentation: http://localhost:8000/docs (after starting backend)"
echo ""
echo "🧪 Testing:"
echo "- Test Groq setup: python scripts/testing/test_groq_setup.py"
echo "- Test PDF generation: python scripts/testing/test_pdf_llm.py"
echo ""
print_success "Happy coding! 🚀"
