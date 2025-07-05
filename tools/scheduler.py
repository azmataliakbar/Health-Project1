from typing import Dict, Any
from context import UserSessionContext
from datetime import datetime, timedelta
import asyncio

DATE_FORMAT = "%Y-%m-%d (%A)"

class CheckinSchedulerTool:
    """Schedules recurring progress check-ins"""
    
    def __init__(self):
        self.reminder_templates = {
            "weekly": {
                "name": "Weekly check-in reminder",
                "description": "Regular weekly progress reviews",
                "activities": ["Weight check", "Progress photos", "Measurements", "Goal review"]
            },
            "bi-weekly": {
                "name": "Bi-weekly progress review",
                "description": "Comprehensive progress assessment every two weeks",
                "activities": ["Detailed measurements", "Workout plan review", "Nutrition assessment", "Goal adjustment"]
            },
            "monthly": {
                "name": "Monthly goal assessment",
                "description": "Complete monthly evaluation and planning",
                "activities": ["Full body assessment", "Goal achievement review", "Plan modifications", "New goal setting"]
            }
        }

    async def execute(self, user_input: str, context: UserSessionContext) -> Dict[str, Any]:
        """Schedule check-in reminders - NOW ASYNC"""
        print("📅 Scheduler - Processing:", user_input)
        
        # Simulate processing time
        await asyncio.sleep(0.1)
        
        # Determine frequency
        frequency = self._determine_frequency(user_input)
        
        # Calculate next check-in dates
        next_checkins = self._calculate_checkin_dates(frequency)
        
        # Create schedule
        schedule = {
            "frequency": frequency,
            "next_checkins": next_checkins,
            "reminder_info": self.reminder_templates[frequency]
        }
        
        # ✅ FIXED: Don't modify context, just log the schedule creation
        print(f"📅 Schedule created: {frequency} check-ins")
        
        return {
            "success": True,
            "schedule": schedule,
            "message": f"📅 **{frequency.title()} Check-in Schedule Created!**\n\n**Next Check-in:** {next_checkins[0]}\n\n**What to expect:**\n{chr(10).join(f'• {activity}' for activity in self.reminder_templates[frequency]['activities'])}\n\n**Upcoming Dates:**\n{chr(10).join(f'• {date}' for date in next_checkins[:4])}\n\n💡 **Tips:**\n• Set reminders on your phone\n• Keep a progress journal\n• Take photos for visual progress\n• Celebrate small wins!"
        }

    def _determine_frequency(self, user_input: str) -> str:
        """Determine check-in frequency from user input"""
        user_input_lower = user_input.lower()
        
        if "weekly" in user_input_lower or "week" in user_input_lower:
            return "weekly"
        elif "monthly" in user_input_lower or "month" in user_input_lower:
            return "monthly"
        elif "bi-weekly" in user_input_lower or "biweekly" in user_input_lower or "two week" in user_input_lower:
            return "bi-weekly"
        else:
            return "weekly"  # Default

    def _calculate_checkin_dates(self, frequency: str) -> list:
        """Calculate next 4 check-in dates"""
        today = datetime.now()
        dates = []
        
        if frequency == "weekly":
            for i in range(1, 5):
                next_date = today + timedelta(weeks=i)
                dates.append(next_date.strftime(DATE_FORMAT))
        elif frequency == "monthly":
            for i in range(1, 5):
                next_date = today + timedelta(days=30*i)
                dates.append(next_date.strftime(DATE_FORMAT))
        else:  # bi-weekly
            for i in range(1, 5):
                next_date = today + timedelta(weeks=2*i)
                dates.append(next_date.strftime(DATE_FORMAT))
        
        return dates
