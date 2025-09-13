import openai
from typing import List, Optional
import asyncio
from ..config import settings

class OpenAIService:
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts"""
        try:
            response = await self.client.embeddings.create(
                model=settings.embedding_model,
                input=texts
            )
            return [embedding.embedding for embedding in response.data]
        except Exception as e:
            print(f"Error generating embeddings: {e}")
            return []
    
    async def generate_text(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate text using OpenAI's chat completion"""
        try:
            response = await self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating text: {e}")
            return ""
    
    async def analyze_content_quality(self, title: str, description: str, url: str) -> dict:
        """Analyze content quality and extract metadata"""
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
