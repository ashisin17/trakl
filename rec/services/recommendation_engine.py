from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime

from ..database import ContentSource, LearningPreference, LearningGoal, Recommendation, UserInteraction
from ..models import ContentType, DifficultyLevel
from .embedding_service import EmbeddingService
from .openai_service import DedalusService

class RecommendationEngine:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.embedding_service = EmbeddingService()
        self.dedalus_service = DedalusService()
    
    async def generate_recommendations(
        self,
        user_id: str,
        user_preferences: LearningPreference,
        learning_goal: Optional[LearningGoal] = None,
        query: Optional[str] = None,
        max_results: int = 10,
        content_types: Optional[List[ContentType]] = None,
        difficulty_levels: Optional[List[DifficultyLevel]] = None
    ) -> List[Recommendation]:
        """Generate personalized recommendations for a user"""
        
        # Get candidate content
        candidates = await self._get_candidate_content(
            content_types=content_types,
            difficulty_levels=difficulty_levels,
            user_preferences=user_preferences
        )
        
        # Calculate scores for each candidate
        scored_candidates = []
        
        for content in candidates:
            # Calculate similarity score
            similarity_score = await self._calculate_similarity_score(
                content, learning_goal, query
            )
            
            # Calculate preference score
            preference_score = self._calculate_preference_score(
                content, user_preferences
            )
            
            # Calculate final score (weighted combination)
            final_score = (similarity_score * 0.6) + (preference_score * 0.4)
            
            # Generate reasoning
            reasoning = await self._generate_reasoning(
                content, user_preferences, similarity_score, preference_score
            )
            
            scored_candidates.append({
                'content': content,
                'similarity_score': similarity_score,
                'preference_score': preference_score,
                'final_score': final_score,
                'reasoning': reasoning
            })
        
        # Sort by final score and take top results
        scored_candidates.sort(key=lambda x: x['final_score'], reverse=True)
        top_candidates = scored_candidates[:max_results]
        
        # Create recommendation records
        recommendations = []
        for candidate in top_candidates:
            recommendation = Recommendation(
                user_id=uuid.UUID(user_id),
                goal_id=learning_goal.id if learning_goal else None,
                content_id=candidate['content'].id,
                similarity_score=candidate['similarity_score'],
                preference_score=candidate['preference_score'],
                final_score=candidate['final_score'],
                reasoning=candidate['reasoning']
            )
            
            self.db.add(recommendation)
            recommendations.append(recommendation)
        
        await self.db.commit()
        
        # Refresh to get IDs
        for rec in recommendations:
            await self.db.refresh(rec)
        
        return recommendations
    
    async def _get_candidate_content(
        self,
        content_types: Optional[List[ContentType]] = None,
        difficulty_levels: Optional[List[DifficultyLevel]] = None,
        user_preferences: Optional[LearningPreference] = None,
        limit: int = 100
    ) -> List[ContentSource]:
        """Get candidate content for recommendation"""
        
        conditions = []
        
        # Filter by content types
        if content_types:
            conditions.append(ContentSource.content_type.in_([ct.value for ct in content_types]))
        
        # Filter by difficulty levels
        if difficulty_levels:
            conditions.append(ContentSource.difficulty_level.in_([dl.value for dl in difficulty_levels]))
        elif user_preferences and user_preferences.preferred_difficulty:
            conditions.append(ContentSource.difficulty_level == user_preferences.preferred_difficulty)
        
        # Build query
        query = select(ContentSource)
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def _calculate_similarity_score(
        self,
        content: ContentSource,
        learning_goal: Optional[LearningGoal] = None,
        query: Optional[str] = None
    ) -> float:
        """Calculate content similarity score based on goal/query"""
        
        if not learning_goal and not query:
            return 0.5  # Neutral score if no goal or query
        
        # Use goal embedding if available
        if learning_goal and learning_goal.goal_embedding and content.content_embedding:
            similarity = self.embedding_service.calculate_similarity(
                learning_goal.goal_embedding,
                content.content_embedding
            )
            return max(0.0, min(1.0, similarity))
        
        # Use query embedding if available
        if query and content.content_embedding:
            query_embeddings = await self.dedalus_service.generate_embeddings([query])
            if query_embeddings:
                similarity = self.embedding_service.calculate_similarity(
                    query_embeddings[0],
                    content.content_embedding
                )
                return max(0.0, min(1.0, similarity))
        
        # Fallback: keyword matching
        if learning_goal:
            goal_keywords = set((learning_goal.title + " " + learning_goal.description).lower().split())
            content_keywords = set((content.title + " " + (content.description or "")).lower().split())
            
            if goal_keywords and content_keywords:
                overlap = len(goal_keywords.intersection(content_keywords))
                return min(1.0, overlap / len(goal_keywords))
        
        return 0.3  # Default low similarity
    
    def _calculate_preference_score(
        self,
        content: ContentSource,
        user_preferences: LearningPreference
    ) -> float:
        """Calculate how well content matches user preferences"""
        
        score = 0.0
        
        # Content type preference
        content_type_scores = {
            'video': user_preferences.video_preference,
            'article': user_preferences.article_preference,
            'interactive': user_preferences.interactive_preference,
            'course': user_preferences.course_preference
        }
        
        if content.content_type in content_type_scores:
            score += content_type_scores[content.content_type] * 0.4
        
        # Difficulty level preference
        if content.difficulty_level == user_preferences.preferred_difficulty:
            score += 0.3
        elif content.difficulty_level:
            # Partial score for adjacent difficulty levels
            difficulty_order = ['beginner', 'intermediate', 'advanced']
            try:
                content_idx = difficulty_order.index(content.difficulty_level)
                pref_idx = difficulty_order.index(user_preferences.preferred_difficulty)
                diff = abs(content_idx - pref_idx)
                if diff == 1:
                    score += 0.15  # Adjacent difficulty
            except ValueError:
                pass
        
        # Duration preference (session length)
        if content.duration_minutes and user_preferences.preferred_session_length:
            duration_ratio = min(
                content.duration_minutes / user_preferences.preferred_session_length,
                user_preferences.preferred_session_length / content.duration_minutes
            )
            score += duration_ratio * 0.2
        
        # Interest/topic matching
        if user_preferences.interests and content.topics:
            user_interests = set([interest.lower() for interest in user_preferences.interests])
            content_topics = set([topic.lower() for topic in content.topics])
            
            if user_interests and content_topics:
                overlap = len(user_interests.intersection(content_topics))
                score += min(0.1, overlap / len(user_interests))
        
        return max(0.0, min(1.0, score))
    
    async def _generate_reasoning(
        self,
        content: ContentSource,
        user_preferences: LearningPreference,
        similarity_score: float,
        preference_score: float
    ) -> str:
        """Generate AI explanation for why content was recommended"""
        
        # Determine dominant learning style
        style_scores = {
            'visual': user_preferences.visual_preference,
            'auditory': user_preferences.auditory_preference,
            'kinesthetic': user_preferences.kinesthetic_preference,
            'reading': user_preferences.reading_preference
        }
        dominant_style = max(style_scores, key=style_scores.get)
        
        # Build reasoning components
        reasons = []
        
        if similarity_score > 0.7:
            reasons.append("highly relevant to your learning goals")
        elif similarity_score > 0.5:
            reasons.append("matches your learning objectives")
        
        if preference_score > 0.7:
            reasons.append(f"perfectly suited for your {dominant_style} learning style")
        elif preference_score > 0.5:
            reasons.append("aligns well with your preferences")
        
        if content.difficulty_level == user_preferences.preferred_difficulty:
            reasons.append(f"matches your {user_preferences.preferred_difficulty} level")
        
        if content.duration_minutes and user_preferences.preferred_session_length:
            if abs(content.duration_minutes - user_preferences.preferred_session_length) <= 10:
                reasons.append("fits your preferred session length")
        
        if content.rating and content.rating >= 4.0:
            reasons.append("highly rated by other learners")
        
        # Combine reasons
        if reasons:
            if len(reasons) == 1:
                return f"Recommended because it's {reasons[0]}."
            elif len(reasons) == 2:
                return f"Recommended because it's {reasons[0]} and {reasons[1]}."
            else:
                return f"Recommended because it's {', '.join(reasons[:-1])}, and {reasons[-1]}."
        
        return "Recommended based on your learning profile and goals."
    
    async def update_recommendations_from_feedback(
        self,
        user_id: str,
        recommendation_id: str,
        feedback: Dict[str, Any]
    ):
        """Update recommendation algorithm based on user feedback"""
        
        # This would be used to improve future recommendations
        # Could adjust user preferences, content scoring weights, etc.
        
        # For now, just log the feedback
        print(f"Received feedback for recommendation {recommendation_id}: {feedback}")
        
        # In production, you might:
        # 1. Adjust user preferences based on positive/negative feedback
        # 2. Update content quality scores
        # 3. Retrain recommendation models
        # 4. A/B test different recommendation strategies
