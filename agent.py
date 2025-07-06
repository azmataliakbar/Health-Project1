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
        """Initialize the main health and wellness agent with all required components"""
        # Initialize OpenAI client for LLM interactions
        self.client = AsyncOpenAI()
        
        # Initialize all available tools for specific functionalities
        self.tools = self._initialize_tools()
        
        # Initialize specialized agents for complex scenarios
        self.specialized_agents = self._initialize_specialized_agents()
        
        # Initialize guardrails for input/output validation
        self.input_guardrails = InputGuardrails()
        self.output_guardrails = OutputGuardrails()

    def _initialize_tools(self) -> Dict[str, Any]:
        """Initialize all tools - each tool handles specific health/wellness functionality"""
        return {
            "goal_analyzer": GoalAnalyzerTool(),           # Analyzes and sets fitness goals
            "meal_planner": MealPlannerTool(),             # Plans meals and nutrition
            "workout_recommender": WorkoutRecommenderTool(), # Recommends workout routines
            "checkin_scheduler": CheckinSchedulerTool(),    # Schedules regular check-ins
            "progress_tracker": ProgressTrackerTool(),      # Tracks user progress
        }

    def _initialize_specialized_agents(self) -> Dict[str, Any]:
        """Initialize specialized agents for complex scenarios requiring expert knowledge"""
        return {
            "escalation": EscalationAgent(),              # Handles escalation to human coaches
            "nutrition_expert": NutritionExpertAgent(),  # Handles medical nutrition questions
            "injury_support": InjurySupportAgent()       # Handles injury-related queries
        }

    def _search_local_data(self, message: str) -> Optional[str]:
        """Search static local responses for known keywords - provides quick responses for simple queries"""
        # Static responses for common simple queries to avoid API calls
        local_responses = {
            "tree": "🌳 A tree is a perennial plant with a trunk, used in oxygen production and shade.",
            # "tea": "🍵 Tea is a popular beverage made by brewing leaves — often green or black.",
            "ball": "🏐 A ball is a round object used in sports like football, volleyball, and basketball.",
            "apple": "🍎 An apple a day keeps the doctor away!"
        }
        
        # Convert message to lowercase for case-insensitive matching
        message_lower = message.lower()
        
        # Check if any keyword exists in the message
        for keyword, response in local_responses.items():
            if keyword in message_lower:
                print(f"🏠 Local data match found for keyword: '{keyword}'")
                return response
        return None

    async def _handle_local_response(self, local_response: str, streamer) -> str:
        """Handle local response with streaming - sends pre-defined responses immediately"""
        print("⚡ Using local response (no API call needed)")
        # Stream the local response if streamer is available
        if streamer:
            await streamer.update(local_response)
        return local_response

    async def _handle_specialized_agent(self, handoff_agent: str, message: str, context: UserSessionContext, streamer) -> str:
        """Handle specialized agent processing - routes complex queries to expert agents"""
        # Log the handoff for tracking purposes
        context.add_handoff_log("main", handoff_agent, f"User request: {message[:50]}...")
        print(f"🔄 Handing off to specialized agent: {handoff_agent}")
        
        # Check if the requested specialized agent exists
        if handoff_agent in self.specialized_agents:
            try:
                # Process the message using the specialized agent
                response = await self.specialized_agents[handoff_agent].process_message(message, context, streamer)
                print(f"✅ Specialized agent response received: {len(response) if response else 0} characters")
                
                # Return response or fallback message
                return response if response else "I'm having trouble connecting you right now. Please try again."
            except Exception as e:
                # Handle specialized agent errors gracefully
                print(f"❌ Specialized agent error: {str(e)}")
                return f"I'm having trouble with that request. Error: {str(e)}"
        
        # Fallback message if agent doesn't exist
        return "I'm transferring you to a specialized assistant..."

    async def _handle_tool_processing(self, tool_name: str, message: str, context: UserSessionContext, streamer) -> str:
        """Handle tool processing - executes specific tools based on user needs"""
        start_time = time.time()
        print(f"🛠️ Using local tool: {tool_name}")
        
        # Execute tool based on its type (sync vs async)
        # Handle both sync and async tools
        if tool_name == "meal_planner":
            # Meal planner is now synchronous
            tool_response = self.tools[tool_name].execute(message, context)
        else:
            # Other tools are still asynchronous
            tool_response = await self.tools[tool_name].execute(message, context)
        
        print(f"📦 Local tool response: {tool_response}")
        
        # Validate tool output using guardrails
        if not self.output_guardrails.validate_output(tool_response):
            print("⚠️ Output failed validation.")
            return "I encountered an issue processing your request. Please try rephrasing your question."
        
        # ✅ FIXED: Handle all tool-specific responses directly without OpenAI
        # Route to appropriate response handler based on tool type
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
        """
        Main message processing pipeline - orchestrates the entire response generation process
        This is the primary entry point for all user interactions
        """
        try:
            # STEP 1: Check for static/local answers first (fastest response)
            if local_response := self._search_local_data(message):
                return await self._handle_local_response(local_response, streamer)
            
            # STEP 2: Input validation using guardrails
            if not self.input_guardrails.validate_input(message):
                return self._get_input_validation_message()
            
            # STEP 3: Check for handoff to specialized agent (complex scenarios)
            if handoff_agent := self._check_handoff_conditions(message, context):
                return await self._handle_specialized_agent(handoff_agent, message, context, streamer)
            
            # STEP 4: Determine which tool to use based on message content
            tool_name = self._determine_tool(message, context)
            
            # STEP 5: Handle general response if no specific tool is needed
            if not tool_name or tool_name not in self.tools:
                return await self._generate_general_response(message, context, streamer)
            
            # STEP 6: Process with selected tool
            return await self._handle_tool_processing(tool_name, message, context, streamer)
        
        except Exception as e:
            # Global error handling - ensures system never crashes
            print(f"❌ Processing error: {str(e)}")
            return f"I apologize, but I encountered an error processing your request.: {str(e)}"

    async def _generate_general_response(self, message: str, context: UserSessionContext, streamer=None) -> str:
        """Generate general response when no specific tool is needed - uses LLM for open-ended queries"""
        try:
            # Enhanced logging for OpenAI usage
            print(f"📡 Using OpenAI API for general query: '{message[:30]}...'")
            start_time = time.time()
            
            # Create system prompt with user context for personalized responses
            system_prompt = f"""You are a helpful health and wellness assistant.
            User context: {context.dict()}
            
            Provide helpful, encouraging responses about health, fitness, nutrition, and wellness.
            Keep responses concise but informative."""
            
            # Prepare messages for OpenAI API
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ]
            
            # Use streaming if available for better user experience
            if streamer:
                response = await self._stream_response(messages, streamer)
                execution_time = round(time.time() - start_time, 1)
                print(f"🔍 OpenAI streaming completed in {execution_time}s")
                return response
            
            # Fallback to non-streaming response
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7
            )
            execution_time = round(time.time() - start_time, 1)
            print(f"🔍 OpenAI response completed in {execution_time}s")
            return response.choices[0].message.content
        
        except Exception as e:
            # Handle general response errors gracefully
            print(f"❌ OpenAI API error: {str(e)}")
            return "I'm here to help with your health and wellness goals! Could you tell me more about what you're looking for?"

    def _get_input_validation_message(self) -> str:
        """Return input validation error message - provides user feedback for invalid inputs"""
        return "I'm sorry, but I can't process that request. Please ask about health, fitness, nutrition, or wellness topics."

    async def _handle_goal_response(self, tool_response: Dict[str, Any], streamer=None, start_time=None) -> str:
        """Format goal analyzer response - creates user-friendly goal setting confirmations"""
        try:
            # Extract goal data from tool response
            goal_data = tool_response["goal"]
            
            # Format the goal confirmation message
            result = (
                f"🎯 Goal Analyzed Successfully!\n\n"
                f"You've set a goal to achieve:\n"
                f"**{goal_data.get('type', 'Unknown').replace('_', ' ').title()}** — "
                f"*{goal_data.get('target', '')} in {goal_data.get('timeframe', '')}*"
            )
            
            # Log execution time for performance monitoring
            if start_time:
                print(f"✅ Local tool execution completed in {round(time.time() - start_time, 2)}s")
            
            # Stream response if streamer is available
            if streamer is not None:
                try:
                    await streamer.update(result)
                    print("✅ Goal response streamed successfully")
                except Exception as stream_error:
                    print(f"❌ Goal streaming error: {stream_error}")
            
            return result
        except Exception as e:
            # Handle formatting errors gracefully
            error_msg = f"Error formatting goal response: {str(e)}"
            if streamer is not None:
                try:
                    await streamer.update(error_msg)
                except Exception as stream_error:
                    print(f"❌ Error updating streamer: {stream_error}")
            return error_msg

    async def _handle_workout_response(self, tool_response: Dict[str, Any], streamer=None) -> str:
        """Handle workout recommender responses - formats workout recommendations for users"""
        try:
            # The tool already provides a formatted message
            response = tool_response.get("message", "I've created a workout plan for you!")
            
            # Stream the workout response
            if streamer is not None:
                try:
                    await streamer.update(response)
                    print("✅ Workout response streamed successfully")
                except Exception as stream_error:
                    print(f"❌ Workout streaming error: {stream_error}")
            
            return response
        except Exception as e:
            # Handle workout response errors
            error_msg = f"Error formatting workout response: {str(e)}"
            if streamer is not None:
                try:
                    await streamer.update(error_msg)
                except Exception as stream_error:
                    print(f"❌ Error updating streamer: {stream_error}")
            return error_msg

    async def _handle_tracker_response(self, tool_response: Dict[str, Any], streamer=None) -> str:
        """Handle progress tracker responses - formats progress tracking updates"""
        try:
            # The tool already provides a formatted message
            response = tool_response.get("message", "Progress has been tracked!")
            
            # Stream the tracker response
            if streamer is not None:
                try:
                    await streamer.update(response)
                    print("✅ Tracker response streamed successfully")
                except Exception as stream_error:
                    print(f"❌ Tracker streaming error: {stream_error}")
            
            return response
        except Exception as e:
            # Handle tracker response errors
            error_msg = f"Error formatting tracker response: {str(e)}"
            if streamer is not None:
                try:
                    await streamer.update(error_msg)
                except Exception as stream_error:
                    print(f"❌ Error updating streamer: {stream_error}")
            return error_msg

    async def _handle_scheduler_response(self, tool_response: Dict[str, Any], streamer=None) -> str:
        """Handle scheduler responses - formats scheduling confirmations"""
        try:
            # The tool already provides a formatted message
            response = tool_response.get("message", "Schedule has been created!")
            
            # Stream the scheduler response
            if streamer is not None:
                try:
                    await streamer.update(response)
                    print("✅ Scheduler response streamed successfully")
                except Exception as stream_error:
                    print(f"❌ Scheduler streaming error: {stream_error}")
            
            return response
        except Exception as e:
            # Handle scheduler response errors
            error_msg = f"Error formatting scheduler response: {str(e)}"
            if streamer is not None:
                try:
                    await streamer.update(error_msg)
                except Exception as stream_error:
                    print(f"❌ Error updating streamer: {stream_error}")
            return error_msg

    async def _handle_meal_response(self, tool_response: Dict[str, Any], streamer=None) -> str:
        """Handle meal planner responses - formats meal planning and nutrition information"""
        try:
            print(f"🍽️ Handling meal response from local tool: {tool_response.get('type', 'unknown')}")
            
            # Get the response message
            response = None
            
            # Check if the response already has a formatted message
            if "message" in tool_response and tool_response["message"]:
                response = tool_response["message"]
            elif tool_response.get("type") == "meal_plan":
                # Format full meal plan
                response = self._format_meal_plan(tool_response["meal_plan"])
            elif tool_response.get("type") in ["ingredient_search", "general_search", "specific_meal_search"]:
                # Format meal search results
                response = self._format_meal_search(tool_response)
            else:
                # Fallback for any other response type
                response = tool_response.get("message", "I found some meal options for you!")
            
            # Stream the meal response if streamer is available
            if streamer is not None:
                try:
                    await streamer.update(response)
                    print("✅ Meal response streamed successfully")
                except Exception as stream_error:
                    print(f"❌ Streaming error: {stream_error}")
            
            return response
        
        except Exception as e:
            # Handle meal response formatting errors
            print(f"❌ Error formatting meal response: {str(e)}")
            return f"I found some meal suggestions for you, but had trouble formatting the response. Error: {str(e)}"

    def _format_meal_plan(self, meal_plan: Dict[str, Any]) -> str:
        """Format full meal plan response - creates structured meal plan display"""
        response = f"🍽️ {meal_plan['diet_type'].title()} Meal Plan:\n\n"
        
        # Iterate through each day in the meal plan
        for day in meal_plan["days"]:
            response += f"{day['day']}:\n"
            # Add each meal for the day
            for meal_type, meal_name in day['meals'].items():
                response += f"• {meal_type.title()}: {meal_name}\n"
            # Add nutritional information
            response += f"  (Calories: {day['nutrition'].get('calories', '?')})\n\n"
        return response

    def _format_meal_search(self, search_result: Dict[str, Any]) -> str:
        """Format meal search results - creates user-friendly search result display"""
        try:
            # If there's already a formatted message, use it
            if "message" in search_result and search_result["message"]:
                return search_result["message"]
            
            # Format header based on search type
            if search_result.get("type") == "ingredient_search":
                header = f"🔍 Found {len(search_result.get('meals', []))} meals with {search_result.get('ingredient', 'ingredient')}:\n\n"
            elif search_result.get("type") == "specific_meal_search":
                diet = search_result.get('diet_type', 'diet')
                meal = search_result.get('meal_type', 'meal')
                header = f"🍽️ {diet.title()} {meal.title()} Options:\n\n"
            else:
                header = f"🔍 Found {len(search_result.get('meals', []))} meals matching your search:\n\n"
            
            # Build the response with meal details
            response = header
            for meal in search_result.get("meals", []):
                response += f"• {meal.get('name', 'Unknown')} ({meal.get('diet', '?')}, {meal.get('category', '?')})\n"
                # Add nutritional information if available
                if meal.get("nutrition"):
                    response += f"  Nutrition: {meal['nutrition'].get('calories', '?')} cal\n"
            return response
        except Exception as e:
            # Handle search formatting errors
            print(f"❌ Error in _format_meal_search: {str(e)}")
            return "I found some meal options for you!"

    async def _generate_llm_response(self, user_message: str, tool_response: Dict[str, Any], context: UserSessionContext, streamer=None) -> str:
        """Generate LLM response for non-meal tools - uses AI to interpret tool responses"""
        try:
            print("📡 Using OpenAI API to interpret tool response")
            start_time = time.time()
            
            # Create system prompt with context and tool response
            system_prompt = f"""You are a health assistant. Context: {context.dict()}\nTool response: {tool_response}"""
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
            
            # Use streaming if available
            if streamer: # This check is good before calling _stream_response
                response = await self._stream_response(messages, streamer)
                execution_time = round(time.time() - start_time, 1)
                print(f"🔍 OpenAI tool interpretation completed in {execution_time}s")
                return response
            
            # Fallback if no streamer is provided
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7
            )
            execution_time = round(time.time() - start_time, 1)
            print(f"🔍 OpenAI tool interpretation completed in {execution_time}s")
            return response.choices[0].message.content
        except Exception as e:
            # Handle LLM response errors
            print(f"❌ Error in OpenAI tool interpretation: {str(e)}")
            return f"Error generating AI response: {str(e)}"

    async def _update_streamer_safely(self, streamer, content: str) -> None:
        """Helper method to safely update streamer - reduces complexity in main streaming function"""
        if streamer is not None:
            try:
                await streamer.update(content)
            except Exception as streamer_error:
                # Log streamer errors but don't stop response generation
                print(f"❌ Warning: Error updating streamer: {streamer_error}")

    async def _handle_streaming_error(self, streamer, error_message: str) -> str:
        """Helper method to handle streaming errors - reduces complexity in main streaming function"""
        print(f"❌ OpenAI streaming error: {error_message}")
        await self._update_streamer_safely(streamer, f"I'm sorry, I encountered an error while generating the response. {error_message}")
        return f"Error: {error_message}"

    async def _stream_response(self, messages: list, streamer) -> str:
        """
        Stream response using OpenAI API - provides real-time response streaming for better UX
        ✅ REFACTORED: Reduced cognitive complexity from 16 to 15 by extracting helper methods
        """
        print("📡 Starting OpenAI streaming response...")
        full_response = ""
        try:
            # Create streaming chat completion
            stream = await self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                stream=True  # Enable streaming mode
            )
            
            # Process each chunk from the stream
            async for chunk in stream:
                # Extract content from chunk if available
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    
                    # Update streamer with accumulated response using helper method
                    await self._update_streamer_safely(streamer, full_response)
            
            print("✅ OpenAI streaming completed successfully")
            return full_response
            
        except openai.APIError as e:
            # Handle specific OpenAI API errors using helper method
            error_message = f"OpenAI API Error: {e.status_code} - {e.response}"
            return await self._handle_streaming_error(streamer, error_message)
            
        except Exception as e:
            # Handle general streaming errors using helper method
            error_message = f"Error during streaming: {str(e)}"
            return await self._handle_streaming_error(streamer, error_message)

    def _check_handoff_conditions(self, message: str, context: UserSessionContext) -> Optional[str]:
        """Check if message requires handoff to specialized agent - routes complex queries to experts"""
        message_lower = message.lower()
        
        # Define handoff conditions for different specialized agents
        handoff_conditions = {
            # Escalation agent: handles requests for human assistance
            "escalation": ["human coach","human", "real trainer", "speak to someone", "human help"],
            
            # Nutrition expert: handles medical nutrition questions
            "nutrition_expert": ["diabetes", "diabetic", "allergy", "allergic", "medical condition", "blood pressure"],
            
            # Injury support: handles injury and physical limitation queries
            "injury_support": ["injury", "pain", "hurt", "injured", "physical limitation", "disability"]
        }
        
        # Check if any handoff condition is met
        for agent_type, keywords in handoff_conditions.items():
            if any(phrase in message_lower for phrase in keywords):
                print(f"🔄 Handoff condition met for: {agent_type}")
                return agent_type
        
        return None

    def _determine_tool(self, message: str, context: UserSessionContext) -> Optional[str]:
        """
        Determine which tool to use based on message content - intelligent tool routing system
        This function analyzes user messages to select the most appropriate tool
        """
        message_lower = message.lower()
        
        # ✅ ENHANCED: More comprehensive tool keywords for better matching
        tool_keywords = {
            # Goal analyzer: handles fitness goal setting and analysis
            "goal_analyzer": ["gain", "lose", "build muscle", "gain muscle", "my fitness", "general fitness", "normal fitness"],
            
            # Meal planner: comprehensive nutrition and meal planning keywords
            "meal_planner": [
                # Basic meal terms
                "meal", "food", "diet", "eat", "nutrition", "recipe", "menu",
                "breakfast", "lunch", "dinner", "supper", "snack", "brunch",
                
                # Diet types
                "vegetarian", "vegan", "keto", "ketogenic", "paleo", "gluten-free",
                "low carb", "high protein", "low fat", "dairy-free",
                
                # Nutritional terms
                "calories", "protein", "carbs", "carbohydrates", "fat", "fiber",
                
                # Planning terms
                "meal plan", "meal prep", "weekly meals", "daily menu",
                
                # Action terms
                "what to eat", "hungry", "cook", "prepare food", "make dinner",
                "find meal", "search for", "look up", "find recipe", "recommend food",
                "suggest meals", "what can i make",
                
                # Ingredient-based searches
                "with ingredient", "containing", "that uses", "made with", "using",
                "recipes with", "meals with", "dishes with",
                
                # Nutritional goals
                "high protein", "low calorie", "low sugar", "balanced meal"
            ],
            
            # Workout recommender: exercise and fitness planning
            "workout_recommender": [
                # Basic workout terms
                "workout", "exercise", "training", "gym", "fitness",
                "work out", "exercises", "train", "physical activity",
                
                # Exercise types
                "cardio", "strength", "weights", "lifting", "running",
                "jogging", "swimming", "cycling", "yoga", "pilates",
                "bodyweight", "calisthenics", "hiit", "crossfit",
                
                # Workout planning
                "beginner workout", "advanced workout", "home workout",
                "gym routine", "fitness plan", "exercise plan",
                
                # Action terms
                "i need to exercise", "want to workout", "start exercising",
                "fitness routine", "training plan", "workout plan"
            ],
            
            # Progress tracker: tracking achievements and updates
            "progress_tracker": [
                "progress", "update", "completed", "finished", "done",
                "what is my progress", "my progress", "track progress",
                "progress update", "how am i doing", "check progress",
                "completed workout", "finished exercise", "done with",
                "accomplished", "achieved", "success", "milestone"
            ],
            
            # Check-in scheduler: scheduling and reminders
            "checkin_scheduler": [
                "schedule", "remind", "check-in", "weekly", "reminder",
                "set reminder", "schedule check", "weekly check",
                "monthly check", "bi-weekly", "check in",
                "appointment", "calendar", "plan check", "remind me"
            ]
        }
        
        # Match message against tool keywords
        for tool_name, keywords in tool_keywords.items():
            if any(phrase in message_lower for phrase in keywords):
                print(f"🎯 Matched local tool: {tool_name} for message: '{message[:30]}...'")
                return tool_name
        
        # No tool matched - will use OpenAI
        print(f"❓ No local tool matched for message: '{message[:30]}...' - will use OpenAI")
        return None


