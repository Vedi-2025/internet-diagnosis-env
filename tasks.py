from models import Observation, Action, Reward
from scenarios import get_scenarios_by_difficulty, get_scenario, SCENARIOS

# ─────────────────────────────────────────────
# What is this file?
# This file defines the 3 tasks the AI must solve
# and the GRADERS that score the AI's performance
# Think of graders as "answer keys" for each task
# ─────────────────────────────────────────────


# ─────────────────────────────────────────────
# THE GRADER FUNCTION
# This is the most important function here
# It takes what the AI did and scores it 0.0-1.0
# ─────────────────────────────────────────────

def grade_diagnosis(action: Action, scenario_name: str) -> float:
    """
    Compares AI's diagnosis against the correct answer.
    Returns a score between 0.0 and 1.0

    0.0 = completely wrong
    0.5 = partially correct
    1.0 = perfect diagnosis
    """

    # Get the correct answer for this scenario
    scenario = get_scenario(scenario_name)
    correct_diagnosis  = scenario["correct_diagnosis"]
    correct_component  = scenario["correct_component"]

    score = 0.0

    # ── Check 1: Is the diagnosis type correct? ──
    # This is worth 60% of the score
    if action.diagnosis == correct_diagnosis:
        score += 0.6
    elif action.diagnosis == "request_more_info":
        # Asking for more info is acceptable but not perfect
        score += 0.2
    elif action.diagnosis == "escalate_to_engineer":
        # Escalating is safe but not ideal for simple cases
        difficulty = scenario["difficulty"]
        if difficulty == "hard":
            score += 0.3   # reasonable for hard cases
        else:
            score += 0.1   # unnecessary for easy/medium cases

    # ── Check 2: Is the failing component correct? ──
    # This is worth 25% of the score
    if correct_component.lower() in action.failing_component.lower():
        score += 0.25
    # Partial match — at least mentioned the right area
    elif any(
        word in action.failing_component.lower()
        for word in correct_component.lower().split()
    ):
        score += 0.1

    # ── Check 3: Did they suggest a reasonable fix? ──
    # This is worth 15% of the score
    # We check if the fix makes sense for the diagnosis
    fix_keywords = {
        "diagnose_router"  : ["restart", "router", "reboot", "reset"],
        "diagnose_device"  : ["device", "restart", "driver", "settings"],
        "diagnose_isp"     : ["isp", "provider", "call", "contact", "line"],
        "diagnose_dns"     : ["dns", "8.8.8.8", "1.1.1.1", "nameserver"],
        "diagnose_partial" : ["signal", "congestion", "interference", "devices"],
        "escalate_to_engineer": ["engineer", "technician", "physical", "inspect"],
        "request_more_info": ["more", "additional", "information", "data"]
    }

    expected_keywords = fix_keywords.get(correct_diagnosis, [])
    fix_lower = action.suggested_fix.lower()

    if any(keyword in fix_lower for keyword in expected_keywords):
        score += 0.15

    # Round to 2 decimal places and cap at 1.0
    return min(round(score, 2), 1.0)


# ─────────────────────────────────────────────
# THE REWARD FUNCTION
# Called after EVERY step during an episode
# Gives live feedback (not just end score)
# ─────────────────────────────────────────────

def calculate_reward(action: Action, scenario_name: str) -> Reward:
    """
    Gives a reward after each action.
    This runs DURING the episode, not just at end.
    """

    scenario           = get_scenario(scenario_name)
    correct_diagnosis  = scenario["correct_diagnosis"]
    observation        = scenario["observation"]

    value  = 0.0
    reason = ""

    # ── Perfect diagnosis ──
    if action.diagnosis == correct_diagnosis:
        value  = 1.0
        reason = "Correct diagnosis! Well done."

    # ── Correct component but wrong diagnosis type ──
    elif scenario["correct_component"].lower() in action.failing_component.lower():
        value  = 0.4
        reason = "Identified the right component but wrong diagnosis category."

    # ── Asking for more info ──
    elif action.diagnosis == "request_more_info":
        # Reward more for asking when data is genuinely ambiguous
        if observation.packet_loss > 20 and observation.packet_loss < 60:
            value  = 0.3
            reason = "Smart to ask for more info — situation is ambiguous."
        else:
            value  = 0.1
            reason = "Asked for more info but data was clear enough to diagnose."

    # ── Escalating to engineer ──
    elif action.diagnosis == "escalate_to_engineer":
        if scenario["difficulty"] == "hard":
            value  = 0.5
            reason = "Reasonable to escalate — this is a complex case."
        else:
            value  = -0.1
            reason = "Unnecessary escalation — this could be diagnosed directly."

    # ── Completely wrong diagnosis ──
    else:
        value  = -0.3
        reason = "Incorrect diagnosis. Review the network data carefully."

    # ── Penalty: very low confidence on correct answer ──
    if action.diagnosis == correct_diagnosis and action.confidence < 0.3:
        value  -= 0.1
        reason += " (confidence was very low despite correct answer)"

    # ── Bonus: high confidence on correct answer ──
    if action.diagnosis == correct_diagnosis and action.confidence > 0.8:
        value  += 0.1
        reason += " (bonus for high confidence on correct answer)"

    # Cap value between -1.0 and 1.0
    value = max(-1.0, min(1.0, round(value, 2)))

    return Reward(value=value, reason=reason)


# ─────────────────────────────────────────────
# THE 3 TASKS
# Each task is a dictionary describing:
# - what the task is
# - which scenarios to use
# - difficulty level
# ─────────────────────────────────────────────

TASKS = {

    # ── TASK 1: EASY ──
    "task_1_easy": {
        "name"       : "Single Point Failure Diagnosis",
        "description": (
            "Diagnose simple, single-point network failures. "
            "The data will clearly point to one failing component. "
            "Expected difficulty: Easy."
        ),
        "scenarios"  : get_scenarios_by_difficulty("easy"),
        "difficulty" : "easy",
        "max_steps"  : 3,       # AI gets 3 chances per scenario
        "pass_score" : 0.6,     # Must score above 0.6 to pass
    },

    # ── TASK 2: MEDIUM ──
    "task_2_medium": {
        "name"       : "Multi-Layer Network Diagnosis",
        "description": (
            "Diagnose failures that require reading multiple data points. "
            "Some signals may be misleading. "
            "Expected difficulty: Medium."
        ),
        "scenarios"  : get_scenarios_by_difficulty("medium"),
        "difficulty" : "medium",
        "max_steps"  : 5,
        "pass_score" : 0.5,
    },

    # ── TASK 3: HARD ──
    "task_3_hard": {
        "name"       : "Complex Intermittent Failure Diagnosis",
        "description": (
            "Diagnose complex failures with overlapping issues, "
            "misleading data, and no single clear cause. "
            "Expected difficulty: Hard."
        ),
        "scenarios"  : get_scenarios_by_difficulty("hard"),
        "difficulty" : "hard",
        "max_steps"  : 7,
        "pass_score" : 0.4,
    }
}


# ─────────────────────────────────────────────
# Helper: get a task by its ID
# ─────────────────────────────────────────────

def get_task(task_id: str):
    if task_id not in TASKS:
        raise ValueError(f"Task '{task_id}' not found.")
    return TASKS[task_id]


# ─────────────────────────────────────────────
# Helper: get all task IDs
# ─────────────────────────────────────────────

def get_all_task_ids():
    return list(TASKS.keys())
