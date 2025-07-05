import re
from typing import Dict, Any, List

class InputGuardrails:
    """Validate and sanitize user inputs"""
    
    def __init__(self):
        self.goal_pattern = re.compile(r'(lose|gain|maintain)\s+(\d+)\s*(kg|lbs?|pounds?)\s+in\s+(\d+)\s*(weeks?|months?)', re.IGNORECASE)
        self.blocked_words = ['hack', 'cheat', 'dangerous', 'extreme']
    
    def validate_input(self, user_input: str) -> bool:
        """Validate user input for safety and completeness"""
        if not user_input or len(user_input.strip()) < 3:
            return False
        
        # Check for blocked words
        if any(word in user_input.lower() for word in self.blocked_words):
            return False
        
        # Input is valid
        return True
    
    def extract_goal(self, user_input: str) -> Dict[str, Any]:
        """Extract structured goal from user input"""
        match = self.goal_pattern.search(user_input)
        if match:
            action, quantity, unit, duration, time_unit = match.groups()
            return {
                "action": action.lower(),
                "quantity": int(quantity),
                "unit": unit.lower(),
                "duration": int(duration),
                "time_unit": time_unit.lower()
            }
        return {}
    
    def validate_dietary_input(self, dietary_info: str) -> bool:
        """Validate dietary preferences input"""
        valid_diets = ['vegetarian', 'vegan', 'keto', 'paleo', 'mediterranean', 'low-carb', 'gluten-free']
        return any(diet in dietary_info.lower() for diet in valid_diets)

class OutputGuardrails:
    """Validate tool outputs for structure and safety"""
    
    def validate_output(self, output: Any) -> bool:
        """Validate tool output structure"""
        if output is None:
            return False
        
        if isinstance(output, dict):
            return len(output) > 0
        
        if isinstance(output, list):
            return len(output) > 0
        
        if isinstance(output, str):
            return len(output.strip()) > 0
        
        return True
    
    def validate_meal_plan(self, meal_plan: List[str]) -> bool:
        """Validate meal plan structure"""
        if not isinstance(meal_plan, list) or len(meal_plan) != 7:
            return False
        
        return all(isinstance(day, str) and len(day) > 10 for day in meal_plan)
    
    def validate_workout_plan(self, workout_plan: Dict[str, Any]) -> bool:
        """Validate workout plan structure"""
        required_keys = ['exercises', 'duration', 'frequency']
        return all(key in workout_plan for key in required_keys)
