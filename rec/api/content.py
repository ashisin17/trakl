from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
import uuid

from database import get_db, ContentSource
from models import (
    ContentSourceCreate,
    ContentSourceResponse, 
    ContentDiscoveryRequest,
    ContentDiscoveryResponse,
    ContentType
)
from services.content_discovery import ContentDiscoveryService
from services.embedding_service import EmbeddingService

router = APIRouter()

@router.post("/discover", response_model=ContentDiscoveryResponse)
async def discover_content(
    request: ContentDiscoveryRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Discover and index new learning content from the internet"""
    discovery_service = ContentDiscoveryService(db)
    
    # Search for content
    discovered_sources = await discovery_service.search_content(
        query=request.query,
        content_types=request.content_types,
        max_results=request.max_results,
        platforms=request.platforms
    )
    
    # Schedule background indexing for embeddings
    for source in discovered_sources:
        background_tasks.add_task(
            discovery_service.index_content_embeddings,
            source.id
        )
    
    return ContentDiscoveryResponse(
        sources=discovered_sources,
        query=request.query,
        total_found=len(discovered_sources)
    )

@router.post("/", response_model=ContentSourceResponse)
async def create_content_source(
    content: ContentSourceCreate,
    db: AsyncSession = Depends(get_db)
):
    """Manually add a content source"""
    # Check if URL already exists
    result = await db.execute(
        select(ContentSource).where(ContentSource.url == content.url)
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(status_code=400, detail="Content source already exists")
    
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
    
    db.add(db_content)
    await db.commit()
    await db.refresh(db_content)
    
    # Generate embeddings in background
    embedding_service = EmbeddingService()
    await embedding_service.generate_content_embeddings(db, str(db_content.id))
    
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

@router.get("/search")
async def search_content(
    query: str,
    content_types: Optional[List[ContentType]] = None,
    difficulty_levels: Optional[List[str]] = None,
    topics: Optional[List[str]] = None,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """Search existing content sources"""
    # Build query conditions
    conditions = []
    
    if content_types:
        conditions.append(ContentSource.content_type.in_([ct.value for ct in content_types]))
    
    if difficulty_levels:
        conditions.append(ContentSource.difficulty_level.in_(difficulty_levels))
    
    if topics:
        # Search for content that has any of the specified topics
        topic_conditions = []
        for topic in topics:
            topic_conditions.append(ContentSource.topics.contains([topic]))
        if topic_conditions:
            conditions.append(or_(*topic_conditions))
    
    # Execute search
    query_stmt = select(ContentSource)
    if conditions:
        query_stmt = query_stmt.where(and_(*conditions))
    
    query_stmt = query_stmt.limit(limit)
    
    result = await db.execute(query_stmt)
    sources = result.scalars().all()
    
    return [
        ContentSourceResponse(
            id=str(source.id),
            url=source.url,
            title=source.title,
            description=source.description,
            content_type=ContentType(source.content_type),
            source_platform=source.source_platform,
            duration_minutes=source.duration_minutes,
            difficulty_level=source.difficulty_level,
            topics=source.topics,
            rating=source.rating,
            view_count=source.view_count,
            created_at=source.created_at
        )
        for source in sources
    ]

@router.get("/{content_id}", response_model=ContentSourceResponse)
async def get_content_source(
    content_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific content source by ID"""
    result = await db.execute(
        select(ContentSource).where(ContentSource.id == uuid.UUID(content_id))
    )
    source = result.scalar_one_or_none()
    
    if not source:
        raise HTTPException(status_code=404, detail="Content source not found")
    
    return ContentSourceResponse(
        id=str(source.id),
        url=source.url,
        title=source.title,
        description=source.description,
        content_type=ContentType(source.content_type),
        source_platform=source.source_platform,
        duration_minutes=source.duration_minutes,
        difficulty_level=source.difficulty_level,
        topics=source.topics,
        rating=source.rating,
        view_count=source.view_count,
        created_at=source.created_at
    )

@router.delete("/{content_id}")
async def delete_content_source(
    content_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a content source"""
    result = await db.execute(
        select(ContentSource).where(ContentSource.id == uuid.UUID(content_id))
    )
    source = result.scalar_one_or_none()
    
    if not source:
        raise HTTPException(status_code=404, detail="Content source not found")
    
    await db.delete(source)
    await db.commit()
    
    return {"message": "Content source deleted successfully"}

@router.get("/platforms/list")
async def list_platforms(db: AsyncSession = Depends(get_db)):
    """Get list of available content platforms"""
    result = await db.execute(
        select(ContentSource.source_platform).distinct()
    )
    platforms = [row[0] for row in result.fetchall()]
    return {"platforms": platforms}

@router.get("/topics/list")
async def list_topics(db: AsyncSession = Depends(get_db)):
    """Get list of available topics"""
    result = await db.execute(select(ContentSource.topics))
    all_topics = set()
    
    for row in result.fetchall():
        if row[0]:  # topics array
            all_topics.update(row[0])
    
    return {"topics": sorted(list(all_topics))}
