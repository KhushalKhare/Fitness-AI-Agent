

#  Fitness AI Agent (LangGraph + FastAPI + Streamlit)

An agent-based fitness assistant that generates personalized workout and nutrition plans using LangGraph for workflow orchestration and Groq as the LLM provider.

This project demonstrates production-style AI agent architecture with backend–frontend separation and modular state-driven logic.

---

##  Tech Stack

* Python
* LangGraph
* FastAPI
* Streamlit
* Groq LLM API
* Pydantic
* Uvicorn

---

##  Architecture

User → Streamlit UI → FastAPI → LangGraph Graph → Tools → Groq LLM → Response

### Backend Responsibilities

* Agent graph definition (`graph.py`)
* LLM integration (`llm.py`)
* API routing (`main.py`)
* Request/response models (`schemas.py`)
* Lightweight storage (`storage.py`)

### Frontend Responsibilities

* User interaction and plan visualization (`streamlit_app.py`)

---

##  Project Structure

```
FITNESS AGENT LANGGRAPH/
│
├── backend/
│   └── app/
│       ├── graph.py
│       ├── llm.py
│       ├── main.py
│       ├── schemas.py
│       ├── storage.py
│       └── __init__.py
│
├── frontend/
│   ├── streamlit_app.py
│   └── requirements.txt
│
├── fitness_agent.db
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

##  Setup Instructions

### 1️ Create virtual environment

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Mac/Linux:

```bash
source .venv/bin/activate
```

---

### 2️ Install backend dependencies

```bash
pip install -r requirements.txt
```

If frontend has separate dependencies:

```bash
pip install -r frontend/requirements.txt
```

---

### 3️ Configure Environment Variables

Copy `.env.example`:

```bash
copy .env.example .env
```

Add your Groq key:

```
GROQ_API_KEY=your_api_key_here
```

⚠ `.env` is ignored by git.

---

##  Running the Application

### Start FastAPI backend

From project root:

```bash
uvicorn backend.app.main:app --reload
```

API will run at:

```
http://127.0.0.1:8000
```

---

### Start Streamlit frontend

In a new terminal:

```bash
streamlit run frontend/streamlit_app.py
```

Frontend runs at:

```
http://localhost:8501
```

---

##  Agent Workflow

1. User submits fitness goal
2. FastAPI validates input via Pydantic schemas
3. LangGraph builds state machine
4. Agent decides:

   * Generate workout plan
   * Generate nutrition guidance
   * Store / retrieve session data
5. Groq LLM produces structured output
6. Response is returned to frontend

This architecture avoids simple prompt chaining and instead uses state-driven agent logic.

---

##  Storage

* SQLite database (`fitness_agent.db`)
* Lightweight session storage via `storage.py`
* Easily extendable to Postgres or cloud DB

---

##  Why This Project

Demonstrates:

* Agent-based AI workflows
* Modular backend design
* LLM tool integration
* State graph orchestration
* Full-stack AI application structure

Designed as a portfolio-ready demonstration of applied agent engineering.

---

##  Future Improvements

* Persistent user profiles
* Multi-agent coordination
* Progress tracking analytics
* Docker containerization
* Deployment to cloud


