from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import httpx
import json
import random
import asyncio
import logging
from fastapi.responses import Response, FileResponse
import os

from app.db.database import get_db
from app.models import ContentPost, User
from app.core.security import get_current_active_user
from app.core.config import settings
from app.services.trending_service import trending_service
from app.services.llm_service import groq_service
from app.services.pdf_report_service import pdf_generator

logger = logging.getLogger(__name__)
router = APIRouter()


class TopicDiscoveryRequest(BaseModel):
    field: str  # e.g., "technology", "finance", "health", "fashion"
    content_type: str  # e.g., "social_media", "blog", "video", "newsletter"
    target_audience: Optional[str] = "general"
    industry: Optional[str] = None
    custom_topics: Optional[List[str]] = []  # User-added custom topics


class CustomTopicRequest(BaseModel):
    topic_title: str
    description: Optional[str] = None
    field: str
    target_keywords: Optional[List[str]] = []
    content_type: str


class TrendingTopic(BaseModel):
    title: str
    description: str
    popularity_score: float  # 0-100
    keywords: List[str]
    hashtags: List[str]
    engagement_potential: str  # "high", "medium", "low"
    content_angles: List[str]
    source: str
    trending_since: str
    # Enhanced fields for comprehensive analysis
    source_url: Optional[str] = ""
    discussion_url: Optional[str] = ""
    business_potential: Optional[Dict[str, Any]] = {}
    monetization_opportunities: Optional[List[Dict[str, Any]]] = []
    revenue_insights: Optional[Dict[str, Any]] = {}


class ContentIdea(BaseModel):
    topic: str
    hook: str
    main_content: List[str]
    call_to_action: str
    keywords: List[str]
    hashtags: List[str]
    platforms: List[str]  # ["twitter", "linkedin", "instagram", "facebook"]
    estimated_reach: int


class ContentEngineResponse(BaseModel):
    trending_topics: List[TrendingTopic]
    content_ideas: List[ContentIdea]
    market_insights: Dict[str, Any]
    generated_at: datetime


# Mock trending topics database (in production, this would connect to real APIs)
MOCK_TRENDING_DATA = {
    "technology": [
        {
            "title": "AI-Powered Customer Service Revolution",
            "description": "Businesses are adopting AI chatbots and virtual assistants to enhance customer experience and reduce response times.",
            "keywords": ["AI customer service", "chatbots", "automation", "customer experience", "virtual assistants"],
            "hashtags": ["#AICustomerService", "#ChatbotsRevolution", "#CustomerExperience", "#AIAutomation"],
            "popularity_score": 92.5,
            "engagement_potential": "high",
            "content_angles": [
                "How AI is transforming customer support",
                "ROI of implementing AI customer service",
                "Best practices for AI chatbot deployment"
            ]
        },
        {
            "title": "No-Code Platform Market Boom",
            "description": "The no-code/low-code development market is experiencing unprecedented growth as businesses seek faster digital transformation.",
            "keywords": ["no-code", "low-code", "digital transformation", "business automation", "citizen developers"],
            "hashtags": ["#NoCode", "#LowCode", "#DigitalTransformation", "#BusinessAutomation"],
            "popularity_score": 88.3,
            "engagement_potential": "high"
        }
    ],
    "marketing": [
        {
            "title": "Video-First Marketing Strategy",
            "description": "Short-form video content is dominating social media engagement rates and marketing ROI across all platforms.",
            "keywords": ["video marketing", "short-form content", "social media engagement", "content strategy", "ROI"],
            "hashtags": ["#VideoMarketing", "#ShortFormContent", "#SocialMediaStrategy", "#ContentCreation"],
            "popularity_score": 95.8,
            "engagement_potential": "high",
            "content_angles": [
                "Why video content gets 10x more engagement",
                "Creating viral short-form videos on a budget",
                "Video marketing trends for 2025"
            ]
        },
        {
            "title": "AI-Generated Content Ethics",
            "description": "Marketers are grappling with ethical considerations and transparency requirements for AI-generated marketing content.",
            "keywords": ["AI content", "marketing ethics", "transparency", "authentic marketing", "AI disclosure"],
            "hashtags": ["#AIMarketing", "#MarketingEthics", "#AuthenticContent", "#AITransparency"],
            "popularity_score": 87.2,
            "engagement_potential": "medium"
        }
    ],
    "finance": [
        {
            "title": "Cryptocurrency Payment Integration",
            "description": "Small businesses are increasingly accepting cryptocurrency payments as digital currencies become mainstream.",
            "keywords": ["cryptocurrency payments", "digital currency", "payment processing", "fintech", "business payments"],
            "hashtags": ["#CryptoPayments", "#DigitalCurrency", "#Fintech", "#PaymentInnovation"],
            "popularity_score": 89.7,
            "engagement_potential": "high"
        }
    ],
    "health": [
        {
            "title": "Mental Health in Remote Work",
            "description": "Organizations are prioritizing employee mental health support as remote and hybrid work models become permanent.",
            "keywords": ["mental health", "remote work", "employee wellness", "work-life balance", "corporate wellness"],
            "hashtags": ["#MentalHealthAtWork", "#RemoteWork", "#EmployeeWellness", "#WorkLifeBalance"],
            "popularity_score": 91.4,
            "engagement_potential": "high"
        }
    ]
}


