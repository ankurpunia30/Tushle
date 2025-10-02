# 🚀 Vercel Deployment Guide - Tushle AI Dashboard

## 📋 Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **GitHub Repository**: Push your code to GitHub
3. **Groq API Key**: Get your API key from [console.groq.com](https://console.groq.com)

## 🛠️ Pre-Deployment Setup

### 1. Install Vercel CLI (Optional)
```bash
npm install -g vercel
vercel login
```

### 2. Verify Project Structure
Ensure your project has these Vercel-specific files:
```
lehar/
├── vercel.json              # Vercel configuration
├── api/index.py             # Backend API handler
├── requirements.txt         # Python dependencies
├── frontend/
│   ├── .env.production     # Production environment
│   └── dist/               # Build output
└── backend/                # FastAPI application
```

## 🔧 Environment Variables Setup

### Required Environment Variables
Set these in your Vercel dashboard or using CLI:

```bash
# Using Vercel CLI
vercel env add GROQ_API_KEY
vercel env add SECRET_KEY
vercel env add DATABASE_URL

# Or set in Vercel Dashboard:
# Project Settings > Environment Variables
```

### Environment Variables List
- `GROQ_API_KEY`: Your Groq AI API key
- `SECRET_KEY`: JWT secret key (generate random string)
- `DATABASE_URL`: SQLite database URL or external database

## 🚀 Deployment Steps

### Method 1: GitHub Integration (Recommended)

1. **Push to GitHub**
   ```bash
   # First create repository at: https://github.com/ankurpunia30/tushle-ai-dashboard
   git add .
   git commit -m "Deploy to Vercel"
   git push origin main
   ```

2. **Connect to Vercel**
   - Visit [vercel.com/dashboard](https://vercel.com/dashboard)
   - Click "New Project"
   - Import your GitHub repository
   - Vercel will auto-detect the configuration

3. **Configure Environment Variables**
   - In project settings, add environment variables
   - Deploy the project

### Method 2: Vercel CLI

1. **Deploy from Local**
   ```bash
   cd /path/to/lehar
   vercel --prod
   ```

2. **Follow CLI Prompts**
   - Link to existing project or create new
   - Set environment variables when prompted

## 📁 Project Configuration

### Frontend Build Settings
```json
{
  "buildCommand": "cd frontend && npm run build",
  "outputDirectory": "frontend/dist",
  "installCommand": "cd frontend && npm install"
}
```

### Backend API Settings
- **Runtime**: Python 3.9
- **Entry Point**: `api/index.py`
- **Max Duration**: 30 seconds
- **Max Lambda Size**: 50MB

## 🔍 Troubleshooting

### Common Issues

1. **Build Failures**
   ```bash
   # Check build logs in Vercel dashboard
   # Common fixes:
   cd frontend && npm install --legacy-peer-deps
   cd frontend && npm run build
   ```

2. **API Errors**
   ```bash
   # Check Function logs in Vercel dashboard
   # Verify environment variables are set
   # Check Python dependencies in requirements.txt
   ```

3. **Database Issues**
   ```bash
   # For SQLite in production, consider external database
   # PostgreSQL recommended for production:
   # DATABASE_URL=postgresql://user:pass@host:port/db
   ```

## 🌐 Custom Domain (Optional)

1. **Add Domain in Vercel**
   - Project Settings > Domains
   - Add your custom domain
   - Follow DNS configuration instructions

2. **Update Environment Variables**
   ```bash
   # Update VITE_API_URL if using custom domain
   VITE_API_URL=https://yourdomain.com/api
   ```

## 📊 Post-Deployment Verification

### 1. Check Frontend
- Visit your Vercel URL
- Test login functionality
- Verify content discovery works

### 2. Check Backend API
- Visit `https://your-vercel-url.vercel.app/api/docs`
- Test API endpoints
- Verify PDF generation works

### 3. Test Complete Workflow
```bash
# Test fashion content discovery
curl -X POST "https://your-vercel-url.vercel.app/api/v1/content/discover-topics" \
  -H "Content-Type: application/json" \
  -d '{"field": "fashion", "content_type": "social_media"}'

# Test PDF generation
curl -X POST "https://your-vercel-url.vercel.app/api/v1/content/generate-pdf-report" \
  -H "Content-Type: application/json" \
  -d '{"field": "fashion", "content_type": "social_media"}'
```

## 🔐 Security Considerations

### Production Security Checklist
- ✅ Strong SECRET_KEY (32+ characters)
- ✅ GROQ_API_KEY properly secured
- ✅ Database credentials secured
- ✅ CORS properly configured
- ✅ HTTPS enabled (automatic with Vercel)

## 📈 Performance Optimization

### Frontend Optimization
```typescript
// Already configured in vite.config.ts
export default defineConfig({
  build: {
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: undefined,
      },
    },
  },
});
```

### Backend Optimization
- Cold start optimization in serverless functions
- Database connection pooling (if using external DB)
- Caching strategies for trending data

## 🚦 Continuous Deployment

### Automatic Deployments
- **Main Branch**: Auto-deploy to production
- **Feature Branches**: Auto-deploy to preview URLs
- **Pull Requests**: Generate preview deployments

### Deployment Hooks
```bash
# Optional: Add deployment hooks in vercel.json
{
  "functions": {
    "api/index.py": {
      "runtime": "python3.9",
      "maxDuration": 30
    }
  }
}
```

## 📞 Support and Monitoring

### Vercel Dashboard Features
- **Analytics**: Track performance and usage
- **Logs**: Monitor function execution
- **Speed Insights**: Optimize performance

### Monitoring Setup
```bash
# Add monitoring to your application
# Consider: Sentry, LogRocket, or Vercel Analytics
```

## 🎯 Success Metrics

After successful deployment, you should have:

- ✅ **Frontend**: Accessible at Vercel URL
- ✅ **Backend API**: Functioning at `/api/*` routes
- ✅ **Content Engine**: 15 sources working
- ✅ **PDF Generation**: Tushle AI reports downloadable
- ✅ **LLM Integration**: Authentic recommendations
- ✅ **Authentication**: User login/register working
- ✅ **Performance**: Fast loading times

## 🔄 Update Workflow

### For Code Updates
```bash
git add .
git commit -m "Update: feature description"
git push origin main
# Vercel auto-deploys
```

### For Environment Variables
```bash
vercel env add NEW_VARIABLE
vercel --prod  # Redeploy with new variables
```

---

**🎉 Your Tushle AI Dashboard is now live on Vercel!**

Access your deployment at: `https://your-project-name.vercel.app`

For issues, check the Vercel dashboard logs and function monitoring.