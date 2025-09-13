from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List
import uuid

from ..database import get_db, LearningPreference, User
from ..models import (
    LearningPreferenceCreate, 
    LearningPreferenceUpdate,
    QuizQuestion,
    QuizResponse,
    QuizResult
)
from ..services.preference_service import PreferenceService

router = APIRouter()

# Learning Style Quiz Questions
QUIZ_QUESTIONS = [
    QuizQuestion(
        id="visual_1",
        question="When learning something new, I prefer to:",
        options=[
            {"value": "diagrams", "text": "See diagrams, charts, and visual aids", "category": "visual", "weight": 1.0},
            {"value": "listen", "text": "Listen to explanations and discussions", "category": "auditory", "weight": 1.0},
            {"value": "hands_on", "text": "Try it out hands-on immediately", "category": "kinesthetic", "weight": 1.0},
            {"value": "read", "text": "Read detailed written instructions", "category": "reading", "weight": 1.0}
        ],
        category="learning_style"
    ),
    QuizQuestion(
        id="content_type_1",
        question="For learning programming, I find most helpful:",
        options=[
            {"value": "video_tutorials", "text": "Video tutorials with screen recordings", "category": "video", "weight": 1.0},
            {"value": "written_guides", "text": "Written tutorials and documentation", "category": "article", "weight": 1.0},
            {"value": "interactive_coding", "text": "Interactive coding exercises", "category": "interactive", "weight": 1.0},
            {"value": "structured_course", "text": "Structured online courses", "category": "course", "weight": 1.0}
        ],
        category="content_type"
    ),
    QuizQuestion(
        id="visual_2",
        question="When I need to remember information, I:",
        options=[
            {"value": "visualize", "text": "Create mental pictures or mind maps", "category": "visual", "weight": 0.8},
            {"value": "repeat", "text": "Repeat it out loud or in my head", "category": "auditory", "weight": 0.8},
            {"value": "write_practice", "text": "Write it down and practice", "category": "kinesthetic", "weight": 0.8},
            {"value": "organize_notes", "text": "Organize it in detailed notes", "category": "reading", "weight": 0.8}
        ],
        category="learning_style"
    ),
    QuizQuestion(
        id="difficulty_pref",
        question="I prefer learning materials that are:",
        options=[
            {"value": "beginner", "text": "Step-by-step from the basics", "category": "difficulty", "weight": 1.0},
            {"value": "intermediate", "text": "Moderately challenging with some prior knowledge", "category": "difficulty", "weight": 1.0},
            {"value": "advanced", "text": "Advanced and assume strong fundamentals", "category": "difficulty", "weight": 1.0}
        ],
        category="difficulty"
    ),
    QuizQuestion(
        id="session_length",
        question="My ideal learning session length is:",
        options=[
            {"value": "15", "text": "15-20 minutes (quick focused bursts)", "category": "session", "weight": 1.0},
            {"value": "30", "text": "30-45 minutes (moderate sessions)", "category": "session", "weight": 1.0},
            {"value": "60", "text": "60+ minutes (deep dive sessions)", "category": "session", "weight": 1.0}
        ],
        category="session_length"
    )
]

@router.get("/quiz", response_model=List[QuizQuestion])
async def get_learning_style_quiz():
    """Get the learning style assessment quiz"""
    return QUIZ_QUESTIONS

@router.post("/quiz/submit", response_model=QuizResult)
async def submit_quiz(
    user_id: str,
    quiz_response: QuizResponse,
    db: AsyncSession = Depends(get_db)
):
    """Submit quiz responses and generate learning preferences"""
    preference_service = PreferenceService(db)
    
    # Calculate preferences from quiz responses
    preferences = await preference_service.calculate_preferences_from_quiz(quiz_response.responses)
    
    # Save or update user preferences
    await preference_service.save_user_preferences(user_id, preferences)
    
    # Generate explanation
    explanation = await preference_service.generate_preference_explanation(preferences)
    
    return QuizResult(
        preferences=preferences,
        explanation=explanation,
        confidence_score=0.85  # Could be calculated based on response consistency
    )

@router.get("/user/{user_id}", response_model=LearningPreferenceCreate)
async def get_user_preferences(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get user's learning preferences"""
    result = await db.execute(
        select(LearningPreference).where(LearningPreference.user_id == user_id)
    )
    preference = result.scalar_one_or_none()
    
    if not preference:
        raise HTTPException(status_code=404, detail="User preferences not found")
    
    return LearningPreferenceCreate(
        visual_preference=preference.visual_preference,
        auditory_preference=preference.auditory_preference,
        kinesthetic_preference=preference.kinesthetic_preference,
        reading_preference=preference.reading_preference,
        video_preference=preference.video_preference,
        article_preference=preference.article_preference,
        interactive_preference=preference.interactive_preference,
        course_preference=preference.course_preference,
        preferred_difficulty=preference.preferred_difficulty,
        preferred_session_length=preference.preferred_session_length,
        interests=preference.interests or []
    )

@router.put("/user/{user_id}", response_model=LearningPreferenceCreate)
async def update_user_preferences(
    user_id: str,
    preferences: LearningPreferenceUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update user's learning preferences"""
    # Check if preferences exist
    result = await db.execute(
        select(LearningPreference).where(LearningPreference.user_id == user_id)
    )
    existing = result.scalar_one_or_none()
    
    if not existing:
        raise HTTPException(status_code=404, detail="User preferences not found")
    
    # Update only provided fields
    update_data = {k: v for k, v in preferences.dict().items() if v is not None}
    
    await db.execute(
        update(LearningPreference)
        .where(LearningPreference.user_id == user_id)
        .values(**update_data)
    )
    await db.commit()
    
    # Return updated preferences
    return await get_user_preferences(user_id, db)

@router.post("/user/{user_id}/interests")
async def add_user_interests(
    user_id: str,
    interests: List[str],
    db: AsyncSession = Depends(get_db)
):
    """Add interests to user's profile"""
    result = await db.execute(
        select(LearningPreference).where(LearningPreference.user_id == user_id)
    )
    preference = result.scalar_one_or_none()
    
    if not preference:
        raise HTTPException(status_code=404, detail="User preferences not found")
    
    # Merge new interests with existing ones
    current_interests = set(preference.interests or [])
    new_interests = current_interests.union(set(interests))
    
    await db.execute(
        update(LearningPreference)
        .where(LearningPreference.user_id == user_id)
        .values(interests=list(new_interests))
    )
    await db.commit()
    
    return {"message": "Interests updated successfully", "interests": list(new_interests)}
