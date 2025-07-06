from typing import Dict, Any
from context import UserSessionContext
import re
import asyncio

# Main class to analyze and structure user goals
class GoalAnalyzerTool:
    """Analyzes user goals and converts them to structured format"""

    # Constants for goal targets
    IMPROVE_FITNESS_TARGET = "Improve overall fitness"
    BUILD_MUSCLE_TARGET = "Build muscle mass"

    # Defines regex patterns to match various goal types like weight loss/gain, muscle gain, fitness, etc.
    def __init__(self):
        self.goal_patterns = {
            'weight_loss': re.compile(
                r'lose\s+(\d+)\s*(kg|lbs?|pounds?)\s+in\s+(\d+)\s*(weeks?|months?)',
                re.IGNORECASE
            ),
            'weight_gain': re.compile(
                r'gain\s+(\d+)\s*(kg|lbs?|pounds?)\s+in\s+(\d+)\s*(weeks?|months?)',
                re.IGNORECASE
            ),
            'muscle_gain': re.compile(
                r'(?:build|gain)\s+(?:muscle|strength)(?:\s+in\s+(?P<duration>\d+)\s*(?P<unit>weeks?|months?))?',
                re.IGNORECASE
            ),
            'fitness': re.compile(
                r'(?:my|general|normal)?\s*fitness|get\s+(?:fit|healthy|in\s+shape)',
                re.IGNORECASE
            ),
            'fitness_with_time': re.compile(
                r'(?:my|general|normal)?\s*fitness\s+in\s+(\d+)\s*(weeks?|months?)',
                re.IGNORECASE
            )
        }

    async def execute(self, user_input: str, context: UserSessionContext) -> Dict[str, Any]:

        # Keeps async interface even though it's not doing background work
        await asyncio.sleep(0)

        # Initializes default structure for goal output
        structured_goal = {
            "type": None,
            "target": None,
            "timeframe": None,
            "specifics": {}
        }

        # Ordered list of methods to check for different goal patterns
        handlers = [
            self._handle_weight_loss,
            self._handle_weight_gain,
            self._handle_muscle_gain,
            self._handle_fitness_with_time,  # New handler for fitness with explicit time
            self._handle_general_fitness,
            self._handle_fallback_keywords
        ]

        for handler in handlers:
            result = handler(user_input)
            if result:

                # Updates structured_goal with matched goal data
                structured_goal.update(result)
                # Stores goal in session context
                context.goal = structured_goal
                return {
                    # Returns the structured goal with success
                    "success": True,
                    "goal": structured_goal,
                    "message": self._goal_message(structured_goal)
                }
        
        # If no match found, returns a failure message with suggestions
        return {
            "success": False,
            "goal": None,
            "message": (
                "I couldn't fully understand your goal format. 💡 Try phrases like:\n"
                "- 'I want to gain 5 kg in 3 months'\n"
                "- 'I want to lose 10 kg in 4 months'\n"
                "- 'I want to build muscle in 6 months'\n"
                "- 'My fitness in 3 months'\n"
                "Please include both what you want to achieve and your timeframe."
            )
        }
    
    # Uses regex to detect goal like "lose 5 kg in 2 months"
    # Extracts quantity, unit, duration, and time unit
    # Returns structured goal dictionary
    def _handle_weight_loss(self, user_input: str):
        match = self.goal_patterns['weight_loss'].search(user_input)
        if match:
            quantity, unit, duration, time_unit = match.groups()
            return {
                "type": "weight_loss",
                "target": f"{quantity} {unit}",
                "timeframe": f"{duration} {time_unit}",
                "specifics": {
                    "quantity": int(quantity),
                    "unit": unit.lower(),
                    "duration": int(duration),
                    "time_unit": time_unit.lower()
                }
            }
        
    # Uses regex to detect goal like "gain 5 kg in 2 months"
    # Extracts quantity, unit, duration, and time unit
    # Returns structured goal dictionary
    def _handle_weight_gain(self, user_input: str):
        match = self.goal_patterns['weight_gain'].search(user_input)
        if match:
            quantity, unit, duration, time_unit = match.groups()
            return {
                "type": "weight_gain",
                "target": f"{quantity} {unit}",
                "timeframe": f"{duration} {time_unit}",
                "specifics": {
                    "quantity": int(quantity),
                    "unit": unit.lower(),
                    "duration": int(duration),
                    "time_unit": time_unit.lower()
                }
            }
        
    # Matches phrases like "build muscle" or "gain strength"
    # Accepts optional duration, defaults to "3 months"
    # Returns goal with focus on strength training
    def _handle_muscle_gain(self, user_input: str):
        match = self.goal_patterns['muscle_gain'].search(user_input)
        if match:
            duration = match.group("duration")
            unit = match.group("unit")
            timeframe = f"{duration} {unit}" if duration and unit else "3 months"
            return {
                "type": "muscle_gain",
                "target": "Build muscle mass",
                "timeframe": timeframe,
                "specifics": {
                    "focus": "strength_training",
                    "quantity": None,
                    "unit": unit.lower() if unit else None,
                    "duration": int(duration) if duration else None,
                    "time_unit": unit.lower() if unit else None
                }
            }
        
    # Matches "my fitness" or "general fitness"
    # Accepts optional duration, defaults to "2 months"
    # Returns structured goal with cardio and strength focus
    def _handle_fitness_with_time(self, user_input: str):
        """Handle explicit fitness goals with timeframes (e.g., 'my fitness in 6 months')"""
        match = self.goal_patterns['fitness_with_time'].search(user_input)
        if match:
            duration, time_unit = match.groups()
            return {
                "type": "general_fitness",  # Using muscle_gain type for consistent display
                "target": self.IMPROVE_FITNESS_TARGET,
                "timeframe": f"{duration} {time_unit}",
                "specifics": {
                    "focus": "cardio_and_strength",
                    "quantity": None,
                    "unit": time_unit.lower(),
                    "duration": int(duration),
                    "time_unit": time_unit.lower()
                }
            }

    # Handles inputs like "my fitness" or "normal fitness" without time
    # Optionally extracts timeframe like "in 2 months", or defaults to 2 months
    def _handle_general_fitness(self, user_input: str):
        """Handle general fitness goals without explicit timeframes"""
        match = self.goal_patterns['fitness'].search(user_input)
        if match:
            # Check for implicit timeframe
            time_match = re.search(r'in\s+(\d+)\s*(weeks?|months?)', user_input, re.IGNORECASE)
            if time_match:
                duration, time_unit = time_match.groups()
                timeframe = f"{duration} {time_unit}"
                specifics = {
                    "focus": "cardio_and_strength",
                    "quantity": None,
                    "unit": time_unit.lower(),
                    "duration": int(duration),
                    "time_unit": time_unit.lower()
                }
            else:
                timeframe = "2 months"
                specifics = {"focus": "cardio_and_strength"}
            
            return {
                "type": "general_fitness",
                "target": self.IMPROVE_FITNESS_TARGET,
                "timeframe": timeframe,
                "specifics": specifics
            }
    
    # Catches generic keywords if no pattern matched (e.g., "my fitness", "lose", "gain")
    # Tries to extract time if mentioned
    # If "my/general/normal fitness" is found, maps to "Improve overall fitness"
    # Used as a last resort for weakly structured goals
    def _handle_fallback_keywords(self, user_input: str):
        fallback_keywords = [
            "fitness", "gain", "lose", "build muscle",
            "improve muscle", "my fitness", "general fitness", "normal fitness"
        ]
        if any(kw in user_input.lower() for kw in fallback_keywords):
            # Try to find a timeframe like "in 6 months"
            time_match = re.search(r'in\s+(\d+)\s*(weeks?|months?)', user_input, re.IGNORECASE)
            if time_match:
                duration, time_unit = time_match.groups()
                timeframe = f"{duration} {time_unit}"
                
                # Special handling for fitness keywords
                if any(fitness_kw in user_input.lower() for fitness_kw in ["my fitness", "general fitness", "normal fitness"]):
                    return {
                        "type": "muscle_gain",
                        "target": self.IMPROVE_FITNESS_TARGET,
                        "timeframe": timeframe,
                        "specifics": {
                            "focus": "cardio_and_strength",
                            "quantity": None,
                            "unit": time_unit.lower(),
                            "duration": int(duration),
                            "time_unit": time_unit.lower()
                        }
                    }
            else:
                timeframe = "2 months"
            
            return {
                "type": "general_fitness",
                "target": self.IMPROVE_FITNESS_TARGET,
                "timeframe": timeframe,
                "specifics": {
                    "focus": "cardio_and_strength"
                }
            }
    
    # Maps internal goal type to a friendly title like "Weight Loss"
    # Formats and returns a message like:
    # "You've set a goal to achieve: Weight Gain — 5 kg in 2 months"
    def _goal_message(self, goal: dict) -> str:
        title_map = {
            "weight_loss": "Weight Loss",
            "weight_gain": "Weight Gain",
            "muscle_gain": "Muscle Gain",
            "general_fitness": "General Fitness"
        }
        goal_type = title_map.get(goal["type"], "Your Goal")
        return (
            f"🎯 Goal Analyzed Successfully!\n\n"
            f"You've set a goal to achieve: {goal_type} — {goal['target']} in {goal['timeframe']}"
        )


