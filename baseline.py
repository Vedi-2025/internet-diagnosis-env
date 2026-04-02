import os
import json
import requests
from groq import Groq

# ─────────────────────────────────────────────
# What is this file?
# This script runs an AI agent (using OpenAI)
# against your environment automatically.
# It tests all 3 tasks and produces scores.
# Judges use this to verify your environment works.
# ─────────────────────────────────────────────

# ── Setup ──
BASE_URL = "https://Vedi23-internet-diagnosis-env.hf.space"  # your environment server
client   = Groq(
    api_key = os.environ.get("GROQ_API_KEY", "your-groq-key-here")
)

# ─────────────────────────────────────────────
# SYSTEM PROMPT
# This tells the AI what its job is
# ─────────────────────────────────────────────

SYSTEM_PROMPT = """
You are an expert network engineer AI agent.
You will be given network diagnostic data and must diagnose 
the root cause of internet connectivity issues.

You must respond ONLY with a valid JSON object in this exact format:
{
    "diagnosis": "<one of: diagnose_device, diagnose_router, diagnose_isp, diagnose_dns, diagnose_partial, request_more_info, escalate_to_engineer>",
    "failing_component": "<what specifically is failing>",
    "suggested_fix": "<what should be done to fix it>",
    "confidence": <a number between 0.0 and 1.0>
}

Rules for diagnosis:
- diagnose_device    → only one device affected, rest work fine
- diagnose_router    → router unreachable, all devices affected
- diagnose_isp       → router fine but no internet, all devices affected
- diagnose_dns       → can ping IPs but DNS resolution fails
- diagnose_partial   → multiple overlapping issues detected
- request_more_info  → data is genuinely too ambiguous to diagnose
- escalate_to_engineer → complex issue needing physical inspection

Key data points to analyze:
- ping_to_router   : -1 means timeout (unreachable)
- ping_to_isp      : -1 means ISP unreachable
- ping_to_google   : -1 means no internet
- packet_loss      : 0 is perfect, 100 is complete outage
- signal_strength  : closer to 0 is better (-40 good, -80 weak)
- dns_resolution   : true means DNS works, false means DNS failed
- connected_devices: how many devices are on the network

Respond ONLY with the JSON. No explanation. No markdown.
"""


# ─────────────────────────────────────────────
# HELPER: Call your environment server
# ─────────────────────────────────────────────

def reset_environment(task_id: str):
    """Starts a new episode for the given task"""
    response = requests.post(
        f"{BASE_URL}/reset",
        params={"task_id": task_id}
    )
    return response.json()


def step_environment(action: dict):
    """Submits AI's action to the environment"""
    response = requests.post(
        f"{BASE_URL}/step",
        json=action
    )
    return response.json()


def get_state():
    """Gets current environment state"""
    response = requests.get(f"{BASE_URL}/state")
    return response.json()


# ─────────────────────────────────────────────
# HELPER: Ask OpenAI to diagnose
# ─────────────────────────────────────────────

def get_ai_diagnosis(observation: dict) -> dict:
    """
    Sends network data to OpenAI.
    Gets back a diagnosis as JSON.
    """

    # Format the observation nicely for the AI
    observation_text = f"""
Network Diagnostic Report:
─────────────────────────
Ping to Router  : {observation['ping_to_router']} ms (-1 = timeout)
Ping to ISP     : {observation['ping_to_isp']} ms (-1 = timeout)
Ping to Google  : {observation['ping_to_google']} ms (-1 = timeout)
Packet Loss     : {observation['packet_loss']}%
Signal Strength : {observation['signal_strength']} dBm
DNS Resolution  : {observation['dns_resolution']}
Connected Devices: {observation['connected_devices']}
Error Message   : {observation.get('error_message', 'None')}

Task: {observation['task_description']}
"""

    # Ask OpenAI
    response = client.chat.completions.create(
        model    = "llama-3.1-8b-instant",
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": observation_text}
        ],
        temperature = 0.1   # low temperature = more consistent answers
    )

    # Parse the JSON response
    raw_text = response.choices[0].message.content.strip()

    try:
        action = json.loads(raw_text)
        return action
    except json.JSONDecodeError:
        # If AI didn't return valid JSON, use safe default
        print(f"   ⚠ AI returned invalid JSON: {raw_text}")
        return {
            "diagnosis"         : "request_more_info",
            "failing_component" : "unknown",
            "suggested_fix"     : "Need more information",
            "confidence"        : 0.1
        }


