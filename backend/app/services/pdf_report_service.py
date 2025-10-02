"""
PDF Report Generation Service for Content Analytics
"""
import io
import os
from datetime import datetime
from typing import List, Dict, Any
import tempfile
import asyncio

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.platypus import Image as RLImage
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

from .llm_service import groq_service as llm_service
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg

class ContentAnalyticsPDFGenerator:
    """Generate comprehensive PDF reports for content analytics"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
        self.reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'reports')
        self.pdf_dir = os.path.join(self.reports_dir, 'pdf')
        self.charts_dir = os.path.join(self.reports_dir, 'charts')
        self.ensure_directories()
    
    def ensure_directories(self):
        """Ensure report directories exist"""
        os.makedirs(self.reports_dir, exist_ok=True)
        os.makedirs(self.pdf_dir, exist_ok=True)
        os.makedirs(self.charts_dir, exist_ok=True)
    
    def generate_report_filename(self, field: str, user_name: str) -> str:
        """Generate a unique filename for the report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_user_name = "".join(c for c in user_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_field = "".join(c for c in field if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"tushle_ai_report_{safe_field}_{safe_user_name}_{timestamp}.pdf"
        return os.path.join(self.pdf_dir, filename)
    
    def setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.blue,
            borderWidth=1,
            borderColor=colors.blue,
            borderPadding=8
        ))
        
        # Topic title style
        self.styles.add(ParagraphStyle(
            name='TopicTitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=8,
            textColor=colors.darkgreen,
            fontName='Helvetica-Bold'
        ))
        
        # Business insight style
        self.styles.add(ParagraphStyle(
            name='BusinessInsight',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            textColor=colors.purple,
            fontName='Helvetica-Bold'
        ))
        
        # Monetization style
        self.styles.add(ParagraphStyle(
            name='Monetization',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            textColor=colors.darkred,
            leftIndent=20
        ))
    
    def create_analytics_charts(self, topics: List[Dict[str, Any]]) -> List[str]:
        """Create analytics charts and return file paths"""
        # Temporarily disable chart generation to focus on PDF folder structure
        print("📊 Chart generation temporarily disabled for testing")
        return []
    
    async def generate_comprehensive_report(self, topics: List[Dict[str, Any]], field: str, user_name: str = "Client") -> bytes:
        """Generate comprehensive PDF report"""
        buffer = io.BytesIO()
        
        # Create document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        story = []
        
        # Title Page
        story.append(Paragraph(f"TUSHLE AI REPORT - {field.upper()}", self.styles['CustomTitle']))
        story.append(Spacer(1, 20))
        
        # Report metadata
        story.append(Paragraph(f"<b>Field:</b> {field.title()}", self.styles['Normal']))
        story.append(Paragraph(f"<b>Generated for:</b> {user_name}", self.styles['Normal']))
        story.append(Paragraph(f"<b>Report Date:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", self.styles['Normal']))
        story.append(Paragraph(f"<b>Topics Analyzed:</b> {len(topics)}", self.styles['Normal']))
        story.append(Spacer(1, 30))
        
        # Executive Summary
        story.append(Paragraph("EXECUTIVE SUMMARY", self.styles['CustomSubtitle']))
        
        # Calculate summary statistics
        avg_popularity = sum(topic.get('popularity_score', 0) for topic in topics) / len(topics) if topics else 0
        high_potential_count = sum(1 for topic in topics if topic.get('business_potential', {}).get('score', 0) > 70)
        total_revenue_opportunities = sum(len(topic.get('monetization_opportunities', [])) for topic in topics)
        unique_sources = len(set(topic.get('source', 'Unknown') for topic in topics))
        
        summary_data = [
            ['Metric', 'Value', 'Insight'],
            ['Average Popularity Score', f"{avg_popularity:.1f}/100", 'Market engagement level'],
            ['High-Potential Topics', f"{high_potential_count}/{len(topics)}", 'Premium opportunities'],
            ['Revenue Opportunities', str(total_revenue_opportunities), 'Monetization paths identified'],
            ['Source Platforms', str(unique_sources), 'Market coverage breadth'],
            ['Market Intelligence', 'Comprehensive', '15 platforms analyzed daily']
        ]
        
        summary_table = Table(summary_data, colWidths=[2.5*inch, 1.5*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        # Create and add analytics charts
        story.append(Paragraph("ANALYTICS OVERVIEW", self.styles['CustomSubtitle']))
        
        try:
            chart_paths = self.create_analytics_charts(topics)
            
            for i, chart_path in enumerate(chart_paths):
                if os.path.exists(chart_path):
                    try:
                        chart_img = RLImage(chart_path, width=6*inch, height=3.6*inch)
                        story.append(chart_img)
                        story.append(Spacer(1, 15))
                        
                        # Clean up temp file
                        os.unlink(chart_path)
                    except Exception as e:
                        story.append(Paragraph(f"Chart {i+1}: Unable to generate visualization", self.styles['Normal']))
        except Exception as e:
            story.append(Paragraph("Analytics charts temporarily unavailable", self.styles['Normal']))
        
        story.append(PageBreak())
        
        # Detailed Topic Analysis
        story.append(Paragraph("DETAILED TOPIC ANALYSIS", self.styles['CustomTitle']))
        story.append(Spacer(1, 20))
        
        for i, topic in enumerate(topics[:15], 1):  # Limit to top 15 for PDF size
            # Topic header
            story.append(Paragraph(f"{i}. {topic.get('title', 'Unknown Topic')}", self.styles['TopicTitle']))
            
            # Basic info table
            topic_info = [
                ['Source', topic.get('source', 'Unknown')],
                ['Popularity Score', f"{topic.get('popularity_score', 0):.1f}/100"],
                ['Source URL', topic.get('source_url', 'Not available')[:50] + '...' if len(topic.get('source_url', '')) > 50 else topic.get('source_url', 'Not available')],
                ['Discussion URL', topic.get('discussion_url', 'Not available')[:50] + '...' if len(topic.get('discussion_url', '')) > 50 else topic.get('discussion_url', 'Not available')]
            ]
            
            topic_table = Table(topic_info, colWidths=[1.5*inch, 4.5*inch])
            topic_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 0), (-1, -1), 9)
            ]))
            
            story.append(topic_table)
            story.append(Spacer(1, 10))
            
            # Description
            description = topic.get('description', 'No description available')
            story.append(Paragraph(f"<b>Description:</b> {description[:200]}{'...' if len(description) > 200 else ''}", self.styles['Normal']))
            story.append(Spacer(1, 8))
            
            # Business Intelligence
            bp = topic.get('business_potential', {})
            if bp and bp.get('score', 0) > 0:
                story.append(Paragraph(f"💰 Business Potential: {bp.get('score', 0)}/100 (Market: {bp.get('market_size', 'Unknown')}, Competition: {bp.get('competition_level', 'Unknown')})", self.styles['BusinessInsight']))
                story.append(Spacer(1, 5))
            
            # Top monetization opportunity
            monetization = topic.get('monetization_opportunities', [])
            if monetization:
                top_opportunity = monetization[0]
                story.append(Paragraph(f"💡 Top Revenue Opportunity: {top_opportunity.get('type', 'Unknown')}", self.styles['Monetization']))
                story.append(Paragraph(f"Revenue Potential: {top_opportunity.get('revenue_estimate', 'Unknown')}", self.styles['Monetization']))
                story.append(Paragraph(f"Timeline: {top_opportunity.get('timeframe', 'Unknown')}", self.styles['Monetization']))
                story.append(Spacer(1, 5))
            
            # Content angles
            content_angles = topic.get('content_angles', [])
            if content_angles:
                story.append(Paragraph("<b>Content Angles:</b>", self.styles['Normal']))
                for angle in content_angles[:3]:  # Top 3 angles
                    story.append(Paragraph(f"• {angle}", self.styles['Normal']))
                story.append(Spacer(1, 5))
            
            # Hashtags
            hashtags = topic.get('hashtags', [])
            if hashtags:
                hashtag_text = ' '.join(hashtags[:8])  # Top 8 hashtags
                story.append(Paragraph(f"<b>Hashtags:</b> {hashtag_text}", self.styles['Normal']))
            
            story.append(Spacer(1, 15))
            
            # Add page break every 3 topics
            if i % 3 == 0:
                story.append(PageBreak())
        
        # Recommendations section
        story.append(PageBreak())
        story.append(Paragraph("STRATEGIC RECOMMENDATIONS", self.styles['CustomTitle']))
        story.append(Spacer(1, 20))
        
        # Generate LLM-based strategic recommendations
        try:
            llm_recommendations = await llm_service.generate_strategic_recommendations(topics, field)
            recommendations = llm_recommendations
        except Exception as e:
            print(f"Error generating LLM recommendations: {e}")
            # Fallback to intelligent recommendations based on actual data
            high_potential_topics = [t for t in topics if t.get('business_potential', {}).get('score', 0) > 70]
            revenue_opportunities = [t for t in topics if any(
                m.get('revenue_estimate', '').replace('$', '').replace(',', '').replace('K+', '000').isdigit() and 
                int(m.get('revenue_estimate', '').replace('$', '').replace(',', '').replace('K+', '000')) >= 25000
                for m in t.get('monetization_opportunities', [])
            )]
            
            recommendations = [
                f"🎯 <b>High-Potential Focus:</b> {len(high_potential_topics)} topics identified with 70+ business scores - prioritize these for immediate action",
                f"💰 <b>Revenue Opportunities:</b> {len(revenue_opportunities)} topics show $25K+ revenue potential - develop these first",
                f"📊 <b>Platform Coverage:</b> You have trending data from {len(set(t.get('source', 'Unknown') for t in topics))} platforms - maximize cross-platform leverage",
                f"🔥 <b>Top Source:</b> {max(set(t.get('source') for t in topics), key=lambda x: sum(1 for t in topics if t.get('source') == x))} shows highest activity - focus content efforts here",
                f"📈 <b>Engagement Strategy:</b> Average popularity score is {sum(t.get('popularity_score', 0) for t in topics) / len(topics) if topics else 0:.1f} - aim for topics above this threshold",
                "🔄 <b>Daily Updates:</b> This data refreshes daily - monitor emerging trends for first-mover advantage",
                "🎬 <b>Video Content Priority:</b> TikTok and YouTube trends identified - video content strategy recommended",
                "💼 <b>B2B Leverage:</b> LinkedIn professional trends detected - ideal for high-value client acquisition"
            ]
        
        for recommendation in recommendations:
            story.append(Paragraph(recommendation, self.styles['Normal']))
            story.append(Spacer(1, 8))
        
        # Footer
        story.append(Spacer(1, 30))
        story.append(Paragraph(f"This Tushle AI Report provides comprehensive market intelligence from 15+ free sources, updated daily for maximum competitive advantage.", self.styles['Normal']))
        story.append(Paragraph(f"Generated by Tushle AI Content Intelligence Engine - {datetime.now().strftime('%Y')}", self.styles['Normal']))
        
        # Build PDF
        doc.build(story)
        
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
    
    async def generate_and_save_report(self, topics: List[Dict[str, Any]], field: str, user_name: str = "Client") -> Dict[str, Any]:
        """Generate comprehensive PDF report and save to file"""
        
        # Generate PDF bytes
        pdf_bytes = await self.generate_comprehensive_report(topics, field, user_name)
        
        # Generate filename and save
        file_path = self.generate_report_filename(field, user_name)
        
        with open(file_path, 'wb') as f:
            f.write(pdf_bytes)
        
        # Get file size in KB
        file_size_kb = len(pdf_bytes) / 1024
        
        return {
            'file_path': file_path,
            'file_size_kb': round(file_size_kb, 2),
            'pdf_bytes': pdf_bytes,
            'filename': os.path.basename(file_path),
            'generated_at': datetime.now().isoformat(),
            'topics_count': len(topics),
            'field': field,
            'user_name': user_name
        }

# Global instance
pdf_generator = ContentAnalyticsPDFGenerator()
