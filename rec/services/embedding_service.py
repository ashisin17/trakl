from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
import uuid
from config import settings
from typing import List, Optional
import numpy as np

from database import ContentSource, LearningGoal
from services.openai_service import DedalusService

class EmbeddingService:
    def __init__(self):
        self.dedalus_service = DedalusService()
    
    async def generate_content_embeddings(self, db: AsyncSession, content_id: str):
        """Generate and store embeddings for content"""
        
        result = await db.execute(
            select(ContentSource).where(ContentSource.id == uuid.UUID(content_id))
        )
        content = result.scalar_one_or_none()
        
        if not content:
            return
        
        # Prepare text for embedding
        title_text = content.title or ""
        content_text = f"{content.title} {content.description or ''} {' '.join(content.topics or [])}"
        
        # Generate embeddings
        embeddings = await self.dedalus_service.generate_embeddings([title_text, content_text])
        
        if len(embeddings) >= 2:
            # Update content with embeddings
            await db.execute(
                update(ContentSource)
                .where(ContentSource.id == uuid.UUID(content_id))
                .values(
                    title_embedding=embeddings[0],
                    content_embedding=embeddings[1]
                )
            )
            await db.commit()
    
    async def generate_goal_embedding(self, db: AsyncSession, goal_id: str):
        """Generate and store embedding for learning goal"""
        
        result = await db.execute(
            select(LearningGoal).where(LearningGoal.id == uuid.UUID(goal_id))
        )
        goal = result.scalar_one_or_none()
        
        if not goal:
            return
        
        # Prepare goal text for embedding
        goal_text = f"{goal.title} {goal.description} {' '.join(goal.target_skills or [])}"
        
        # Generate embedding
        embeddings = await self.dedalus_service.generate_embeddings([goal_text])
        
        if embeddings:
            # Update goal with embedding
            await db.execute(
                update(LearningGoal)
                .where(LearningGoal.id == uuid.UUID(goal_id))
                .values(goal_embedding=embeddings[0])
            )
            await db.commit()
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        
        if not embedding1 or not embedding2:
            return 0.0
        
        # Convert to numpy arrays
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # Calculate cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        return float(similarity)
    
    async def find_similar_content(
        self, 
        db: AsyncSession, 
        query_embedding: List[float], 
        limit: int = 10,
        threshold: float = 0.7
    ) -> List[tuple]:
        """Find content similar to query embedding using vector similarity"""
        
        # In production, you'd use pgvector's similarity operators
        # For now, we'll do a simple implementation
        
        result = await db.execute(
            select(ContentSource).where(ContentSource.content_embedding.isnot(None))
        )
        all_content = result.scalars().all()
        
        similarities = []
        for content in all_content:
            if content.content_embedding:
                similarity = self.calculate_similarity(query_embedding, content.content_embedding)
                if similarity >= threshold:
                    similarities.append((content, similarity))
        
        # Sort by similarity and return top results
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:limit]
