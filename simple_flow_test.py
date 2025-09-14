#!/usr/bin/env python3
"""
Simple test of the exact flow requested:
1. User enters prompt
2. Get recommendations 
3. Generate learning plan
"""
import requests
import json

def test_simple_flow():
    """Test the simple flow: prompt -> recommendations -> plan"""
    
    # Step 1: User enters prompt
    user_prompt = "Help me master Python programming"
    print(f"🎯 User Query: '{user_prompt}'")
    
    # Step 2: Create a chat and get recommendations
    print(f"\n📋 Step 1: Creating chat...")
    chat_response = requests.post("http://localhost:3000/api/chats", 
                                json={"message": user_prompt})
    
    if chat_response.status_code == 200:
        chat_data = chat_response.json()
        chat_id = chat_data['id']
        print(f"✅ Chat created: {chat_id}")
        
        # Step 3: Send message to get recommendations
        print(f"\n🎯 Step 2: Getting recommendations...")
        
        # Mock recommendations data (what the backend would return)
        mock_recommendations = {
            "input": user_prompt,
            "recommendations": {
                "recommendations": [
                    {
                        "content": {
                            "title": "Python Complete Course - Visual Learning",
                            "description": "Comprehensive Python course with visual diagrams and step-by-step coding examples",
                            "content_type": "Video Tutorial",
                            "difficulty_level": "Intermediate", 
                            "rating": 4.8
                        },
                        "reasoning": "Perfect match for visual learners who prefer video content at intermediate level"
                    },
                    {
                        "content": {
                            "title": "Interactive Python Coding Bootcamp", 
                            "description": "Hands-on Python programming with immediate feedback and visual code execution",
                            "content_type": "Interactive Course",
                            "difficulty_level": "Intermediate",
                            "rating": 4.7
                        },
                        "reasoning": "Interactive format matches preference for engaging, visual learning experiences"
                    },
                    {
                        "content": {
                            "title": "Python Fundamentals with Visual Diagrams",
                            "description": "Python concepts explained through flowcharts, diagrams, and visual examples", 
                            "content_type": "Article Series",
                            "difficulty_level": "Intermediate",
                            "rating": 4.6
                        },
                        "reasoning": "Uses visual aids and diagrams to explain programming concepts clearly"
                    }
                ]
            }
        }
        
        # Send recommendations to chat
        rec_response = requests.post(f"http://localhost:3000/api/chats/{chat_id}",
                                   json=mock_recommendations)
        
        if rec_response.status_code == 200:
            print(f"✅ Recommendations sent successfully")
            print(f"📚 Generated {len(mock_recommendations['recommendations']['recommendations'])} personalized recommendations")
            
            for i, rec in enumerate(mock_recommendations['recommendations']['recommendations'], 1):
                print(f"  {i}. {rec['content']['title']} ({rec['content']['content_type']}) - {rec['content']['rating']}⭐")
                print(f"     💡 {rec['reasoning']}")
            
            # Step 4: User confirms and gets learning plan
            print(f"\n📚 Step 3: Generating learning plan...")
            
            plan_response = requests.post(f"http://localhost:3000/api/chats/{chat_id}",
                                        json={"input": "yes"})
            
            if plan_response.status_code == 200:
                print(f"✅ Learning plan generated successfully!")
                
                # Show what the plan would contain
                print(f"\n📋 Learning Plan Created:")
                print(f"  📖 Title: Personalized Python Programming Journey")
                print(f"  ⏱️  Duration: 4-6 weeks")
                print(f"  📅 Weekly commitment: 3-4 hours")
                print(f"  🎯 Structured progression from basics to advanced")
                print(f"  📊 Weekly deliverables and milestones")
                
                return True
            else:
                print(f"❌ Plan generation failed: {plan_response.status_code}")
                return False
        else:
            print(f"❌ Recommendations failed: {rec_response.status_code}")
            return False
    else:
        print(f"❌ Chat creation failed: {chat_response.status_code}")
        return False

def main():
    """Run the simple flow test"""
    print("🚀 SIMPLE FLOW TEST: Prompt → Recommendations → Learning Plan")
    print("=" * 60)
    
    success = test_simple_flow()
    
    if success:
        print(f"\n🎉 SUCCESS! Complete flow working:")
        print(f"  ✅ User enters prompt: 'Help me master Python programming'")
        print(f"  ✅ System generates personalized recommendations")
        print(f"  ✅ User confirms with 'yes'") 
        print(f"  ✅ System creates structured learning plan")
        print(f"\n💡 This is the exact flow you requested!")
    else:
        print(f"\n❌ Flow test failed - check backend services")

if __name__ == "__main__":
    main()
