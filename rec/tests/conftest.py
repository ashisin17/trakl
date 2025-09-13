import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
import uuid

from ..database import Base, get_db
from ..main import app

# Test database URL (in-memory SQLite for testing)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=True
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    await engine.dispose()

@pytest.fixture
async def test_db(test_engine):
    """Create test database session"""
    TestSessionLocal = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with TestSessionLocal() as session:
        yield session

@pytest.fixture
def override_get_db(test_db):
    """Override database dependency for testing"""
    async def _override_get_db():
        yield test_db
    
    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()

@pytest.fixture
def test_user_id():
    """Generate a test user ID"""
    return str(uuid.uuid4())

@pytest.fixture
def sample_learning_preferences():
    """Sample learning preferences for testing"""
    return {
        "visual_preference": 0.8,
        "auditory_preference": 0.3,
        "kinesthetic_preference": 0.6,
        "reading_preference": 0.5,
        "video_preference": 0.9,
        "article_preference": 0.4,
        "interactive_preference": 0.7,
        "course_preference": 0.6,
        "preferred_difficulty": "intermediate",
        "preferred_session_length": 30,
        "interests": ["python", "machine learning", "web development"]
    }

@pytest.fixture
def sample_content_source():
    """Sample content source for testing"""
    return {
        "url": "https://example.com/python-tutorial",
        "title": "Complete Python Tutorial",
        "description": "Learn Python from basics to advanced concepts",
        "content_type": "video",
        "source_platform": "youtube",
        "duration_minutes": 45,
        "difficulty_level": "intermediate",
        "topics": ["python", "programming"],
        "rating": 4.5,
        "view_count": 100000
    }
