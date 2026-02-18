from fastapi import FastAPI
from dotenv import load_dotenv
from pathlib import Path

# Always load backend/.env no matter where you run from
ENV_PATH = Path(__file__).resolve().parents[1] / ".env"   # backend/.env
load_dotenv(ENV_PATH)

#load_dotenv("backend/.env", override=True)
from .schemas import ProfileIn, PlanOut, LogIn, ReviewOut
from .graph import build_plan_graph, build_review_graph
from .storage import init_db, upsert_profile, save_plan, add_log, get_logs

app = FastAPI(title="Fitness Coach Agent (LangGraph + LLM)")

plan_graph = build_plan_graph()
review_graph = build_review_graph()

@app.on_event("startup")
def _startup():
    init_db()

@app.get("/")
def root():
    return {"status": "ok", "docs": "/docs"}

@app.post("/plan", response_model=PlanOut)
def create_plan(profile: ProfileIn):
    profile_dict = profile.model_dump()
    profile_id = upsert_profile(profile.name, profile_dict)

    out = plan_graph.invoke({"profile": profile_dict})
    plan = out.get("plan", {})
    warnings = out.get("warnings", [])

    save_plan(profile_id, plan, warnings)
    return PlanOut(profile=profile, plan=plan, warnings=warnings)

@app.post("/log")
def log_day(profile_name: str, log: LogIn):
    profile_id = upsert_profile(profile_name, {
        "name": profile_name,
        "goal": "lose_fat",
        "level": "beginner",
        "days_per_week": 3,
        "session_minutes": 45,
        "equipment": "bodyweight",
        "weight_kg": None,
        "preferences": {}
    })

    add_log(profile_id, log.model_dump())
    return {"status": "ok"}

@app.get("/review", response_model=ReviewOut)
def weekly_review(profile_name: str):
    profile_id = upsert_profile(profile_name, {
        "name": profile_name,
        "goal": "lose_fat",
        "level": "beginner",
        "days_per_week": 3,
        "session_minutes": 45,
        "equipment": "bodyweight",
        "weight_kg": None,
        "preferences": {}
    })

    logs = get_logs(profile_id)   # <-- FIXED
    out = review_graph.invoke({"logs": logs})

    r = out["review"]
    return ReviewOut(
        adherence=r["adherence"],
        summary=r["summary"],
        next_week_adjustment=r["next_week_adjustment"],
        coach_notes=r.get("coach_notes", "")
    )