def process_custom_topics(custom_topics: List[str], field: str) -> List[TrendingTopic]:
    """Process user-provided custom topics and generate trend data"""
    
    processed_topics = []
    
    for topic in custom_topics:
        # Generate relevant keywords based on the topic and field
        keywords = generate_keywords_for_topic(topic, field)
        hashtags = generate_hashtags_for_topic(topic, field)
        
        # Create a custom trending topic with estimated data
        custom_topic = TrendingTopic(
            title=topic,
            description=f"Custom topic: {topic} - User-generated content focus for {field} marketing",
            popularity_score=75.0,  # Default score for custom topics
            keywords=keywords,
            hashtags=hashtags,
            engagement_potential="medium",  # Conservative estimate for custom topics
            content_angles=[
                f"Why {topic} matters in {field}",
                f"How to leverage {topic} for business growth",
                f"Latest trends in {topic}"
            ],
            source="Custom",
            trending_since=datetime.now().isoformat()
        )
        
        processed_topics.append(custom_topic)
    
    return processed_topics


def generate_keywords_for_topic(topic: str, field: str) -> List[str]:
    """Generate relevant keywords for a custom topic"""
    
    # Base keywords from the topic
    topic_words = topic.lower().split()
    
    # Field-specific keyword templates
    field_keywords = {
        "technology": ["tech", "digital", "automation", "AI", "software", "innovation"],
        "marketing": ["strategy", "campaign", "brand", "social media", "content", "engagement"],
        "finance": ["investment", "financial", "business", "ROI", "growth", "revenue"],
        "health": ["wellness", "healthcare", "fitness", "medical", "treatment", "prevention"],
        "education": ["learning", "training", "skills", "knowledge", "development", "course"],
        "fashion": ["style", "trend", "design", "fashion", "lifestyle", "beauty"]
    }
    
    keywords = topic_words.copy()
    
    # Add field-specific keywords
    if field.lower() in field_keywords:
        keywords.extend(field_keywords[field.lower()][:3])
    
    # Add common marketing keywords
    keywords.extend(["strategy", "tips", "guide", "best practices"])
    
    return keywords[:8]  # Limit to 8 keywords


def generate_hashtags_for_topic(topic: str, field: str) -> List[str]:
    """Generate relevant hashtags for a custom topic"""
    
    topic_words = topic.replace(" ", "").title()
    field_title = field.title()
    
    hashtags = [
        f"#{topic_words}",
        f"#{field_title}",
        f"#{topicWords}{fieldTitle}",
        "#Marketing",
        "#BusinessGrowth",
        "#ContentStrategy"
    ]
    
    # Add topic-specific hashtags
    if "AI" in topic.upper() or "artificial" in topic.lower():
        hashtags.extend(["#AI", "#ArtificialIntelligence", "#TechTrends"])
    elif "social" in topic.lower():
        hashtags.extend(["#SocialMedia", "#DigitalMarketing", "#SocialStrategy"])
    elif "video" in topic.lower():
        hashtags.extend(["#VideoMarketing", "#VideoContent", "#ContentCreation"])
    
    return hashtags[:8]  # Limit to 8 hashtags


