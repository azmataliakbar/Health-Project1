from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import pandas as pd


class UserSessionContext(BaseModel):
    """Shared context for user session across all tools and agents"""
    name: str
    uid: int
    goal: Optional[Dict[str, Any]] = None
    diet_preferences: Optional[str] = None
    workout_plan: Optional[Dict[str, Any]] = None
    meal_plan: Optional[List[str]] = None
    injury_notes: Optional[str] = None
    handoff_logs: List[str] = []
    progress_logs: List[Dict[str, str]] = []
    current_agent: str = "main"
    conversation_history: List[Dict[str, str]] = []
    
    def add_progress_log(self, activity: str, details: str):
        """Add a progress log entry"""
        self.progress_logs.append({
            "activity": activity,
            "details": details,
            "timestamp": str(pd.Timestamp.now())
        })
    
    def add_handoff_log(self, from_agent: str, to_agent: str, reason: str):
        """Log agent handoffs"""
        log_entry = f"Handoff from {from_agent} to {to_agent}: {reason}"
        self.handoff_logs.append(log_entry)
        self.current_agent = to_agent
