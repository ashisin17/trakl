#!/usr/bin/env python3
"""
Simple test of Dedalus Labs integration without Docker complexity
"""

import asyncio
import os
import sys
sys.path.append('/Users/ashis/trakl/rec')
sys.path.append('/Users/ashis/trakl')

# Test the Dedalus service directly
async def test_dedalus_integration():
    print("🧪 Testing Dedalus Labs Integration")
    print("=" * 40)
    
    try:
        # Import the Dedalus service
        from rec.services.openai_service import DedalusService
        
        # Initialize service
        dedalus = DedalusService()
        print("✅ DedalusService imported successfully")
        
        # Test embedding generation
        print("\n📊 Testing embedding generation...")
        test_texts = [
            "Learn Python programming fundamentals",
            "Machine learning with scikit-learn",
            "Web development with FastAPI"
        ]
        
        embeddings = await dedalus.generate_embeddings(test_texts)
        
        if embeddings and len(embeddings) == 3:
            print(f"✅ Generated {len(embeddings)} embeddings")
            print(f"   Embedding dimensions: {len(embeddings[0]) if embeddings[0] else 'N/A'}")
        else:
            print("❌ Failed to generate embeddings")
            
        # Test text generation
        print("\n🤖 Testing text generation...")
        prompt = "Explain the benefits of learning Python programming in 2 sentences."
        
        response = await dedalus.generate_text(prompt)
        
        if response:
            print("✅ Text generation successful")
            print(f"   Response: {response[:100]}...")
        else:
            print("❌ Failed to generate text")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
        
    print("\n" + "=" * 40)
    print("🎉 Dedalus integration test complete!")

if __name__ == "__main__":
    asyncio.run(test_dedalus_integration())
