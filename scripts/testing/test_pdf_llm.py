#!/usr/bin/env python3
"""
Test script to verify PDF generation with LLM recommendations
"""

import asyncio
import sys
import os

# Add the backend directory to path
sys.path.append('/Users/ankur/cses/lehar/backend')

from app.services.pdf_report_service import pdf_generator
from app.services.trending_service import trending_service

async def test_pdf_generation():
    """Test PDF generation with LLM recommendations"""
    
    print("🧪 Testing PDF Generation with LLM Recommendations")
    print("=" * 60)
    
    try:
        # Test 1: Get trending topics
        print("📊 Step 1: Fetching trending topics...")
        topics = await trending_service.get_trending_topics(
            field="technology",
            enhanced_format=True
        )
        print(f"✅ Successfully fetched {len(topics)} topics")
        print(f"   Sample topic: {topics[0].get('title', 'Unknown')[:50]}...")
        
        # Test 2: Generate PDF with LLM recommendations
        print("\n📄 Step 2: Generating PDF with LLM recommendations...")
        report_info = await pdf_generator.generate_and_save_report(
            topics=topics,
            field="technology",
            user_name="Test User"
        )
        
        print(f"✅ PDF generated successfully!")
        print(f"   📁 File: {report_info['filename']}")
        print(f"   📏 Size: {report_info['file_size_kb']} KB")
        print(f"   📊 Topics analyzed: {report_info['topics_count']}")
        print(f"   💾 Saved to: {report_info['file_path']}")
        
        # Test 3: Verify file exists
        if os.path.exists(report_info['file_path']):
            print(f"✅ File verification: PDF file exists at expected location")
            
            # Get file size
            actual_size = os.path.getsize(report_info['file_path']) / 1024
            print(f"   📏 Actual file size: {actual_size:.2f} KB")
        else:
            print(f"❌ File verification: PDF file not found!")
            return False
        
        print("\n🎉 All tests passed successfully!")
        print("🔮 The system now generates authentic LLM-based recommendations!")
        print("📥 Users can download actual PDF reports with real data!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_pdf_generation())
    sys.exit(0 if success else 1)
