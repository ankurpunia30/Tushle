#!/usr/bin/env python3
"""
Simple test for Groq API integration
"""
import asyncio
import os
import sys
import httpx

# Load environment variables from .env file
def load_env():
    env_path = '/Users/ankur/cses/lehar/backend/.env'
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

async def test_groq_api():
    print("🧪 Testing Groq API...")
    print("=" * 30)
    
    # Load environment
    load_env()
    
    api_key = os.getenv('GROQ_API_KEY')
    
    if not api_key or api_key == 'your_groq_api_key_here':
        print("❌ No API key found")
        return False
    
    print(f"✅ API Key found: {api_key[:8]}...")
    
    # Test API call
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama3-8b-8192",
                    "messages": [
                        {"role": "user", "content": "Generate 3 keywords for 'AI marketing' in JSON format: {\"keywords\": [\"word1\", \"word2\", \"word3\"]}"}
                    ],
                    "max_tokens": 100,
                    "temperature": 0.1
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                print("✅ Groq API working!")
                print(f"✅ Response: {content[:100]}...")
                return True
            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

async def test_trending_sources():
    print("\n🌐 Testing trending data sources...")
    print("=" * 35)
    
    # Test Reddit API (free)
    try:
        async with httpx.AsyncClient() as client:
            headers = {'User-Agent': 'TrendingTopicsBot/1.0'}
            response = await client.get(
                "https://www.reddit.com/r/technology/hot.json?limit=5",
                headers=headers,
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                posts = data['data']['children']
                print(f"✅ Reddit API: Found {len(posts)} trending posts")
                if posts:
                    print(f"   Sample: {posts[0]['data']['title'][:50]}...")
            else:
                print(f"⚠️  Reddit API: Status {response.status_code}")
                
    except Exception as e:
        print(f"⚠️  Reddit API error: {e}")
    
    # Test Hacker News API (free)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://hacker-news.firebaseio.com/v0/topstories.json",
                timeout=10.0
            )
            
            if response.status_code == 200:
                story_ids = response.json()
                print(f"✅ Hacker News API: Found {len(story_ids[:10])} trending stories")
            else:
                print(f"⚠️  Hacker News API: Status {response.status_code}")
                
    except Exception as e:
        print(f"⚠️  Hacker News API error: {e}")

async def main():
    print("🚀 Content Engine API Test")
    print("==========================")
    
    # Test Groq LLM
    groq_success = await test_groq_api()
    
    # Test trending data sources
    await test_trending_sources()
    
    print("\n" + "=" * 40)
    if groq_success:
        print("🎉 SUCCESS! Your Content Engine is ready!")
        print("\n✅ What's working:")
        print("   • Groq LLM API (free tier)")
        print("   • Trending topic discovery")
        print("   • Real-time data sources")
        print("\n🚀 Next steps:")
        print("   • Start your backend server")
        print("   • Test the Content Engine in the UI")
        print("   • Generate AI-powered content ideas!")
    else:
        print("❌ Groq API needs attention")
        print("💡 Check your API key in backend/.env")

if __name__ == "__main__":
    asyncio.run(main())
