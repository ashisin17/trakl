import httpx
import asyncio
from bs4 import BeautifulSoup
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Dict, Any
import uuid
from urllib.parse import urljoin, urlparse
import re

from ..database import ContentSource
from ..models import ContentType, ContentSourceResponse, DifficultyLevel
from .openai_service import OpenAIService
from .embedding_service import EmbeddingService

class ContentDiscoveryService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.openai_service = OpenAIService()
        self.embedding_service = EmbeddingService()
        
        # Platform-specific search configurations
        self.search_configs = {
            "youtube": {
                "base_url": "https://www.googleapis.com/youtube/v3/search",
                "requires_api": True
            },
            "coursera": {
                "search_url": "https://www.coursera.org/search?query=",
                "requires_api": False
            },
            "udemy": {
                "search_url": "https://www.udemy.com/courses/search/?q=",
                "requires_api": False
            },
            "medium": {
                "search_url": "https://medium.com/search?q=",
                "requires_api": False
            },
            "dev.to": {
                "search_url": "https://dev.to/search?q=",
                "requires_api": False
            }
        }
    
    async def search_content(
        self, 
        query: str, 
        content_types: Optional[List[ContentType]] = None,
        max_results: int = 20,
        platforms: Optional[List[str]] = None
    ) -> List[ContentSourceResponse]:
        """Search for learning content across multiple platforms"""
        
        discovered_content = []
        
        # Default platforms if none specified
        if not platforms:
            platforms = ["medium", "dev.to", "coursera", "udemy"]
        
        # Search each platform
        for platform in platforms:
            try:
                platform_results = await self._search_platform(platform, query, max_results // len(platforms))
                discovered_content.extend(platform_results)
            except Exception as e:
                print(f"Error searching {platform}: {e}")
                continue
        
        # Filter by content types if specified
        if content_types:
            content_type_values = [ct.value for ct in content_types]
            discovered_content = [
                content for content in discovered_content 
                if content.content_type.value in content_type_values
            ]
        
        # Store in database and return
        stored_content = []
        for content in discovered_content[:max_results]:
            try:
                stored = await self._store_content(content)
                if stored:
                    stored_content.append(stored)
            except Exception as e:
                print(f"Error storing content: {e}")
                continue
        
        return stored_content
    
    async def _search_platform(self, platform: str, query: str, max_results: int) -> List[ContentSourceResponse]:
        """Search a specific platform for content"""
        
        if platform not in self.search_configs:
            return []
        
        config = self.search_configs[platform]
        
        if platform == "youtube":
            return await self._search_youtube(query, max_results)
        elif platform in ["medium", "dev.to", "coursera", "udemy"]:
            return await self._search_web_platform(platform, query, max_results)
        
        return []
    
    async def _search_youtube(self, query: str, max_results: int) -> List[ContentSourceResponse]:
        """Search YouTube for educational videos (mock implementation)"""
        # In production, you'd use YouTube Data API
        # For now, return mock data
        
        mock_results = [
            {
                "title": f"Learn {query} - Complete Tutorial",
                "description": f"Comprehensive tutorial covering {query} from basics to advanced concepts",
                "url": f"https://youtube.com/watch?v=mock_{query.replace(' ', '_')}",
                "duration_minutes": 45,
                "view_count": 125000,
                "rating": 4.5
            },
            {
                "title": f"{query} Crash Course",
                "description": f"Quick crash course in {query} for beginners",
                "url": f"https://youtube.com/watch?v=crash_{query.replace(' ', '_')}",
                "duration_minutes": 20,
                "view_count": 89000,
                "rating": 4.3
            }
        ]
        
        results = []
        for item in mock_results[:max_results]:
            results.append(ContentSourceResponse(
                id=str(uuid.uuid4()),
                url=item["url"],
                title=item["title"],
                description=item["description"],
                content_type=ContentType.VIDEO,
                source_platform="youtube",
                duration_minutes=item["duration_minutes"],
                difficulty_level=DifficultyLevel.INTERMEDIATE,
                topics=[query],
                rating=item["rating"],
                view_count=item["view_count"],
                created_at=None
            ))
        
        return results
    
    async def _search_web_platform(self, platform: str, query: str, max_results: int) -> List[ContentSourceResponse]:
        """Search web platforms by scraping (mock implementation)"""
        
        # Mock results for different platforms
        mock_data = {
            "medium": {
                "content_type": ContentType.ARTICLE,
                "results": [
                    {
                        "title": f"Understanding {query}: A Deep Dive",
                        "description": f"Comprehensive article about {query} with practical examples",
                        "url": f"https://medium.com/@author/understanding-{query.replace(' ', '-')}",
                        "duration_minutes": 8
                    },
                    {
                        "title": f"5 Tips for Mastering {query}",
                        "description": f"Practical tips and tricks for learning {query} effectively",
                        "url": f"https://medium.com/@expert/tips-{query.replace(' ', '-')}",
                        "duration_minutes": 5
                    }
                ]
            },
            "dev.to": {
                "content_type": ContentType.ARTICLE,
                "results": [
                    {
                        "title": f"Getting Started with {query}",
                        "description": f"Beginner-friendly guide to {query}",
                        "url": f"https://dev.to/developer/getting-started-{query.replace(' ', '-')}",
                        "duration_minutes": 6
                    }
                ]
            },
            "coursera": {
                "content_type": ContentType.COURSE,
                "results": [
                    {
                        "title": f"{query} Specialization",
                        "description": f"Complete specialization in {query} from top universities",
                        "url": f"https://coursera.org/specializations/{query.replace(' ', '-')}",
                        "duration_minutes": 1200  # 20 hours
                    }
                ]
            },
            "udemy": {
                "content_type": ContentType.COURSE,
                "results": [
                    {
                        "title": f"Complete {query} Course",
                        "description": f"Learn {query} from scratch with hands-on projects",
                        "url": f"https://udemy.com/course/{query.replace(' ', '-')}",
                        "duration_minutes": 600  # 10 hours
                    }
                ]
            }
        }
        
        if platform not in mock_data:
            return []
        
        platform_data = mock_data[platform]
        results = []
        
        for item in platform_data["results"][:max_results]:
            results.append(ContentSourceResponse(
                id=str(uuid.uuid4()),
                url=item["url"],
                title=item["title"],
                description=item["description"],
                content_type=platform_data["content_type"],
                source_platform=platform,
                duration_minutes=item["duration_minutes"],
                difficulty_level=DifficultyLevel.INTERMEDIATE,
                topics=[query],
                rating=4.2,
                view_count=None,
                created_at=None
            ))
        
        return results
    
    async def _store_content(self, content: ContentSourceResponse) -> Optional[ContentSourceResponse]:
        """Store discovered content in database"""
        
        # Check if URL already exists
        result = await self.db.execute(
            select(ContentSource).where(ContentSource.url == content.url)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            return ContentSourceResponse(
                id=str(existing.id),
                url=existing.url,
                title=existing.title,
                description=existing.description,
                content_type=ContentType(existing.content_type),
                source_platform=existing.source_platform,
                duration_minutes=existing.duration_minutes,
                difficulty_level=existing.difficulty_level,
                topics=existing.topics,
                rating=existing.rating,
                view_count=existing.view_count,
                created_at=existing.created_at
            )
        
        # Create new content source
        db_content = ContentSource(
            url=content.url,
            title=content.title,
            description=content.description,
            content_type=content.content_type.value,
            source_platform=content.source_platform,
            duration_minutes=content.duration_minutes,
            difficulty_level=content.difficulty_level.value if content.difficulty_level else None,
            topics=content.topics,
            rating=content.rating,
            view_count=content.view_count
        )
        
        self.db.add(db_content)
        await self.db.commit()
        await self.db.refresh(db_content)
        
        return ContentSourceResponse(
            id=str(db_content.id),
            url=db_content.url,
            title=db_content.title,
            description=db_content.description,
            content_type=ContentType(db_content.content_type),
            source_platform=db_content.source_platform,
            duration_minutes=db_content.duration_minutes,
            difficulty_level=db_content.difficulty_level,
            topics=db_content.topics,
            rating=db_content.rating,
            view_count=db_content.view_count,
            created_at=db_content.created_at
        )
    
    async def index_content_embeddings(self, content_id: str):
        """Generate and store embeddings for content (background task)"""
        await self.embedding_service.generate_content_embeddings(self.db, content_id)
    
    async def enhance_content_metadata(self, content_id: str):
        """Use AI to enhance content metadata"""
        
        result = await self.db.execute(
            select(ContentSource).where(ContentSource.id == uuid.UUID(content_id))
        )
        content = result.scalar_one_or_none()
        
        if not content:
            return
        
        # Use AI to analyze and enhance metadata
        analysis = await self.openai_service.analyze_content_quality(
            content.title, 
            content.description or "", 
            content.url
        )
        
        # Update content with enhanced metadata
        updates = {}
        if not content.difficulty_level and analysis.get("difficulty_level"):
            updates["difficulty_level"] = analysis["difficulty_level"]
        
        if not content.topics and analysis.get("topics"):
            updates["topics"] = analysis["topics"]
        
        if not content.rating and analysis.get("quality_score"):
            updates["rating"] = analysis["quality_score"]
        
        if updates:
            from sqlalchemy import update as sql_update
            await self.db.execute(
                sql_update(ContentSource)
                .where(ContentSource.id == uuid.UUID(content_id))
                .values(**updates)
            )
            await self.db.commit()
