from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List
import httpx
from datetime import datetime, timedelta
import json
from dedalus_labs import AsyncDedalus, DedalusRunner

from database import get_db, LearningPlan
from models import (
    PlanGenerationResponse, 
    LearningPlanResponse, 
    Milestone, 
    WeeklySchedule,
    PlanStatus
)
from config import settings

class PlanGeneratorService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.dedalus_client = AsyncDedalus(api_key=settings.dedalus_api_key)
        self.dedalus_runner = DedalusRunner(self.dedalus_client)
    
    async def generate_plan(
        self,
        user_id: str,
        goal_id: str,
        user_preferences: Dict[str, Any],
        learning_goal: Dict[str, Any],
        constraints: Dict[str, Any]
    ) -> PlanGenerationResponse:
        """Generate a comprehensive learning plan using AI"""
        
        # Get recommended content from rec service
        recommended_content = await self._get_recommended_content(user_id, goal_id)
        
        # Generate plan structure using AI
        plan_structure = await self._generate_plan_structure(
            learning_goal, user_preferences, constraints, recommended_content
        )
        
        # Create detailed weekly schedule
        weekly_schedule = await self._create_weekly_schedule(
            plan_structure, user_preferences, recommended_content
        )
        
        # Generate milestones
        milestones = await self._generate_milestones(
            learning_goal, plan_structure, weekly_schedule
        )
        
        # Calculate estimated completion date
        total_weeks = plan_structure.get("total_weeks", 8)
        estimated_completion = datetime.now() + timedelta(weeks=total_weeks)
        
        # Create and save the plan
        db_plan = LearningPlan(
            user_id=user_id,
            goal_id=goal_id,
            title=plan_structure["title"],
            description=plan_structure["description"],
            total_weeks=total_weeks,
            sessions_per_week=plan_structure.get("sessions_per_week", 3),
            estimated_hours_total=plan_structure.get("estimated_hours", 40),
            milestones=[milestone.dict() for milestone in milestones],
            weekly_schedule=[week.dict() for week in weekly_schedule],
            recommended_resources=[item["content_id"] for item in recommended_content],
            difficulty_level=plan_structure.get("difficulty_level", "intermediate"),
            tags=plan_structure.get("tags", [])
        )
        
        self.db.add(db_plan)
        await self.db.commit()
        await self.db.refresh(db_plan)
        
        # Create response
        plan_response = LearningPlanResponse(
            id=str(db_plan.id),
            user_id=str(db_plan.user_id),
            goal_id=str(db_plan.goal_id),
            title=db_plan.title,
            description=db_plan.description,
            total_weeks=db_plan.total_weeks,
            sessions_per_week=db_plan.sessions_per_week,
            estimated_hours_total=db_plan.estimated_hours_total,
            milestones=milestones,
            weekly_schedule=weekly_schedule,
            recommended_resources=db_plan.recommended_resources,
            status=PlanStatus.DRAFT,
            progress_percentage=0.0,
            current_week=1,
            difficulty_level=db_plan.difficulty_level,
            tags=db_plan.tags or [],
            created_at=db_plan.created_at
        )
        
        return PlanGenerationResponse(
            plan=plan_response,
            reasoning=plan_structure.get("reasoning", "Generated based on your learning preferences and goals"),
            estimated_completion_date=estimated_completion,
            success_probability=0.85
        )
    
    async def _get_recommended_content(self, user_id: str, goal_id: str) -> List[Dict[str, Any]]:
        """Get recommended content from the recommendation service"""
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{settings.rec_service_url}/api/recommendations/generate",
                    json={
                        "user_id": user_id,
                        "goal_id": goal_id,
                        "max_results": 20
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return [
                        {
                            "content_id": rec["content"]["id"],
                            "title": rec["content"]["title"],
                            "content_type": rec["content"]["content_type"],
                            "duration_minutes": rec["content"]["duration_minutes"],
                            "difficulty_level": rec["content"]["difficulty_level"],
                            "final_score": rec["final_score"]
                        }
                        for rec in data["recommendations"]
                    ]
        except Exception as e:
            print(f"Error fetching recommendations: {e}")
        
        # Fallback mock content
        return [
            {
                "content_id": "mock-1",
                "title": "Introduction to Programming",
                "content_type": "video",
                "duration_minutes": 30,
                "difficulty_level": "beginner",
                "final_score": 0.9
            },
            {
                "content_id": "mock-2", 
                "title": "Programming Fundamentals",
                "content_type": "article",
                "duration_minutes": 15,
                "difficulty_level": "beginner",
                "final_score": 0.8
            }
        ]
    
    async def _generate_plan_structure(
        self,
        learning_goal: Dict[str, Any],
        user_preferences: Dict[str, Any],
        constraints: Dict[str, Any],
        recommended_content: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Use AI to generate the overall plan structure"""
        
        prompt = f"""
        Create a personalized learning plan structure based on:
        
        Learning Goal: {learning_goal.get('title', 'Programming Skills')}
        Description: {learning_goal.get('description', 'Learn programming fundamentals')}
        
        User Preferences:
        - Preferred difficulty: {user_preferences.get('preferred_difficulty', 'intermediate')}
        - Session length: {user_preferences.get('preferred_session_length', 30)} minutes
        - Learning style: Visual={user_preferences.get('visual_preference', 0.5)}, Auditory={user_preferences.get('auditory_preference', 0.5)}
        
        Available Content: {len(recommended_content)} resources
        
        Constraints: {constraints}
        
        Generate a JSON response with:
        {{
            "title": "Plan title",
            "description": "Plan description", 
            "total_weeks": 8,
            "sessions_per_week": 3,
            "estimated_hours": 40,
            "difficulty_level": "intermediate",
            "tags": ["programming", "beginner"],
            "focus_areas": ["fundamentals", "practice", "projects"],
            "reasoning": "Why this plan structure works for the user"
        }}
        """
        
        try:
            response = await self.dedalus_runner.run(
                input=prompt,
                model=settings.dedalus_model
            )
            
            content = response.final_output
            return json.loads(content)
        except Exception as e:
            print(f"Error generating plan structure: {e}")
            # Fallback structure
            return {
                "title": f"Learn {learning_goal.get('title', 'Programming')}",
                "description": "Comprehensive learning plan tailored to your preferences",
                "total_weeks": 8,
                "sessions_per_week": 3,
                "estimated_hours": 40,
                "difficulty_level": user_preferences.get('preferred_difficulty', 'intermediate'),
                "tags": ["learning", "structured"],
                "focus_areas": ["fundamentals", "practice", "application"],
                "reasoning": "Structured approach based on your learning preferences"
            }
    
    async def _create_weekly_schedule(
        self,
        plan_structure: Dict[str, Any],
        user_preferences: Dict[str, Any],
        recommended_content: List[Dict[str, Any]]
    ) -> List[WeeklySchedule]:
        """Create detailed weekly schedule"""
        
        total_weeks = plan_structure["total_weeks"]
        sessions_per_week = plan_structure["sessions_per_week"]
        focus_areas = plan_structure.get("focus_areas", ["study", "practice", "review"])
        
        weekly_schedules = []
        content_index = 0
        
        for week in range(1, total_weeks + 1):
            # Determine focus for this week
            focus_area = focus_areas[(week - 1) % len(focus_areas)]
            
            # Create sessions for the week
            sessions = []
            for session in range(sessions_per_week):
                if content_index < len(recommended_content):
                    content = recommended_content[content_index]
                    sessions.append({
                        "session_number": session + 1,
                        "title": f"Session {session + 1}: {content['title']}",
                        "content_id": content["content_id"],
                        "duration_minutes": content.get("duration_minutes", 30),
                        "activity_type": content.get("content_type", "study")
                    })
                    content_index += 1
                else:
                    # Create practice/review sessions when content runs out
                    sessions.append({
                        "session_number": session + 1,
                        "title": f"Practice Session {session + 1}",
                        "content_id": None,
                        "duration_minutes": 45,
                        "activity_type": "practice"
                    })
            
            weekly_schedule = WeeklySchedule(
                week_number=week,
                focus_areas=[focus_area],
                sessions=sessions,
                milestones=[f"Week {week} checkpoint"] if week % 2 == 0 else [],
                estimated_hours=sum(s["duration_minutes"] for s in sessions) / 60
            )
            
            weekly_schedules.append(weekly_schedule)
        
        return weekly_schedules
    
    async def _generate_milestones(
        self,
        learning_goal: Dict[str, Any],
        plan_structure: Dict[str, Any],
        weekly_schedule: List[WeeklySchedule]
    ) -> List[Milestone]:
        """Generate learning milestones"""
        
        total_weeks = plan_structure["total_weeks"]
        milestones = []
        
        # Create milestones at key intervals
        milestone_weeks = [2, 4, 6, total_weeks]
        
        for i, week in enumerate(milestone_weeks):
            if week <= total_weeks:
                milestone = Milestone(
                    title=f"Milestone {i + 1}: Week {week} Checkpoint",
                    description=f"Assessment of progress through week {week}",
                    target_week=week,
                    milestone_type="skill_check" if week < total_weeks else "final_project",
                    success_criteria=[
                        f"Complete {week * 2} learning sessions",
                        f"Demonstrate understanding of week {week} concepts",
                        "Pass knowledge check quiz"
                    ],
                    required_skills=[f"week_{week}_skills"]
                )
                milestones.append(milestone)
        
        return milestones
