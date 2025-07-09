import re
from typing import Dict, Any, List

# ---------------------- Input Guardrails ----------------------

class InputGuardrails:
    """✅ Validates and sanitizes user inputs to ensure safety and consistency"""
    
    def __init__(self):

        # ✅ Regular expression to extract goals like "lose 5 kg in 2 weeks"
        self.goal_pattern = re.compile(r'(lose|gain|maintain)\s+(\d+)\s*(kg|lbs?|pounds?)\s+in\s+(\d+)\s*(weeks?|months?)', re.IGNORECASE)

        # ✅ Words considered dangerous or inappropriate in health context
        self.blocked_words = ['hack', 'cheat', 'dangerous', 'extreme']
    
    def validate_input(self, user_input: str) -> bool:
        """Validate user input for safety and completeness
        ✅ Validate user input:
        - Must not be empty or too short
        - Must not contain blocked words (like 'hack', 'cheat', etc.)
        """
        if not user_input or len(user_input.strip()) < 3:
            return False
        
        # ❌ Reject if any blocked word is found in the input
        if any(word in user_input.lower() for word in self.blocked_words):
            return False
        
        # ✅ Input is safe and valid then
        return True
    
    def extract_goal(self, user_input: str) -> Dict[str, Any]:
        """
        ✅ Extract structured goal data from the user's input.
        Example: "Lose 5 kg in 2 weeks" becomes:
        {
            "action": "lose",
            "quantity": 5,
            "unit": "kg",
            "duration": 2,
            "time_unit": "weeks"
        }
        """
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
        # ❌ Return empty dict if pattern not matched
        return {}
    
    def validate_dietary_input(self, dietary_info: str) -> bool:
        """
        ✅ Check if user mentioned any valid dietary preference.
        Allowed diets: vegetarian, vegan, keto, paleo, etc.
        """
        valid_diets = ['vegetarian', 'vegan', 'keto', 'paleo', 'mediterranean', 'low-carb', 'gluten-free']
        return any(diet in dietary_info.lower() for diet in valid_diets)
    
    # ---------------------- Output Guardrails ----------------------
class OutputGuardrails:
    """✅ Validates outputs from tools to ensure structure and safety"""
    
    def validate_output(self, output: Any) -> bool:
        """
        ✅ Generic validation to ensure:
        - Output is not None
        - If it's a dict or list, it's not empty
        - If it's a string, it's not blank
        """

        if output is None:
            return False
        
        if isinstance(output, dict):
            return len(output) > 0
        
        if isinstance(output, list):
            return len(output) > 0
        
        if isinstance(output, str):
            return len(output.strip()) > 0
        
        # ✅ All other types are accepted by default
        return True
    
    def validate_meal_plan(self, meal_plan: List[str]) -> bool:
        """
        ✅ Meal plan should be:
        - A list of 7 non-empty strings (1 for each day of the week)
        - Each day's plan must be longer than 10 characters
        """
        if not isinstance(meal_plan, list) or len(meal_plan) != 7:
            return False
        
        return all(isinstance(day, str) and len(day) > 10 for day in meal_plan)
    
    def validate_workout_plan(self, workout_plan: Dict[str, Any]) -> bool:
        """
        ✅ Workout plan must contain required keys:
        - 'exercises': list of exercises
        - 'duration': duration of workout
        - 'frequency': how often per week
        """
        required_keys = ['exercises', 'duration', 'frequency']
        return all(key in workout_plan for key in required_keys)
