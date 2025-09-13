import pytest
from httpx import AsyncClient
from ..main import app

@pytest.mark.asyncio
async def test_get_learning_quiz(override_get_db):
    """Test getting the learning style quiz"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/preferences/quiz")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    
    # Check quiz question structure
    question = data[0]
    assert "id" in question
    assert "question" in question
    assert "options" in question
    assert "category" in question

@pytest.mark.asyncio
async def test_submit_quiz(override_get_db, test_user_id):
    """Test submitting quiz responses"""
    quiz_responses = {
        "responses": [
            {
                "question_id": "visual_1",
                "answer": "diagrams",
                "weight": 1.0
            },
            {
                "question_id": "content_type_1", 
                "answer": "video_tutorials",
                "weight": 1.0
            }
        ]
    }
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            f"/api/preferences/quiz/submit?user_id={test_user_id}",
            json=quiz_responses
        )
    
    assert response.status_code == 200
    data = response.json()
    assert "preferences" in data
    assert "explanation" in data
    assert "confidence_score" in data

@pytest.mark.asyncio
async def test_get_user_preferences_not_found(override_get_db):
    """Test getting preferences for non-existent user"""
    fake_user_id = "00000000-0000-0000-0000-000000000000"
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(f"/api/preferences/user/{fake_user_id}")
    
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_add_user_interests(override_get_db, test_user_id, sample_learning_preferences):
    """Test adding interests to user profile"""
    # First create preferences
    async with AsyncClient(app=app, base_url="http://test") as ac:
        quiz_response = await ac.post(
            f"/api/preferences/quiz/submit?user_id={test_user_id}",
            json={"responses": [{"question_id": "test", "answer": "diagrams", "weight": 1.0}]}
        )
        assert quiz_response.status_code == 200
        
        # Add interests
        interests = ["react", "typescript", "nodejs"]
        response = await ac.post(
            f"/api/preferences/user/{test_user_id}/interests",
            json=interests
        )
    
    assert response.status_code == 200
    data = response.json()
    assert "interests" in data
    assert all(interest in data["interests"] for interest in interests)
