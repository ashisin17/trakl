# Trakl - AI-Powered Learning Platform

An intelligent learning platform that transforms your goals into structured learning journeys. Trakl combines AI-powered recommendations with personalized learning experiences, adapting to your unique learning style and preferences.

## Key Features

### Smart Recommendations
- **Personalized Content Discovery**: AI-powered search across multiple learning platforms
- **Learning Style Analysis**: Tailored content based on VARK (Visual, Auditory, Reading/Writing, Kinesthetic) preferences
- **Adaptive Learning Paths**: Dynamic adjustment of content based on progress and engagement

### Intelligent Agent System
- **Goal-Based Planning**: Converts learning objectives into actionable plans
- **Automated Scheduling**: Seamless calendar integration for session planning
- **Progress Tracking**: Real-time monitoring of learning milestones and achievements

### Interactive Learning Assistant
- **Natural Language Interface**: Chat-based interaction for intuitive learning
- **Context-Aware Responses**: Maintains conversation context for coherent interactions
- **Rich Media Support**: Displays code snippets, videos, and interactive content

## System Architecture

```
trakl/
├── agent/                      # Orchestrator service (FastAPI)
│   ├── api/                    # Plans, sessions, progress APIs
│   ├── services/               # Plan generation, calendar integration
│   └── Dockerfile
├── rec/                        # Recommendation engine (FastAPI)
│   ├── api/                    # REST API endpoints
│   ├── services/               # Business logic
│   └── Dockerfile
├── www/                        # Nuxt.js frontend
│   ├── app/                    # Nuxt 3 application
│   ├── server/                 # API routes
│   └── components/             # Vue components
└── docker-compose.yml          # Container orchestration
```

#### Recommendation Engine (`rec/`)
- **Learning Style Quiz**: Analyzes visual, auditory, kinesthetic, and reading preferences
- **Content Discovery**: Searches YouTube, Coursera, Medium, Dev.to, and other platforms
- **AI-Powered Recommendations**: Uses OpenAI embeddings for semantic content matching
- **Preference Learning**: Adapts recommendations based on user interactions
- **Evaluation Harness**: Built-in testing for recommendation quality metrics

#### Agent Service (`agent/`)
- **AI Plan Generation**: Creates personalized learning plans using GPT-4
- **Session Scheduling**: Integrates with Google Calendar for automatic scheduling
- **Progress Tracking**: Monitors milestones, streaks, and skill development
- **Adaptive Planning**: Adjusts plans based on user progress and feedback
## Technical Stack

### Backend Services
- **Python 3.9+**: Core application logic
- **FastAPI**: High-performance API framework
- **PostgreSQL + pgvector**: Vector database for semantic search
- **Redis**: Caching and real-time features
- **Docker**: Containerization and deployment

### Frontend
- **Nuxt 3**: Vue.js framework for the web interface
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **WebSockets**: Real-time communication

### AI/ML Components
- **OpenAI API**: Natural language understanding
- **Hugging Face Transformers**: Custom model training
- **scikit-learn**: Recommendation algorithms
- **spaCy**: Text processing

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ and npm/yarn
- Python 3.9+
- PostgreSQL 13+
- Redis (for caching)
- OpenAI API key

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/trakl.git
   cd trakl
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Update the environment variables in .env with your API keys and configuration
   ```

3. **Start the development environment**
   ```bash
   # Start all services
   docker-compose up -d
   
   # Or start services individually
   docker-compose up -d postgres redis
   cd www && npm install && npm run dev
   cd ../rec && pip install -r requirements.txt && uvicorn main:app --reload
   cd ../agent && pip install -r requirements.txt && uvicorn main:app --reload
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - API Documentation: http://localhost:8000/docs
   - Database Admin: http://localhost:8080 (if enabled)

## 🛠️ Development

### Running Services Individually

#### Frontend (Nuxt 3)
```bash
cd www
npm install
npm run dev
```

#### Recommendation Service
```bash
cd rec
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

#### Agent Service
```bash
cd agent
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8002
```

## 🧪 Testing

Run the test suite:
```bash
# Unit tests
cd rec && pytest

# E2E tests
cd www && npm run test:e2e
```

## 🚀 Deployment

### Production Build
```bash
# Build all services
docker-compose -f docker-compose.prod.yml build

# Start production environment
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes Deployment (Optional)

1. **Set up Kubernetes cluster**
   ```bash
   # Using minikube for local development
   minikube start --cpus=4 --memory=8192mb
   ```

2. **Deploy to Kubernetes**
   ```bash
   # Apply Kubernetes manifests
   kubectl apply -f k8s/
   
   # Access the application
   minikube service trakl-frontend
   ```

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork** the repository
2. Create a **feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add some amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. Open a **Pull Request**

### Development Guidelines
- Follow the existing code style
- Write tests for new features
- Update documentation as needed
- Keep commits atomic and well-documented

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI** for their powerful language models
- **FastAPI** and **Nuxt.js** communities
- **PostgreSQL** and **Redis** teams
- All our amazing contributors

## 📚 Resources

- [API Documentation](http://localhost:8000/docs) (when running locally)
- [Frontend Style Guide](www/STYLEGUIDE.md)
- [Architecture Decision Records](docs/adr/)
- [Roadmap](docs/ROADMAP.md)

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