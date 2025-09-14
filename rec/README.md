# Trakl Recommendation Engine

A FastAPI-based recommendation service that provides personalized learning content recommendations using AI-powered semantic search and user preference matching.

## Architecture

The recommendation engine consists of several key components:

- **FastAPI Server**: RESTful API endpoints for recommendations and preferences
- **PostgreSQL Database**: Stores user preferences, content metadata, and vector embeddings
- **Vector Search**: Uses pgvector extension for semantic similarity matching
- **AI Integration**: Dedalus Labs API for embeddings and content generation
- **Content Discovery**: Automated content ingestion from various learning platforms

## Features

- **Learning Style Quiz**: Captures user preferences across multiple dimensions
- **Semantic Search**: Vector-based content matching using AI embeddings
- **Personalized Scoring**: Combines user preferences, content quality, and relevance
- **Multi-Platform Content**: Supports YouTube, Coursera, Khan Academy, and more
- **Real-time Recommendations**: Fast API responses with caching

## Setup

### Prerequisites

- Python 3.12+
- PostgreSQL with pgvector extension
- Dedalus Labs API key

### Installation

1. **Clone and navigate to the recommendation service:**
   ```bash
   cd /Users/ashis/trakl/rec
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On macOS/Linux
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Configure database:**
   ```bash
   # Ensure PostgreSQL is running with pgvector extension
   # Update DATABASE_URL in .env
   ```

## Configuration

### Environment Variables (.env)

```bash
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/trakl

# Dedalus Labs API
DEDALUS_API_KEY=your_dedalus_api_key_here
DEDALUS_MODEL=openai/gpt-4o-mini

# External Services
AGENT_SERVICE_URL=http://localhost:8002

# Content Discovery
YOUTUBE_API_KEY=your_youtube_api_key_here
COURSERA_API_KEY=your_coursera_api_key_here

# Performance
REDIS_URL=redis://localhost:6379
CACHE_TTL=3600
```

## Running the Service

### Start the Recommendation Service

```bash
# From the rec directory
cd /Users/ashis/trakl/rec
source .venv/bin/activate
python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

The service will be available at `http://localhost:8001`

### API Documentation

Once running, visit:
- **Swagger UI**: `http://localhost:8001/docs`
- **ReDoc**: `http://localhost:8001/redoc`

## API Endpoints

### Health Check
```bash
GET /health
```

### Learning Preferences

#### Get Quiz Questions
```bash
GET /api/preferences/quiz
```

#### Submit Quiz Responses
```bash
POST /api/preferences/quiz/submit?user_id=123
Content-Type: application/json

{
  "responses": {
    "learning_style": "visual",
    "pace": "self_paced",
    "difficulty": "intermediate",
    "time_commitment": "1-2 hours",
    "interaction": "interactive"
  }
}
```

### Recommendations

#### Generate Recommendations
```bash
POST /api/recommendations/generate
Content-Type: application/json

{
  "user_id": "123",
  "query": "learn Python programming",
  "limit": 10
}
```

### Content Management

#### List Content Sources
```bash
GET /api/content/sources
```

#### Add Content Source
```bash
POST /api/content/sources
Content-Type: application/json

{
  "platform": "youtube",
  "url": "https://www.youtube.com/watch?v=example",
  "title": "Python Tutorial",
  "description": "Learn Python basics",
  "tags": ["python", "programming", "tutorial"]
}
```

## Testing the Backend

### 1. Manual API Testing

#### Test Health Endpoint
```bash
curl http://localhost:8001/health
# Expected: {"status": "healthy"}
```

#### Test Quiz Endpoint
```bash
curl http://localhost:8001/api/preferences/quiz
# Expected: JSON array of quiz questions
```

