import pytest
from httpx import AsyncClient
from ..main import app

@pytest.mark.asyncio
async def test_generate_recommendations_no_preferences(override_get_db, test_user_id):
    """Test generating recommendations without user preferences should fail"""
    recommendation_request = {
        "user_id": test_user_id,
        "query": "learn python",
        "max_results": 5
    }
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/recommendations/generate", json=recommendation_request)
    
    assert response.status_code == 404
    assert "preferences not found" in response.json()["detail"]

@pytest.mark.asyncio
async def test_generate_recommendations_with_preferences(override_get_db, test_user_id, sample_content_source):
    """Test generating recommendations with user preferences"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # First create user preferences
        quiz_response = await ac.post(
            f"/api/preferences/quiz/submit?user_id={test_user_id}",
            json={"responses": [{"question_id": "test", "answer": "diagrams", "weight": 1.0}]}
        )
        assert quiz_response.status_code == 200
        
        # Create some content
        await ac.post("/api/content/", json=sample_content_source)
        
        # Generate recommendations
        recommendation_request = {
            "user_id": test_user_id,
            "query": "python programming",
            "max_results": 5
        }
        
        response = await ac.post("/api/recommendations/generate", json=recommendation_request)
    
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert "total_count" in data
    assert "user_preferences" in data

@pytest.mark.asyncio
async def test_get_recommendation_history(override_get_db, test_user_id):
    """Test getting user's recommendation history"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(f"/api/recommendations/user/{test_user_id}/history")
    
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert "total_count" in data

@pytest.mark.asyncio
async def test_provide_recommendation_feedback(override_get_db):
    """Test providing feedback on recommendations"""
    recommendation_id = "00000000-0000-0000-0000-000000000000"
    feedback = {
        "rating": 4,
        "helpful": True,
        "comments": "Great recommendation!"
    }
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            f"/api/recommendations/feedback/{recommendation_id}",
            json=feedback
        )
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