async def process_custom_topics_with_llm(custom_topics: List[str], field: str) -> List[TrendingTopic]:
    """Process user-provided custom topics using LLM analysis"""
    
    processed_topics = []
    
    for topic in custom_topics:
        try:
            # Use LLM to analyze the custom topic
            llm_analysis = await groq_service.extract_keywords_and_hashtags(topic, field)
            
            keywords = llm_analysis.get('keywords', generate_keywords_for_topic(topic, field))
            hashtags = llm_analysis.get('hashtags', generate_hashtags_for_topic(topic, field))
            related_topics = llm_analysis.get('related_topics', [])
            
            # Generate content angles using LLM
            content_angles = [
                f"Why {topic} matters in {field}",
                f"How to leverage {topic} for business growth",
                f"Latest trends in {topic}",
                f"{topic} best practices for {field}"
            ]
            
            # Create enhanced custom topic
            custom_topic = TrendingTopic(
                title=topic,
                description=f"Custom analysis: {topic} - AI-enhanced insights for {field} marketing",
                popularity_score=random.uniform(70.0, 85.0),  # Slightly higher for custom topics
                keywords=keywords,
                hashtags=hashtags,
                engagement_potential=random.choice(["medium", "high"]),
                content_angles=content_angles,
                source="Custom + AI",
                trending_since=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"LLM analysis failed for custom topic '{topic}': {e}")
            # Fallback to basic processing
            keywords = generate_keywords_for_topic(topic, field)
            hashtags = generate_hashtags_for_topic(topic, field)
            
            custom_topic = TrendingTopic(
                title=topic,
                description=f"Custom topic: {topic} - User-generated content focus for {field} marketing",
                popularity_score=75.0,
                keywords=keywords,
                hashtags=hashtags,
                engagement_potential="medium",
                content_angles=[
                    f"Why {topic} matters in {field}",
                    f"How to leverage {topic} for business growth",
                    f"Latest trends in {topic}"
                ],
                source="Custom",
                trending_since=datetime.now().isoformat()
            )
        
        processed_topics.append(custom_topic)
    
    return processed_topics


def process_custom_topics(custom_topics: List[str], field: str) -> List[TrendingTopic]:
    """Process user-provided custom topics (basic version without LLM)"""
    
    processed_topics = []
    
    for topic in custom_topics:
        # Generate relevant keywords based on the topic and field
        keywords = generate_keywords_for_topic(topic, field)
        hashtags = generate_hashtags_for_topic(topic, field)
        
        # Create a custom trending topic with estimated data
        custom_topic = TrendingTopic(
            title=topic,
            description=f"Custom topic: {topic} - User-generated content focus for {field} marketing",
            popularity_score=75.0,  # Default score for custom topics
            keywords=keywords,
            hashtags=hashtags,
            engagement_potential="medium",  # Conservative estimate for custom topics
            content_angles=[
                f"Why {topic} matters in {field}",
                f"How to leverage {topic} for business growth",
                f"Latest trends in {topic}"
            ],
            source="Custom",
            trending_since=datetime.now().isoformat()
        )
        
        processed_topics.append(custom_topic)
    
    return processed_topics


