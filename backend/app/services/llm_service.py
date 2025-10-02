import json
import httpx
from typing import Dict, List, Optional, Any
from app.core.config import get_settings

settings = get_settings()

class GroqLLMService:
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.base_url = "https://api.groq.com/openai/v1"
        self.model = "llama-3.1-8b-instant"
        
    async def extract_keywords_and_hashtags(self, topic: str, industry: str = "general") -> Dict[str, List[str]]:
        """Extract keywords and hashtags for a given topic using Groq LLM - WITH SAFETY CHECKS"""
        if not self.api_key:
            # Always use fallback when API key is not available
            return self._extract_fallback_content(topic, industry)
        
        try:
            # Add safety note to prompt to reduce hallucination
            prompt = f"""
            IMPORTANT: Only extract actual keywords and hashtags based on the real topic: "{topic}" in {industry} industry.
            DO NOT make up or invent new information. Only use words directly related to the given topic.
            
            Return ONLY a JSON object in this exact format:
            {{
                "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],
                "hashtags": ["#hashtag1", "#hashtag2", "#hashtag3", "#hashtag4", "#hashtag5"]
            }}
            
            Base keywords and hashtags ONLY on the actual topic provided: "{topic}"
            """
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": "You are a factual keyword extractor. Only provide keywords directly related to the given topic. Do not invent or hallucinate content."},
                            {"role": "user", "content": prompt}
                        ],
                        "max_tokens": 300,  # Reduced to limit output
                        "temperature": 0.1  # Low temperature for more factual responses
                    },
                    timeout=15.0  # Reduced timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"].strip()
                    
                    # Try to parse JSON from the response
                    try:
                        parsed_content = json.loads(content)
                        # Validate that we got reasonable results
                        if (isinstance(parsed_content.get('keywords'), list) and 
                            isinstance(parsed_content.get('hashtags'), list)):
                            return parsed_content
                        else:
                            return self._extract_fallback_content(topic, industry)
                    except json.JSONDecodeError:
                        # If JSON parsing fails, use fallback
                        return self._extract_fallback_content(topic, industry)
                else:
                    print(f"Groq API error: {response.status_code}")
                    return self._extract_fallback_content(topic, industry)
                    
        except Exception as e:
            print(f"Error calling Groq API: {str(e)}")
            return self._extract_fallback_content(topic, industry)
    
    def _extract_fallback_content(self, topic: str, industry: str) -> Dict[str, List[str]]:
        """Fallback keyword and hashtag extraction when LLM is not available"""
        # Create basic keywords from the topic
        words = topic.lower().split()
        keywords = words[:5] if len(words) >= 5 else words + [industry, "trending", "popular"][:5-len(words)]
        
        # Create hashtags from keywords
        hashtags = [f"#{word.replace(' ', '')}" for word in keywords]
        
        return {
            "keywords": keywords,
            "hashtags": hashtags
        }
    
    async def analyze_trending_topics(self, topics_data: List[Dict], field: str = "general") -> Dict[str, Any]:
        """Analyze trending topics data - WITH SAFETY CHECKS FOR PRODUCTION"""
        if not self.api_key:
            # Always use fallback when API key is not available
            return self._analyze_fallback_trends(topics_data, field)
        
        try:
            # Create a safe prompt that doesn't hallucinate
            topics_summary = []
            for topic in topics_data[:5]:  # Limit to top 5 to avoid token limits
                topics_summary.append(f"- {topic.get('title', 'Unknown')} (Score: {topic.get('popularity_score', 0)})")
            
            prompt = f"""
            IMPORTANT: Only analyze the provided real trending data. DO NOT make up or invent information.
            
            Real trending topics in {field}:
            {chr(10).join(topics_summary)}
            
            Provide ONLY factual analysis based on the data provided. Return JSON in this format:
            {{
                "summary": "Factual summary of what topics are trending",
                "insights": ["Fact 1 based on data", "Fact 2 based on data"],
                "field_analysis": "Factual analysis of the {field} field trends"
            }}
            
            Base analysis ONLY on the actual data provided above.
            """
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": "You are a factual data analyst. Only analyze provided data. Do not invent or hallucinate content."},
                            {"role": "user", "content": prompt}
                        ],
                        "max_tokens": 400,
                        "temperature": 0.1  # Low temperature for factual responses
                    },
                    timeout=15.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"].strip()
                    
                    try:
                        parsed_content = json.loads(content)
                        # Validate that we got reasonable results
                        if isinstance(parsed_content, dict):
                            return parsed_content
                        else:
                            return self._analyze_fallback_trends(topics_data, field)
                    except json.JSONDecodeError:
                        return self._analyze_fallback_trends(topics_data, field)
                else:
                    print(f"Groq API error: {response.status_code}")
                    return self._analyze_fallback_trends(topics_data, field)
                    
        except Exception as e:
            print(f"Error calling Groq API: {str(e)}")
            return self._analyze_fallback_trends(topics_data, field)
    
    def _analyze_fallback_trends(self, topics_data: List[Dict], field: str) -> Dict[str, Any]:
        """Fallback trend analysis when LLM is not available"""
        total_topics = len(topics_data)
        avg_score = sum(topic.get('popularity_score', 0) for topic in topics_data) / max(total_topics, 1)
        
        return {
            "summary": f"Analysis of {total_topics} trending topics in {field} field",
            "insights": [
                f"Total topics analyzed: {total_topics}",
                f"Average popularity score: {avg_score:.2f}",
                "Analysis based on real trending data sources"
            ],
            "field_analysis": f"Current trends in {field} show active engagement with {total_topics} topics"
        }
    
    async def generate_strategic_recommendations(self, topics: List[Dict[str, Any]], field: str) -> List[str]:
        """Generate strategic recommendations based on actual trending topics"""
        if not self.api_key:
            return self._generate_fallback_recommendations(topics, field)
        
        try:
            # Prepare actual topic data for LLM
            topic_summaries = []
            for topic in topics[:5]:  # Use top 5 topics
                business_score = topic.get('business_potential', {}).get('score', 0)
                monetization = topic.get('monetization_opportunities', [])
                revenue_estimate = monetization[0].get('revenue_estimate', 'Unknown') if monetization else 'No estimate'
                
                topic_summaries.append({
                    'title': topic.get('title', 'Unknown'),
                    'source': topic.get('source', 'Unknown'),
                    'popularity': topic.get('popularity_score', 0),
                    'business_score': business_score,
                    'revenue_potential': revenue_estimate
                })
            
            prompt = f"""
            Based on these ACTUAL trending topics in {field}, generate 5 specific, actionable strategic recommendations:
            
            REAL TOPICS DATA:
            {json.dumps(topic_summaries, indent=2)}
            
            Generate recommendations that:
            1. Reference specific topics from the data above
            2. Provide actionable next steps
            3. Include realistic revenue/growth estimates
            4. Are based on the actual trending data provided
            5. Help capitalize on these specific opportunities
            
            Return as a JSON array of 5 strings, each starting with an emoji and being specific to the data provided.
            """
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": "You are a strategic business advisor. Generate specific recommendations based only on the provided real data. Do not make up information."},
                            {"role": "user", "content": prompt}
                        ],
                        "max_tokens": 800,
                        "temperature": 0.3
                    },
                    timeout=15.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    recommendations_text = result['choices'][0]['message']['content'].strip()
                    
                    try:
                        # Try to parse as JSON
                        recommendations = json.loads(recommendations_text)
                        if isinstance(recommendations, list):
                            return recommendations[:5]
                    except json.JSONDecodeError:
                        # If not JSON, split by lines and clean up
                        lines = [line.strip() for line in recommendations_text.split('\n') if line.strip()]
                        return lines[:5]
                        
                return self._generate_fallback_recommendations(topics, field)
                
        except Exception as e:
            print(f"Error generating LLM recommendations: {str(e)}")
            return self._generate_fallback_recommendations(topics, field)
    
    def _generate_fallback_recommendations(self, topics: List[Dict[str, Any]], field: str) -> List[str]:
        """Generate fallback recommendations based on actual topic data"""
        recommendations = []
        
        # Analyze actual data
        high_potential_topics = [t for t in topics if t.get('business_potential', {}).get('score', 0) > 70]
        monetizable_topics = [t for t in topics if t.get('monetization_opportunities', [])]
        sources = list(set(t.get('source', 'Unknown') for t in topics))
        
        if high_potential_topics:
            top_topic = max(high_potential_topics, key=lambda x: x.get('business_potential', {}).get('score', 0))
            recommendations.append(f"🎯 Prioritize '{top_topic.get('title', 'Unknown')[:50]}...' from {top_topic.get('source', 'Unknown')} - shows {top_topic.get('business_potential', {}).get('score', 0)}/100 business potential")
        
        if monetizable_topics:
            recommendations.append(f"💰 Focus on {len(monetizable_topics)} topics with clear monetization paths - immediate revenue opportunities identified")
        
        recommendations.append(f"📊 Leverage {len(sources)} active platforms: {', '.join(sources[:3])}{'...' if len(sources) > 3 else ''}")
        
        if len(topics) > 10:
            recommendations.append(f"⚡ Act quickly on {len(topics)} trending opportunities - daily variation ensures fresh content")
        
        recommendations.append(f"🚀 Implement multi-platform strategy across identified {field} trends for maximum market penetration")
        
        return recommendations[:5]

# Create a singleton instance
groq_service = GroqLLMService()
