# Vercel Environment Variables Setup Guide

## Required Environment Variables for Tushle AI Dashboard

### Database (from Vercel Postgres)
DATABASE_URL="[paste your PRISMA_DATABASE_URL here]"
POSTGRES_URL="[paste your POSTGRES_URL here]" 
PRISMA_DATABASE_URL="[paste your PRISMA_DATABASE_URL here]"

### AI Service
GROQ_API_KEY="[your Groq API key from console.groq.com]"

### Security
SECRET_KEY="KiYXjvhnO_eYBz_9WlFNlLZ8mvezzIZk3zVjUW7pPOY"

### Optional
ENVIRONMENT="production"

## Setup Instructions:
1. Copy PRISMA_DATABASE_URL value and paste it as DATABASE_URL
2. Add all variables in Vercel dashboard under Settings > Environment Variables
3. Set environment scope to: Production, Preview, Development
4. Redeploy your application

## Database Commands (after deployment):
- Check connection: Visit /api/health endpoint
- Your Prisma schema will auto-sync with the database
