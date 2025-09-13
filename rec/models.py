from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ContentType(str, Enum):
    VIDEO = "video"
    ARTICLE = "article"
    COURSE = "course"
    INTERACTIVE = "interactive"
    PODCAST = "podcast"
    BOOK = "book"

class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class InteractionType(str, Enum):
    VIEWED = "viewed"
    LIKED = "liked"
    COMPLETED = "completed"
    BOOKMARKED = "bookmarked"
    SKIPPED = "skipped"
    RATED = "rated"

# Learning Preference Models
class LearningStyleQuizResponse(BaseModel):
    question_id: str
    answer: str
    weight: float = 1.0

class LearningPreferenceCreate(BaseModel):
    visual_preference: float = Field(ge=0, le=1, default=0.5)
    auditory_preference: float = Field(ge=0, le=1, default=0.5)
    kinesthetic_preference: float = Field(ge=0, le=1, default=0.5)
    reading_preference: float = Field(ge=0, le=1, default=0.5)
    
    video_preference: float = Field(ge=0, le=1, default=0.5)
    article_preference: float = Field(ge=0, le=1, default=0.5)
    interactive_preference: float = Field(ge=0, le=1, default=0.5)
    course_preference: float = Field(ge=0, le=1, default=0.5)
    
    preferred_difficulty: DifficultyLevel = DifficultyLevel.INTERMEDIATE
    preferred_session_length: int = Field(ge=5, le=180, default=30)
    interests: List[str] = []

class LearningPreferenceUpdate(BaseModel):
    visual_preference: Optional[float] = Field(None, ge=0, le=1)
    auditory_preference: Optional[float] = Field(None, ge=0, le=1)
    kinesthetic_preference: Optional[float] = Field(None, ge=0, le=1)
    reading_preference: Optional[float] = Field(None, ge=0, le=1)
    
    video_preference: Optional[float] = Field(None, ge=0, le=1)
    article_preference: Optional[float] = Field(None, ge=0, le=1)
    interactive_preference: Optional[float] = Field(None, ge=0, le=1)
    course_preference: Optional[float] = Field(None, ge=0, le=1)
    
    preferred_difficulty: Optional[DifficultyLevel] = None
    preferred_session_length: Optional[int] = Field(None, ge=5, le=180)
    interests: Optional[List[str]] = None

# Content Models
class ContentSourceCreate(BaseModel):
    url: str
    title: str
    description: Optional[str] = None
    content_type: ContentType
    source_platform: str
    duration_minutes: Optional[int] = None
    difficulty_level: Optional[DifficultyLevel] = None
    topics: List[str] = []
    rating: Optional[float] = Field(None, ge=0, le=5)
    view_count: Optional[int] = None

class ContentSourceResponse(BaseModel):
    id: str
    url: str
    title: str
    description: Optional[str]
    content_type: ContentType
    source_platform: str
    duration_minutes: Optional[int]
    difficulty_level: Optional[DifficultyLevel]
    topics: List[str]
    rating: Optional[float]
    view_count: Optional[int]
    created_at: datetime

# Learning Goal Models
class LearningGoalCreate(BaseModel):
    title: str
    description: str
    target_skills: List[str]
    timeframe_weeks: int = Field(ge=1, le=52)
    difficulty_level: DifficultyLevel = DifficultyLevel.INTERMEDIATE

class LearningGoalResponse(BaseModel):
    id: str
    title: str
    description: str
    target_skills: List[str]
    timeframe_weeks: int
    difficulty_level: DifficultyLevel
    status: str
    progress_percentage: float
    created_at: datetime

# Recommendation Models
class RecommendationRequest(BaseModel):
    user_id: str
    goal_id: Optional[str] = None
    query: Optional[str] = None
    max_results: int = Field(default=10, ge=1, le=50)
    content_types: Optional[List[ContentType]] = None
    difficulty_levels: Optional[List[DifficultyLevel]] = None

class RecommendationResponse(BaseModel):
    id: str
    content: ContentSourceResponse
    similarity_score: float
    preference_score: float
    final_score: float
    reasoning: str

class RecommendationListResponse(BaseModel):
    recommendations: List[RecommendationResponse]
    total_count: int
    user_preferences: Optional[Dict[str, Any]] = None

# User Interaction Models
class UserInteractionCreate(BaseModel):
    content_id: str
    interaction_type: InteractionType
    rating: Optional[float] = Field(None, ge=1, le=5)
    time_spent_minutes: Optional[int] = Field(None, ge=0)
    completion_percentage: Optional[float] = Field(None, ge=0, le=100)

# Content Discovery Models
class ContentDiscoveryRequest(BaseModel):
    query: str
    content_types: Optional[List[ContentType]] = None
    max_results: int = Field(default=20, ge=1, le=100)
    platforms: Optional[List[str]] = None

class ContentDiscoveryResponse(BaseModel):
    sources: List[ContentSourceResponse]
    query: str
    total_found: int

# Quiz Models for Learning Preferences
class QuizQuestion(BaseModel):
    id: str
    question: str
    options: List[Dict[str, Any]]
    category: str  # visual, auditory, kinesthetic, reading

class QuizResponse(BaseModel):
    responses: List[LearningStyleQuizResponse]

class QuizResult(BaseModel):
    preferences: LearningPreferenceCreate
    explanation: str
    confidence_score: float