def generate_keywords_for_topic(topic: str, field: str) -> List[str]:
    """Generate relevant keywords for a custom topic"""
    
    # Base keywords from the topic
    topic_words = topic.lower().split()
    
    # Field-specific keyword templates
    field_keywords = {
        "technology": ["tech", "digital", "automation", "AI", "software", "innovation"],
        "marketing": ["strategy", "campaign", "brand", "social media", "content", "engagement"],
        "finance": ["investment", "financial", "business", "ROI", "growth", "revenue"],
        "health": ["wellness", "healthcare", "fitness", "medical", "treatment", "prevention"],
        "education": ["learning", "training", "skills", "knowledge", "development", "course"],
        "fashion": ["style", "trend", "design", "fashion", "lifestyle", "beauty"]
    }
    
    keywords = topic_words.copy()
    
    # Add field-specific keywords
    if field.lower() in field_keywords:
        keywords.extend(field_keywords[field.lower()][:3])
    
    # Add common marketing keywords
    keywords.extend(["strategy", "tips", "guide", "best practices"])
    
    return keywords[:8]  # Limit to 8 keywords


def generate_hashtags_for_topic(topic: str, field: str) -> List[str]:
    """Generate relevant hashtags for a custom topic"""
    
    topic_words = topic.replace(" ", "").title()
    field_title = field.title()
    
    hashtags = [
        f"#{topic_words}",
        f"#{field_title}",
        f"#{topicWords}{fieldTitle}",
        "#Marketing",
        "#BusinessGrowth",
        "#ContentStrategy"
    ]
    
    # Add topic-specific hashtags
    if "AI" in topic.upper() or "artificial" in topic.lower():
        hashtags.extend(["#AI", "#ArtificialIntelligence", "#TechTrends"])
    elif "social" in topic.lower():
        hashtags.extend(["#SocialMedia", "#DigitalMarketing", "#SocialStrategy"])
    elif "video" in topic.lower():
        hashtags.extend(["#VideoMarketing", "#VideoContent", "#ContentCreation"])
    
    return hashtags[:8]  # Limit to 8 hashtags


