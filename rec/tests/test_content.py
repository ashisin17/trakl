import pytest
from httpx import AsyncClient
from ..main import app

@pytest.mark.asyncio
async def test_discover_content(override_get_db):
    """Test content discovery endpoint"""
    discovery_request = {
        "query": "python programming",
        "content_types": ["video", "article"],
        "max_results": 5,
        "platforms": ["youtube", "medium"]
    }
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/content/discover", json=discovery_request)
    
    assert response.status_code == 200
    data = response.json()
    assert "sources" in data
    assert "query" in data
    assert "total_found" in data
    assert data["query"] == "python programming"

@pytest.mark.asyncio
async def test_create_content_source(override_get_db, sample_content_source):
    """Test creating a new content source"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/content/", json=sample_content_source)
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == sample_content_source["title"]
    assert data["url"] == sample_content_source["url"]
    assert data["content_type"] == sample_content_source["content_type"]

@pytest.mark.asyncio
async def test_create_duplicate_content_source(override_get_db, sample_content_source):
    """Test creating duplicate content source should fail"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Create first content source
        response1 = await ac.post("/api/content/", json=sample_content_source)
        assert response1.status_code == 200
        
        # Try to create duplicate
        response2 = await ac.post("/api/content/", json=sample_content_source)
        assert response2.status_code == 400

@pytest.mark.asyncio
async def test_search_content(override_get_db, sample_content_source):
    """Test searching content"""
    # First create some content
    async with AsyncClient(app=app, base_url="http://test") as ac:
        await ac.post("/api/content/", json=sample_content_source)
        
        # Search for content
        response = await ac.get(
            "/api/content/search",
            params={
                "query": "python",
                "content_types": ["video"],
                "limit": 10
            }
        )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

@pytest.mark.asyncio
async def test_get_content_source(override_get_db, sample_content_source):
    """Test getting specific content source"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Create content source
        create_response = await ac.post("/api/content/", json=sample_content_source)
        content_id = create_response.json()["id"]
        
        # Get content source
        response = await ac.get(f"/api/content/{content_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == content_id

@pytest.mark.asyncio
async def test_get_nonexistent_content_source(override_get_db):
    """Test getting non-existent content source"""
    fake_id = "00000000-0000-0000-0000-000000000000"
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(f"/api/content/{fake_id}")
    
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_list_platforms(override_get_db):
    """Test listing available platforms"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/content/platforms/list")
    
    assert response.status_code == 200
    data = response.json()
    assert "platforms" in data

@pytest.mark.asyncio
async def test_list_topics(override_get_db):
    """Test listing available topics"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/content/topics/list")
    
    assert response.status_code == 200
    data = response.json()
    assert "topics" in data
