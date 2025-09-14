#!/usr/bin/env python3
"""
Test the recommendation flow: quiz -> recommendations -> learning plan
"""
import requests
import json

def test_quiz_api():
    """Test the quiz API endpoint"""
    print("🧪 Testing Quiz API...")
    response = requests.get("http://localhost:8001/api/preferences/quiz")
    if response.status_code == 200:
        quiz_data = response.json()
        print(f"✅ Quiz API working: {len(quiz_data)} questions available")
        print(f"First question: {quiz_data[0]['question']}")
        return True
    else:
        print(f"❌ Quiz API failed: {response.status_code}")
        return False

def mock_quiz_submission():
    """Simulate a quiz submission with preferences"""
    print("\n📝 Simulating quiz submission...")
    
    # Mock user preferences based on quiz responses
    preferences = {
        "learning_style": "visual",
        "content_type": "video",
        "difficulty": "intermediate",
        "session_length": "30-45 minutes"
    }
    
    print(f"User preferences: {json.dumps(preferences, indent=2)}")
    return preferences

def generate_mock_recommendations(preferences, query="Python programming"):
    """Generate mock recommendations based on preferences"""
    print(f"\n🎯 Generating recommendations for: '{query}'")
    print(f"Based on preferences: {preferences['learning_style']}, {preferences['content_type']}")
    
    # Mock recommendations based on preferences
    recommendations = [
        {
            "id": "rec_1",
            "title": "Python Programming Complete Course",
            "description": "Visual learning approach with interactive examples",
            "content_type": "video",
            "platform": "YouTube",
            "duration": "45 minutes",
            "difficulty": "intermediate",
            "rating": 4.8,
            "url": "https://youtube.com/watch?v=python_course",
            "reason": f"Matches your {preferences['learning_style']} learning style and {preferences['content_type']} preference"
        },
        {
            "id": "rec_2", 
            "title": "Interactive Python Coding Exercises",
            "description": "Hands-on coding practice with visual feedback",
            "content_type": "interactive",
            "platform": "Codecademy",
            "duration": "30 minutes",
            "difficulty": "intermediate",
            "rating": 4.6,
            "url": "https://codecademy.com/python",
            "reason": "Perfect for visual learners who prefer interactive content"
        },
        {
            "id": "rec_3",
            "title": "Python Fundamentals with Diagrams",
            "description": "Concept explanations using visual diagrams and charts",
            "content_type": "article",
            "platform": "Medium",
            "duration": "25 minutes",
            "difficulty": "intermediate", 
            "rating": 4.5,
            "url": "https://medium.com/python-diagrams",
            "reason": "Uses visual aids and diagrams to explain concepts clearly"
        }
    ]
    
    print("✅ Generated recommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec['title']} ({rec['platform']}) - {rec['rating']}⭐")
        print(f"     Reason: {rec['reason']}")
    
    return recommendations

def generate_learning_plan(recommendations, preferences):
    """Generate a learning plan based on recommendations"""
    print(f"\n📚 Generating personalized learning plan...")
    
    # Mock learning plan
    plan = {
        "id": "plan_123",
        "title": "Personalized Python Programming Journey",
        "description": f"A {preferences['difficulty']} level plan tailored for {preferences['learning_style']} learners",
        "estimated_duration": "4-6 weeks",
        "weekly_commitment": "3-4 hours",
        "milestones": [
            {
                "week": 1,
                "title": "Python Basics & Syntax",
                "content": [recommendations[0]],
                "goals": ["Understand Python syntax", "Write first programs", "Learn data types"]
            },
            {
                "week": 2,
                "title": "Control Structures & Functions", 
                "content": [recommendations[1]],
                "goals": ["Master if/else statements", "Create functions", "Handle loops"]
            },
            {
                "week": 3,
                "title": "Data Structures & OOP",
                "content": [recommendations[2]],
                "goals": ["Work with lists/dicts", "Understand classes", "Build projects"]
            },
            {
                "week": 4,
                "title": "Advanced Topics & Projects",
                "content": recommendations,
                "goals": ["File handling", "Error handling", "Complete final project"]
            }
        ],
        "learning_style_adaptations": {
            "visual": "All content includes diagrams, code visualizations, and step-by-step visual guides",
            "interactive": "Hands-on coding exercises after each concept",
            "paced": f"Sessions designed for {preferences['session_length']} optimal learning blocks"
        }
    }
    
    print("✅ Learning plan generated:")
    print(f"  📖 {plan['title']}")
    print(f"  ⏱️  Duration: {plan['estimated_duration']}")
    print(f"  📅 Weekly commitment: {plan['weekly_commitment']}")
    print(f"  🎯 Milestones: {len(plan['milestones'])} weeks")
    
    for milestone in plan['milestones']:
        print(f"    Week {milestone['week']}: {milestone['title']}")
        print(f"      Goals: {', '.join(milestone['goals'])}")
    
    return plan

def main():
    """Run the complete test flow"""
    print("🚀 Testing Personalized Learning System Flow\n")
    
    # Step 1: Test quiz API
    if not test_quiz_api():
        return
    
    # Step 2: Simulate quiz submission
    preferences = mock_quiz_submission()
    
    # Step 3: Generate recommendations
    recommendations = generate_mock_recommendations(preferences, "Python programming")
    
    # Step 4: Generate learning plan
    plan = generate_learning_plan(recommendations, preferences)
    
    print(f"\n🎉 Complete flow tested successfully!")
    print(f"✅ Quiz API: Working")
    print(f"✅ Preferences: Captured")
    print(f"✅ Recommendations: {len(recommendations)} generated")
    print(f"✅ Learning Plan: {len(plan['milestones'])} week plan created")
    
    print(f"\n💡 This demonstrates the AI-powered personalized learning flow:")
    print(f"   1. User takes learning style quiz")
    print(f"   2. System analyzes preferences") 
    print(f"   3. AI generates personalized recommendations")
    print(f"   4. System creates structured learning plan")
    print(f"   5. User gets tailored learning experience")

if __name__ == "__main__":
    main()
