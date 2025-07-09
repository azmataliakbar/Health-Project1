from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import pandas as pd

# -------------------- UserSessionContext Class --------------------
class UserSessionContext(BaseModel):
    """
    ✅ Shared user session context to hold state across tools and agents.
    - Acts like memory for one user session.
    - Stores personal goals, preferences, history, logs, and agent tracking.
    """
    # 🔹 Basic user identification
    name: str        # User's name
    uid: int         # Unique user ID

    # 🔹 Health goals and plans
    goal: Optional[Dict[str, Any]] = None          # User's health goal (parsed from input)
    diet_preferences: Optional[str] = None         # User's dietary preferences (e.g., vegan, keto)
    workout_plan: Optional[Dict[str, Any]] = None  # Structured workout plan for the user
    meal_plan: Optional[List[str]] = None          # Weekly meal plan (7 strings)

    # 🔹 Special considerations
    injury_notes: Optional[str] = None             # Any injuries or conditions to consider

    # 🔹 Logs for auditing or context memory
    handoff_logs: List[str] = []                   # Logs for handoffs between agents/tools
    progress_logs: List[Dict[str, str]] = []       # Logs of user's activity progress
    current_agent: str = "main"                    # 🔹 Agent tracking
    conversation_history: List[Dict[str, str]] = [] # History of user messages and replies
    
    def add_progress_log(self, activity: str, details: str):
        """
        ✅ Adds a new progress entry.
        Useful for tracking user achievements or tool usage.
        Automatically includes current timestamp.
        """
        self.progress_logs.append({
            "activity": activity,
            "details": details,
            "timestamp": str(pd.Timestamp.now())
        })
    
    def add_handoff_log(self, from_agent: str, to_agent: str, reason: str):
        """ ✅ Logs a handoff from one agent to another.
        - Stores a human-readable log string.
        - Updates current_agent to the new agent.
        """
        log_entry = f"Handoff from {from_agent} to {to_agent}: {reason}"
        self.handoff_logs.append(log_entry)
        self.current_agent = to_agent
