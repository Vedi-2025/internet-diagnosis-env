from models import Observation

# This file contains all the network situations
# (scenarios) that the AI will be given to diagnose.
# Think of these as "exam questions" for the AI.

SCENARIOS = {

    # EASY SCENARIOS (Task 1)
    # One clear, obvious failure point

    "easy_router_failure": {
        "observation": Observation(
            ping_to_router    = -1,       # timeout — router dead
            ping_to_isp       = -1,       # can't reach ISP either
            ping_to_google    = -1,       # no internet at all
            packet_loss       = 100,      # 100% packet loss
            signal_strength   = -40,      # WiFi signal itself is fine
            dns_resolution    = False,    # DNS not working
            connected_devices = 0,        # no devices connected
            error_message     = "Router not responding to ping",
            task_description  = (
                "A customer reports complete internet outage. "
                "Their WiFi signal appears fine but nothing loads. "
                "Diagnose the root cause."
            )
        ),
        "correct_diagnosis" : "diagnose_router",
        "correct_component" : "router",
        "difficulty"        : "easy"
    },

    "easy_device_failure": {
        "observation": Observation(
            ping_to_router    = 1,        # router perfectly fine
            ping_to_isp       = 15,       # ISP perfectly fine
            ping_to_google    = 20,       # internet working fine
            packet_loss       = 0,        # no packet loss at all
            signal_strength   = -45,      # strong signal
            dns_resolution    = True,     # DNS working
            connected_devices = 4,        # other devices work fine
            error_message     = "Only one device cannot connect",
            task_description  = (
                "A customer says internet is not working on their laptop. "
                "All other devices in the house work fine. "
                "Diagnose the root cause."
            )
        ),
        "correct_diagnosis" : "diagnose_device",
        "correct_component" : "device",
        "difficulty"        : "easy"
    },

    # MEDIUM SCENARIOS (Task 2)
    # Requires reading data carefully

    "medium_dns_failure": {
        "observation": Observation(
            ping_to_router    = 2,        # router fine
            ping_to_isp       = 30,       # ISP fine
            ping_to_google    = -1,       # can't reach google by name
            packet_loss       = 5,        # slight packet loss
            signal_strength   = -60,      # decent signal
            dns_resolution    = False,    # DNS specifically failing
            connected_devices = 3,
            error_message     = "DNS lookup failed for all domains",
            task_description  = (
                "Customer can't open any websites but their "
                "connection seems active. Router and ISP appear "
                "reachable. Diagnose the root cause."
            )
        ),
        "correct_diagnosis" : "diagnose_dns",
        "correct_component" : "DNS server",
        "difficulty"        : "medium"
    },

    "medium_isp_failure": {
        "observation": Observation(
            ping_to_router    = 3,        # router perfectly fine
            ping_to_isp       = -1,       # ISP not reachable
            ping_to_google    = -1,       # internet dead
            packet_loss       = 95,       # almost total packet loss
            signal_strength   = -55,      # good signal
            dns_resolution    = False,
            connected_devices = 5,        # all devices affected
            error_message     = "No route to ISP gateway",
            task_description  = (
                "All devices in the house lost internet suddenly. "
                "Router is working and WiFi is connected but "
                "nothing loads. Diagnose the root cause."
            )
        ),
        "correct_diagnosis" : "diagnose_isp",
        "correct_component" : "ISP connection",
        "difficulty"        : "medium"
    },

    # HARD SCENARIOS (Task 3)
    # Multiple overlapping issues
    # Misleading data

    "hard_partial_failure": {
        "observation": Observation(
            ping_to_router    = 180,      # very high — router struggling
            ping_to_isp       = 750,      # extremely high
            ping_to_google    = 900,      # barely alive
            packet_loss       = 38,       # significant loss
            signal_strength   = -81,      # weak WiFi signal
            dns_resolution    = True,     # DNS technically works
            connected_devices = 8,        # many devices — congestion?
            error_message     = "Intermittent connectivity on all devices",
            task_description  = (
                "Customer says internet works sometimes but is very slow "
                "and keeps dropping. Issue started in the evening. "
                "Multiple devices affected. Diagnose the root cause."
            )
        ),
        "correct_diagnosis" : "diagnose_partial",
        "correct_component" : "weak WiFi signal + ISP congestion",
        "difficulty"        : "hard"
    },

    "hard_escalate": {
        "observation": Observation(
            ping_to_router    = 45,       # slightly high
            ping_to_isp       = 200,      # high
            ping_to_google    = 300,      # high but works
            packet_loss       = 22,       # moderate loss
            signal_strength   = -70,      # borderline signal
            dns_resolution    = True,     # DNS works
            connected_devices = 2,
            error_message     = "Packet loss varies between 10-40% randomly",
            task_description  = (
                "Customer has had degraded internet for 3 days. "
                "Issue is random — sometimes fine, sometimes terrible. "
                "ISP already restarted connection remotely with no fix. "
                "Diagnose and recommend next steps."
            )
        ),
        "correct_diagnosis" : "escalate_to_engineer",
        "correct_component" : "unknown — requires physical inspection",
        "difficulty"        : "hard"
    }
}


# Helper function to get a scenario by name

def get_scenario(name: str):
    """
    Takes a scenario name like "easy_router_failure"
    Returns the full scenario dictionary
    """
    if name not in SCENARIOS:
        raise ValueError(f"Scenario '{name}' not found.")
    return SCENARIOS[name]


# Helper to get all scenarios of one difficulty

def get_scenarios_by_difficulty(difficulty: str):
    """
    Takes "easy", "medium", or "hard"
    Returns list of matching scenario names
    """
    return [
        name for name, data in SCENARIOS.items()
        if data["difficulty"] == difficulty
    ]