from pydantic import BaseModel
from typing import Optional
from enum import Enum

# ─────────────────────────────────────────────
# PART 1: The possible diagnoses AI can make
# ─────────────────────────────────────────────

class DiagnosisType(str, Enum):
    DEVICE     = "diagnose_device"      # Problem in user's device
    ROUTER     = "diagnose_router"      # Problem in router
    ISP        = "diagnose_isp"         # Problem at ISP level
    DNS        = "diagnose_dns"         # DNS failure
    PARTIAL    = "diagnose_partial"     # Multiple issues
    MORE_INFO  = "request_more_info"    # Need more data
    ESCALATE   = "escalate_to_engineer" # Too complex

# ─────────────────────────────────────────────
# PART 2: What the AI SEES (network diagnostics)
# ─────────────────────────────────────────────

class Observation(BaseModel):
    # Ping times in milliseconds (-1 means timeout/unreachable)
    ping_to_router  : float
    ping_to_isp     : float
    ping_to_google  : float

    # Packet loss percentage (0 to 100)
    packet_loss     : float

    # WiFi signal strength in dBm (closer to 0 is better)
    # Example: -40 is excellent, -80 is weak, -90 is dead
    signal_strength : float

    # DNS working or not
    dns_resolution  : bool

    # How many devices are connected to router
    connected_devices : int

    # Any error message from the network
    error_message   : Optional[str] = None

    # Task description shown to AI
    task_description : str

# ─────────────────────────────────────────────
# PART 3: What the AI DOES (its action)
# ─────────────────────────────────────────────

class Action(BaseModel):
    # The diagnosis the AI makes
    diagnosis       : DiagnosisType

    # Which part it thinks is failing
    # Example: "router", "ISP", "DNS server"
    failing_component : str

    # What fix it suggests
    # Example: "Restart the router", "Call ISP", "Change DNS to 8.8.8.8"
    suggested_fix   : str

    # How confident the AI is (0.0 to 1.0)
    confidence      : float

# ─────────────────────────────────────────────
# PART 4: The reward after each action
# ─────────────────────────────────────────────

class Reward(BaseModel):
    # The score for this step (-1.0 to +1.0)
    value           : float

    # Reason for the score
    reason          : str