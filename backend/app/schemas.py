from pydantic import BaseModel, Field
from typing import Literal, Optional, List, Dict

Goal = Literal["lose_fat", "build_muscle", "improve_stamina"]
Equipment = Literal["gym", "dumbbells", "bodyweight"]

class ProfileIn(BaseModel):
    name: str = Field(default="User", min_length=1)
    goal: Goal
    level: Literal["beginner", "intermediate"] = "beginner"
    days_per_week: int = Field(ge=1, le=7)
    session_minutes: int = Field(ge=15, le=180)
    equipment: Equipment
    weight_kg: Optional[float] = Field(default=None, ge=30, le=250)
    preferences: Dict[str, str] = Field(default_factory=dict)

class PlanOut(BaseModel):
    profile: ProfileIn
    plan: Dict
    warnings: List[str] = Field(default_factory=list)

class LogIn(BaseModel):
    date: str  # YYYY-MM-DD
    workout_done: bool = False
    steps: Optional[int] = Field(default=None, ge=0, le=200000)
    weight_kg: Optional[float] = Field(default=None, ge=30, le=250)
    notes: Optional[str] = ""

class ReviewOut(BaseModel):
    adherence: float
    summary: str
    next_week_adjustment: str
    coach_notes: str = ""
