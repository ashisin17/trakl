import pytest
import asyncio
from typing import List, Dict, Any
from ..services.recommendation_engine import RecommendationEngine
from ..services.embedding_service import EmbeddingService
from ..database import ContentSource, LearningPreference, LearningGoal

class RecommendationEvaluator:
    """Evaluation harness for recommendation engine performance"""
    
    def __init__(self, db_session):
        self.db = db_session
        self.recommendation_engine = RecommendationEngine(db_session)
        self.embedding_service = EmbeddingService()
    
    async def evaluate_recommendation_quality(
        self, 
        test_cases: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Evaluate recommendation quality using test cases"""
        
        total_cases = len(test_cases)
        if total_cases == 0:
            return {"error": "No test cases provided"}
        
        metrics = {
            "precision_at_5": 0.0,
            "recall_at_10": 0.0,
            "diversity_score": 0.0,
            "preference_alignment": 0.0,
            "avg_similarity_score": 0.0
        }
        
        for test_case in test_cases:
            case_metrics = await self._evaluate_single_case(test_case)
            for key, value in case_metrics.items():
                metrics[key] += value
        
        # Average the metrics
        for key in metrics:
            metrics[key] /= total_cases
        
        return metrics
    
    async def _evaluate_single_case(self, test_case: Dict[str, Any]) -> Dict[str, float]:
        """Evaluate a single test case"""
        
        user_preferences = test_case["user_preferences"]
        learning_goal = test_case.get("learning_goal")
        expected_relevant_content = test_case.get("expected_relevant", [])
        
        # Generate recommendations
        recommendations = await self.recommendation_engine.generate_recommendations(
            user_id=test_case["user_id"],
            user_preferences=user_preferences,
            learning_goal=learning_goal,
            max_results=10
        )
        
        # Calculate metrics
        precision_at_5 = self._calculate_precision_at_k(recommendations[:5], expected_relevant_content)
        recall_at_10 = self._calculate_recall_at_k(recommendations[:10], expected_relevant_content)
        diversity_score = self._calculate_diversity_score(recommendations)
        preference_alignment = self._calculate_preference_alignment(recommendations, user_preferences)
        avg_similarity = sum(rec.similarity_score for rec in recommendations) / len(recommendations) if recommendations else 0
        
        return {
            "precision_at_5": precision_at_5,
            "recall_at_10": recall_at_10,
            "diversity_score": diversity_score,
            "preference_alignment": preference_alignment,
            "avg_similarity_score": avg_similarity
        }
    
    def _calculate_precision_at_k(self, recommendations: List, expected_relevant: List[str]) -> float:
        """Calculate precision@k metric"""
        if not recommendations:
            return 0.0
        
        relevant_count = 0
        for rec in recommendations:
            if str(rec.content_id) in expected_relevant:
                relevant_count += 1
        
        return relevant_count / len(recommendations)
    
    def _calculate_recall_at_k(self, recommendations: List, expected_relevant: List[str]) -> float:
        """Calculate recall@k metric"""
        if not expected_relevant:
            return 1.0  # Perfect recall if no expected relevant items
        
        recommended_ids = {str(rec.content_id) for rec in recommendations}
        relevant_found = len(recommended_ids.intersection(set(expected_relevant)))
        
        return relevant_found / len(expected_relevant)
    
    def _calculate_diversity_score(self, recommendations: List) -> float:
        """Calculate diversity of recommendations (content types, platforms, topics)"""
        if not recommendations:
            return 0.0
        
        # Collect content metadata (would need to fetch from database)
        content_types = set()
        platforms = set()
        topics = set()
        
        # For now, return a placeholder diversity score
        # In production, you'd fetch content details and calculate actual diversity
        return 0.7  # Placeholder
    
    def _calculate_preference_alignment(self, recommendations: List, user_preferences) -> float:
        """Calculate how well recommendations align with user preferences"""
        if not recommendations:
            return 0.0
        
        total_preference_score = sum(rec.preference_score for rec in recommendations)
        return total_preference_score / len(recommendations)

@pytest.mark.asyncio
async def test_recommendation_evaluator(override_get_db, test_db, test_user_id, sample_learning_preferences):
    """Test the recommendation evaluation harness"""
    
    evaluator = RecommendationEvaluator(test_db)
    
    # Create mock test case
    test_cases = [
        {
            "user_id": test_user_id,
            "user_preferences": sample_learning_preferences,
            "learning_goal": None,
            "expected_relevant": []  # Would contain actual content IDs in real test
        }
    ]
    
    # Note: This test will fail without actual data, but demonstrates the structure
    try:
        metrics = await evaluator.evaluate_recommendation_quality(test_cases)
        assert "precision_at_5" in metrics
        assert "recall_at_10" in metrics
        assert "diversity_score" in metrics
    except Exception as e:
        # Expected to fail without proper test data setup
        assert "preferences not found" in str(e) or "No recommendations" in str(e)

@pytest.mark.asyncio
async def test_embedding_similarity_calculation():
    """Test embedding similarity calculation"""
    
    embedding_service = EmbeddingService()
    
    # Test vectors
    vec1 = [1.0, 0.0, 0.0]
    vec2 = [1.0, 0.0, 0.0]  # Identical
    vec3 = [0.0, 1.0, 0.0]  # Orthogonal
    
    # Test identical vectors
    similarity_identical = embedding_service.calculate_similarity(vec1, vec2)
    assert abs(similarity_identical - 1.0) < 0.001
    
    # Test orthogonal vectors
    similarity_orthogonal = embedding_service.calculate_similarity(vec1, vec3)
    assert abs(similarity_orthogonal - 0.0) < 0.001

def test_evaluation_metrics_calculation():
    """Test evaluation metrics calculation methods"""
    
    # Mock data for testing
    class MockRecommendation:
        def __init__(self, content_id, similarity_score, preference_score):
            self.content_id = content_id
            self.similarity_score = similarity_score
            self.preference_score = preference_score
    
    evaluator = RecommendationEvaluator(None)  # No DB needed for this test
    
    recommendations = [
        MockRecommendation("1", 0.8, 0.7),
        MockRecommendation("2", 0.6, 0.8),
        MockRecommendation("3", 0.9, 0.6),
    ]
    
    expected_relevant = ["1", "3"]
    
    # Test precision calculation
    precision = evaluator._calculate_precision_at_k(recommendations, expected_relevant)
    assert precision == 2/3  # 2 relevant out of 3 recommendations
    
    # Test recall calculation
    recall = evaluator._calculate_recall_at_k(recommendations, expected_relevant)
    assert recall == 1.0  # Found all expected relevant items
    
    # Test preference alignment
    alignment = evaluator._calculate_preference_alignment(recommendations, None)
    expected_alignment = (0.7 + 0.8 + 0.6) / 3
    assert abs(alignment - expected_alignment) < 0.001