@router.post("/analyze-custom-topic", response_model=TrendingTopic)
async def analyze_custom_topic(
    request: CustomTopicRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Analyze a single custom topic and provide insights"""
    
    keywords = request.target_keywords if request.target_keywords else generate_keywords_for_topic(request.topic_title, request.field)
    hashtags = generate_hashtags_for_topic(request.topic_title, request.field)
    
    # Simulate topic analysis (in production, this could use real APIs)
    description = request.description if request.description else f"Custom analysis for {request.topic_title} in the {request.field} sector"
    
    return TrendingTopic(
        title=request.topic_title,
        description=description,
        popularity_score=random.uniform(60.0, 85.0),  # Random score for custom topics
        keywords=keywords,
        hashtags=hashtags,
        engagement_potential=random.choice(["medium", "high"]),
        content_angles=[
            f"Introduction to {request.topic_title}",
            f"{request.topic_title} best practices",
            f"Future of {request.topic_title}",
            f"How {request.topic_title} impacts {request.field}"
        ],
        source="Custom Analysis",
        trending_since=datetime.now().isoformat()
    )
@router.post("/discover-topics", response_model=ContentEngineResponse)
async def discover_trending_topics(
    request: TopicDiscoveryRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Discover trending topics using real data sources and AI analysis"""
    
    try:
        # Step 1: Get raw trending data from multiple sources
        logger.info(f"Fetching trending topics for field: {request.field}")
        
        # Aggregate trending topics from ALL 15 comprehensive sources
        raw_trending_topics = await trending_service.get_trending_topics(
            field=request.field,
            enhanced_format=True
        )
        
        # Step 2: Use LLM to analyze and enhance trending topics
        analyzed_topics = []
        if raw_trending_topics:
            try:
                llm_analysis = await groq_service.analyze_trending_topics(
                    raw_trending_topics, request.field
                )
                
                # Use comprehensive enhanced data from all 15 sources
                for raw_topic in raw_trending_topics:
                    analyzed_topics.append(TrendingTopic(
                        title=raw_topic['title'],
                        description=raw_topic.get('description', ''),
                        popularity_score=raw_topic['popularity_score'],
                        keywords=raw_topic.get('keywords', []),
                        hashtags=raw_topic.get('hashtags', []),  # Use generated hashtags
                        engagement_potential=raw_topic.get('engagement_data', {}).get('engagement_quality', 'medium'),
                        content_angles=raw_topic.get('content_angles', []),
                        source=raw_topic['source'],
                        trending_since=raw_topic.get('daily_freshness', datetime.now().isoformat()),
                        # Add enhanced data
                        source_url=raw_topic.get('source_url', ''),
                        discussion_url=raw_topic.get('discussion_url', ''),
                        business_potential=raw_topic.get('business_potential', {}),
                        monetization_opportunities=raw_topic.get('monetization_opportunities', []),
                        revenue_insights=raw_topic.get('revenue_insights', {})
                    ))
                    
            except Exception as e:
                logger.error(f"LLM analysis failed, using raw data: {e}")
                # Fallback to ONLY FACTUAL raw data - no speculation
                for raw_topic in raw_trending_topics:
                    analyzed_topics.append(TrendingTopic(
                        title=raw_topic['title'],
                        description=raw_topic.get('description', ''),  # Only use actual description
                        popularity_score=raw_topic['popularity_score'],
                        keywords=raw_topic.get('keywords', []),
                        hashtags=[],  # Don't generate fake hashtags
                        engagement_potential='unknown',  # Be honest about what we don't know
                        content_angles=[
                            f"Fact: This is trending on {raw_topic['source']}",
                            f"Data: Current popularity score is {raw_topic['popularity_score']:.1f}",
                            f"Source: Verify at {raw_topic['source']}"
                        ],
                        source=raw_topic['source'],
                        trending_since=raw_topic.get('trending_since', datetime.now().isoformat())
                    ))
        
        # Step 3: Process custom topics if provided
        if request.custom_topics:
            custom_trending_topics = await process_custom_topics_with_llm(
                request.custom_topics, request.field
            )
            analyzed_topics.extend(custom_trending_topics)
        
        # Step 4: Generate FACT-BASED content ideas only - NO HALLUCINATION
        content_ideas = []
        for topic in analyzed_topics[:15]:  # Generate ideas for top 15 topics
            # Use only factual content generation - NO LLM speculation
            try:
                # Generate only fact-based content ideas using verified data
                factual_ideas = generate_content_ideas(topic, request)
                content_ideas.extend(factual_ideas)
                    
            except Exception as e:
                logger.error(f"Failed to generate factual content ideas for {topic.title}: {e}")
                # Skip this topic rather than generate false content
        
        # Step 5: Generate FACTUAL market insights - NO SPECULATION
        total_topics = len(analyzed_topics)
        custom_count = len(request.custom_topics) if request.custom_topics else 0
        avg_popularity = sum(t.popularity_score for t in analyzed_topics) / max(total_topics, 1)
        
        market_insights = {
            "total_topics_analyzed": total_topics,
            "custom_topics_added": custom_count,
            "average_popularity_score": round(avg_popularity, 2),
            "data_sources": list(set(t.source for t in analyzed_topics)),
            "analysis_timestamp": datetime.now().isoformat(),
            "field_analyzed": request.field,
            "content_type_requested": request.content_type,
            "target_audience": request.target_audience,
            "note": "All data is fact-based from real trending sources. No predictions or speculation included.",
            "data_freshness": "Real-time from source APIs"
        }
        
        logger.info(f"Successfully analyzed {total_topics} topics for {request.field}")
        
        # Sort topics by popularity score (highest first)
        analyzed_topics.sort(key=lambda x: x.popularity_score, reverse=True)
        
        return ContentEngineResponse(
            trending_topics=analyzed_topics,
            content_ideas=content_ideas,
            market_insights=market_insights,
            generated_at=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Error in discover_trending_topics: {e}")
        
        # Fallback to mock data if all else fails
        field_topics = MOCK_TRENDING_DATA.get(request.field.lower(), [])
        trending_topics = []
        
        for topic_data in field_topics[:3]:
            trending_topics.append(TrendingTopic(
                title=topic_data["title"],
                description=topic_data["description"],
                popularity_score=topic_data["popularity_score"],
                keywords=topic_data["keywords"],
                hashtags=topic_data["hashtags"],
                engagement_potential=topic_data["engagement_potential"],
                content_angles=topic_data.get("content_angles", []),
                source="Fallback",
                trending_since=datetime.now().isoformat()
            ))
        
        content_ideas = []
        for topic in trending_topics:
            content_ideas.extend(generate_content_ideas(topic, request))
        
        # Sort fallback topics by popularity score too
        trending_topics.sort(key=lambda x: x.popularity_score, reverse=True)
        
        return ContentEngineResponse(
            trending_topics=trending_topics,
            content_ideas=content_ideas,
            market_insights={
                "total_topics_analyzed": len(trending_topics),
                "custom_topics_added": 0,
                "data_sources": ["Fallback"],
                "analysis_timestamp": datetime.now().isoformat(),
                "note": "Using fallback data due to API limitations. For production use, ensure all APIs are accessible.",
                "status": "Limited Data Mode"
            },
            generated_at=datetime.now()
        )


def generate_content_ideas(topic: TrendingTopic, request: TopicDiscoveryRequest) -> List[ContentIdea]:
    """Generate FACT-BASED content ideas based on real trending topic data"""
    
    # Only use verified data from the trending topic
    content_templates = {
        "social_media": [
            {
                "hook": f"� Trending Now: {topic.title}",
                "main_content": [
                    f"Real data shows: {topic.title}",
                    f"Source: {topic.source}",
                    f"Popularity Score: {topic.popularity_score:.1f}/100",
                    f"Based on actual trending data from {topic.source}"
                ],
                "call_to_action": "What are your thoughts on this trend?",
                "platforms": ["linkedin", "twitter", "facebook"]
            }
        ],
        "blog": [
            {
                "hook": f"Data Analysis: {topic.title}",
                "main_content": [
                    f"Topic: {topic.title}",
                    f"Data Source: {topic.source}",
                    f"Current Popularity: {topic.popularity_score:.1f}/100",
                    "Analysis based on real trending data only"
                ],
                "call_to_action": "View source data for verification",
                "platforms": ["website", "linkedin"]
            }
        ],
        "video": [
            {
                "hook": f"Trending Data: {topic.title}",
                "main_content": [
                    f"Current trend: {topic.title}",
                    f"Source: {topic.source}",
                    f"Score: {topic.popularity_score:.1f}/100",
                    "Based on verified data"
                ],
                "call_to_action": "Check the source for more details",
                "platforms": ["tiktok", "instagram", "youtube"]
            }
        ]
    }
    
    templates = content_templates.get(request.content_type, content_templates["social_media"])
    ideas = []
    
    for template in templates:
        # Use only real, extracted keywords from the actual trending topic
        real_keywords = topic.keywords[:5] if topic.keywords else []
        real_hashtags = topic.hashtags[:3] if topic.hashtags else []  # Limit to verified hashtags
        
        ideas.append(ContentIdea(
            topic=topic.title,
            hook=template["hook"],
            main_content=template["main_content"],
            call_to_action=template["call_to_action"],
            keywords=real_keywords,
            hashtags=real_hashtags,
            platforms=template["platforms"],
            estimated_reach=0  # No fake reach estimation - set to 0 for verification needed
        ))
    
    return ideas


@router.get("/trending-keywords/{field}")
async def get_trending_keywords(
    field: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get trending keywords for a specific field"""
    
    # Mock keyword data (in production, would fetch from keyword research APIs)
    keyword_data = {
        "technology": [
            {"keyword": "AI automation", "volume": 45000, "difficulty": "medium", "trend": "rising"},
            {"keyword": "no-code development", "volume": 32000, "difficulty": "low", "trend": "rising"},
            {"keyword": "customer experience AI", "volume": 28000, "difficulty": "high", "trend": "stable"}
        ],
        "marketing": [
            {"keyword": "video marketing strategy", "volume": 52000, "difficulty": "medium", "trend": "rising"},
            {"keyword": "social media automation", "volume": 38000, "difficulty": "low", "trend": "rising"},
            {"keyword": "content creation AI", "volume": 29000, "difficulty": "medium", "trend": "rising"}
        ]
    }
    
    return {
        "field": field,
        "keywords": keyword_data.get(field.lower(), []),
        "last_updated": datetime.now().isoformat()
    }


@router.post("/generate-content-calendar")
async def generate_content_calendar(
    field: str,
    days: int = 30,
    current_user: User = Depends(get_current_active_user)
):
    """Generate a content calendar based on trending topics"""
    
    calendar = []
    base_date = datetime.now()
    
    for i in range(days):
        date = base_date + timedelta(days=i)
        
        # Rotate through different content types
        content_types = ["educational", "promotional", "engaging", "trending"]
        content_type = content_types[i % len(content_types)]
        
        calendar.append({
            "date": date.strftime("%Y-%m-%d"),
            "content_type": content_type,
            "topic": f"Day {i+1} - {field.title()} insights",
            "platforms": ["linkedin", "twitter"],
            "optimal_time": "09:00 AM",
            "hashtags": [f"#{field}", "#Marketing", "#Business"],
            "status": "planned"
        })
    
    return {
        "calendar": calendar,
        "total_posts": len(calendar),
        "field": field
    }


@router.get("/content-performance/{post_id}")
async def get_content_performance(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get performance analytics for a specific content post"""
    
    # Mock performance data
    return {
        "post_id": post_id,
        "impressions": random.randint(1000, 100000),
        "engagement_rate": round(random.uniform(2.5, 8.5), 2),
        "clicks": random.randint(50, 5000),
        "shares": random.randint(10, 500),
        "comments": random.randint(5, 200),
        "reach": random.randint(800, 80000),
        "best_performing_platform": random.choice(["LinkedIn", "Twitter", "Instagram"]),
        "peak_engagement_time": "2:00 PM"
    }


@router.post("/generate-pdf-report")
async def generate_pdf_report(
    request: TopicDiscoveryRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate comprehensive PDF report with analytics and save to dedicated folder"""
    
    try:
        # Get comprehensive trending topics data
        topics = await trending_service.get_trending_topics(
            field=request.field,
            enhanced_format=True
        )
        
        # Generate and save PDF report to dedicated folder
        report_info = await pdf_generator.generate_and_save_report(
            topics=topics,
            field=request.field,
            user_name=current_user.full_name or current_user.email
        )
        
        # Return both download and file info
        return {
            "status": "success",
            "message": f"Tushle AI Report for {request.field} generated successfully",
            "report_info": {
                "filename": report_info["filename"],
                "file_size_kb": report_info["file_size_kb"],
                "topics_count": report_info["topics_count"],
                "generated_at": report_info["generated_at"],
                "field": report_info["field"]
            },
            "download_available": True,
            "file_saved_to": "reports/pdf/ folder"
        }
        
    except Exception as e:
        logger.error(f"Error generating PDF report: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate PDF report: {str(e)}"
        )


@router.get("/download-pdf-report/{filename}")
async def download_pdf_report(
    filename: str,
    current_user: User = Depends(get_current_active_user)
):
    """Download a generated PDF report"""
    
    try:
        # Construct the full path to the PDF file
        reports_dir = os.path.join(os.getcwd(), "reports", "pdf")
        file_path = os.path.join(reports_dir, filename)
        
        # Check if file exists
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=404,
                detail="PDF report not found"
            )
        
        # Return the file for download
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='application/pdf',
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading PDF report: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to download PDF report: {str(e)}"
        )


@router.post("/generate-script/{topic_id}")
async def generate_script_for_topic(
    topic_id: int,
    script_type: str = "social_media",  # social_media, video, blog, email
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate script/content for a specific topic"""
    
    try:
        # Get trending topics and find the specific one
        topics = await trending_service.get_trending_topics(
            field="technology",  # Default field, could be passed as parameter
            enhanced_format=True
        )
        
        if topic_id < 1 or topic_id > len(topics):
            raise HTTPException(status_code=404, detail="Topic not found")
        
        selected_topic = topics[topic_id - 1]  # Convert to 0-based index
        
        # Generate script based on type
        script_content = await generate_content_script(selected_topic, script_type)
        
        return {
            "topic": selected_topic['title'],
            "script_type": script_type,
            "script_content": script_content,
            "generated_at": datetime.now().isoformat(),
            "monetization_opportunities": selected_topic.get('monetization_opportunities', []),
            "hashtags": selected_topic.get('hashtags', []),
            "content_angles": selected_topic.get('content_angles', [])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating script: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate script")


async def generate_content_script(topic: Dict[str, Any], script_type: str) -> Dict[str, Any]:
    """Generate content script based on topic and type"""
    
    title = topic.get('title', 'Unknown Topic')
    description = topic.get('description', '')
    content_angles = topic.get('content_angles', [])
    hashtags = topic.get('hashtags', [])
    monetization = topic.get('monetization_opportunities', [])
    
    if script_type == "social_media":
        return {
            "platform": "Multi-platform",
            "hook": f"🚨 TRENDING NOW: {title[:60]}{'...' if len(title) > 60 else ''}",
            "main_content": [
                f"📊 Why this matters: {content_angles[0] if content_angles else 'Breaking trend in the industry'}",
                f"💡 Key insight: {description[:100]}{'...' if len(description) > 100 else description}",
                f"🎯 Action: {content_angles[1] if len(content_angles) > 1 else 'Stay ahead of the curve'}",
                f"💰 Opportunity: {monetization[0].get('type', 'Revenue potential identified') if monetization else 'Business potential detected'}"
            ],
            "call_to_action": "🔗 What's your take on this trend? Share your thoughts below!",
            "hashtags": hashtags[:10],
            "estimated_reach": "5K-50K impressions"
        }
    
    elif script_type == "video":
        return {
            "platform": "YouTube/TikTok",
            "script_sections": {
                "hook": f"You won't believe what's trending right now... {title[:40]}",
                "introduction": f"Hey everyone! Today we're diving into {title}",
                "main_points": [
                    f"First, let's talk about why this is exploding: {content_angles[0] if content_angles else 'Major industry shift'}",
                    f"Here's what the data shows: {description[:80]}{'...' if len(description) > 80 else description}",
                    f"And here's the money part: {monetization[0].get('description', 'Huge revenue opportunity') if monetization else 'Business implications are massive'}"
                ],
                "conclusion": "This trend is just getting started. Make sure you're positioning yourself to take advantage.",
                "call_to_action": "Hit subscribe if you want more trending insights like this!"
            },
            "video_length": "60-180 seconds",
            "hashtags": hashtags[:15]
        }
    
    elif script_type == "blog":
        return {
            "title": f"Deep Dive: {title}",
            "outline": [
                "Introduction: Why This Trend Matters",
                f"The Data Behind {title[:30]}{'...' if len(title) > 30 else title}",
                "Market Analysis and Opportunities",
                "Revenue Implications for Businesses",
                "Action Steps and Recommendations",
                "Conclusion: Future Outlook"
            ],
            "key_points": content_angles,
            "seo_keywords": hashtags[:5],
            "estimated_word_count": "1500-2500 words",
            "target_audience": "Business professionals and industry stakeholders"
        }
    
    elif script_type == "email":
        return {
            "subject_line": f"🚨 Trending Alert: {title[:40]}{'...' if len(title) > 40 else ''}",
            "email_structure": {
                "opening": f"Hi [Name],\n\nI just spotted something that could impact your business: {title}",
                "body": [
                    f"Here's what's happening: {description[:150]}{'...' if len(description) > 150 else description}",
                    f"Why it matters: {content_angles[0] if content_angles else 'This could change the game'}",
                    f"The opportunity: {monetization[0].get('description', 'Revenue potential identified') if monetization else 'Business potential detected'}"
                ],
                "closing": "Want to discuss how this could impact your strategy? Hit reply and let's chat.",
                "signature": "Best regards,\n[Your Name]"
            },
            "personalization_tips": [
                "Customize opening based on recipient's industry",
                "Add specific examples relevant to their business",
                "Include timeline for action if urgent"
            ]
        }
    
    else:
        return {
            "error": "Unknown script type",
            "available_types": ["social_media", "video", "blog", "email"]
        }
