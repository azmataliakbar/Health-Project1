from typing import Dict, Any
from context import UserSessionContext
import asyncio

class WorkoutRecommenderTool:
    """Recommends workout plans based on user goals and experience"""
    
    def __init__(self):
        self.workout_templates = {
            "weight_loss": {
                "beginner": {
                    "exercises": ["Walking", "Bodyweight squats", "Push-ups", "Planks"],
                    "duration": "30 minutes",
                    "frequency": "2 times per week",
                    "intensity": "Moderate",
                    "description": "Perfect for starting your weight loss journey"
                },
                "intermediate": {
                    "exercises": ["Jogging", "Burpees", "Mountain climbers", "Jump squats"],
                    "duration": "45 minutes",
                    "frequency": "6 times per week",
                    "intensity": "High",
                    "description": "Accelerated weight loss with higher intensity"
                },
                "advanced": {
                    "exercises": ["HIIT sprints", "Advanced burpees", "Plyometric circuits", "CrossFit workouts"],
                    "duration": "50 minutes",
                    "frequency": "6 times per week",
                    "intensity": "Very High",
                    "description": "Maximum calorie burn for experienced athletes"
                }
            },
            "muscle_gain": {
                "beginner": {
                    "exercises": ["Push-ups", "Squats", "Lunges", "Dumbbell rows"],
                    "duration": "40 minutes",
                    "frequency": "3 times per week",
                    "intensity": "Moderate",
                    "description": "Build foundation strength and muscle"
                },
                "intermediate": {
                    "exercises": ["Bench press", "Deadlifts", "Pull-ups", "Overhead press"],
                    "duration": "60 minutes",
                    "frequency": "4 times per week",
                    "intensity": "High",
                    "description": "Progressive overload for muscle growth"
                },
                "advanced": {
                    "exercises": ["Heavy compound lifts", "Advanced variations", "Supersets", "Drop sets"],
                    "duration": "75 minutes",
                    "frequency": "5 times per week",
                    "intensity": "Very High",
                    "description": "Advanced muscle building techniques"
                }
            },
            "general_fitness": {
                "beginner": {
                    "exercises": ["Walking", "Stretching", "Light weights", "Yoga"],
                    "duration": "30 minutes",
                    "frequency": "3 times per week",
                    "intensity": "Low to Moderate",
                    "description": "Gentle introduction to fitness"
                },
                "intermediate": {
                    "exercises": ["Jogging", "Circuit training", "Moderate weights", "Pilates"],
                    "duration": "45 minutes",
                    "frequency": "4 times per week",
                    "intensity": "Moderate",
                    "description": "Well-rounded fitness improvement"
                },
                "advanced": {
                    "exercises": ["Running", "Complex movements", "Heavy weights", "Sport-specific training"],
                    "duration": "60 minutes",
                    "frequency": "5 times per week",
                    "intensity": "High",
                    "description": "Peak fitness and performance"
                }
            }
        }

    async def execute(self, user_input: str, context: UserSessionContext) -> Dict[str, Any]:
        """Generate workout recommendations - NOW ASYNC"""
        print("🏋️ Workout Recommender - Processing:", user_input)
        
        # Simulate processing time
        await asyncio.sleep(0.1)
        
        # Determine goal type
        goal_type = self._determine_goal_type(context)
        
        # Determine experience level
        experience_level = self._determine_experience_level(user_input)
        
        # Get workout plan
        workout_plan = self._get_workout_plan(goal_type, experience_level)
        
        # ✅ FIXED: Don't modify context, just log the workout creation
        print(f"🏋️ Workout plan created: {goal_type} - {experience_level}")
        
        return {
            "success": True,
            "goal_type": goal_type,
            "experience_level": experience_level,
            "workout_plan": workout_plan,
            "message": f"🏋️ **{experience_level.title()} {goal_type.replace('_', ' ').title()} Workout Plan Created!**\n\n**Description:** {workout_plan.get('description', '')}\n\n**Exercises:** {', '.join(workout_plan.get('exercises', []))}\n\n**Duration:** {workout_plan.get('duration', '')}\n**Frequency:** {workout_plan.get('frequency', '')}\n**Intensity:** {workout_plan.get('intensity', '')}\n\n💡 **Tips:**\n• Start slowly and gradually increase intensity\n• Focus on proper form over speed\n• Rest 48 hours between strength sessions\n• Stay hydrated and listen to your body"
        }

    def _determine_goal_type(self, context: UserSessionContext) -> str:
        """Determine workout goal from context"""
        if context.goal and context.goal.get("type"):
            goal_type = context.goal["type"]
            if goal_type in ["weight_loss"]:
                return "weight_loss"
            elif goal_type in ["muscle_gain"]:
                return "muscle_gain"
            else:
                return "general_fitness"
        return "general_fitness"

    def _determine_experience_level(self, user_input: str) -> str:
        """Determine user's fitness experience level"""
        user_input_lower = user_input.lower()
        
        if any(word in user_input_lower for word in ["beginner", "new", "start", "never", "first time"]):
            return "beginner"
        elif any(word in user_input_lower for word in ["intermediate", "some experience", "moderate", "few months"]):
            return "intermediate"
        elif any(word in user_input_lower for word in ["advanced", "experienced", "expert", "years"]):
            return "advanced"
        else:
            return "beginner"  # Default to beginner for safety

    def _get_workout_plan(self, goal_type: str, experience_level: str) -> Dict[str, Any]:
        """Get workout plan based on goal and experience"""
        if goal_type in self.workout_templates:
            if experience_level in self.workout_templates[goal_type]:
                return self.workout_templates[goal_type][experience_level]
            else:
                # Fallback to beginner if experience level not found
                return self.workout_templates[goal_type]["beginner"]
        else:
            # Fallback to general fitness beginner
            return self.workout_templates["general_fitness"]["beginner"]

