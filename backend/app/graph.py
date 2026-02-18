from typing import TypedDict, Dict, List, Any
from langgraph.graph import StateGraph, END
from .llm import generate_text

class State(TypedDict, total=False):
    profile: Dict[str, Any]
    plan: Dict[str, Any]
    warnings: List[str]
    logs: List[Dict[str, Any]]
    review: Dict[str, Any]

def intake_normalizer(state: State) -> State:
    state.setdefault("warnings", [])
    return state

def safety_check(state: State) -> State:
    p = state["profile"]
    warnings = state.get("warnings", [])

    if p["days_per_week"] > 6:
        warnings.append("Capped training days to 6 for recovery.")
        p["days_per_week"] = 6

    if p["level"] == "beginner" and p["session_minutes"] > 90:
        warnings.append("Beginner sessions capped at 90 minutes.")
        p["session_minutes"] = 90

    state["profile"] = p
    state["warnings"] = warnings
    return state

def plan_workouts(state: State) -> State:
    p = state["profile"]
    days = p["days_per_week"]
    duration = p["session_minutes"]
    equipment = p["equipment"]
    goal = p["goal"]
    level = p["level"]

    workouts = []
    for d in range(1, days + 1):
        workouts.append({
            "day": d,
            "title": _session_title(goal, d),
            "duration_minutes": duration,
            "session": _template_session(goal, equipment, level),
        })

    state["plan"] = {"workouts": workouts}
    return state

def plan_nutrition(state: State) -> State:
    p = state["profile"]
    weight = p.get("weight_kg")

    protein = None
    if weight:
        protein = int(round(1.6 * weight))

    state["plan"]["nutrition"] = {
        "protein_g_per_day": protein,
        "plate_method": [
            "1/2 plate: vegetables/salad",
            "1/4 plate: protein",
            "1/4 plate: carbs",
            "Add healthy fats in small amounts"
        ],
        "notes": "Not medical advice. Focus on consistency: protein + fiber + sleep + steps."
    }
    return state

def plan_explanation_llm(state: State) -> State:
    p = state["profile"]
    plan = state["plan"]
    prefs = p.get("preferences", {})
    warnings = state.get("warnings", [])

    system = (
        "You are a practical fitness coach. Be concise and encouraging. "
        "No medical advice. Do not invent user details."
    )
    user = f"""
User profile:
- goal: {p['goal']}
- level: {p['level']}
- days_per_week: {p['days_per_week']}
- session_minutes: {p['session_minutes']}
- equipment: {p['equipment']}
- weight_kg: {p.get('weight_kg')}
- preferences: {prefs}

Safety warnings: {warnings}

Plan:
{plan}

Write:
1) 5 bullet points explaining why this plan fits this user.
2) 3 personalization tips aligned with equipment and time.
3) One fallback rule for missed sessions.

Keep it realistic.
"""
    plan["explanation"] = generate_text(system, user)
    state["plan"] = plan
    return state

def weekly_review_rules(state: State) -> State:
    logs = state.get("logs", [])

    if not logs:
        state["review"] = {
            "adherence": 0.0,
            "summary": "No logs yet. Log a few days to get feedback.",
            "next_week_adjustment": "Keep it simple: schedule 2–3 sessions and walk daily."
        }
        return state

    total = len(logs)
    done = sum(1 for l in logs if l.get("workout_done"))
    adherence = done / max(1, total)

    if adherence >= 0.85:
        summary = "Strong consistency. Add a small progression next week."
        adj = "Add +1 set to two exercises OR +2 reps per set."
    elif adherence >= 0.6:
        summary = "Decent consistency. Keep the plan and reduce friction."
        adj = "Pre-plan workout slots and keep sessions short and repeatable."
    else:
        summary = "Low consistency. The plan likely didn’t fit your week."
        adj = "Reduce complexity: fewer exercises and shorter sessions."

    state["review"] = {
        "adherence": round(adherence, 2),
        "summary": summary,
        "next_week_adjustment": adj
    }
    return state

def weekly_review_llm(state: State) -> State:
    logs = state.get("logs", [])
    review = state.get("review", {})

    system = (
        "You are a fitness coach writing a weekly reflection. "
        "Be specific, non-judgmental, and actionable. No medical advice. "
        "Don't invent facts not present in logs/review."
    )
    user = f"""
Deterministic review:
{review}

Logs:
{logs[-14:]}

Write:
- 3 observations based only on logs
- 2 likely friction points (if unclear, say 'possibly')
- 3 small changes for next week
- a 1–2 sentence motivational closer
"""
    state["review"]["coach_notes"] = generate_text(system, user)
    return state

def _session_title(goal: str, day: int) -> str:
    if goal == "improve_stamina":
        return "Cardio + mobility"
    return "Full body strength" if day % 2 == 1 else "Strength + conditioning"

def _template_session(goal: str, equipment: str, level: str) -> Dict[str, Any]:
    if goal == "improve_stamina":
        return {
            "warmup": "5 min easy cardio",
            "main": ["20–30 min steady cardio (zone 2)", "5–10 min mobility"],
            "cooldown": "5 min walk + breathing"
        }

    if equipment == "bodyweight":
        base = ["Squats", "Push-ups", "Glute bridge", "Plank"]
    elif equipment == "dumbbells":
        base = ["Goblet squat", "Dumbbell press", "One-arm row", "RDL", "Plank"]
    else:
        base = ["Leg press or squat", "Bench press", "Lat pulldown/row", "RDL", "Core"]

    sets = "2–3 sets" if level == "beginner" else "3–4 sets"
    reps = "8–12 reps"
    return {
        "warmup": "5–8 min mobility + light cardio",
        "main": [f"{ex}: {sets} x {reps}" for ex in base],
        "cooldown": "5 min stretch"
    }

def build_plan_graph():
    g = StateGraph(State)
    g.add_node("intake_normalizer", intake_normalizer)
    g.add_node("safety_check", safety_check)
    g.add_node("plan_workouts", plan_workouts)
    g.add_node("plan_nutrition", plan_nutrition)
    g.add_node("plan_explanation_llm", plan_explanation_llm)

    g.set_entry_point("intake_normalizer")
    g.add_edge("intake_normalizer", "safety_check")
    g.add_edge("safety_check", "plan_workouts")
    g.add_edge("plan_workouts", "plan_nutrition")
    g.add_edge("plan_nutrition", "plan_explanation_llm")
    g.add_edge("plan_explanation_llm", END)

    return g.compile()

def build_review_graph():
    g = StateGraph(State)
    g.add_node("weekly_review_rules", weekly_review_rules)
    g.add_node("weekly_review_llm", weekly_review_llm)

    g.set_entry_point("weekly_review_rules")
    g.add_edge("weekly_review_rules", "weekly_review_llm")
    g.add_edge("weekly_review_llm", END)

    return g.compile()
