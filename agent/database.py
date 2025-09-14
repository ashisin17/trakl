from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, String, DateTime, Text, JSON, Float, Integer, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY
import uuid
from datetime import datetime
from config import settings

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

class LearningPlan(Base):
    __tablename__ = "learning_plans"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), index=True)
    goal_id = Column(UUID(as_uuid=True), index=True)  # References learning_goals from rec service
    
    title = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Plan structure
    total_weeks = Column(Integer, nullable=False)
    sessions_per_week = Column(Integer, default=3)
    estimated_hours_total = Column(Float)
    
    # Plan content
    milestones = Column(JSON)  # List of milestone objects
    weekly_schedule = Column(JSON)  # Week-by-week breakdown
    recommended_resources = Column(JSON)  # Content IDs from rec service
    
    # Status and progress
    status = Column(String(20), default="draft")  # draft, active, completed, paused
    progress_percentage = Column(Float, default=0.0)
    current_week = Column(Integer, default=1)
    
    # Metadata
    difficulty_level = Column(String(20))
    tags = Column(ARRAY(String))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class LearningSession(Base):
    __tablename__ = "learning_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), index=True)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("learning_plans.id"), index=True)
    
    # Session details
    title = Column(String(200), nullable=False)
    description = Column(Text)
    session_type = Column(String(50))  # study, practice, review, assessment
    
    # Timing
    scheduled_start = Column(DateTime)
    scheduled_end = Column(DateTime)
    actual_start = Column(DateTime)
    actual_end = Column(DateTime)
    duration_minutes = Column(Integer)
    
    # Content and activities
    content_items = Column(JSON)  # List of content IDs and activities
    learning_objectives = Column(ARRAY(String))
    
    # Status and completion
    status = Column(String(20), default="scheduled")  # scheduled, in_progress, completed, skipped, cancelled
    completion_percentage = Column(Float, default=0.0)
    
    # Results and feedback
    user_rating = Column(Float)  # 1-5 rating
    user_notes = Column(Text)
    ai_feedback = Column(Text)
    
    # Calendar integration
    calendar_event_id = Column(String(200))  # Google Calendar event ID
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ProgressMilestone(Base):
    __tablename__ = "progress_milestones"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), index=True)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("learning_plans.id"), index=True)
    
    title = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Milestone details
    target_week = Column(Integer, nullable=False)
    milestone_type = Column(String(50))  # skill_check, project, assessment, review
    
    # Completion criteria
    success_criteria = Column(JSON)  # List of criteria objects
    required_skills = Column(ARRAY(String))
    
    # Status
    status = Column(String(20), default="pending")  # pending, in_progress, completed, failed
    completion_date = Column(DateTime)
    
    # Results
    score = Column(Float)  # 0-100 score
    feedback = Column(Text)
    evidence = Column(JSON)  # Links, files, etc.
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserProgress(Base):
    __tablename__ = "user_progress"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), index=True)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("learning_plans.id"), index=True)
    
    # Time tracking
    total_study_time_minutes = Column(Integer, default=0)
    sessions_completed = Column(Integer, default=0)
    sessions_scheduled = Column(Integer, default=0)
    
    # Skill progression
    skills_mastered = Column(ARRAY(String), default=[])
    skills_in_progress = Column(ARRAY(String), default=[])
    
    # Performance metrics
    average_session_rating = Column(Float)
    consistency_score = Column(Float)  # Based on adherence to schedule
    engagement_score = Column(Float)   # Based on session completion and feedback
    
    # Streaks and achievements
    current_streak_days = Column(Integer, default=0)
    longest_streak_days = Column(Integer, default=0)
    achievements = Column(JSON, default=[])
    
    # Weekly summaries
    weekly_summaries = Column(JSON, default=[])  # Array of weekly progress objects
    
    last_updated = Column(DateTime, default=datetime.utcnow)

class CalendarIntegration(Base):
    __tablename__ = "calendar_integrations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), unique=True, index=True)
    
    # OAuth credentials
    access_token = Column(Text)
    refresh_token = Column(Text)
    token_expiry = Column(DateTime)
    
    # Calendar settings
    primary_calendar_id = Column(String(200))
    auto_schedule_enabled = Column(Boolean, default=False)
    preferred_time_slots = Column(JSON)  # User's preferred learning times
    
    # Sync status
    last_sync = Column(DateTime)
    sync_enabled = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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
