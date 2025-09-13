from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, String, DateTime, Text, JSON, Float, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from pgvector.sqlalchemy import Vector
import uuid
from datetime import datetime
from .config import settings

# Create async engine
engine = create_async_engine(
    settings.database_url.replace("postgresql://", "postgresql+asyncpg://"),
    echo=True
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True)
    name = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

class LearningPreference(Base):
    __tablename__ = "learning_preferences"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), index=True)
    
    # Learning style preferences
    visual_preference = Column(Float, default=0.5)  # 0-1 scale
    auditory_preference = Column(Float, default=0.5)
    kinesthetic_preference = Column(Float, default=0.5)
    reading_preference = Column(Float, default=0.5)
    
    # Content type preferences
    video_preference = Column(Float, default=0.5)
    article_preference = Column(Float, default=0.5)
    interactive_preference = Column(Float, default=0.5)
    course_preference = Column(Float, default=0.5)
    
    # Difficulty and pacing
    preferred_difficulty = Column(String(20), default="intermediate")  # beginner, intermediate, advanced
    preferred_session_length = Column(Integer, default=30)  # minutes
    
    # Topics and interests
    interests = Column(ARRAY(String), default=[])
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ContentSource(Base):
    __tablename__ = "content_sources"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    url = Column(String(500), unique=True, index=True)
    title = Column(String(200))
    description = Column(Text)
    content_type = Column(String(50))  # video, article, course, interactive, etc.
    source_platform = Column(String(100))  # youtube, coursera, medium, etc.
    
    # Content metadata
    duration_minutes = Column(Integer)
    difficulty_level = Column(String(20))
    topics = Column(ARRAY(String))
    
    # Embeddings for similarity search
    title_embedding = Column(Vector(1536))  # OpenAI embedding dimension
    content_embedding = Column(Vector(1536))
    
    # Quality metrics
    rating = Column(Float)
    view_count = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow)

class UserInteraction(Base):
    __tablename__ = "user_interactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), index=True)
    content_id = Column(UUID(as_uuid=True), index=True)
    
    interaction_type = Column(String(50))  # viewed, liked, completed, bookmarked, skipped
    rating = Column(Float)  # user rating 1-5
    time_spent_minutes = Column(Integer)
    completion_percentage = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class LearningGoal(Base):
    __tablename__ = "learning_goals"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), index=True)
    
    title = Column(String(200))
    description = Column(Text)
    target_skills = Column(ARRAY(String))
    timeframe_weeks = Column(Integer)
    difficulty_level = Column(String(20))
    
    # Goal embedding for content matching
    goal_embedding = Column(Vector(1536))
    
    status = Column(String(20), default="active")  # active, completed, paused
    progress_percentage = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Recommendation(Base):
    __tablename__ = "recommendations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), index=True)
    goal_id = Column(UUID(as_uuid=True), index=True)
    content_id = Column(UUID(as_uuid=True), index=True)
    
    similarity_score = Column(Float)
    preference_score = Column(Float)
    final_score = Column(Float)
    
    reasoning = Column(Text)  # AI-generated explanation
    
    created_at = Column(DateTime, default=datetime.utcnow)

# Dependency to get database session
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
