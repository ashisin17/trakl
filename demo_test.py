#!/usr/bin/env python3
"""
Comprehensive demo of Trakl AI Learning System with Dedalus Labs
This shows the AI recommendations and learning plan generation in action
"""

import asyncio
import sys
import os
sys.path.append('/Users/ashis/trakl')

async def demo_ai_recommendations():
    print("🎯 TRAKL AI LEARNING SYSTEM DEMO")
    print("=" * 60)
    print("Powered by Dedalus Labs AI")
    print("=" * 60)
    
    try:
        from rec.services.openai_service import DedalusService
        from agent.services.plan_generator import PlanGeneratorService
        
        # Initialize AI services
        dedalus = DedalusService()
        print("✅ AI Services initialized")
        
        # Demo 1: Content Analysis & Embeddings
        print("\n📊 DEMO 1: AI-Powered Content Analysis")
        print("-" * 40)
        
        learning_contents = [
            "Introduction to Python Programming: Variables, Data Types, and Control Flow",
            "Advanced Machine Learning with TensorFlow and Neural Networks",
            "Web Development with React: Building Interactive User Interfaces",
            "Data Science Fundamentals: Statistics, Pandas, and Visualization",
            "DevOps and Cloud Computing: Docker, Kubernetes, and AWS"
        ]
        
        print("Analyzing learning content with AI...")
        embeddings = await dedalus.generate_embeddings(learning_contents)
        
        if embeddings:
            print(f"✅ Generated embeddings for {len(embeddings)} content items")
            print(f"   Embedding dimensions: {len(embeddings[0])}")
            
            # Calculate similarity between contents
            import numpy as np
            
            def cosine_similarity(a, b):
                return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
            
            print("\n🔍 Content Similarity Analysis:")
            for i in range(len(learning_contents)):
                for j in range(i+1, len(learning_contents)):
                    similarity = cosine_similarity(embeddings[i], embeddings[j])
                    content1 = learning_contents[i][:30] + "..."
                    content2 = learning_contents[j][:30] + "..."
                    print(f"   {content1} ↔ {content2}: {similarity:.3f}")
        
        # Demo 2: Personalized Learning Plan Generation
        print("\n🤖 DEMO 2: AI Learning Plan Generation")
        print("-" * 40)
        
        user_goal = "Learn full-stack web development from beginner to advanced level"
        user_preferences = {
            "learning_style": "hands-on projects",
            "time_availability": "2 hours per day",
            "experience_level": "beginner",
            "preferred_technologies": ["JavaScript", "React", "Node.js"]
        }
        
        print(f"Goal: {user_goal}")
        print(f"Preferences: {user_preferences}")
        print("\nGenerating personalized learning plan with AI...")
        
        plan_prompt = f"""
        Create a detailed 12-week learning plan for: {user_goal}
        
        User preferences:
        - Learning style: {user_preferences['learning_style']}
        - Time availability: {user_preferences['time_availability']}
        - Experience level: {user_preferences['experience_level']}
        - Preferred technologies: {', '.join(user_preferences['preferred_technologies'])}
        
        Provide a structured plan with:
        1. Weekly topics and goals
        2. Recommended projects
        3. Key skills to develop
        4. Time allocation suggestions
        
        Format as a clear, actionable plan.
        """
        
        learning_plan = await dedalus.generate_text(plan_prompt, max_tokens=800)
        
        if learning_plan:
            print("✅ AI-Generated Learning Plan:")
            print("-" * 30)
            print(learning_plan)
        
        # Demo 3: Smart Content Recommendations
        print("\n🎯 DEMO 3: Smart Content Recommendations")
        print("-" * 40)
        
        user_query = "I want to learn React hooks and state management"
        print(f"User query: '{user_query}'")
        print("\nGenerating AI-powered recommendations...")
        
        # Generate embedding for user query
        query_embedding = await dedalus.generate_embeddings([user_query])
        
        if query_embedding and embeddings:
            print("✅ Matching content based on AI similarity:")
            
            # Calculate similarities with all content
            similarities = []
            for i, content_embedding in enumerate(embeddings):
                similarity = cosine_similarity(query_embedding[0], content_embedding)
                similarities.append((similarity, learning_contents[i]))
            
            # Sort by similarity (highest first)
            similarities.sort(reverse=True)
            
            print("\n📋 Recommended Learning Content (by AI relevance):")
            for i, (score, content) in enumerate(similarities[:3]):
                print(f"   {i+1}. [{score:.3f}] {content}")
        
        # Demo 4: Adaptive Learning Suggestions
        print("\n🧠 DEMO 4: Adaptive Learning Suggestions")
        print("-" * 40)
        
        learning_progress = {
            "completed_topics": ["HTML basics", "CSS fundamentals", "JavaScript variables"],
            "current_struggle": "Understanding JavaScript async/await",
            "learning_pace": "slower than expected",
            "preferred_difficulty": "gradual increase"
        }
        
        adaptation_prompt = f"""
        Based on this learner's progress, suggest 3 specific next steps:
        
        Completed: {', '.join(learning_progress['completed_topics'])}
        Current challenge: {learning_progress['current_struggle']}
        Learning pace: {learning_progress['learning_pace']}
        Preference: {learning_progress['preferred_difficulty']}
        
        Provide actionable, encouraging suggestions that address their current struggle while building on what they know.
        """
        
        suggestions = await dedalus.generate_text(adaptation_prompt, max_tokens=400)
        
        if suggestions:
            print("✅ AI-Powered Learning Adaptation:")
            print("-" * 30)
            print(suggestions)
        
        print("\n" + "=" * 60)
        print("🎉 TRAKL AI DEMO COMPLETE!")
        print("The system successfully demonstrated:")
        print("✅ AI-powered content analysis and embeddings")
        print("✅ Personalized learning plan generation")
        print("✅ Smart content recommendations")
        print("✅ Adaptive learning suggestions")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Demo error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(demo_ai_recommendations())