#### Test Quiz Submission
```bash
curl -X POST "http://localhost:8001/api/preferences/quiz/submit?user_id=test123" \
  -H "Content-Type: application/json" \
  -d '{
    "responses": {
      "learning_style": "visual",
      "pace": "self_paced",
      "difficulty": "intermediate",
      "time_commitment": "1-2 hours",
      "interaction": "interactive"
    }
  }'
```

#### Test Recommendations
```bash
curl -X POST "http://localhost:8001/api/recommendations/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test123",
    "query": "learn Python programming",
    "limit": 5
  }'
```

### 2. Automated Testing

#### Run Unit Tests
```bash
cd /Users/ashis/trakl/rec
source .venv/bin/activate
python -m pytest tests/ -v
```

#### Run Specific Test Files
```bash
# Test recommendations
python -m pytest tests/test_recommendations.py -v

# Test content API
python -m pytest tests/test_content.py -v

# Test preferences
python -m pytest tests/test_preferences.py -v
```

#### Run Tests with Coverage
```bash
python -m pytest tests/ --cov=. --cov-report=html
# View coverage report in htmlcov/index.html
```

### 3. Integration Testing

#### Test Complete Flow
```bash
# 1. Submit quiz preferences
curl -X POST "http://localhost:8001/api/preferences/quiz/submit?user_id=integration_test" \
  -H "Content-Type: application/json" \
  -d '{
    "responses": {
      "learning_style": "visual",
      "pace": "instructor_led",
      "difficulty": "beginner",
      "time_commitment": "30 minutes",
      "interaction": "interactive"
    }
  }'

# 2. Get recommendations
curl -X POST "http://localhost:8001/api/recommendations/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "integration_test",
    "query": "machine learning basics",
    "limit": 3
  }'
```

### 4. Performance Testing

#### Load Testing with curl
```bash
# Test concurrent requests
for i in {1..10}; do
  curl -X POST "http://localhost:8001/api/recommendations/generate" \
    -H "Content-Type: application/json" \
    -d '{"user_id":"load_test_'$i'","query":"data science","limit":5}' &
done
wait
```

#### Database Performance
```bash
# Check database connections
curl http://localhost:8001/api/health/db

# Monitor query performance in PostgreSQL logs
```

## Development

### Database Schema

The service uses the following main tables:
- `user_preferences`: Stores quiz responses and learning preferences
- `content_sources`: Learning content metadata and embeddings
- `recommendations`: Cached recommendation results
- `content_interactions`: User engagement tracking

### Adding New Content Sources

1. **Implement content discovery service:**
   ```python
   # In services/content_discovery.py
   class NewPlatformDiscovery:
       async def discover_content(self, query: str):
           # Implementation for new platform
   ```

2. **Add API endpoints:**
   ```python
   # In api/content.py
   @router.post("/sources/{platform}")
   async def add_platform_content(platform: str, content: ContentCreate):
       # Handle new platform content
   ```

3. **Update content ingestion:**
   ```python
   # Add to content ingestion pipeline
   ```

### Monitoring and Logging

The service includes structured logging and metrics:

```bash
# View logs
tail -f logs/recommendation_service.log

# Monitor metrics (if configured)
curl http://localhost:8001/metrics
```

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   ```bash
   # Check PostgreSQL is running
   pg_isready -h localhost -p 5432
   
   # Verify pgvector extension
   psql -d trakl -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
   ```

2. **Missing API Keys**
   ```bash
   # Verify environment variables
   echo $DEDALUS_API_KEY
   ```

3. **Import Errors**
   ```bash
   # Reinstall dependencies
   pip install -r requirements.txt --force-reinstall
   ```

4. **Port Already in Use**
   ```bash
   # Find and kill process
   lsof -ti:8001 | xargs kill -9
   ```

### Debug Mode

Run with debug logging:
```bash
LOG_LEVEL=DEBUG python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

## Contributing

1. Follow PEP 8 style guidelines
2. Add tests for new features
3. Update API documentation
4. Run tests before committing

## License

MIT License - see LICENSE file for details.
