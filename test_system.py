#!/usr/bin/env python3
"""
Test script for the Trakl AI Learning System
This script helps you test the integrated Dedalus Labs functionality
"""

import asyncio
import httpx
import json
from datetime import datetime

# Service URLs
REC_SERVICE_URL = "http://localhost:8001"
AGENT_SERVICE_URL = "http://localhost:8002"
WEBSITE_URL = "http://localhost:3000"

async def test_service_health():
    """Test if all services are running"""
    print("🔍 Testing service health...")
    
    services = {
        "Recommendation Service": f"{REC_SERVICE_URL}/health",
        "Agent Service": f"{AGENT_SERVICE_URL}/health", 
        "Website": WEBSITE_URL
    }
    
    async with httpx.AsyncClient() as client:
        for name, url in services.items():
            try:
                response = await client.get(url, timeout=5.0)
                if response.status_code == 200:
                    print(f"✅ {name}: Running")
                else:
                    print(f"❌ {name}: Error {response.status_code}")
            except Exception as e:
                print(f"❌ {name}: Not reachable - {str(e)}")

async def test_recommendation_api():
    """Test the recommendation service API"""
    print("\n🎯 Testing Recommendation API...")
    
    # Test data
    test_user_id = "test-user-123"
    test_preferences = {
        "preferred_content_types": ["video", "article"],
        "difficulty_level": "intermediate",
        "learning_style": "visual",
        "time_availability": 30
    }
    
    async with httpx.AsyncClient() as client:
        try:
            # Test content discovery
            print("  Testing content discovery...")
            response = await client.post(
                f"{REC_SERVICE_URL}/api/content/discover",
                json={
                    "query": "learn python programming",
                    "content_types": ["video", "article"],
                    "max_results": 5
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                content = response.json()
                print(f"  ✅ Found {len(content.get('results', []))} content items")
            else:
                print(f"  ❌ Content discovery failed: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Recommendation API error: {str(e)}")

async def test_agent_api():
    """Test the agent service API"""
    print("\n🤖 Testing Agent API...")
    
    test_goal = {
        "title": "Learn Python Programming",
        "description": "Master Python fundamentals and build projects",
        "target_skills": ["variables", "functions", "classes", "web development"],
        "timeline_weeks": 8,
        "difficulty_level": "beginner"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            print("  Testing plan generation...")
            response = await client.post(
                f"{AGENT_SERVICE_URL}/api/plans/generate",
                json={
                    "user_id": "test-user-123",
                    "learning_goal": test_goal,
                    "preferences": {
                        "sessions_per_week": 3,
                        "session_duration": 60,
                        "preferred_times": ["evening"]
                    }
                },
                timeout=60.0
            )
            
            if response.status_code == 200:
                plan = response.json()
                print(f"  ✅ Generated plan: {plan.get('title', 'Untitled')}")
                print(f"  📅 Duration: {plan.get('total_weeks', 0)} weeks")
            else:
                print(f"  ❌ Plan generation failed: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Agent API error: {str(e)}")

async def main():
    """Run all tests"""
    print("🚀 Starting Trakl System Tests")
    print("=" * 50)
    
    await test_service_health()
    await test_recommendation_api()
    await test_agent_api()
    
    print("\n" + "=" * 50)
    print("🎉 Testing complete!")
    print("\n💡 Next steps:")
    print("1. Visit http://localhost:3000 to see the web interface")
    print("2. Check the API documentation at:")
    print("   - http://localhost:8001/docs (Recommendation Service)")
    print("   - http://localhost:8002/docs (Agent Service)")

if __name__ == "__main__":
    asyncio.run(main())
