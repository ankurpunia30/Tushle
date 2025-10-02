# Content Engine Setup Guide

## Overview
The Content Engine now supports real-time trending topic discovery using multiple data sources and AI analysis. You can choose between free and paid options based on your needs.

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Data Sources  │    │   LLM Analysis   │    │   Frontend UI   │
│                 │    │                  │    │                 │
│ • Reddit API    │───▶│ • Groq (Free)    │───▶│ • Topic Cards   │
│ • HackerNews    │    │ • GPT-4 (Paid)   │    │ • Custom Topics │
│ • Google Trends │    │ • Claude (Paid)  │    │ • Content Ideas │
│ • NewsAPI       │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Best Data Sources for Trending Topics

### 1. **Free Options** ⭐ (Recommended for MVP)

#### Reddit API (Free)
- **Best for**: Community discussions, authentic engagement
- **Coverage**: All industries with subreddit-specific data
- **Rate limits**: 100 requests/minute
- **Setup**: No API key needed for public data
- **Quality**: High authenticity, real user discussions

#### Hacker News API (Free)
- **Best for**: Technology, startup, business trends
- **Coverage**: Tech-focused but high-quality discussions
- **Rate limits**: No official limits
- **Setup**: No API key needed
- **Quality**: Very high for tech industry

#### Google Trends (Free)
- **Best for**: Search volume trends, geographic data
- **Coverage**: Global search trends across all topics
- **Rate limits**: Built-in throttling
- **Setup**: No API key needed
- **Quality**: High for search-based insights

### 2. **Freemium Options**

#### NewsAPI
- **Free tier**: 1,000 requests/day
- **Best for**: Breaking news, media coverage analysis
- **Coverage**: Global news sources
- **Cost**: Free → $449/month
- **Quality**: High for news-driven trends

#### Twitter API v2
- **Free tier**: 1,500 tweets/month
- **Best for**: Real-time social sentiment
- **Coverage**: Global social media trends
- **Cost**: Free → $100/month
- **Quality**: High for viral content

### 3. **Premium Options** (For Production)

#### Ahrefs API
- **Cost**: $99-$999/month
- **Best for**: SEO keywords, search volume
- **Coverage**: Comprehensive keyword data
- **Quality**: Excellent for SEO-focused content

#### SEMrush API
- **Cost**: $119-$449/month
- **Best for**: Competitor analysis, keyword research
- **Coverage**: Marketing intelligence
- **Quality**: Excellent for competitive insights

## LLM Options for Topic Analysis

### 1. **Groq (Recommended)** ⭐
- **Cost**: Free tier available
- **Speed**: Very fast (100+ tokens/second)
- **Models**: Mixtral, Llama 2, Code Llama
- **Best for**: Real-time analysis, keyword extraction
- **Setup**: Easy API integration

### 2. **OpenAI GPT-4**
- **Cost**: $0.03/1K tokens
- **Quality**: Highest quality analysis
- **Best for**: Complex content strategy
- **Rate limits**: 10K RPM

### 3. **Anthropic Claude**
- **Cost**: $0.015/1K tokens
- **Quality**: Great for analytical tasks
- **Best for**: Detailed content insights

### 4. **Local LLMs** (Self-hosted)
- **Cost**: Hardware only
- **Options**: Ollama, LM Studio
- **Models**: Llama 2, Mistral, CodeLlama
- **Best for**: Privacy-focused setups

## Implementation Steps

### 1. Quick Start (Free Tier)
```bash
# Install dependencies
pip install pytrends aiohttp beautifulsoup4

# Set environment variables
export GROQ_API_KEY="your_groq_key"  # Optional but recommended
export ENABLE_REAL_TRENDING_DATA=true
```

### 2. Production Setup
```bash
# Install all dependencies
pip install -r requirements.txt

# Configure API keys in .env
cp .env.example .env
# Edit .env with your API keys

# Enable premium features
export ENABLE_LLM_ANALYSIS=true
export NEWS_API_KEY="your_news_api_key"
export TWITTER_BEARER_TOKEN="your_twitter_token"
```

### 3. API Key Setup

#### Groq (Free LLM Analysis)
1. Visit: https://console.groq.com/
2. Sign up for free account
3. Generate API key
4. Add to `.env`: `GROQ_API_KEY=your_key`

#### NewsAPI (Optional)
1. Visit: https://newsapi.org/
2. Free: 1,000 requests/day
3. Add to `.env`: `NEWS_API_KEY=your_key`

#### Reddit API (Optional)
1. Visit: https://www.reddit.com/prefs/apps
2. Create application
3. Add credentials to `.env`

## Current Implementation

### Data Flow
1. **User Request** → Topic discovery for specific field
2. **Data Aggregation** → Fetch from Reddit, HN, Google Trends
3. **LLM Analysis** → Enhance with AI insights (Groq)
4. **Custom Topics** → Process user-added topics
5. **Content Generation** → Create marketing content ideas
6. **Response** → Return structured data to frontend

### Features Available
✅ **Multi-source aggregation** (Reddit, HN, Google Trends)
✅ **AI-powered topic analysis** (Groq integration)
✅ **Custom topic processing**
✅ **Keyword extraction**
✅ **Hashtag generation**
✅ **Content idea generation**
✅ **Performance prediction**
✅ **Market insights**

### Fallback Strategy
- If APIs fail → Use mock data
- If LLM fails → Use template-based analysis
- Graceful degradation ensures system always works

## Monitoring and Analytics

### Track These Metrics
- API response times
- LLM analysis accuracy
- Topic discovery success rate
- User engagement with generated content
- Cost per analysis (if using paid APIs)

### Performance Optimization
- Cache trending topics (refresh every 2-4 hours)
- Batch LLM requests for efficiency
- Use async processing for all API calls
- Implement circuit breakers for external APIs

## Cost Optimization

### Free Tier Strategy
- Use Reddit + HN + Google Trends (free)
- Use Groq for LLM analysis (free tier)
- Cache results to reduce API calls
- **Estimated cost**: $0/month for ~1K topics/day

### Paid Tier Strategy
- Add NewsAPI ($449/month) for news trends
- Use Twitter API ($100/month) for social trends
- Premium LLM (GPT-4: ~$30/month for moderate usage)
- **Estimated cost**: $500-600/month for ~10K topics/day

## Next Steps

1. **Phase 1**: Deploy with free tier (Reddit + HN + Google Trends + Groq)
2. **Phase 2**: Add NewsAPI for news coverage
3. **Phase 3**: Integrate Twitter API for social trends
4. **Phase 4**: Add premium keyword tools (Ahrefs/SEMrush)
5. **Phase 5**: Implement real-time trend monitoring

## Testing

Test the system with:
```bash
# Start backend with new trending service
cd backend
python -m pytest tests/test_trending_service.py

# Test API endpoints
curl -X POST "http://localhost:8000/api/v1/content/discover-topics" \
  -H "Content-Type: application/json" \
  -d '{"field": "technology", "content_type": "social_media"}'
```

This setup gives you a production-ready trending topic discovery system that can scale from free to enterprise usage!
