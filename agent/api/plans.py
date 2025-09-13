from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List
import uuid
import httpx

from ..database import get_db, LearningPlan
from ..models import (
    LearningPlanCreate,
    LearningPlanResponse,
    PlanGenerationRequest,
    PlanGenerationResponse,
    PlanStatus
)
from ..services.plan_generator import PlanGeneratorService
from ..config import settings

router = APIRouter()

@router.post("/generate", response_model=PlanGenerationResponse)
async def generate_learning_plan(
    request: PlanGenerationRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Generate a personalized learning plan using AI"""
    
    plan_generator = PlanGeneratorService(db)
    
    # Get user preferences and goal from recommendation service
    async with httpx.AsyncClient() as client:
        # Get user preferences
        prefs_response = await client.get(
            f"{settings.rec_service_url}/api/preferences/user/{request.user_id}"
        )
        if prefs_response.status_code != 200:
            raise HTTPException(status_code=404, detail="User preferences not found")
        
        user_preferences = prefs_response.json()
        
        # Get learning goal (assuming it exists in rec service)
        # This would need to be implemented in the rec service
        learning_goal = {"title": "Sample Goal", "description": "Learn programming"}
    
    # Generate the plan
    plan_response = await plan_generator.generate_plan(
        user_id=request.user_id,
        goal_id=request.goal_id,
        user_preferences=user_preferences,
        learning_goal=learning_goal,
        constraints=request.constraints or {}
    )
    
    return plan_response

@router.post("/", response_model=LearningPlanResponse)
async def create_learning_plan(
    plan: LearningPlanCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new learning plan manually"""
    
    db_plan = LearningPlan(
        user_id=uuid.UUID(plan.user_id),
        goal_id=uuid.UUID(plan.goal_id),
        title=plan.title,
        description=plan.description,
        total_weeks=plan.total_weeks,
        sessions_per_week=plan.sessions_per_week,
        difficulty_level=plan.difficulty_level,
        tags=plan.tags,
        milestones=[],
        weekly_schedule=[],
        recommended_resources=[]
    )
    
    db.add(db_plan)
    await db.commit()
    await db.refresh(db_plan)
    
    return LearningPlanResponse(
        id=str(db_plan.id),
        user_id=str(db_plan.user_id),
        goal_id=str(db_plan.goal_id),
        title=db_plan.title,
        description=db_plan.description,
        total_weeks=db_plan.total_weeks,
        sessions_per_week=db_plan.sessions_per_week,
        estimated_hours_total=db_plan.estimated_hours_total,
        milestones=db_plan.milestones or [],
        weekly_schedule=db_plan.weekly_schedule or [],
        recommended_resources=db_plan.recommended_resources or [],
        status=PlanStatus(db_plan.status),
        progress_percentage=db_plan.progress_percentage,
        current_week=db_plan.current_week,
        difficulty_level=db_plan.difficulty_level,
        tags=db_plan.tags or [],
        created_at=db_plan.created_at
    )

@router.get("/user/{user_id}", response_model=List[LearningPlanResponse])
async def get_user_plans(
    user_id: str,
    status: str = None,
    db: AsyncSession = Depends(get_db)
):
    """Get all learning plans for a user"""
    
    query = select(LearningPlan).where(LearningPlan.user_id == uuid.UUID(user_id))
    
    if status:
        query = query.where(LearningPlan.status == status)
    
    result = await db.execute(query)
    plans = result.scalars().all()
    
    return [
        LearningPlanResponse(
            id=str(plan.id),
            user_id=str(plan.user_id),
            goal_id=str(plan.goal_id),
            title=plan.title,
            description=plan.description,
            total_weeks=plan.total_weeks,
            sessions_per_week=plan.sessions_per_week,
            estimated_hours_total=plan.estimated_hours_total,
            milestones=plan.milestones or [],
            weekly_schedule=plan.weekly_schedule or [],
            recommended_resources=plan.recommended_resources or [],
            status=PlanStatus(plan.status),
            progress_percentage=plan.progress_percentage,
            current_week=plan.current_week,
            difficulty_level=plan.difficulty_level,
            tags=plan.tags or [],
            created_at=plan.created_at
        )
        for plan in plans
    ]

@router.get("/{plan_id}", response_model=LearningPlanResponse)
async def get_learning_plan(
    plan_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific learning plan"""
    
    result = await db.execute(
        select(LearningPlan).where(LearningPlan.id == uuid.UUID(plan_id))
    )
    plan = result.scalar_one_or_none()
    
    if not plan:
        raise HTTPException(status_code=404, detail="Learning plan not found")
    
    return LearningPlanResponse(
        id=str(plan.id),
        user_id=str(plan.user_id),
        goal_id=str(plan.goal_id),
        title=plan.title,
        description=plan.description,
        total_weeks=plan.total_weeks,
        sessions_per_week=plan.sessions_per_week,
        estimated_hours_total=plan.estimated_hours_total,
        milestones=plan.milestones or [],
        weekly_schedule=plan.weekly_schedule or [],
        recommended_resources=plan.recommended_resources or [],
        status=PlanStatus(plan.status),
        progress_percentage=plan.progress_percentage,
        current_week=plan.current_week,
        difficulty_level=plan.difficulty_level,
        tags=plan.tags or [],
        created_at=plan.created_at
    )

@router.put("/{plan_id}/status")
async def update_plan_status(
    plan_id: str,
    status: PlanStatus,
    db: AsyncSession = Depends(get_db)
):
    """Update learning plan status"""
    
    result = await db.execute(
        select(LearningPlan).where(LearningPlan.id == uuid.UUID(plan_id))
    )
    plan = result.scalar_one_or_none()
    
    if not plan:
        raise HTTPException(status_code=404, detail="Learning plan not found")
    
    await db.execute(
        update(LearningPlan)
        .where(LearningPlan.id == uuid.UUID(plan_id))
        .values(status=status.value)
    )
    await db.commit()
    
    return {"message": "Plan status updated successfully", "status": status.value}

@router.delete("/{plan_id}")
async def delete_learning_plan(
    plan_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a learning plan"""
    
    result = await db.execute(
        select(LearningPlan).where(LearningPlan.id == uuid.UUID(plan_id))
    )
    plan = result.scalar_one_or_none()
    
    if not plan:
        raise HTTPException(status_code=404, detail="Learning plan not found")
    
    await db.delete(plan)
    await db.commit()
    
    return {"message": "Learning plan deleted successfully"}
