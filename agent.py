import openai
from openai import AsyncOpenAI
from typing import Dict, Any, Optional
from context import UserSessionContext
from tools.goal_analyzer import GoalAnalyzerTool
from tools.meal_planner import MealPlannerTool
from tools.workout_recommender import WorkoutRecommenderTool
from tools.scheduler import CheckinSchedulerTool
from tools.tracker import ProgressTrackerTool
from agents.escalation_agent import EscalationAgent
from agents.nutrition_expert_agent import NutritionExpertAgent
from agents.injury_support_agent import InjurySupportAgent
from guardrails import InputGuardrails, OutputGuardrails
import json
import time
import re
import asyncio

class HealthWellnessAgent:
    def __init__(self):
        self.client = AsyncOpenAI()
        self.tools = self._initialize_tools()
        self.specialized_agents = self._initialize_specialized_agents()
        self.input_guardrails = InputGuardrails()
        self.output_guardrails = OutputGuardrails()

    def _initialize_tools(self) -> Dict[str, Any]:
        """Initialize all tools"""
        return {
            "goal_analyzer": GoalAnalyzerTool(),
            "meal_planner": MealPlannerTool(),
            "workout_recommender": WorkoutRecommenderTool(),
            "checkin_scheduler": CheckinSchedulerTool(),
            "progress_tracker": ProgressTrackerTool(),
        }

    def _initialize_specialized_agents(self) -> Dict[str, Any]:
        """Initialize all specialized agents"""
        return {
            "escalation": EscalationAgent(),
            "nutrition_expert": NutritionExpertAgent(),
            "injury_support": InjurySupportAgent()
        }

    def _search_local_data(self, message: str) -> Optional[str]:
        """Search static local responses for known keywords"""
        local_responses = {
            "tree": "🌳 A tree is a perennial plant with a trunk, used in oxygen production and shade.",
            "tea": "🍵 Tea is a popular beverage made by brewing leaves — often green or black.",
            "ball": "🏐 A ball is a round object used in sports like football, volleyball, and basketball.",
            "apple": "🍎 An apple a day keeps the doctor away!"
        }
        
        message_lower = message.lower()
        for keyword, response in local_responses.items():
            if keyword in message_lower:
                return response
        return None

    async def _handle_local_response(self, local_response: str, streamer) -> str:
        """Handle local response with streaming"""
        if streamer:
            await streamer.update(local_response)
        return local_response

    async def _handle_specialized_agent(self, handoff_agent: str, message: str, context: UserSessionContext, streamer) -> str:
        """Handle specialized agent processing"""
        context.add_handoff_log("main", handoff_agent, f"User request: {message[:50]}...")
        print(f"🔄 Handing off to: {handoff_agent}")
        
        if handoff_agent in self.specialized_agents:
            try:
                response = await self.specialized_agents[handoff_agent].process_message(message, context, streamer)
                print(f"✅ Specialized agent response received: {len(response) if response else 0} characters")
                return response if response else "I'm having trouble connecting you right now. Please try again."
            except Exception as e:
                print(f"❌ Specialized agent error: {str(e)}")
                return f"I'm having trouble with that request. Error: {str(e)}"
        
        return "I'm transferring you to a specialized assistant..."

    async def _handle_tool_processing(self, tool_name: str, message: str, context: UserSessionContext, streamer) -> str:
        """Handle tool processing"""
        start_time = time.time()
        print(f"🛠️ Using tool: {tool_name}")
        
        # Handle both sync and async tools
        if tool_name == "meal_planner":
            # Meal planner is now synchronous
            tool_response = self.tools[tool_name].execute(message, context)
        else:
            # Other tools are still asynchronous
            tool_response = await self.tools[tool_name].execute(message, context)
        
        print(f"📦 Tool response: {tool_response}")
        
        if not self.output_guardrails.validate_output(tool_response):
            print("⚠️ Output failed validation.")
            return "I encountered an issue processing your request. Please try rephrasing your question."
        
        # ✅ FIXED: Handle all tool-specific responses directly without OpenAI
        if tool_name == "goal_analyzer":
            return await self._handle_goal_response(tool_response, streamer, start_time)
        elif tool_name == "meal_planner":
            return await self._handle_meal_response(tool_response, streamer)
        elif tool_name == "workout_recommender":
            return await self._handle_workout_response(tool_response, streamer)
        elif tool_name == "progress_tracker":
            return await self._handle_tracker_response(tool_response, streamer)
        elif tool_name == "checkin_scheduler":
            return await self._handle_scheduler_response(tool_response, streamer)
        
        # Only use OpenAI for unknown tools
        return await self._generate_llm_response(message, tool_response, context, streamer)

    # ✅ REFACTORED: Reduced cognitive complexity from 22 to under 15
    async def process_message(self, message: str, context: UserSessionContext, streamer=None) -> str:
        """Process user message and return response - refactored for lower complexity"""
        try:
            # Check for static/local answers first
            if local_response := self._search_local_data(message):
                return await self._handle_local_response(local_response, streamer)
            
            # Input validation
            if not self.input_guardrails.validate_input(message):
                return self._get_input_validation_message()
            
            # Check for handoff to specialized agent
            if handoff_agent := self._check_handoff_conditions(message, context):
                return await self._handle_specialized_agent(handoff_agent, message, context, streamer)
            
            # Determine which tool to use
            tool_name = self._determine_tool(message, context)
            
            if not tool_name or tool_name not in self.tools:
                return await self._generate_general_response(message, context, streamer)
            
            # Process with selected tool
            return await self._handle_tool_processing(tool_name, message, context, streamer)
            
        except Exception as e:
            print(f"❌ Processing error: {str(e)}")
            return f"I apologize, but I encountered an error processing your request.: {str(e)}"

    async def _generate_general_response(self, message: str, context: UserSessionContext, streamer=None) -> str:
        """Generate general response when no specific tool is needed"""
        try:
            system_prompt = f"""You are a helpful health and wellness assistant. 
            User context: {context.dict()}
            
            Provide helpful, encouraging responses about health, fitness, nutrition, and wellness.
            Keep responses concise but informative."""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ]
            
            if streamer:
                return await self._stream_response(messages, streamer)
            
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7
            )
            return response.choices[0].message.content
        
        except Exception as e:
            print(f"❌ General response error: {str(e)}")
            return "I'm here to help with your health and wellness goals! Could you tell me more about what you're looking for?"

    def _get_input_validation_message(self) -> str:
        """Return input validation error message"""
        return "I'm sorry, but I can't process that request. Please ask about health, fitness, nutrition, or wellness topics."

    async def _handle_goal_response(self, tool_response: Dict[str, Any], streamer=None, start_time=None) -> str:
        """Format goal analyzer response - FIXED TO BE ASYNC"""
        try:
            goal_data = tool_response["goal"]
            result = (
                f"🎯 Goal Analyzed Successfully!\n\n"
                f"You've set a goal to achieve:\n"
                f"**{goal_data.get('type', 'Unknown').replace('_', ' ').title()}** — "
                f"*{goal_data.get('target', '')} in {goal_data.get('timeframe', '')}*"
            )
            
            if start_time:
                print(f"✅ Total execution time: {round(time.time() - start_time, 2)}s")
            
            # ✅ FIXED: Proper null check for streamer
            if streamer is not None:
                try:
                    await streamer.update(result)
                    print("✅ Goal response streamed successfully")
                except Exception as stream_error:
                    print(f"❌ Goal streaming error: {stream_error}")
            
            return result
        except Exception as e:
            error_msg = f"Error formatting goal response: {str(e)}"
            if streamer is not None:
                try:
                    await streamer.update(error_msg)
                except Exception as stream_error:
                    print(f"❌ Error updating streamer: {stream_error}")
            return error_msg

    async def _handle_workout_response(self, tool_response: Dict[str, Any], streamer=None) -> str:
        """Handle workout recommender responses"""
        try:
            # The tool already provides a formatted message
            response = tool_response.get("message", "I've created a workout plan for you!")
            
            if streamer is not None:
                try:
                    await streamer.update(response)
                    print("✅ Workout response streamed successfully")
                except Exception as stream_error:
                    print(f"❌ Workout streaming error: {stream_error}")
            
            return response
        except Exception as e:
            error_msg = f"Error formatting workout response: {str(e)}"
            if streamer is not None:
                try:
                    await streamer.update(error_msg)
                except Exception as stream_error:
                    print(f"❌ Error updating streamer: {stream_error}")
            return error_msg

    async def _handle_tracker_response(self, tool_response: Dict[str, Any], streamer=None) -> str:
        """Handle progress tracker responses"""
        try:
            # The tool already provides a formatted message
            response = tool_response.get("message", "Progress has been tracked!")
            
            if streamer is not None:
                try:
                    await streamer.update(response)
                    print("✅ Tracker response streamed successfully")
                except Exception as stream_error:
                    print(f"❌ Tracker streaming error: {stream_error}")
            
            return response
        except Exception as e:
            error_msg = f"Error formatting tracker response: {str(e)}"
            if streamer is not None:
                try:
                    await streamer.update(error_msg)
                except Exception as stream_error:
                    print(f"❌ Error updating streamer: {stream_error}")
            return error_msg

    async def _handle_scheduler_response(self, tool_response: Dict[str, Any], streamer=None) -> str:
        """Handle scheduler responses"""
        try:
            # The tool already provides a formatted message
            response = tool_response.get("message", "Schedule has been created!")
            
            if streamer is not None:
                try:
                    await streamer.update(response)
                    print("✅ Scheduler response streamed successfully")
                except Exception as stream_error:
                    print(f"❌ Scheduler streaming error: {stream_error}")
            
            return response
        except Exception as e:
            error_msg = f"Error formatting scheduler response: {str(e)}"
            if streamer is not None:
                try:
                    await streamer.update(error_msg)
                except Exception as stream_error:
                    print(f"❌ Error updating streamer: {stream_error}")
            return error_msg

    async def _handle_meal_response(self, tool_response: Dict[str, Any], streamer=None) -> str:
        """Handle meal planner responses - FIXED ASYNC ISSUE"""
        try:
            print(f"🍽️ Handling meal response: {tool_response.get('type', 'unknown')}")
            
            # Get the response message
            response = None
            
            # Check if the response already has a formatted message
            if "message" in tool_response and tool_response["message"]:
                response = tool_response["message"]
            elif tool_response.get("type") == "meal_plan":
                response = self._format_meal_plan(tool_response["meal_plan"])
            elif tool_response.get("type") in ["ingredient_search", "general_search", "specific_meal_search"]:
                response = self._format_meal_search(tool_response)
            else:
                # Fallback for any other response type
                response = tool_response.get("message", "I found some meal options for you!")
            
            # ✅ FIXED: Only await if streamer exists and is not None
            if streamer is not None:
                try:
                    await streamer.update(response)
                except Exception as stream_error:
                    print(f"❌ Streaming error: {stream_error}")
            
            return response
        
        except Exception as e:
            print(f"❌ Error formatting meal response: {str(e)}")
            return f"I found some meal suggestions for you, but had trouble formatting the response. Error: {str(e)}"

    def _format_meal_plan(self, meal_plan: Dict[str, Any]) -> str:
        """Format full meal plan response"""
        response = f"🍽️ {meal_plan['diet_type'].title()} Meal Plan:\n\n"
        for day in meal_plan["days"]:
            response += f"{day['day']}:\n"
            for meal_type, meal_name in day['meals'].items():
                response += f"• {meal_type.title()}: {meal_name}\n"
            response += f"  (Calories: {day['nutrition'].get('calories', '?')})\n\n"
        return response

    def _format_meal_search(self, search_result: Dict[str, Any]) -> str:
        """Format meal search results - FIXED"""
        try:
            # If there's already a formatted message, use it
            if "message" in search_result and search_result["message"]:
                return search_result["message"]
            
            # Otherwise format based on type
            if search_result.get("type") == "ingredient_search":
                header = f"🔍 Found {len(search_result.get('meals', []))} meals with {search_result.get('ingredient', 'ingredient')}:\n\n"
            elif search_result.get("type") == "specific_meal_search":
                diet = search_result.get('diet_type', 'diet')
                meal = search_result.get('meal_type', 'meal')
                header = f"🍽️ {diet.title()} {meal.title()} Options:\n\n"
            else:
                header = f"🔍 Found {len(search_result.get('meals', []))} meals matching your search:\n\n"
            
            response = header
            for meal in search_result.get("meals", []):
                response += f"• {meal.get('name', 'Unknown')} ({meal.get('diet', '?')}, {meal.get('category', '?')})\n"
                if meal.get("nutrition"):
                    response += f"  Nutrition: {meal['nutrition'].get('calories', '?')} cal\n"
            return response
        except Exception as e:
            print(f"❌ Error in _format_meal_search: {str(e)}")
            return "I found some meal options for you!"

    async def _generate_llm_response(self, user_message: str, tool_response: Dict[str, Any], context: UserSessionContext, streamer=None) -> str:
        """Generate LLM response for non-meal tools"""
        try:
            system_prompt = f"""You are a health assistant. Context: {context.dict()}\nTool response: {tool_response}"""
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
            
            if streamer:
                return await self._stream_response(messages, streamer)
            
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating AI response: {str(e)}"

    async def _stream_response(self, messages: list, streamer) -> str:
        """Stream response using OpenAI"""
        full_response = ""
        try:
            stream = await self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    await streamer.update(full_response)
            
            return full_response
        except Exception as e:
            return f"Error streaming response: {str(e)}"

    def _check_handoff_conditions(self, message: str, context: UserSessionContext) -> Optional[str]:
        """Check if message requires handoff to specialized agent"""
        message_lower = message.lower()
        
        # Define handoff conditions
        handoff_conditions = {
            "escalation": ["human coach", "real trainer", "speak to someone", "human help"],
            "nutrition_expert": ["diabetes", "diabetic", "allergy", "allergic", "medical condition", "blood pressure"],
            "injury_support": ["injury", "pain", "hurt", "injured", "physical limitation", "disability"]
        }
        
        for agent_type, keywords in handoff_conditions.items():
            if any(phrase in message_lower for phrase in keywords):
                return agent_type
        
        return None

    def _determine_tool(self, message: str, context: UserSessionContext) -> Optional[str]:
        """Determine which tool to use based on message content - ENHANCED KEYWORDS"""
        message_lower = message.lower()
        
        # ✅ ENHANCED: More comprehensive tool keywords
        tool_keywords = {
            "goal_analyzer": ["gain", "lose", "build muscle", "gain muscle", "my fitness", "general fitness", "normal fitness"],
            "meal_planner": [
                "meal", "food", "diet", "eat", "nutrition", "recipe", "menu",
                "breakfast", "lunch", "dinner", "supper", "snack", "brunch",
                "vegetarian", "vegan", "keto", "ketogenic", "paleo", "gluten-free",
                "low carb", "high protein", "low fat", "dairy-free",
                "calories", "protein", "carbs", "carbohydrates", "fat", "fiber",
                "meal plan", "meal prep", "weekly meals", "daily menu",
                "what to eat", "hungry", "cook", "prepare food", "make dinner",
                "find meal", "search for", "look up", "find recipe", "recommend food",
                "suggest meals", "what can i make",
                "with ingredient", "containing", "that uses", "made with", "using",
                "recipes with", "meals with", "dishes with",
                "high protein", "low calorie", "low sugar", "balanced meal"
            ],
            "workout_recommender": [
                "workout", "exercise", "training", "gym", "fitness",
                "work out", "exercises", "train", "physical activity",
                "cardio", "strength", "weights", "lifting", "running",
                "jogging", "swimming", "cycling", "yoga", "pilates",
                "bodyweight", "calisthenics", "hiit", "crossfit",
                "beginner workout", "advanced workout", "home workout",
                "gym routine", "fitness plan", "exercise plan",
                "i need to exercise", "want to workout", "start exercising",
                "fitness routine", "training plan", "workout plan"
            ],
            "progress_tracker": [
                "progress", "update", "completed", "finished", "done",
                "what is my progress", "my progress", "track progress",
                "progress update", "how am i doing", "check progress",
                "completed workout", "finished exercise", "done with",
                "accomplished", "achieved", "success", "milestone"
            ],
            "checkin_scheduler": [
                "schedule", "remind", "check-in", "weekly", "reminder",
                "set reminder", "schedule check", "weekly check",
                "monthly check", "bi-weekly", "check in",
                "appointment", "calendar", "plan check", "remind me"
            ]
        }
        
        for tool_name, keywords in tool_keywords.items():
            if any(phrase in message_lower for phrase in keywords):
                print(f"🎯 Matched tool: {tool_name} for message: {message[:30]}...")
                return tool_name
        
        print(f"❓ No tool matched for message: {message[:30]}...")
        return None



