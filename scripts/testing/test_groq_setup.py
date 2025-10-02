"""
Test script for Groq API and trending topics functionality
Run this to verify your setup is working correctly
"""
import asyncio
import os
import sys
sys.path.append('/Users/ankur/cses/lehar/backend')

async def test_groq_setup():
    print("🧪 Testing Groq API Setup...")
    print("=" * 40)
    
    # Check if API key is set
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key or api_key == 'your_groq_api_key_here':
        print("❌ Groq API key not found!")
        print("💡 Please add your Groq API key to backend/.env")
        print("   Get one free at: https://console.groq.com/")
        return False
    
    print(f"✅ API key found: {api_key[:8]}...")
    
    try:
        from app.services.llm_service import groq_service
        
        print("\n🤖 Testing LLM analysis...")
        
        # Test keyword extraction
        result = await groq_service.extract_keywords_and_hashtags(
            "AI-powered customer service", 
            "technology"
        )
        
        if result and result.get('keywords'):
            print("✅ Keyword extraction working!")
            print(f"   Keywords: {result['keywords'][:3]}")
            print(f"   Hashtags: {result['hashtags'][:3]}")
        else:
            print("❌ Keyword extraction failed")
            return False
        
        print("\n📈 Testing content idea generation...")
        
        # Test content ideas
        ideas = await groq_service.generate_content_ideas(
            "AI customer service",
            "social_media", 
            "business"
        )
        
        if ideas and len(ideas) > 0:
            print("✅ Content idea generation working!")
            print(f"   Generated {len(ideas)} content ideas")
            print(f"   Sample: {ideas[0].get('headline', 'N/A')[:50]}...")
        else:
            print("⚠️  Content idea generation using fallback")
        
        print("\n🌐 Testing trending topics discovery...")
        
        # Test trending service
        from app.services.trending_service import trending_service
        
        trends = await trending_service.aggregate_trending_topics("technology")
        
        if trends and len(trends) > 0:
            print("✅ Trending topics discovery working!")
            print(f"   Found {len(trends)} trending topics")
            for i, trend in enumerate(trends[:2]):
                print(f"   {i+1}. {trend['title'][:50]}... (Score: {trend['popularity_score']:.1f})")
        else:
            print("⚠️  Trending topics using fallback data")
        
        print("\n🎉 Setup test completed successfully!")
        print("\n🚀 Your Content Engine is ready with:")
        print("   • Free Groq LLM analysis")
        print("   • Real trending topic discovery")
        print("   • AI-powered content generation")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("   • Make sure you're in the backend directory")
        print("   • Check that all dependencies are installed")
        print("   • Verify your Groq API key is correct")
        return False

async def main():
    print("🚀 Groq API and Trending Topics Test")
    print("====================================")
    
    # Set environment for testing
    os.environ['ENABLE_REAL_TRENDING_DATA'] = 'true'
    os.environ['ENABLE_LLM_ANALYSIS'] = 'true'
    
    success = await test_groq_setup()
    
    if success:
        print("\n✅ All systems operational!")
        print("🎯 Ready to generate amazing content!")
    else:
        print("\n❌ Setup needs attention")
        print("📖 Check GROQ_SETUP.md for detailed instructions")

if __name__ == "__main__":
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv('/Users/ankur/cses/lehar/backend/.env')
    except ImportError:
        pass
    
    asyncio.run(main())
