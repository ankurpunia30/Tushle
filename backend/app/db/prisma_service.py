"""
Prisma database service for Tushle AI Dashboard
"""
import os
from prisma import Prisma
from typing import Optional

# Global prisma instance
prisma = Prisma()

class DatabaseService:
    """Database service using Prisma ORM"""
    
    def __init__(self):
        self.db = prisma
        
    async def connect(self):
        """Connect to database"""
        if not self.db.is_connected():
            await self.db.connect()
    
    async def disconnect(self):
        """Disconnect from database"""
        if self.db.is_connected():
            await self.db.disconnect()
    
    async def get_user_by_email(self, email: str):
        """Get user by email"""
        return await self.db.user.find_unique(where={"email": email})
    
    async def create_user(self, email: str, username: str, password: str):
        """Create new user"""
        return await self.db.user.create(
            data={
                "email": email,
                "username": username,
                "password": password
            }
        )
    
    async def get_trending_content(self, category: str, limit: int = 50):
        """Get trending content by category"""
        return await self.db.trendingcontent.find_many(
            where={"category": category},
            order_by={"score": "desc"},
            take=limit
        )
    
    async def create_trending_content(self, title: str, source: str, category: str, 
                                    description: Optional[str] = None, 
                                    url: Optional[str] = None,
                                    score: Optional[float] = None,
                                    engagement: Optional[int] = None):
        """Create trending content entry"""
        return await self.db.trendingcontent.create(
            data={
                "title": title,
                "description": description,
                "url": url,
                "source": source,
                "category": category,
                "score": score,
                "engagement": engagement
            }
        )
    
    async def create_report(self, title: str, category: str, user_id: str,
                          description: Optional[str] = None):
        """Create new report"""
        return await self.db.report.create(
            data={
                "title": title,
                "description": description,
                "category": category,
                "userId": user_id
            }
        )
    
    async def get_user_reports(self, user_id: str):
        """Get all reports for a user"""
        return await self.db.report.find_many(
            where={"userId": user_id},
            order_by={"createdAt": "desc"}
        )
    
    async def update_report_status(self, report_id: str, status: str, file_path: Optional[str] = None):
        """Update report status and file path"""
        update_data = {"status": status}
        if file_path:
            update_data["filePath"] = file_path
            
        return await self.db.report.update(
            where={"id": report_id},
            data=update_data
        )

# Global database service instance
db_service = DatabaseService()

async def get_database():
    """Dependency to get database service"""
    await db_service.connect()
    try:
        yield db_service
    finally:
        pass  # Keep connection alive for serverless

async def init_database():
    """Initialize database connection"""
    await db_service.connect()
    print("✅ Database connected successfully")

async def close_database():
    """Close database connection"""
    await db_service.disconnect()
    print("✅ Database disconnected")
