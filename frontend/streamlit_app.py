import os
import json
import requests
import streamlit as st
from dotenv import load_dotenv
from datetime import date

load_dotenv()

DEFAULT_API = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")

st.set_page_config(page_title="Fitness Coach Agent", page_icon="💪", layout="centered")

st.title("💪 Fitness Coach Agent")
st.caption("LangGraph + FastAPI + Groq. A UI so you don’t have to curl like it’s 1999.")

# Sidebar
st.sidebar.header("Backend")
api_base = st.sidebar.text_input("API Base URL", value=DEFAULT_API).rstrip("/")

st.sidebar.markdown("---")
st.sidebar.write("Available endpoints:")
st.sidebar.code("/plan (POST)\n/log (POST)\n/review (GET)")

# Helpers
def pretty(obj) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False)

def post_json(path: str, payload: dict, params: dict | None = None):
    url = f"{api_base}{path}"
    return requests.post(url, params=params, json=payload, timeout=60)

def get_json(path: str, params: dict | None = None):
    url = f"{api_base}{path}"
    return requests.get(url, params=params, timeout=60)

tabs = st.tabs(["🧠 Create Plan", "📅 Log Day", "📊 Weekly Review"])

# -------------------------
# TAB 1: CREATE PLAN
# -------------------------
with tabs[0]:
    st.subheader("Create a training plan")

    with st.form("plan_form"):
        name = st.text_input("Name", value="khushal")

        # IMPORTANT: match backend schema enums exactly
        goal = st.selectbox("Goal", ["lose_fat", "build_muscle", "improve_stamina"], index=0)
        level = st.selectbox("Level", ["beginner", "intermediate"], index=0)
        equipment = st.selectbox("Equipment", ["bodyweight", "dumbbells", "gym"], index=0)

        days_per_week = st.slider("Days per week", 1, 7, 3)
        session_minutes = st.slider("Session length (minutes)", 15, 180, 45, step=5)

        weight_kg = st.number_input(
            "Weight (kg) (optional)", min_value=0.0, max_value=250.0, value=0.0, step=0.5
        )

        injuries = st.text_input("Injuries / limitations (optional)", value="")
        pref_notes = st.text_area("Preferences (optional)", value="")

        submitted = st.form_submit_button("Generate Plan")

    if submitted:
        # preferences must be Dict[str, str] (no None)
        prefs: dict[str, str] = {}
        if injuries.strip():
            prefs["injuries"] = injuries.strip()
        if pref_notes.strip():
            prefs["notes"] = pref_notes.strip()

        profile = {
            "name": name.strip() or "User",
            "goal": goal,
            "level": level,
            "days_per_week": int(days_per_week),
            "session_minutes": int(session_minutes),
            "equipment": equipment,
            "weight_kg": None if weight_kg == 0.0 else float(weight_kg),
            "preferences": prefs,
        }

try:
    with st.spinner("Generating plan..."):
        r = post_json("/plan", profile)

    if r.status_code == 200:
        data = r.json()
        st.success("Plan generated ✅")

        #st.markdown("### Plan")
        #st.code(pretty(data.get("plan", {})), language="json")
        plan = data.get("plan", {})

        st.markdown("## 🏋️ Your Training Plan")

        if "week" in plan:
            for day in plan["week"]:
                st.markdown(f"### {day.get('day', 'Workout Day')}")
                st.write(day.get("workout", ""))

        if "explanation" in plan:
            st.markdown("### Why this works")
            st.write(plan["explanation"])

        warnings = data.get("warnings", [])
        if warnings:
            st.warning("Warnings")
            st.code(pretty(warnings), language="json")

        with st.expander("Full response JSON"):
            st.code(pretty(data), language="json")

    else:
        st.error(f"Backend error: {r.status_code}")
        st.code(r.text)

except Exception as e:
    st.error("Request failed")
    st.code(str(e))

# -------------------------
# TAB 2: LOG DAY
# -------------------------
with tabs[1]:
    st.subheader("Log a day")

    with st.form("log_form"):
        profile_name = st.text_input("Profile name", value="khushal")
        log_date = st.date_input("Date", value=date.today())
        workout_done = st.checkbox("Workout done", value=True)

        steps = st.number_input("Steps (optional)", min_value=0, max_value=200000, value=0, step=500)
        weight = st.number_input("Weight (kg) (optional)", min_value=0.0, max_value=250.0, value=0.0, step=0.1)
        notes = st.text_area("Notes (optional)", value="")

        submitted = st.form_submit_button("Save Log")

    if submitted:
        payload = {
            "date": str(log_date),
            "workout_done": bool(workout_done),
            "steps": None if int(steps) == 0 else int(steps),
            "weight_kg": None if float(weight) == 0.0 else float(weight),
            "notes": notes.strip(),
        }

        try:
            with st.spinner("Saving log..."):
                r = post_json("/log", payload, params={"profile_name": profile_name.strip() or "User"})

            if r.status_code == 200:
                st.success("Log saved ✅")
                st.code(pretty(r.json()), language="json")
            else:
                st.error(f"Backend error: {r.status_code}")
                st.code(r.text)

        except Exception as e:
            st.error("Request failed")
            st.code(str(e))

# -------------------------
# TAB 3: WEEKLY REVIEW
# -------------------------
with tabs[2]:
    st.subheader("Weekly review")

    profile_name = st.text_input("Profile name for review", value="khushal", key="review_profile")

    if st.button("Get Review"):
        try:
            with st.spinner("Reviewing..."):
                r = get_json("/review", params={"profile_name": profile_name.strip() or "User"})

            if r.status_code == 200:
                data = r.json()
                st.success("Review ready ✅")

                st.markdown("### Summary")
                st.write(data.get("summary", ""))

                st.markdown("### Adherence")
                st.write(data.get("adherence", ""))

                st.markdown("### Next Week Adjustment")
                st.write(data.get("next_week_adjustment", ""))

                coach_notes = data.get("coach_notes", "")
                if coach_notes:
                    st.markdown("### Coach Notes")
                    st.write(coach_notes)

                with st.expander("Full response JSON"):
                    st.code(pretty(data), language="json")

            else:
                st.error(f"Backend error: {r.status_code}")
                st.code(r.text)

        except Exception as e:
            st.error("Request failed")
            st.code(str(e))
