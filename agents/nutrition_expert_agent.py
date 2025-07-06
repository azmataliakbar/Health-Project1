from typing import Dict, Any
from context import UserSessionContext
import asyncio

# Defines a specialized class for handling nutrition-related queries
class NutritionExpertAgent:
    """Specialized agent for nutrition and dietary concerns"""

    # Initializes the agent with predefined nutrition plans for common conditions
    def __init__(self):
        # Dictionary defining avoid/recommend/tips for conditions like diabetes, hypertension, allergies
        self.dietary_conditions = {
            "diabetes": {
                "avoid": ["High sugar foods", "Refined carbs", "Sugary drinks", "White bread"],
                "recommend": ["Whole grains", "Lean proteins", "Non-starchy vegetables", "Healthy fats"],
                "tips": ["Monitor blood sugar regularly", "Eat at consistent times", "Control portion sizes"]
            },
            "hypertension": {
                "avoid": ["High sodium foods", "Processed meats", "Canned soups", "Fast food"],
                "recommend": ["Fresh fruits", "Vegetables", "Whole grains", "Low-fat dairy"],
                "tips": ["Limit sodium to 2300mg/day", "Use herbs and spices for flavor", "Read nutrition labels"]
            },
            "allergies": {
                "avoid": ["Known allergens", "Cross-contaminated foods", "Processed foods with unclear ingredients"],
                "recommend": ["Fresh whole foods", "Carefully labeled products", "Home-cooked meals"],
                "tips": ["Always read ingredient labels", "Carry emergency medication", "Inform restaurants about allergies"]
            }
        }

    # Asynchronously processes incoming messages, uses context, and optionally streams response
    async def process_message(self, message: str, context: UserSessionContext, streamer=None) -> str:
        """Process nutrition-related concerns"""

        # Logs the handoff of conversation to the nutrition expert for tracking (inside the context)
        print("🥗 Nutrition Expert Agent - User said:", message)
        
        try:
            context.add_handoff_log("main", "nutrition_expert", f"Nutrition consultation: {message[:50]}...")
        except Exception as e:
            print(f"Warning: Could not add handoff log: {e}")
        
        # Prints a trimmed version of the user’s message as a log entry
        print(f"📝 Nutrition consultation logged: {message[:50]}...")
        
        # Detects if message contains keywords for specific dietary conditions like "diabetes"
        condition = self._identify_dietary_condition(message)
        
        if condition and condition != "unknown":
            # Creates advice tailored to the detected condition
            response = self._generate_condition_specific_advice(condition, context)
        else:
            # If no condition found, generate general healthy eating advice
            response = self._generate_general_nutrition_advice(context)
        
        # If streaming is enabled, send the response via stream
        if streamer:
            try:
                # Asynchronously streams the response to the frontend/client
                await streamer.update(response)
                print("✅ Nutrition expert response streamed successfully")
            except Exception as e:
                print(f"❌ Nutrition streaming error: {e}")
        
        print(f"✅ Nutrition expert returning response: {len(response)} characters")
        # Returns the final nutrition advice response
        return response
    
    # Extracts condition type (e.g., diabetes, hypertension) from user's message using keyword matching
    def _identify_dietary_condition(self, message: str) -> str:
        """Identify dietary condition from message"""

        # Converts message to lowercase to simplify keyword matching
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["diabetes", "diabetic", "blood sugar", "glucose"]):
            return "diabetes"
        elif any(word in message_lower for word in ["blood pressure", "hypertension", "high bp"]):
            return "hypertension"
        elif any(word in message_lower for word in ["allergy", "allergic", "intolerance"]):
            return "allergies"
        
        # Returns 'unknown' if no condition keywords are found
        return "unknown"

    # Returns a formatted string of advice based on the detected condition (like diabetes or allergies)
    def _generate_condition_specific_advice(self, condition: str, context: UserSessionContext) -> str:
        """Generate advice for specific dietary conditions"""
        
        # If somehow an unsupported condition is passed, fallback to general advice
        if condition not in self.dietary_conditions:
            return self._generate_general_nutrition_advice(context)
        
        # Fetch advice data (avoid/recommend/tips) from the dictionary
        condition_info = self.dietary_conditions[condition]
        
        # Constructs a rich text response including foods to avoid, recommend, and practical tips
        response = f"""🥗 **{condition.upper()} NUTRITION MANAGEMENT**

I understand you're managing {condition}. Here's your personalized nutrition plan:

❌ **Foods to AVOID:**
{chr(10).join(f"• {food}" for food in condition_info["avoid"])}

✅ **RECOMMENDED Foods:**
{chr(10).join(f"• {food}" for food in condition_info["recommend"])}

💡 **Management Tips:**
{chr(10).join(f"• {tip}" for tip in condition_info["tips"])}

🍽️ **Meal Planning Guidelines:**
• Plan meals in advance
• Keep a food diary
• Stay hydrated with water
• Eat regular, balanced meals

⚠️ **Important Reminders:**
• Always consult with your healthcare provider
• Monitor your condition regularly
• Don't make drastic dietary changes without medical supervision
• Consider working with a registered dietitian

Would you like me to suggest specific meal ideas that work well for managing {condition}?"""

        return response
    
    # Returns a comprehensive guide to healthy eating, hydration, and portion control
    def _generate_general_nutrition_advice(self, context: UserSessionContext) -> str:
        """Generate general nutrition advice"""

        # Static message covering general healthy eating practices, ideal for users with no specific conditions
        return """🥗 **COMPREHENSIVE NUTRITION GUIDANCE**

I'm here to help you with your nutrition and dietary concerns!

🌟 **Balanced Nutrition Principles:**
• **Variety**: Eat foods from all food groups
• **Moderation**: Control portion sizes
• **Balance**: Include proteins, carbs, and healthy fats
• **Timing**: Eat regular meals throughout the day

🍎 **Essential Food Groups:**

**Fruits & Vegetables (5-9 servings/day):**
• Rich in vitamins, minerals, and fiber
• Choose colorful varieties
• Fresh, frozen, or canned (without added sugar/salt)

**Whole Grains (6-8 servings/day):**
• Brown rice, quinoa, oats, whole wheat bread
• Provides sustained energy and fiber

**Lean Proteins (2-3 servings/day):**
• Fish, poultry, beans, nuts, eggs
• Essential for muscle maintenance and repair

**Healthy Fats (in moderation):**
• Avocados, nuts, olive oil, fatty fish
• Important for brain health and nutrient absorption

💧 **Hydration Guidelines:**
• 8+ glasses of water daily
• More if you're active or in hot weather
• Limit sugary drinks and excessive caffeine

🍽️ **Meal Planning Tips:**
• Plan meals and snacks in advance
• Prep ingredients on weekends
• Keep healthy snacks available
• Read nutrition labels

⚖️ **Portion Control:**
• Use smaller plates and bowls
• Fill half your plate with vegetables
• Listen to hunger and fullness cues
• Eat slowly and mindfully

🏥 **When to Seek Professional Help:**
• Managing chronic health conditions
• Significant weight changes needed
• Food allergies or intolerances
• Eating disorders or disordered eating patterns

Can you tell me more about your specific nutrition goals or dietary concerns? I can provide more targeted advice based on your needs."""

