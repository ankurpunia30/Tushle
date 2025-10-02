# 🚀 Quick Groq API Setup Guide

## Get Your FREE Groq API Key (2 minutes)

### Step 1: Sign Up for Groq (Free)
1. Visit: **https://console.groq.com/**
2. Click "Sign Up" and create a free account
3. Verify your email address

### Step 2: Generate API Key
1. Log into Groq Console
2. Click "API Keys" in the sidebar
3. Click "Create API Key" 
4. Give it a name (e.g., "Content Engine")
5. Copy the generated key (starts with `gsk_...`)

### Step 3: Add Key to Your Project
1. Open `backend/.env` file
2. Find the line: `GROQ_API_KEY=your_groq_api_key_here`
3. Replace with: `GROQ_API_KEY=gsk_your_actual_key_here`
4. Save the file

### Step 4: Install Dependencies
```bash
cd backend
pip install aiohttp pytrends beautifulsoup4 lxml requests
```

### Step 5: Test Your Setup
```bash
cd backend
python -c "
import asyncio
import os
from app.services.llm_service import groq_service

async def test():
    result = await groq_service.extract_keywords_and_hashtags('AI marketing', 'technology')
    print('✅ Groq working!' if result.get('keywords') else '❌ Check your API key')

asyncio.run(test())
"
```

## Free Models Available

✅ **llama3-8b-8192** (Default) - Fast, high quality  
✅ **mixtral-8x7b-32768** - Best quality, larger context  
✅ **gemma-7b-it** - Fastest for simple tasks  

## Free Tier Limits

- **Rate Limit**: 30 requests/minute
- **Daily Quota**: ~14,400 requests/day  
- **Context**: Up to 32K tokens (Mixtral)
- **Cost**: $0 (completely free)

## What You Get

🎯 **Real Trending Topics** from Reddit, Hacker News, Google Trends  
🤖 **AI Analysis** with keyword extraction and hashtag generation  
📊 **Content Ideas** with engagement predictions  
💡 **Performance Insights** and market analysis  

## Troubleshooting

**"API key not working"**
- Make sure key starts with `gsk_`
- Check for extra spaces in .env file
- Verify account is activated

**"Rate limit exceeded"**
- Free tier: 30 requests/minute
- System will auto-retry with simpler models

**"Import errors"**
- Run: `pip install -r requirements.txt`
- Make sure you're in backend directory

---

That's it! Your Content Engine now has AI-powered trending topic discovery. 🎉
