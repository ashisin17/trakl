# Trakl - AI Learning Agent

An AI learning agent that turns goals into curated plans, schedules sessions, and gives feedback. Trakl discovers content across the internet, analyzes your learning preferences through a quiz system, and provides personalized recommendations based on your visual, auditory, and kinesthetic learning styles.

## Architecture

```
trakl/
├── docker-compose.yml          # Container orchestration
├── schema.sql                  # PostgreSQL + pgvector schema
├── README.md                   # This file
├── rec/                        # Recommendation engine (FastAPI)
│   ├── api/                    # REST API endpoints
│   ├── services/               # Business logic
│   ├── tests/                  # Test suite + evaluation harness
│   └── Dockerfile
├── agent/                      # Orchestrator service (FastAPI)
│   ├── api/                    # Plans, sessions, progress APIs
│   ├── services/               # Plan generation, calendar integration
│   └── Dockerfile
└── www/                        # Nuxt.js frontend
    ├── app/                    # Nuxt 3 application
    ├── server/                 # API routes
    └── components/             # Vue components
```

## Features

### 🎯 Recommendation Engine (`rec/`)
- **Learning Style Quiz**: Analyzes visual, auditory, kinesthetic, and reading preferences
- **Content Discovery**: Searches YouTube, Coursera, Medium, Dev.to, and other platforms
- **AI-Powered Recommendations**: Uses OpenAI embeddings for semantic content matching
- **Preference Learning**: Adapts recommendations based on user interactions
- **Evaluation Harness**: Built-in testing for recommendation quality metrics

### 🤖 Agent Service (`agent/`)
- **AI Plan Generation**: Creates personalized learning plans using GPT-4
- **Session Scheduling**: Integrates with Google Calendar for automatic scheduling
- **Progress Tracking**: Monitors milestones, streaks, and skill development
- **Adaptive Planning**: Adjusts plans based on user progress and feedback

### 🌐 Web Interface (`www/`)
- **Nuxt 3 Application**: Modern Vue.js frontend with SSR
- **Chat Interface**: Interactive learning assistant
- **Progress Dashboard**: Visual progress tracking and analytics
- **Responsive Design**: Works on desktop and mobile devices

## Quick Start

### Prerequisites
- Docker and Docker Compose
- OpenAI API key
- (Optional) Google Calendar API credentials

### 1. Environment Setup
```bash
# Clone the repository
git clone <repository-url>
cd trakl

# Copy environment files
cp rec/.env.example rec/.env
cp agent/.env.example agent/.env

# Add your OpenAI API key to both .env files
echo "OPENAI_API_KEY=your_key_here" >> rec/.env
echo "OPENAI_API_KEY=your_key_here" >> agent/.env
```

### 2. Start Services
```bash
# Start all services with Docker Compose
docker-compose up -d

# Check service health
docker-compose ps
```

### 3. Access the Application
- **Web Interface**: http://localhost:3000
- **Recommendation API**: http://localhost:8001/docs
- **Agent API**: http://localhost:8002/docs
- **PostgreSQL**: localhost:5432 (user: postgres, password: password)

## API Usage

### Take Learning Style Quiz
```bash
# Get quiz questions
curl http://localhost:8001/api/preferences/quiz

# Submit quiz responses
curl -X POST http://localhost:8001/api/preferences/quiz/submit?user_id=USER_ID \
  -H "Content-Type: application/json" \
  -d '{
    "responses": [
      {"question_id": "visual_1", "answer": "diagrams", "weight": 1.0}
    ]
  }'
```

### Discover Learning Content
```bash
# Search for content
curl -X POST http://localhost:8001/api/content/discover \
  -H "Content-Type: application/json" \
  -d '{
    "query": "python programming",
    "content_types": ["video", "article"],
    "max_results": 10
  }'
```

### Generate Learning Plan
```bash
# Create AI-generated learning plan
curl -X POST http://localhost:8002/api/plans/generate \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "USER_ID",
    "goal_id": "GOAL_ID"
  }'
```

### Get Personalized Recommendations
```bash
# Get recommendations based on preferences
curl -X POST http://localhost:8001/api/recommendations/generate \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "USER_ID",
    "query": "learn react",
    "max_results": 5
  }'
```

## Development

### Running Tests
```bash
# Test recommendation engine
cd rec
pytest tests/ -v

# Test with coverage
pytest tests/ --cov=. --cov-report=html
```

### Database Migrations
```bash
# The schema is automatically applied on startup
# To reset the database:
docker-compose down -v
docker-compose up -d
```

### Adding New Content Sources
1. Extend `ContentDiscoveryService` in `rec/services/content_discovery.py`
2. Add platform-specific search logic
3. Update content type mappings
4. Add tests for new discovery methods

## Configuration

### Environment Variables

**Recommendation Service (`rec/.env`)**:
```env
DATABASE_URL=postgresql://postgres:password@postgres:5432/trakl
OPENAI_API_KEY=your_openai_api_key
REDIS_URL=redis://redis:6379
MAX_SEARCH_RESULTS=50
SIMILARITY_THRESHOLD=0.7
```

**Agent Service (`agent/.env`)**:
```env
DATABASE_URL=postgresql://postgres:password@postgres:5432/trakl
OPENAI_API_KEY=your_openai_api_key
REC_SERVICE_URL=http://rec-service:8001
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
```

### Learning Preference System

The quiz system evaluates:
- **Visual Learning**: Preference for diagrams, charts, visual aids
- **Auditory Learning**: Preference for explanations, discussions, audio content
- **Kinesthetic Learning**: Preference for hands-on practice, interactive content
- **Reading/Writing**: Preference for written materials, note-taking

Content recommendations are weighted based on these preferences combined with semantic similarity to learning goals.

## Tech Stack

- **Backend**: Python 3.11, FastAPI, SQLAlchemy 2.x, Pydantic v2
- **Database**: PostgreSQL 15 + pgvector for embeddings
- **AI/ML**: OpenAI GPT-4, text-embedding-3-small
- **Frontend**: Nuxt 3, Vue.js, TypeScript
- **Caching**: Redis (optional)
- **Testing**: pytest, httpx
- **Deployment**: Docker, Docker Compose

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Run the test suite: `pytest`
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions or issues:
1. Check the API documentation at `/docs` endpoints
2. Review the test cases for usage examples
3. Open an issue on GitHub
