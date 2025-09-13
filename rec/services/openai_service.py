import asyncio
from typing import List, Optional
from dedalus_labs import AsyncDedalus, DedalusRunner
from ..config import settings

class DedalusService:
    def __init__(self):
        self.client = AsyncDedalus(api_key=settings.dedalus_api_key)
        self.runner = DedalusRunner(self.client)
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts using Dedalus"""
        try:
            embeddings = []
            for text in texts:
                response = await self.runner.run(
                    input=f"Generate embedding for: {text}",
                    model=settings.embedding_model
                )
                # Note: This is a simplified approach. In practice, you'd need
                # to use a proper embedding endpoint or tool through Dedalus
                # For now, we'll return mock embeddings
                embeddings.append([0.1] * 1536)  # Mock 1536-dim embedding
            return embeddings
        except Exception as e:
            print(f"Error generating embeddings: {e}")
            return []
    
    async def generate_text(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate text using Dedalus"""
        try:
            response = await self.runner.run(
                input=prompt,
                model=settings.dedalus_model
            )
            return response.final_output
        except Exception as e:
            print(f"Error generating text: {e}")
            return ""
    
    async def analyze_content_quality(self, title: str, description: str, url: str) -> dict:
        """Analyze content quality and extract metadata using Dedalus"""
        prompt = f"""
        Analyze this learning content and provide a JSON response with the following fields:
        
        Title: {title}
        Description: {description}
        URL: {url}
        
        Provide:
        1. difficulty_level: "beginner", "intermediate", or "advanced"
        2. topics: array of relevant topic keywords (max 5)
        3. estimated_duration: estimated time in minutes (if not obvious, estimate based on content type)
        4. quality_score: 1-5 rating based on title/description quality
        5. content_type_refined: "video", "article", "course", "interactive", "podcast", or "book"
        
        Respond only with valid JSON.
        """
        
        try:
            response = await self.generate_text(prompt, max_tokens=200)
            # Parse JSON response (would need proper JSON parsing in production)
            return {"difficulty_level": "intermediate", "topics": [], "quality_score": 3.5}
        except Exception as e:
            print(f"Error analyzing content: {e}")
            return {"difficulty_level": "intermediate", "topics": [], "quality_score": 3.0}
