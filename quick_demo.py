#!/usr/bin/env python3
"""
Quick demo showing the AI recommendation engine outputs
"""

import asyncio
import sys
sys.path.append('/Users/ashis/trakl')

async def show_recommendation_outputs():
    print("🎯 TRAKL AI RECOMMENDATION ENGINE - LIVE DEMO")
    print("=" * 55)
    
    from rec.services.openai_service import DedalusService
    
    dedalus = DedalusService()
    
    # Simulate a user's learning profile
    user_profile = {
        "name": "Alex",
        "experience": "beginner",
        "interests": ["web development", "mobile apps"],
        "goals": ["build a portfolio website", "learn React"],
        "time_available": "1-2 hours daily"
    }
    
    print(f"👤 User Profile: {user_profile['name']}")
    print(f"   Experience: {user_profile['experience']}")
    print(f"   Interests: {', '.join(user_profile['interests'])}")
    print(f"   Goals: {', '.join(user_profile['goals'])}")
    print(f"   Time: {user_profile['time_available']}")
    
    # Generate personalized recommendations
    print(f"\n🤖 Generating AI recommendations for {user_profile['name']}...")
    
    recommendation_prompt = f"""
    Based on this user profile, recommend 3 specific learning resources:
    
    User: {user_profile['name']} ({user_profile['experience']} level)
    Interests: {', '.join(user_profile['interests'])}
    Goals: {', '.join(user_profile['goals'])}
    Available time: {user_profile['time_available']}
    
    For each recommendation, provide:
    1. Resource title
    2. Why it's perfect for this user
    3. Estimated time commitment
    4. Key skills they'll gain
    
    Make it personalized and encouraging.
    """
    
    recommendations = await dedalus.generate_text(recommendation_prompt, max_tokens=600)
    
    print("\n📋 AI-GENERATED PERSONALIZED RECOMMENDATIONS:")
    print("=" * 55)
    print(recommendations)
    
    # Show learning path adaptation
    print(f"\n🛤️  ADAPTIVE LEARNING PATH")
    print("=" * 55)
    
    progress_prompt = f"""
    {user_profile['name']} has been learning for 2 weeks. They've completed:
    - HTML basics ✅
    - CSS fundamentals ✅
    - Started JavaScript variables ⏳
    
    They're finding JavaScript challenging but are motivated. 
    Create a personalized 1-week learning plan that:
    1. Builds confidence with JavaScript
    2. Connects to their goal of building a portfolio website
    3. Fits their {user_profile['time_available']} schedule
    
    Be specific and encouraging.
    """
    
    learning_path = await dedalus.generate_text(progress_prompt, max_tokens=500)
    
    print(learning_path)
    
    # Show content matching
    print(f"\n🔍 SMART CONTENT MATCHING")
    print("=" * 55)
    
    available_content = [
        "React Hooks Tutorial - Building Interactive Components",
        "JavaScript Fundamentals - Variables and Functions",
        "CSS Grid Layout - Modern Web Design",
        "Node.js Backend Development - REST APIs",
        "Python Data Science - Pandas and Visualization"
    ]
    
    print("Available content in our database:")
    for i, content in enumerate(available_content, 1):
        print(f"   {i}. {content}")
    
    # Generate embeddings and find best matches
    user_query = "I want to learn React for building interactive websites"
    print(f"\nUser query: '{user_query}'")
    print("🧠 AI is analyzing semantic similarity...")
    
    query_embedding = await dedalus.generate_embeddings([user_query])
    content_embeddings = await dedalus.generate_embeddings(available_content)
    
    if query_embedding and content_embeddings:
        import numpy as np
        
        def cosine_similarity(a, b):
            return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
        
        matches = []
        for i, content_emb in enumerate(content_embeddings):
            similarity = cosine_similarity(query_embedding[0], content_emb)
            matches.append((similarity, available_content[i]))
        
        matches.sort(reverse=True)
        
        print("\n🎯 BEST MATCHES (by AI semantic analysis):")
        for i, (score, content) in enumerate(matches[:3], 1):
            print(f"   {i}. [{score:.3f}] {content}")
            if i == 1:
                print("      👆 Perfect match! This aligns with your React goals")
    
    print(f"\n" + "=" * 55)
    print("🎉 This is how Trakl's AI creates personalized learning!")
    print("✅ Understands user context and goals")
    print("✅ Generates tailored recommendations") 
    print("✅ Adapts based on progress and challenges")
    print("✅ Matches content using semantic understanding")
    print("=" * 55)

if __name__ == "__main__":
    asyncio.run(show_recommendation_outputs())
