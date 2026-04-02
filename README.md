---
title: Internet Diagnosis Env
emoji: 🌐
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
license: mit
---
```

Your README.md should now start like this:
```
---
title: Internet Diagnosis Env
emoji: 🌐
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
license: mit
---

# 🌐 Internet Outage Diagnosis Environment

An OpenEnv environment where an AI agent diagnoses
real-world internet connectivity failures.

## What is this?

This environment simulates a real-world network support
scenario. An AI agent receives network diagnostic data
(ping times, packet loss, signal strength, DNS status)
and must identify the root cause of internet outages.

This is a task humans actually do every day — network
engineers, ISP support staff, and IT helpdesks diagnose
these issues constantly.

---

## Observation Space

What the AI sees at each step:

| Field | Type | Description |
|-------|------|-------------|
| ping_to_router | float | Ping in ms, -1 means timeout |
| ping_to_isp | float | Ping in ms, -1 means timeout |
| ping_to_google | float | Ping in ms, -1 means timeout |
| packet_loss | float | 0-100%, 0 is perfect |
| signal_strength | float | dBm, closer to 0 is better |
| dns_resolution | boolean | True if DNS is working |
| connected_devices | integer | Devices on network |
| error_message | string | Optional error details |
| task_description | string | What to diagnose |

---

## Action Space

What the AI can do:

| Action | When to use |
|--------|------------|
| diagnose_device | Only one device affected |
| diagnose_router | Router unreachable, all devices fail |
| diagnose_isp | Router fine but no internet |
| diagnose_dns | Can ping IPs but websites fail |
| diagnose_partial | Multiple overlapping issues |
| request_more_info | Data too ambiguous |
| escalate_to_engineer | Needs physical inspection |

Along with:
- `failing_component` — what specifically is broken
- `suggested_fix` — how to fix it
- `confidence` — how sure the AI is (0.0 to 1.0)

---

## Tasks

### Task 1 — Easy: Single Point Failure
- 2 scenarios with one obvious failure
- Max 3 steps per episode
- Pass score: 0.6

### Task 2 — Medium: Multi-Layer Diagnosis
- 2 scenarios requiring careful analysis
- Max 5 steps per episode
- Pass score: 0.5

### Task 3 — Hard: Complex Intermittent Failure
- 2 scenarios with overlapping issues
- Max 7 steps per episode
- Pass score: 0.4

---

## Reward Function

| Situation | Reward |
|-----------|--------|
| Correct diagnosis | +1.0 |
| Right component, wrong category | +0.4 |
| Smart request for more info | +0.3 |
| Unnecessary escalation | -0.1 |
| Wrong diagnosis | -0.3 |
| High confidence on correct answer | +0.1 bonus |

---

## Baseline Scores

Running `baseline.py` with `llama-3.1-8b-instant` via Groq:

| Task | Score |
|------|-------|
| Task 1 (Easy) | 1.0 |
| Task 2 (Medium) | 0.85 |
| Task 3 (Hard) | 0.15 |
| **Average** | **0.67** |

---

## Setup Instructions

### Option 1 — Run Locally

**Step 1 — Install dependencies:**
```bash
pip install -r requirements.txt
```

**Step 2 — Start the server:**
```bash
python server.py
```

**Step 3 — Run baseline:**
```bash
export GROQ_API_KEY=your-key-here
python baseline.py
```

**Step 4 — Visit interactive docs:**
```
http://127.0.0.1:7860/docs
```

### Option 2 — Run with Docker

**Step 1 — Build:**
```bash
docker build -t internet-diagnosis-env .
```

**Step 2 — Run:**
```bash
docker run -p 7860:7860 internet-diagnosis-env
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| / | GET | Health check |
| /reset | POST | Start new episode |
| /step | POST | Submit diagnosis |
| /state | GET | Current state |
| /tasks | GET | List all tasks |

---

## Project Structure
```
internet-diagnosis-env/
├── models.py        # Pydantic data models
├── scenarios.py     # Network failure scenarios
├── tasks.py         # Tasks and graders
├── environment.py   # Core step/reset/state logic
├── server.py        # FastAPI server
├── baseline.py      # Baseline inference script
├── openenv.yaml     # OpenEnv metadata
├── Dockerfile       # Container setup
├── requirements.txt # Dependencies
└── README.md        # This file
```
```

