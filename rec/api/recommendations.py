from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import List, Optional
import uuid

from ..database import get_db, ContentSource, LearningPreference, LearningGoal, Recommendation
from ..models import (
    RecommendationRequest,
    RecommendationResponse,
    RecommendationListResponse,
    ContentSourceResponse,
    ContentType
)
from ..services.recommendation_engine import RecommendationEngine

router = APIRouter()

@router.post("/generate", response_model=RecommendationListResponse)
async def generate_recommendations(
    request: RecommendationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Generate personalized content recommendations for a user"""
    recommendation_engine = RecommendationEngine(db)
    
    # Get user preferences
    user_prefs_result = await db.execute(
        select(LearningPreference).where(LearningPreference.user_id == uuid.UUID(request.user_id))
    )
    user_preferences = user_prefs_result.scalar_one_or_none()
    
    if not user_preferences:
        raise HTTPException(status_code=404, detail="User preferences not found. Please complete the learning style quiz first.")
    
    # Get learning goal if specified
    learning_goal = None
    if request.goal_id:
        goal_result = await db.execute(
            select(LearningGoal).where(LearningGoal.id == uuid.UUID(request.goal_id))
        )
        learning_goal = goal_result.scalar_one_or_none()
    
    # Generate recommendations
    recommendations = await recommendation_engine.generate_recommendations(
        user_id=request.user_id,
        user_preferences=user_preferences,
        learning_goal=learning_goal,
        query=request.query,
        max_results=request.max_results,
        content_types=request.content_types,
        difficulty_levels=request.difficulty_levels
    )
    
    # Convert to response format
    recommendation_responses = []
    for rec in recommendations:
        content_result = await db.execute(
            select(ContentSource).where(ContentSource.id == rec.content_id)
        )
        content = content_result.scalar_one()
        
        recommendation_responses.append(
            RecommendationResponse(
                id=str(rec.id),
                content=ContentSourceResponse(
                    id=str(content.id),
                    url=content.url,
                    title=content.title,
                    description=content.description,
                    content_type=ContentType(content.content_type),
                    source_platform=content.source_platform,
                    duration_minutes=content.duration_minutes,
                    difficulty_level=content.difficulty_level,
                    topics=content.topics,
                    rating=content.rating,
                    view_count=content.view_count,
                    created_at=content.created_at
                ),
                similarity_score=rec.similarity_score,
                preference_score=rec.preference_score,
                final_score=rec.final_score,
                reasoning=rec.reasoning
            )
        )
    
    # Prepare user preferences summary
    user_prefs_summary = {
        "learning_style": {
            "visual": user_preferences.visual_preference,
            "auditory": user_preferences.auditory_preference,
            "kinesthetic": user_preferences.kinesthetic_preference,
            "reading": user_preferences.reading_preference
        },
        "content_preferences": {
            "video": user_preferences.video_preference,
            "article": user_preferences.article_preference,
            "interactive": user_preferences.interactive_preference,
            "course": user_preferences.course_preference
        },
        "preferred_difficulty": user_preferences.preferred_difficulty,
        "preferred_session_length": user_preferences.preferred_session_length,
        "interests": user_preferences.interests
    }
    
    return RecommendationListResponse(
        recommendations=recommendation_responses,
        total_count=len(recommendation_responses),
        user_preferences=user_prefs_summary
    )

@router.get("/user/{user_id}/history")
async def get_recommendation_history(
    user_id: str,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """Get user's recommendation history"""
    result = await db.execute(
        select(Recommendation)
        .where(Recommendation.user_id == uuid.UUID(user_id))
        .order_by(Recommendation.created_at.desc())
        .limit(limit)
    )
    recommendations = result.scalars().all()
    
    # Get content details for each recommendation
    recommendation_responses = []
    for rec in recommendations:
        content_result = await db.execute(
            select(ContentSource).where(ContentSource.id == rec.content_id)
        )
        content = content_result.scalar_one_or_none()
        
        if content:  # Only include if content still exists
            recommendation_responses.append(
                RecommendationResponse(
                    id=str(rec.id),
                    content=ContentSourceResponse(
                        id=str(content.id),
                        url=content.url,
                        title=content.title,
                        description=content.description,
                        content_type=ContentType(content.content_type),
                        source_platform=content.source_platform,
                        duration_minutes=content.duration_minutes,
                        difficulty_level=content.difficulty_level,
                        topics=content.topics,
                        rating=content.rating,
                        view_count=content.view_count,
                        created_at=content.created_at
                    ),
                    similarity_score=rec.similarity_score,
                    preference_score=rec.preference_score,
                    final_score=rec.final_score,
                    reasoning=rec.reasoning
                )
            )
    
    return {"recommendations": recommendation_responses, "total_count": len(recommendation_responses)}

@router.post("/feedback/{recommendation_id}")
async def provide_recommendation_feedback(
    recommendation_id: str,
    feedback: dict,  # {"rating": 1-5, "helpful": bool, "comments": str}
    db: AsyncSession = Depends(get_db)
):
    """Provide feedback on a recommendation to improve future suggestions"""
    # This would be used to improve the recommendation algorithm
    # For now, just acknowledge the feedback
    return {"message": "Feedback received successfully", "recommendation_id": recommendation_id}

@router.get("/explain/{recommendation_id}")
async def explain_recommendation(
    recommendation_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get detailed explanation of why a recommendation was made"""
    result = await db.execute(
        select(Recommendation).where(Recommendation.id == uuid.UUID(recommendation_id))
    )
    recommendation = result.scalar_one_or_none()
    
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    return {
        "recommendation_id": recommendation_id,
        "similarity_score": recommendation.similarity_score,
        "preference_score": recommendation.preference_score,
        "final_score": recommendation.final_score,
        "reasoning": recommendation.reasoning,
        "factors": {
            "content_match": "How well the content matches your learning goals",
            "style_preference": "How well it aligns with your learning style",
            "difficulty_level": "Appropriate difficulty for your level",
            "content_type": "Matches your preferred content format"
        }
    }
