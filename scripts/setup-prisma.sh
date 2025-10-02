#!/bin/bash

# Prisma setup script for Tushle AI Dashboard

echo "🔧 Setting up Prisma for Tushle AI Dashboard..."

# Navigate to backend directory
cd backend

# Install Prisma CLI (if not already installed)
echo "📦 Installing Prisma..."
pip install prisma

# Generate Prisma client
echo "🔄 Generating Prisma client..."
prisma generate

# Run database migrations (when database is available)
echo "🗄️  Database migration ready..."
echo "Run 'prisma db push' when database is connected"

echo "✅ Prisma setup complete!"
echo ""
echo "Next steps:"
echo "1. Set up Vercel Postgres database"
echo "2. Add DATABASE_URL environment variable"
echo "3. Run 'prisma db push' to sync schema"
echo ""
