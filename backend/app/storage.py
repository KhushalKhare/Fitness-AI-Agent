from typing import Optional, List, Dict, Any
from sqlmodel import SQLModel, Field, create_engine, Session, select
import json

DB_URL = "sqlite:///./fitness_agent.db"
engine = create_engine(DB_URL, echo=False)

class Profile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    data_json: str

class Plan(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    profile_id: int = Field(index=True)
    created_at: str = Field(default="")
    plan_json: str
    warnings_json: str

class Log(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    profile_id: int = Field(index=True)
    date: str = Field(index=True)
    workout_done: bool = False
    steps: Optional[int] = None
    weight_kg: Optional[float] = None
    notes: Optional[str] = ""

def init_db() -> None:
    SQLModel.metadata.create_all(engine)

def upsert_profile(name: str, data: Dict[str, Any]) -> int:
    with Session(engine) as s:
        existing = s.exec(select(Profile).where(Profile.name == name)).first()
        if existing:
            existing.data_json = json.dumps(data, ensure_ascii=False)
            s.add(existing)
            s.commit()
            return existing.id

        p = Profile(name=name, data_json=json.dumps(data, ensure_ascii=False))
        s.add(p)
        s.commit()
        s.refresh(p)
        return p.id

def save_plan(profile_id: int, plan: Dict[str, Any], warnings: List[str]) -> int:
    with Session(engine) as s:
        rec = Plan(
            profile_id=profile_id,
            plan_json=json.dumps(plan, ensure_ascii=False),
            warnings_json=json.dumps(warnings, ensure_ascii=False),
        )
        s.add(rec)
        s.commit()
        s.refresh(rec)
        return rec.id

def add_log(profile_id: int, log: Dict[str, Any]) -> int:
    with Session(engine) as s:
        rec = Log(profile_id=profile_id, **log)
        s.add(rec)
        s.commit()
        s.refresh(rec)
        return rec.id

def get_logs(profile_id: int, limit: int = 60) -> List[Dict[str, Any]]:
    with Session(engine) as s:
        rows = list(
            s.exec(
                select(Log)
                .where(Log.profile_id == profile_id)
                .order_by(Log.date.asc())
            )
        )
        rows = rows[-limit:] if limit else rows
        return [
            {
                "date": r.date,
                "workout_done": r.workout_done,
                "steps": r.steps,
                "weight_kg": r.weight_kg,
                "notes": r.notes,
            }
            for r in rows
        ]