# ─────────────────────────────────────────────
# RUN ONE TASK
# Resets environment, gets AI diagnosis, scores
# ─────────────────────────────────────────────

def run_task(task_id: str) -> float:
    """
    Runs the AI agent on one full task.
    Returns the final score (0.0 to 1.0)
    """

    print(f"\n{'='*50}")
    print(f"  TASK: {task_id}")
    print(f"{'='*50}")

    # ── Start episode ──
    reset_data  = reset_environment(task_id)
    observation = reset_data["observation"]

    print(f"\n  Scenario loaded.")
    print(f"  Task description: {observation['task_description']}")
    print(f"\n  Network Data:")
    print(f"    Ping to Router  : {observation['ping_to_router']} ms")
    print(f"    Ping to ISP     : {observation['ping_to_isp']} ms")
    print(f"    Ping to Google  : {observation['ping_to_google']} ms")
    print(f"    Packet Loss     : {observation['packet_loss']}%")
    print(f"    Signal Strength : {observation['signal_strength']} dBm")
    print(f"    DNS Resolution  : {observation['dns_resolution']}")
    print(f"    Error Message   : {observation.get('error_message')}")

    # ── Get AI diagnosis ──
    print(f"\n  Asking AI to diagnose...")
    action = get_ai_diagnosis(observation)

    print(f"\n  AI Diagnosis:")
    print(f"    Diagnosis        : {action['diagnosis']}")
    print(f"    Failing Component: {action['failing_component']}")
    print(f"    Suggested Fix    : {action['suggested_fix']}")
    print(f"    Confidence       : {action['confidence']}")

    # ── Submit to environment ──
    result = step_environment(action)

    # ── Show results ──
    print(f"\n  Results:")
    print(f"    Reward          : {result['reward']['value']}")
    print(f"    Reward Reason   : {result['reward']['reason']}")
    print(f"    Episode Done    : {result['done']}")

    if result['done'] and 'final_score' in result['info']:
        score  = result['info']['final_score']
        passed = result['info']['passed']
        correct_diagnosis  = result['info']['correct_diagnosis']
        correct_component  = result['info']['correct_component']

        print(f"    Final Score     : {score}")
        print(f"    Passed          : {passed}")
        print(f"    Correct Answer  : {correct_diagnosis} ({correct_component})")
        return score

    return 0.0


# ─────────────────────────────────────────────
# MAIN — Run all 3 tasks
# ─────────────────────────────────────────────

def main():
    print("\n" + "="*50)
    print("  INTERNET DIAGNOSIS ENV — BASELINE SCRIPT")
    print("="*50)
    print("  Running AI agent across all 3 tasks...")

    tasks  = ["task_1_easy", "task_2_medium", "task_3_hard"]
    scores = []

    for task_id in tasks:
        try:
            score = run_task(task_id)
            scores.append(score)
        except Exception as e:
            print(f"\n   ERROR on {task_id}: {e}")
            scores.append(0.0)

    # ── Final Summary ──
    print(f"\n{'='*50}")
    print(f"  FINAL RESULTS")
    print(f"{'='*50}")
    print(f"  Task 1 (Easy)   : {scores[0]}")
    print(f"  Task 2 (Medium) : {scores[1]}")
    print(f"  Task 3 (Hard)   : {scores[2]}")
    print(f"  Average Score   : {round(sum(scores)/len(scores), 2)}")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    main()
