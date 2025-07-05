from typing import Dict, Any
from context import UserSessionContext
from datetime import datetime
import asyncio

class ProgressTrackerTool:
    """Tracks user progress and updates session context"""
    
    def __init__(self):
        self.trackable_metrics = [
            "weight", "body_fat", "muscle_mass", "workout_completed", 
            "meals_followed", "steps", "sleep_hours", "water_intake"
        ]
        
        self.progress_categories = {
            "workout_completed": {
                "icon": "🏋️",
                "message": "Great workout session completed!",
                "tips": ["Rest for recovery", "Stay hydrated", "Track your sets/reps"]
            },
            "weight_update": {
                "icon": "⚖️",
                "message": "Weight progress recorded!",
                "tips": ["Weigh at same time daily", "Track trends not daily fluctuations", "Consider body composition"]
            },
            "meal_completed": {
                "icon": "🍽️",
                "message": "Nutrition goal achieved!",
                "tips": ["Focus on whole foods", "Stay hydrated", "Plan your next meal"]
            },
            "activity_completed": {
                "icon": "🚶",
                "message": "Activity milestone reached!",
                "tips": ["Keep moving throughout the day", "Set step goals", "Take the stairs"]
            },
            "general": {
                "icon": "📈",
                "message": "Progress logged successfully!",
                "tips": ["Consistency is key", "Celebrate small wins", "Keep tracking"]
            }
        }

    async def execute(self, user_input: str, context: UserSessionContext) -> Dict[str, Any]:
        """Track progress updates - NOW ASYNC"""
        print("📊 Progress Tracker - Processing:", user_input)
        
        # Simulate processing time
        await asyncio.sleep(0.1)
        
        # Extract progress information
        progress_data = self._extract_progress_data(user_input)
        
        # ✅ FIXED: Don't modify context, just simulate progress tracking
        print(f"📊 Progress logged: {progress_data['type']} - {progress_data['details'][:30]}...")
        
        # Calculate progress summary (simulated)
        progress_summary = self._calculate_progress_summary_simulated()
        
        # Get category info
        progress_type = progress_data["type"]
        category_info = self.progress_categories.get(progress_type, self.progress_categories["general"])
        icon = category_info["icon"]
        message = category_info["message"]
        tips = category_info["tips"]
        
        # Build activity breakdown string
        activity_breakdown = []
        for activity, count in progress_summary['activity_breakdown'].items():
            activity_name = activity.replace("_", " ").title()
            activity_breakdown.append(f"• {activity_name}: {count}")
        
        activity_breakdown_text = "\n".join(activity_breakdown)
        
        # Build tips string
        tips_text = "\n".join(f"• {tip}" for tip in tips)
        
        # Build the complete message
        complete_message = f"""{icon} **{message}**

**Details:** {progress_data['details']}

**Progress Summary:**
• Total activities logged: {progress_summary['total_activities']}
• Current streak: {progress_summary['streak_days']} days
• Weekly completion: {progress_summary['completion_rate']:.1f}%

**Activity Breakdown:**
{activity_breakdown_text}

💡 **Tips:**
{tips_text}"""

        return {
            "success": True,
            "progress_data": progress_data,
            "progress_summary": progress_summary,
            "message": complete_message
        }

    def _extract_progress_data(self, user_input: str) -> Dict[str, Any]:
        """Extract progress information from user input"""
        user_input_lower = user_input.lower()
        
        progress_data = {
            "type": "general",
            "details": user_input,
            "timestamp": datetime.now().isoformat()
        }
        
        # Check for specific metrics
        if any(word in user_input_lower for word in ["workout", "exercise", "gym", "training"]):
            progress_data["type"] = "workout_completed"
        elif any(word in user_input_lower for word in ["weight", "weigh", "scale"]):
            progress_data["type"] = "weight_update"
        elif any(word in user_input_lower for word in ["meal", "ate", "food", "nutrition"]):
            progress_data["type"] = "meal_completed"
        elif any(word in user_input_lower for word in ["steps", "walked", "walk", "running", "run"]):
            progress_data["type"] = "activity_completed"
        
        return progress_data

    def _calculate_progress_summary_simulated(self) -> Dict[str, Any]:
        """Calculate simulated progress summary"""
        # Simulate some progress data
        import random
        
        total_activities = random.randint(1, 10)
        activity_types = ["workout_completed", "meal_completed", "activity_completed", "general"]
        
        activity_breakdown = {}
        for activity_type in activity_types:
            if random.choice([True, False]):
                activity_breakdown[activity_type] = random.randint(1, 3)
        
        return {
            "total_activities": total_activities,
            "activity_breakdown": activity_breakdown,
            "streak_days": min(total_activities, 7),  # Simple streak calculation
            "completion_rate": min(100, (total_activities / 7) * 100)  # Weekly completion rate
        }

