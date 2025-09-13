from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List, Dict, Any
import uuid
from datetime import datetime

from ..database import LearningPreference, User
from ..models import LearningPreferenceCreate, LearningStyleQuizResponse
from .openai_service import OpenAIService

class PreferenceService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.openai_service = OpenAIService()
    
    async def calculate_preferences_from_quiz(self, responses: List[LearningStyleQuizResponse]) -> LearningPreferenceCreate:
        """Calculate learning preferences from quiz responses"""
        
        # Initialize preference scores
        scores = {
            'visual': 0.0,
            'auditory': 0.0,
            'kinesthetic': 0.0,
            'reading': 0.0,
            'video': 0.0,
            'article': 0.0,
            'interactive': 0.0,
            'course': 0.0
        }
        
        # Preference mapping from quiz answers
        preference_mapping = {
            'diagrams': {'visual': 1.0, 'video': 0.8},
            'listen': {'auditory': 1.0, 'video': 0.6},
            'hands_on': {'kinesthetic': 1.0, 'interactive': 1.0},
            'read': {'reading': 1.0, 'article': 0.9},
            'video_tutorials': {'video': 1.0, 'visual': 0.7},
            'written_guides': {'article': 1.0, 'reading': 0.8},
            'interactive_coding': {'interactive': 1.0, 'kinesthetic': 0.8},
            'structured_course': {'course': 1.0},
            'visualize': {'visual': 0.8},
            'repeat': {'auditory': 0.8},
            'write_practice': {'kinesthetic': 0.8, 'reading': 0.6},
            'organize_notes': {'reading': 0.8, 'article': 0.6}
        }
        
        # Process responses
        total_weight = 0.0
        for response in responses:
            if response.answer in preference_mapping:
                mappings = preference_mapping[response.answer]
                for pref_type, score in mappings.items():
                    if pref_type in scores:
                        scores[pref_type] += score * response.weight
                total_weight += response.weight
        
        # Normalize scores
        if total_weight > 0:
            for key in scores:
                scores[key] = min(1.0, scores[key] / total_weight)
        
        # Extract difficulty and session length from responses
        difficulty = "intermediate"
        session_length = 30
        
        for response in responses:
            if response.answer in ["beginner", "intermediate", "advanced"]:
                difficulty = response.answer
            elif response.answer in ["15", "30", "60"]:
                session_length = int(response.answer)
        
        return LearningPreferenceCreate(
            visual_preference=scores['visual'],
            auditory_preference=scores['auditory'],
            kinesthetic_preference=scores['kinesthetic'],
            reading_preference=scores['reading'],
            video_preference=scores['video'],
            article_preference=scores['article'],
            interactive_preference=scores['interactive'],
            course_preference=scores['course'],
            preferred_difficulty=difficulty,
            preferred_session_length=session_length,
            interests=[]
        )
    
    async def save_user_preferences(self, user_id: str, preferences: LearningPreferenceCreate):
        """Save or update user preferences in database"""
        
        # Check if preferences already exist
        result = await self.db.execute(
            select(LearningPreference).where(LearningPreference.user_id == uuid.UUID(user_id))
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            # Update existing preferences
            await self.db.execute(
                update(LearningPreference)
                .where(LearningPreference.user_id == uuid.UUID(user_id))
                .values(
                    visual_preference=preferences.visual_preference,
                    auditory_preference=preferences.auditory_preference,
                    kinesthetic_preference=preferences.kinesthetic_preference,
                    reading_preference=preferences.reading_preference,
                    video_preference=preferences.video_preference,
                    article_preference=preferences.article_preference,
                    interactive_preference=preferences.interactive_preference,
                    course_preference=preferences.course_preference,
                    preferred_difficulty=preferences.preferred_difficulty,
                    preferred_session_length=preferences.preferred_session_length,
                    interests=preferences.interests,
                    updated_at=datetime.utcnow()
                )
            )
        else:
            # Create new preferences
            new_preference = LearningPreference(
                user_id=uuid.UUID(user_id),
                visual_preference=preferences.visual_preference,
                auditory_preference=preferences.auditory_preference,
                kinesthetic_preference=preferences.kinesthetic_preference,
                reading_preference=preferences.reading_preference,
                video_preference=preferences.video_preference,
                article_preference=preferences.article_preference,
                interactive_preference=preferences.interactive_preference,
                course_preference=preferences.course_preference,
                preferred_difficulty=preferences.preferred_difficulty,
                preferred_session_length=preferences.preferred_session_length,
                interests=preferences.interests
            )
            self.db.add(new_preference)
        
        await self.db.commit()
    
    async def generate_preference_explanation(self, preferences: LearningPreferenceCreate) -> str:
        """Generate AI explanation of user's learning preferences"""
        
        # Determine dominant learning style
        style_scores = {
            'Visual': preferences.visual_preference,
            'Auditory': preferences.auditory_preference,
            'Kinesthetic': preferences.kinesthetic_preference,
            'Reading/Writing': preferences.reading_preference
        }
        dominant_style = max(style_scores, key=style_scores.get)
        
        # Determine preferred content types
        content_scores = {
            'Videos': preferences.video_preference,
            'Articles': preferences.article_preference,
            'Interactive content': preferences.interactive_preference,
            'Structured courses': preferences.course_preference
        }
        preferred_content = max(content_scores, key=content_scores.get)
        
        prompt = f"""
        Based on a learning style assessment, generate a personalized explanation for a user with these preferences:
        
        Learning Style Scores:
        - Visual: {preferences.visual_preference:.2f}
        - Auditory: {preferences.auditory_preference:.2f}
        - Kinesthetic: {preferences.kinesthetic_preference:.2f}
        - Reading/Writing: {preferences.reading_preference:.2f}
        
        Content Type Preferences:
        - Videos: {preferences.video_preference:.2f}
        - Articles: {preferences.article_preference:.2f}
        - Interactive: {preferences.interactive_preference:.2f}
        - Courses: {preferences.course_preference:.2f}
        
        Preferred difficulty: {preferences.preferred_difficulty}
        Preferred session length: {preferences.preferred_session_length} minutes
        
        Write a friendly, encouraging explanation (2-3 sentences) of their learning profile and how Trakl will personalize content for them.
        """
        
        try:
            explanation = await self.openai_service.generate_text(prompt, max_tokens=150)
            return explanation.strip()
        except Exception as e:
            # Fallback explanation
            return f"Based on your responses, you have a {dominant_style.lower()} learning style and prefer {preferred_content.lower()}. Trakl will recommend content that matches your {preferences.preferred_difficulty} level and fits your {preferences.preferred_session_length}-minute learning sessions."
    
    async def update_preferences_from_interactions(self, user_id: str, interaction_data: Dict[str, Any]):
        """Update user preferences based on their interactions with content"""
        
        # This would analyze user behavior and adjust preferences
        # For example, if user consistently skips videos, reduce video preference
        # If user completes interactive content, increase interactive preference
        
        result = await self.db.execute(
            select(LearningPreference).where(LearningPreference.user_id == uuid.UUID(user_id))
        )
        preferences = result.scalar_one_or_none()
        
        if not preferences:
            return
        
        # Simple adjustment logic (can be made more sophisticated)
        adjustments = {}
        
        if interaction_data.get('skipped_videos', 0) > 3:
            adjustments['video_preference'] = max(0.1, preferences.video_preference - 0.1)
        
        if interaction_data.get('completed_interactive', 0) > 2:
            adjustments['interactive_preference'] = min(1.0, preferences.interactive_preference + 0.1)
        
        if adjustments:
            await self.db.execute(
                update(LearningPreference)
                .where(LearningPreference.user_id == uuid.UUID(user_id))
                .values(**adjustments, updated_at=datetime.utcnow())
            )
            await self.db.commit()
