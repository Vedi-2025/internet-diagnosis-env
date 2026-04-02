from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import Action
from environment import InternetDiagnosisEnvironment
from tasks import get_all_task_ids

# ─────────────────────────────────────────────
# What is this file?
# This is the FRONT DOOR of your environment.
# It turns your Python code into a web API.
# Judges, AI agents, and validators will
# talk to your environment through this file.
# ─────────────────────────────────────────────

# ── Create the FastAPI app ──
app = FastAPI(
    title       = "Internet Outage Diagnosis Environment",
    description = (
        "An OpenEnv environment where an AI agent diagnoses "
        "real-world internet connectivity failures. "
        "The agent observes network diagnostic data and must "
        "identify the root cause of the outage."
    ),
    version     = "1.0.0"
)

# ── Allow all origins (needed for HuggingFace) ──
app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)

# ── Create one environment instance ──
env = InternetDiagnosisEnvironment()


# ─────────────────────────────────────────────
# ROUTE 1: Health Check
# Judges ping this first to check if server works
# ─────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "status"     : "ok",
        "environment": "Internet Outage Diagnosis",
        "version"    : "1.0.0",
        "endpoints"  : ["/reset", "/step", "/state", "/tasks"]
    }


# ─────────────────────────────────────────────
# ROUTE 2: Reset
# Starts a fresh episode
# ─────────────────────────────────────────────

@app.post("/reset")
def reset(task_id: str = "task_1_easy"):
    """
    Starts a new episode.
    Returns the first observation (network diagnostic data).

    task_id options:
    - task_1_easy
    - task_2_medium
    - task_3_hard
    """
    try:
        observation = env.reset(task_id=task_id)
        return {
            "observation" : observation.model_dump(),
            "task_id"     : task_id,
            "message"     : "Episode started. Analyze the network data and diagnose."
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ─────────────────────────────────────────────
# ROUTE 3: Step
# AI submits its action/diagnosis
# ─────────────────────────────────────────────

@app.post("/step")
def step(action: Action):
    """
    AI submits its diagnosis.
    Returns: observation, reward, done, info.

    Example action:
    {
        "diagnosis"         : "diagnose_router",
        "failing_component" : "router",
        "suggested_fix"     : "Restart the router",
        "confidence"        : 0.9
    }
    """
    try:
        observation, reward, done, info = env.step(action)
        return {
            "observation" : observation.model_dump(),
            "reward"      : reward.model_dump(),
            "done"        : done,
            "info"        : info
        }
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ─────────────────────────────────────────────
# ROUTE 4: State
# Returns current state of environment
# ─────────────────────────────────────────────

@app.get("/state")
def state():
    """
    Returns the full current state of the environment.
    Useful for debugging and inspection.
    """
    return env.state()


# ─────────────────────────────────────────────
# ROUTE 5: Tasks
# Lists all available tasks
# ─────────────────────────────────────────────

@app.get("/tasks")
def tasks():
    """
    Lists all available tasks with descriptions.
    """
    from tasks import TASKS
    return {
        "total_tasks" : len(TASKS),
        "tasks"       : {
            task_id: {
                "name"       : task["name"],
                "description": task["description"],
                "difficulty" : task["difficulty"],
                "max_steps"  : task["max_steps"],
                "pass_score" : task["pass_score"],
                "scenarios"  : task["scenarios"]
            }
            for task_id, task in TASKS.items()
        }
    }


# ─────────────────────────────────────────────
# Run the server
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)