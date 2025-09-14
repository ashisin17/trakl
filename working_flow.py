#!/usr/bin/env python3
"""
Direct implementation of the requested flow:
User enters prompt → Get recommendations → Generate learning plan
"""

def demonstrate_flow():
    print("🎯 PERSONALIZED LEARNING FLOW")
    print("=" * 50)
    
    # Step 1: User enters prompt
    user_prompt = "Help me master Python programming"
    print(f"\n👤 USER INPUT: '{user_prompt}'")
    
    # Step 2: System generates recommendations based on quiz preferences
    print(f"\n🤖 SYSTEM: Analyzing your request and quiz preferences...")
    print(f"📊 Based on your learning style: Visual learner, prefers videos, intermediate level")
    
    recommendations = [
        {
            "title": "Python Complete Course - Visual Learning",
            "platform": "YouTube", 
            "type": "Video Tutorial",
            "duration": "45 minutes",
            "rating": 4.8,
            "reason": "Perfect match for visual learners who prefer video content"
        },
        {
            "title": "Interactive Python Coding Bootcamp",
            "platform": "Codecademy",
            "type": "Interactive Course", 
            "duration": "30 minutes per session",
            "rating": 4.7,
            "reason": "Interactive format matches your learning preferences"
        },
        {
            "title": "Python Fundamentals with Diagrams",
            "platform": "Medium",
            "type": "Article Series",
            "duration": "25 minutes per article",
            "rating": 4.6,
            "reason": "Uses visual aids to explain concepts clearly"
        }
    ]
    
    print(f"\n🎯 RECOMMENDATIONS GENERATED:")
    print(f"Here are the best resources based on your quiz:")
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. 📚 {rec['title']}")
        print(f"   Platform: {rec['platform']} | Type: {rec['type']}")
        print(f"   Duration: {rec['duration']} | Rating: {rec['rating']}⭐")
        print(f"   💡 Why: {rec['reason']}")
    
    print(f"\n🤖 SYSTEM: Would you like me to create a learning plan based on these?")
    
    # Step 3: User responds with yes
    user_response = "yes"
    print(f"\n👤 USER: '{user_response}'")
    
    # Step 4: Generate learning plan
    print(f"\n🤖 SYSTEM: Creating your personalized learning plan...")
    
    learning_plan = {
        "title": "Personalized Python Programming Journey",
        "duration": "4 weeks",
        "commitment": "3-4 hours per week",
        "weeks": [
            {
                "week": 1,
                "title": "Python Basics & Syntax",
                "goals": ["Understand Python syntax", "Learn data types", "Write first programs"],
                "deliverable": "Simple calculator program"
            },
            {
                "week": 2, 
                "title": "Control Flow & Functions",
                "goals": ["Master if/else statements", "Create functions", "Handle loops"],
                "deliverable": "Interactive quiz game"
            },
            {
                "week": 3,
                "title": "Data Structures & File Handling",
                "goals": ["Work with lists/dicts", "Read/write files", "Process data"],
                "deliverable": "Data analysis script"
            },
            {
                "week": 4,
                "title": "Object-Oriented Programming",
                "goals": ["Understand classes", "Build applications", "Final project"],
                "deliverable": "Complete Python application"
            }
        ]
    }
    
    print(f"\n📚 LEARNING PLAN GENERATED:")
    print(f"📖 {learning_plan['title']}")
    print(f"⏱️  Duration: {learning_plan['duration']}")
    print(f"📅 Weekly commitment: {learning_plan['commitment']}")
    
    print(f"\n📋 Weekly Breakdown:")
    for week in learning_plan['weeks']:
        print(f"\n   Week {week['week']}: {week['title']}")
        print(f"   Goals: {', '.join(week['goals'])}")
        print(f"   Deliverable: {week['deliverable']}")
    
    print(f"\n🎉 COMPLETE! Your personalized learning journey is ready.")
    print(f"✅ This demonstrates the exact flow you requested:")
    print(f"   1. User enters prompt: '{user_prompt}'")
    print(f"   2. System shows recommendations based on quiz")
    print(f"   3. User confirms with: '{user_response}'")
    print(f"   4. System generates structured learning plan")

if __name__ == "__main__":
    demonstrate_flow()
