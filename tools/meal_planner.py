from typing import Dict, Any, List, Optional
from context import UserSessionContext
import random

# Meal constants
MEAL_OATMEAL_FRUITS = "Oatmeal with fruits"
MEAL_AVOCADO_TOAST = "Avocado toast"

class MealPlannerTool:
    """Generates personalized meal plans based on dietary preferences"""
    
    def __init__(self):
        # Initialize meal templates, nutritional info, and ingredient index
        # These are the core data structures needed for meal planning functionality
        self.meal_templates = self._initialize_meal_templates()
        self.nutritional_info = self._initialize_nutritional_info()
        self.ingredient_index = self._build_ingredient_index()

    def _initialize_meal_templates(self) -> Dict[str, Dict[str, List[str]]]:
        """Initialize meal templates for different diets"""
        return {
            "vegetarian": {
                "breakfast": [MEAL_OATMEAL_FRUITS, "Greek yogurt with granola1", MEAL_AVOCADO_TOAST, "Smoothie bowl"],
                "lunch": ["Quinoa salad1", "Vegetable wrap", "Lentil soup1", "Caprese sandwich"],
                "dinner": ["Vegetable stir-fry", "Pasta primavera", "Bean curry", "Stuffed bell peppers"],
                "snacks": ["Mixed nuts", "Fruit", "Hummus with veggies", "Greek yogurt"]
            },
            "vegan": {
                "breakfast": ["Chia pudding", "Oat smoothie", "Avocado toast", "Fruit bowl", "Tofu scramble"],
                "lunch": ["Buddha bowl", "Veggie wrap", "Lentil salad", "Vegetable soup", "Chickpea salad sandwich"],
                "dinner": ["Tofu stir-fry1", "Quinoa curry", "Vegetable pasta", "Stuffed sweet potato", "Lentil loaf"],
                "snacks": ["Nuts", "Fruit", "Vegetable sticks", "Energy balls", "Roasted chickpeas"]
            },
            "keto": {
                "breakfast": ["Eggs with avocado1", "Keto smoothie", "Bacon and eggs", "Cheese omelet", "Chia seed pudding"],
                "lunch": ["Chicken salad1", "Zucchini noodles", "Tuna salad", "Cauliflower rice bowl", "Burger without bun"],
                "dinner": ["Grilled salmon1", "Steak with vegetables", "Chicken thighs", "Pork chops", "Shrimp stir-fry"],
                "snacks": ["Cheese", "Nuts", "Olives", "Hard-boiled eggs", "Pepperoni slices"]
            },
            "mediterranean": {
                "breakfast": ["Greek yogurt with honey", "Feta omelet", "Whole grain toast", "Fruit salad", "Oatmeal with nuts"],
                "lunch": ["Greek salad", "Hummus wrap", "Grilled fish", "Lentil soup", "Tabbouleh"],
                "dinner": ["Grilled salmon1", "Chicken souvlaki", "Vegetable moussaka", "Shrimp pasta", "Stuffed grape leaves"],
                "snacks": ["Olives", "Feta cheese", "Nuts", "Fresh fruit", "Yogurt"]
            }
        }

    def _initialize_nutritional_info(self) -> Dict[str, Dict[str, int]]:
        """Initialize nutritional information for meals"""
        return {
            MEAL_OATMEAL_FRUITS: {"calories": 300, "protein": 8, "carbs": 50, "fat": 5},
            MEAL_AVOCADO_TOAST: {"calories": 350, "protein": 10, "carbs": 30, "fat": 20},
            "Greek yogurt with granola": {"calories": 250, "protein": 12, "carbs": 30, "fat": 8},
            "Chicken salad": {"calories": 450, "protein": 35, "carbs": 10, "fat": 30},
            "Grilled salmon": {"calories": 400, "protein": 34, "carbs": 5, "fat": 28},
            "Tofu stir-fry": {"calories": 320, "protein": 22, "carbs": 20, "fat": 18},
            "Quinoa salad": {"calories": 380, "protein": 14, "carbs": 58, "fat": 12},
            "Vegetable wrap": {"calories": 290, "protein": 8, "carbs": 45, "fat": 10},
            "Lentil soup": {"calories": 230, "protein": 18, "carbs": 40, "fat": 1},
            "Buddha bowl": {"calories": 420, "protein": 16, "carbs": 65, "fat": 14}
        }

    def _build_ingredient_index(self) -> Dict[str, List[str]]:
        """Build index of meals by ingredients"""
        return {
            "oatmeal": [MEAL_OATMEAL_FRUITS, "Oatmeal with nuts"],
            "avocado": [MEAL_AVOCADO_TOAST, "Eggs with avocado"],
            "chicken": ["Chicken salad", "Chicken thighs", "Chicken souvlaki"],
            "salmon": ["Grilled salmon", "Shrimp pasta"],
            "tofu": ["Tofu scramble", "Tofu stir-fry"],
            "quinoa": ["Quinoa salad", "Quinoa curry"],
            "yogurt": ["Greek yogurt with granola", "Greek yogurt with honey"],
            "eggs": ["Eggs with avocado", "Bacon and eggs", "Cheese omelet"]
        }

    def execute(self, user_input: str, context: UserSessionContext) -> Dict[str, Any]:
        """Main execution method that routes requests properly"""
        try:
            print(f"🍽️ Meal Planner - Processing: {user_input}")
            
            # Check if this is a specific diet + meal type search
            if self._is_specific_meal_search(user_input):
                return self._handle_specific_meal_search(user_input, context)
            elif self._is_search_query(user_input):
                return self._handle_search_request(user_input, context)
            else:
                return self._generate_meal_plan(user_input, context)
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Sorry, I couldn't process that request"
            }

    def _is_specific_meal_search(self, user_input: str) -> bool:
        """Check if user is asking for specific diet + meal type"""
        user_input_lower = user_input.lower()
        
        # Check for diet types
        diet_keywords = ["vegetarian", "vegan", "keto", "mediterranean"]
        meal_keywords = ["breakfast", "lunch", "dinner", "snack"]
        
        has_diet = any(diet in user_input_lower for diet in diet_keywords)
        has_meal = any(meal in user_input_lower for meal in meal_keywords)
        
        return has_diet and has_meal

    def _handle_specific_meal_search(self, user_input: str, context: UserSessionContext) -> Dict[str, Any]:
        """Handle specific diet + meal type searches like 'vegetarian breakfast'"""
        user_input_lower = user_input.lower()
        
        # Extract diet and meal types
        diet_type = self._extract_diet_type(user_input_lower)
        meal_type = self._extract_meal_type(user_input_lower)
        
        if not diet_type or not meal_type:
            return self._create_search_error_response()
        
        # Handle snacks vs snack mismatch
        meal_type_key = "snacks" if meal_type == "snack" else meal_type
        
        # Get meals for this combination
        meals = self._get_meals_for_diet_and_type(diet_type, meal_type_key)
        
        if not meals:
            return self._create_search_error_response()
        
        # Create meal list with nutrition info
        meal_list = self._create_meal_list(meals, meal_type, diet_type)
        
        return self._create_successful_search_response(diet_type, meal_type, meal_list)

    def _extract_diet_type(self, user_input_lower: str) -> Optional[str]:
        """Extract diet type from user input"""
        for diet in ["vegetarian", "vegan", "keto", "mediterranean"]:
            if diet in user_input_lower:
                return diet
        return None

    def _extract_meal_type(self, user_input_lower: str) -> Optional[str]:
        """Extract meal type from user input"""
        for meal in ["breakfast", "lunch", "dinner", "snack"]:
            if meal in user_input_lower:
                return meal
        return None

    def _get_meals_for_diet_and_type(self, diet_type: str, meal_type_key: str) -> list:
        """Get meals for specific diet and meal type combination"""
        if diet_type in self.meal_templates and meal_type_key in self.meal_templates[diet_type]:
            return self.meal_templates[diet_type][meal_type_key]
        return []

    def _create_meal_list(self, meals: list, meal_type: str, diet_type: str) -> list:
        """Create formatted meal list with nutrition info"""
        meal_list = []
        for meal in meals:
            nutrition = self.nutritional_info.get(meal, {"calories": "Unknown"})
            meal_list.append({
                "name": meal,
                "category": meal_type,
                "diet": diet_type,
                "nutrition": nutrition
            })
        return meal_list

    def _create_successful_search_response(self, diet_type: str, meal_type: str, meal_list: list) -> Dict[str, Any]:
        """Create successful search response"""
        return {
            "success": True,
            "type": "specific_meal_search",
            "diet_type": diet_type,
            "meal_type": meal_type,
            "meals": meal_list,
            "message": f"🍽️ **{diet_type.title()} {meal_type.title()} Options:**\n\n" + 
                      "\n".join(f"• **{meal['name']}** ({meal['nutrition'].get('calories', '?')} calories)" 
                                for meal in meal_list) +
                      f"\n\n💡 **Tip:** All options are {diet_type} and perfect for {meal_type}!"
        }

    def _create_search_error_response(self) -> Dict[str, Any]:
        """Create error response for failed searches"""
        return {
            "success": False,
            "message": "I couldn't find specific meals for that combination. Try: 'vegetarian breakfast' or 'vegan dinner'"
        }

    def _is_search_query(self, user_input: str) -> bool:
        """Determines if the query is a search request"""
        search_keywords = ["find", "search", "look up", "with", "containing", "recipes with", "meals with"]
        return any(keyword in user_input.lower() for keyword in search_keywords)

    def _handle_search_request(self, user_input: str, context: UserSessionContext) -> Dict[str, Any]:
        """Handle meal search requests more robustly"""
        try:
            # Check if this is an ingredient search
            ingredient = self._extract_ingredient(user_input)
            
            if ingredient:
                meals = self.search_by_ingredient(ingredient)
                return {
                    "success": True,
                    "type": "ingredient_search",
                    "ingredient": ingredient,
                    "meals": meals,
                    "message": f"🔍 **Found {len(meals)} meals containing {ingredient}:**\n\n" +
                          "\n".join(f"• **{_['name']}** ({_['diet']}, {_['category']})" 
                                    for _ in meals) +
                          f"\n\n💡 **Tip:** All these meals include {ingredient} as an ingredient!"
                }
            
            # General meal search
            meals = self.search_meals(user_input)
            return {
                "success": True,
                "type": "general_search",
                "query": user_input,
                "meals": meals,
                "message": f"🔍 **Found {len(meals)} meals matching your search:**\n\n" +
                          "\n".join(f"• **{meal['name']}** ({meal['diet']}, {meal['category']})" 
                                    for meal in meals) +
                          "\n\n💡 **Tip:** Try being more specific like 'vegetarian breakfast' for better results!"
            }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Sorry, I couldn't process your search request"
            }

    def _extract_ingredient(self, user_input: str) -> Optional[str]:
        """Extract ingredient from search query"""
        ingredient_keywords = ["with", "containing", "that uses", "made with"]
        user_input_lower = user_input.lower()
        
        for keyword in ingredient_keywords:
            if keyword in user_input_lower:
                parts = user_input_lower.split(keyword)
                if len(parts) > 1:
                    return parts[1].strip()
        return None

    def search_meals(self, query: str, diet_type: Optional[str] = None) -> List[Dict]:
        """Search meals by name/description"""
        results = []
        query = query.lower()
        
        for diet, meals in self.meal_templates.items():
            if diet_type and diet != diet_type:
                continue
            for category, items in meals.items():
                for item in items:
                    if query in item.lower():
                        results.append({
                            "name": item,
                            "category": category,
                            "diet": diet,
                            "nutrition": self.nutritional_info.get(item, {"calories": "Unknown"})
                        })
        return results

    def search_by_ingredient(self, ingredient: str) -> List[Dict]:
        """Find meals containing specific ingredient"""
        ingredient = ingredient.lower()
        meal_names = self.ingredient_index.get(ingredient, [])
        return self._get_meal_details(meal_names)

    def _get_meal_details(self, meal_names: List[str]) -> List[Dict]:
        """Get details for list of meal names"""
        results = []
        for meal_name in meal_names:
            for diet, meals in self.meal_templates.items():
                for category, items in meals.items():
                    if meal_name in items:
                        results.append({
                            "name": meal_name,
                            "category": category,
                            "diet": diet,
                            "nutrition": self.nutritional_info.get(meal_name, {"calories": "Unknown"})
                        })
                        break
        return results

    def _generate_meal_plan(self, user_input: str, context: UserSessionContext) -> Dict[str, Any]:
        """Generate a personalized meal plan"""
        diet_type = self._determine_diet_type(user_input, context)
        meal_plan = {
            "diet_type": diet_type,
            "days": [],
            "total_nutrition": {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}
        }
        
        # Generate 7-day plan
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for day in days:
            day_plan = self._generate_daily_plan(diet_type, day)
            meal_plan["days"].append(day_plan)
            
            # Update nutrition totals
            for nutrient in meal_plan["total_nutrition"]:
                meal_plan["total_nutrition"][nutrient] += day_plan["nutrition"].get(nutrient, 0)
        
        return {
            "success": True,
            "type": "meal_plan",
            "meal_plan": meal_plan
        }

    def _generate_daily_plan(self, diet_type: str, day_name: str) -> Dict[str, Any]:
        """Generate a single day's meal plan"""
        template = self.meal_templates.get(diet_type, self.meal_templates["vegetarian"])
        meals = {
            "breakfast": random.choice(template["breakfast"]),
            "lunch": random.choice(template["lunch"]),
            "dinner": random.choice(template["dinner"]),
            "snack": random.choice(template["snacks"])
        }
        
        # Calculate daily nutrition
        nutrition = dict.fromkeys(["calories", "protein", "carbs", "fat"], 0)
        for meal_name in meals.values():
            meal_nutrition = self.nutritional_info.get(meal_name, {})
            for nutrient in nutrition:
                nutrition[nutrient] += meal_nutrition.get(nutrient, 0)
        
        return {
            "day": day_name,
            "meals": meals,
            "nutrition": nutrition
        }

    def _determine_diet_type(self, user_input: str, context: UserSessionContext) -> str:
        """Determine diet type from input or context"""
        # Check context first
        if context.diet_preferences and context.diet_preferences.get("diet_type"):
            return context.diet_preferences["diet_type"].lower()
        
        # Check user input
        user_input_lower = user_input.lower()
        diet_mapping = {
            "vegetarian": ["vegetarian", "veggie", "no meat"],
            "vegan": ["vegan", "plant-based", "dairy-free"],
            "keto": ["keto", "ketogenic", "low carb"],
            "mediterranean": ["mediterranean", "olive oil", "fish"]
        }
        
        for diet, keywords in diet_mapping.items():
            if any(keyword in user_input_lower for keyword in keywords):
                return diet
        
        return "balanced"  # Default diet type

