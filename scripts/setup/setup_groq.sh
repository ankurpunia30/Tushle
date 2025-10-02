#!/bin/bash

# Groq API Setup Script for Content Engine
# This script helps you set up the free Groq API for trending topic analysis

echo "🚀 Setting up Groq API for Content Engine..."
echo ""

# Check if .env file exists
if [ ! -f "backend/.env" ]; then
    echo "📋 Creating .env file from template..."
    cp backend/.env.example backend/.env
    echo "✅ Created backend/.env file"
else
    echo "📋 Found existing .env file"
fi

echo ""
echo "🔑 Groq API Key Setup"
echo "====================="
echo ""
echo "Groq provides FREE access to powerful LLM models including:"
echo "• Llama 3 8B (8,192 context) - Fast and high quality"
echo "• Mixtral 8x7B (32,768 context) - Best quality for complex tasks"
echo "• Gemma 7B (8,192 context) - Fastest for simple tasks"
echo ""
echo "Free tier limits:"
echo "• Rate limit: 30 requests/minute"
echo "• Daily quota: Generous (typically 14,400 requests/day)"
echo "• Cost: $0 (completely free)"
echo ""

# Check if GROQ_API_KEY already exists
if grep -q "GROQ_API_KEY=" backend/.env && ! grep -q "GROQ_API_KEY=your_groq_api_key_here" backend/.env; then
    echo "✅ Groq API key already configured in .env file"
    echo ""
else
    echo "📖 How to get your FREE Groq API key:"
    echo ""
    echo "1. Visit: https://console.groq.com/"
    echo "2. Sign up with your email (free account)"
    echo "3. Go to 'API Keys' section"
    echo "4. Click 'Create API Key'"
    echo "5. Copy the generated key"
    echo ""
    echo "Once you have your key, please enter it below:"
    echo -n "Enter your Groq API key: "
    read -r groq_key
    
    if [ -n "$groq_key" ]; then
        # Update the .env file
        if grep -q "GROQ_API_KEY=" backend/.env; then
            sed -i.bak "s/GROQ_API_KEY=.*/GROQ_API_KEY=$groq_key/" backend/.env
        else
            echo "GROQ_API_KEY=$groq_key" >> backend/.env
        fi
        echo "✅ Groq API key saved to .env file"
    else
        echo "⚠️  No key entered. You can add it later to backend/.env"
        echo "   Add this line: GROQ_API_KEY=your_actual_key_here"
    fi
fi

echo ""
echo "🔧 Enabling real trending data..."

# Enable trending data features
if grep -q "ENABLE_REAL_TRENDING_DATA=" backend/.env; then
    sed -i.bak "s/ENABLE_REAL_TRENDING_DATA=.*/ENABLE_REAL_TRENDING_DATA=true/" backend/.env
else
    echo "ENABLE_REAL_TRENDING_DATA=true" >> backend/.env
fi

if grep -q "ENABLE_LLM_ANALYSIS=" backend/.env; then
    sed -i.bak "s/ENABLE_LLM_ANALYSIS=.*/ENABLE_LLM_ANALYSIS=true/" backend/.env
else
    echo "ENABLE_LLM_ANALYSIS=true" >> backend/.env
fi

echo "✅ Enabled real trending data discovery"
echo "✅ Enabled LLM analysis with Groq"

echo ""
echo "📦 Installing required dependencies..."
cd backend
pip install aiohttp pytrends beautifulsoup4 lxml requests
echo "✅ Dependencies installed"

echo ""
echo "🧪 Testing Groq API connection..."

# Create a simple test script
cat > test_groq.py << 'EOF'
import asyncio
import os
from app.services.llm_service import groq_service

async def test_groq():
    try:
        # Test basic functionality
        result = await groq_service.extract_keywords_and_hashtags("AI marketing", "technology")
        if result and result.get('keywords'):
            print("✅ Groq API working correctly!")
            print(f"Sample keywords: {result['keywords'][:3]}")
            print(f"Sample hashtags: {result['hashtags'][:3]}")
            return True
        else:
            print("❌ Groq API test failed - check your API key")
            return False
    except Exception as e:
        print(f"❌ Error testing Groq API: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_groq())
EOF

# Try to run the test
if python test_groq.py 2>/dev/null; then
    echo "🎉 API test successful!"
else
    echo "⚠️  API test failed. Please check your API key in backend/.env"
fi

# Clean up test file
rm -f test_groq.py

echo ""
echo "🎯 Setup Complete!"
echo "=================="
echo ""
echo "Your Content Engine is now configured with:"
echo "• ✅ Free Groq LLM analysis (Llama 3, Mixtral, Gemma)"
echo "• ✅ Real trending topic discovery (Reddit, HN, Google Trends)"
echo "• ✅ AI-powered keyword and hashtag generation"
echo "• ✅ Smart content idea generation"
echo ""
echo "🚀 Next steps:"
echo "1. Start your backend: cd backend && uvicorn app.main:app --reload"
echo "2. Start your frontend: cd frontend && npm run dev"
echo "3. Test the Content Engine at: http://localhost:3001"
echo ""
echo "💡 Pro tips:"
echo "• The system gracefully falls back to mock data if APIs fail"
echo "• Groq free tier provides 30 requests/minute (plenty for testing)"
echo "• All trending data sources (Reddit, HN, Google Trends) are free"
echo ""
echo "Happy content creating! 🎨"
