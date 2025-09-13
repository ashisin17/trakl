#!/bin/bash

# Trakl System Startup Script
echo "🚀 Starting Trakl AI Learning System..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Please create a .env file with your DEDALUS_API_KEY"
    echo "Example: DEDALUS_API_KEY=your_api_key_here"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi

echo "📦 Building and starting services..."
docker-compose up --build -d

echo "⏳ Waiting for services to start..."
sleep 10

echo "🔍 Checking service status..."
docker-compose ps

echo ""
echo "✅ System started! Access points:"
echo "🌐 Website: http://localhost:3000"
echo "📊 Recommendation API: http://localhost:8001/docs"
echo "🤖 Agent API: http://localhost:8002/docs"
echo "🗄️  Database: localhost:5432"
echo ""
echo "📝 To test the system, run: python test_system.py"
echo "🛑 To stop the system, run: docker-compose down"
