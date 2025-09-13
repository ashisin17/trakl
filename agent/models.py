from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class PlanStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"

class SessionStatus(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"

class SessionType(str, Enum):
    STUDY = "study"
    PRACTICE = "practice"
    REVIEW = "review"
    ASSESSMENT = "assessment"

class MilestoneStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

# Learning Plan Models
class Milestone(BaseModel):
    title: str
    description: str
    target_week: int
    milestone_type: str
    success_criteria: List[str]
    required_skills: List[str]

class WeeklySchedule(BaseModel):
    week_number: int
    focus_areas: List[str]
    sessions: List[Dict[str, Any]]
    milestones: List[str]
    estimated_hours: float

class LearningPlanCreate(BaseModel):
    user_id: str
    goal_id: str
    title: str
    description: str
    total_weeks: int = Field(ge=1, le=52)
    sessions_per_week: int = Field(ge=1, le=7, default=3)
    difficulty_level: str = "intermediate"
    tags: List[str] = []

class LearningPlanResponse(BaseModel):
    id: str
    user_id: str
    goal_id: str
    title: str
    description: str
    total_weeks: int
    sessions_per_week: int
    estimated_hours_total: Optional[float]
    milestones: List[Milestone]
    weekly_schedule: List[WeeklySchedule]
    recommended_resources: List[str]
    status: PlanStatus
    progress_percentage: float
    current_week: int
    difficulty_level: str
    tags: List[str]
    created_at: datetime

class PlanGenerationRequest(BaseModel):
    user_id: str
    goal_id: str
    preferences: Optional[Dict[str, Any]] = None
    constraints: Optional[Dict[str, Any]] = None

# Learning Session Models
class SessionActivity(BaseModel):
    content_id: str
    activity_type: str  # read, watch, practice, quiz
    estimated_minutes: int
    description: str

class LearningSessionCreate(BaseModel):
    user_id: str
    plan_id: str
    title: str
    description: str
    session_type: SessionType
    scheduled_start: datetime
    duration_minutes: int = Field(ge=5, le=300)
    content_items: List[SessionActivity]
    learning_objectives: List[str]

class LearningSessionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    scheduled_start: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, ge=5, le=300)
    status: Optional[SessionStatus] = None
    completion_percentage: Optional[float] = Field(None, ge=0, le=100)
    user_rating: Optional[float] = Field(None, ge=1, le=5)
    user_notes: Optional[str] = None

class LearningSessionResponse(BaseModel):
    id: str
    user_id: str
    plan_id: str
    title: str
    description: str
    session_type: SessionType
    scheduled_start: Optional[datetime]
    scheduled_end: Optional[datetime]
    actual_start: Optional[datetime]
    actual_end: Optional[datetime]
    duration_minutes: int
    content_items: List[SessionActivity]
    learning_objectives: List[str]
    status: SessionStatus
    completion_percentage: float
    user_rating: Optional[float]
    user_notes: Optional[str]
    ai_feedback: Optional[str]
    calendar_event_id: Optional[str]
    created_at: datetime

# Progress Models
class SkillProgress(BaseModel):
    skill_name: str
    proficiency_level: float  # 0-1 scale
    last_practiced: Optional[datetime]
    practice_sessions: int

class WeeklyProgressSummary(BaseModel):
    week_number: int
    sessions_completed: int
    sessions_scheduled: int
    total_study_time_minutes: int
    skills_practiced: List[str]
    milestones_achieved: List[str]
    average_rating: Optional[float]
    notes: str

class UserProgressResponse(BaseModel):
    id: str
    user_id: str
    plan_id: str
    total_study_time_minutes: int
    sessions_completed: int
    sessions_scheduled: int
    skills_mastered: List[str]
    skills_in_progress: List[str]
    average_session_rating: Optional[float]
    consistency_score: Optional[float]
    engagement_score: Optional[float]
    current_streak_days: int
    longest_streak_days: int
    achievements: List[Dict[str, Any]]
    weekly_summaries: List[WeeklyProgressSummary]
    last_updated: datetime

class ProgressUpdateRequest(BaseModel):
    session_id: str
    completion_percentage: float = Field(ge=0, le=100)
    time_spent_minutes: int = Field(ge=0)
    skills_practiced: List[str] = []
    user_feedback: Optional[str] = None

# Calendar Integration Models
class TimeSlot(BaseModel):
    day_of_week: int  # 0-6 (Monday-Sunday)
    start_time: str   # HH:MM format
    end_time: str     # HH:MM format

class CalendarPreferences(BaseModel):
    auto_schedule_enabled: bool = False
    preferred_time_slots: List[TimeSlot] = []
    buffer_minutes: int = Field(default=15, ge=0, le=60)
    max_sessions_per_day: int = Field(default=3, ge=1, le=8)

class CalendarIntegrationResponse(BaseModel):
    id: str
    user_id: str
    primary_calendar_id: Optional[str]
    auto_schedule_enabled: bool
    preferred_time_slots: List[TimeSlot]
    last_sync: Optional[datetime]
    sync_enabled: bool
    created_at: datetime

class ScheduleSessionRequest(BaseModel):
    session_id: str
    preferred_datetime: Optional[datetime] = None
    auto_find_slot: bool = True

# AI Generation Models
class PlanGenerationResponse(BaseModel):
    plan: LearningPlanResponse
    reasoning: str
    estimated_completion_date: datetime
    success_probability: float
