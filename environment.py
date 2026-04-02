import random
from typing import Optional
from models import Observation, Action, Reward
from scenarios import SCENARIOS, get_scenario
from tasks import grade_diagnosis, calculate_reward, get_task, get_all_task_ids

# ─────────────────────────────────────────────
# What is this file?
# This is the HEART of the entire project.
# It contains the 3 core methods:
#   reset()  → start a fresh episode
#   step()   → AI takes an action, get response
#   state()  → see current situation
# ─────────────────────────────────────────────

class InternetDiagnosisEnvironment:

    def __init__(self):
        # ── These variables track the current episode ──

        self.current_scenario_name  = None  # which scenario is active
        self.current_scenario       = None  # full scenario data
        self.current_task_id        = None  # which task is active
        self.current_task           = None  # full task data

        self.steps_taken            = 0     # how many steps AI has used
        self.max_steps              = 0     # max steps allowed for this task
        self.episode_rewards        = []    # list of rewards earned so far
        self.is_done                = False # is episode over?
        self.final_score            = None  # end of episode grade

        self.action_history         = []    # all actions AI has taken

    # ─────────────────────────────────────────
    # RESET — Start a fresh episode
    # Called at the beginning of every episode
    # ─────────────────────────────────────────

    def reset(self, task_id: Optional[str] = None) -> Observation:
        """
        Starts a new episode.
        Picks a task and scenario.
        Returns the first observation (what AI sees first).
        """

        # ── Pick a task ──
        # If no task specified, pick Task 1 (easy) by default
        if task_id is None:
            task_id = "task_1_easy"

        if task_id not in get_all_task_ids():
            raise ValueError(f"Unknown task: {task_id}")

        self.current_task_id = task_id
        self.current_task    = get_task(task_id)

        # ── Pick a random scenario from this task's scenarios ──
        scenario_list             = self.current_task["scenarios"]
        self.current_scenario_name = random.choice(scenario_list)
        self.current_scenario      = get_scenario(self.current_scenario_name)

        # ── Reset all tracking variables ──
        self.steps_taken    = 0
        self.max_steps      = self.current_task["max_steps"]
        self.episode_rewards = []
        self.is_done        = False
        self.final_score    = None
        self.action_history = []

        # ── Return initial observation ──
        # This is what the AI sees at the start
        return self.current_scenario["observation"]


    # ─────────────────────────────────────────
    # STEP — AI takes an action
    # This is called every time AI makes a move
    # Returns: observation, reward, done, info
    # ─────────────────────────────────────────

    def step(self, action: Action):
        """
        Processes the AI's action.
        Returns what happened as a result.
        """

        # ── Safety check: is episode already over? ──
        if self.is_done:
            raise RuntimeError(
                "Episode is already done. Call reset() to start a new one."
            )

        # ── Safety check: has reset been called? ──
        if self.current_scenario is None:
            raise RuntimeError(
                "No active scenario. Call reset() first."
            )

        # ── Count this step ──
        self.steps_taken += 1

        # ── Save action to history ──
        self.action_history.append({
            "step"     : self.steps_taken,
            "diagnosis": action.diagnosis,
            "component": action.failing_component,
            "fix"      : action.suggested_fix,
            "confidence": action.confidence
        })

        # ── Calculate reward for this action ──
        reward = calculate_reward(action, self.current_scenario_name)
        self.episode_rewards.append(reward.value)

        # ── Check if episode should end ──
        # Episode ends if:
        # 1. AI made a definitive diagnosis (not asking for more info)
        # 2. AI used all allowed steps

        definitive_actions = [
            "diagnose_device",
            "diagnose_router",
            "diagnose_isp",
            "diagnose_dns",
            "diagnose_partial",
            "escalate_to_engineer"
        ]

        made_final_diagnosis = action.diagnosis in definitive_actions
        used_all_steps       = self.steps_taken >= self.max_steps

        if made_final_diagnosis or used_all_steps:
            self.is_done = True

            # ── Calculate final grade ──
            self.final_score = grade_diagnosis(
                action,
                self.current_scenario_name
            )

            # ── Build info dictionary ──
            info = {
                "episode_complete"  : True,
                "final_score"       : self.final_score,
                "steps_taken"       : self.steps_taken,
                "correct_diagnosis" : self.current_scenario["correct_diagnosis"],
                "correct_component" : self.current_scenario["correct_component"],
                "passed"            : self.final_score >= self.current_task["pass_score"],
                "action_history"    : self.action_history,
                "total_reward"      : round(sum(self.episode_rewards), 2)
            }

        else:
            # ── Episode still ongoing ──
            # Give AI same observation with a hint
            info = {
                "episode_complete"  : False,
                "steps_taken"       : self.steps_taken,
                "steps_remaining"   : self.max_steps - self.steps_taken,
                "hint"              : "Keep analyzing the data carefully.",
                "total_reward_so_far": round(sum(self.episode_rewards), 2)
            }

        # ── Return the 4 standard things ──
        return (
            self.current_scenario["observation"],  # what AI sees next
            reward,                                # reward for this step
            self.is_done,                          # is episode over?
            info                                   # extra information
        )


    # ─────────────────────────────────────────
    # STATE — Current snapshot of environment
    # Called anytime to inspect what's happening
    # ─────────────────────────────────────────

    def state(self):
        """
        Returns the full current state.
        Useful for debugging and inspection.
        """

        # ── If no episode is active ──
        if self.current_scenario is None:
            return {
                "status"  : "No active episode. Call reset() to start.",
                "tasks_available": get_all_task_ids()
            }

        # ── Return full current state ──
        return {
            "status"            : "Episode in progress" if not self.is_done else "Episode complete",
            "current_task"      : self.current_task_id,
            "current_scenario"  : self.current_scenario_name,
            "difficulty"        : self.current_scenario["difficulty"],
            "steps_taken"       : self.steps_taken,
            "steps_remaining"   : self.max_steps - self.steps_taken,
            "is_done"           : self.is_done,
            "final_score"       : self.final_score,
            "episode_rewards"   : self.episode_rewards,
            "action_history"    : self.action_history,
            "current_observation": self.current_scenario["observation"].model_dump()
        }
