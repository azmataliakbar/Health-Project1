import streamlit as st          # UI rendering
import asyncio
import time
from agent import HealthWellnessAgent
from context import UserSessionContext
from utils.streaming import StreamlitStreamer
import os
from dotenv import load_dotenv    # Load .env variables

# Constants
NONE_SELECTED = "None Selected"

# 📥 Load environment variables (e.g. OpenAI API key)
load_dotenv()

# 🎨 Set up the Streamlit page layout and appearance
st.set_page_config(
    page_title="Health & Wellness Planner",
    page_icon="💪",
    layout="wide")

def initialize_session_state():
    """Initialize all session state variables"""
    if 'context' not in st.session_state:
        st.session_state.context = UserSessionContext(name="User", uid=1)
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'agent' not in st.session_state:
        st.session_state.agent = HealthWellnessAgent()
    if "goal_updated" not in st.session_state:
        st.session_state.goal_updated = False
    # ✅ NEW: Initialize workout and progress tracking states
    if 'current_workout_plan' not in st.session_state:
        st.session_state.current_workout_plan = None
    if 'progress_entries' not in st.session_state:
        st.session_state.progress_entries = []

# 🔰 UI SECTION RENDER FUNCTIONS
def render_header():
    """Render the main header section"""
    st.markdown("<div style='color:red;font-size:40px; font-weight: bold'>💪🏋️‍♂️🦥 Health & Wellness Planner Agent 🦥🚴‍♂️🏃‍♀️</div>", unsafe_allow_html=True)
    st.markdown("<div style='color:orange;font-size:25px;'>🤖📱 Your AI-powered wellness assistant for personalized health plans! 💻</div>", unsafe_allow_html=True)

def render_health_tips():
    """Render the health tips section"""
    st.markdown("""
    <div style='margin-top: 20px; margin-bottom: 20px;'>
        <details>
            <summary style='font-size: 20px; font-weight: bold; color: #4CAF50; cursor: pointer;'>
                🌿 General Health Care Tips
            </summary>
            <div style='background-color: #f0f8ff; padding: 20px; border-radius: 5px; margin-t10px;'>
                <ul style='font-size: 20px; font-weight: bold; color: #2e7d32;'>
                    <li>🌅 Wake up early in the morning</li>
                    <li>🏋️‍♂️ Do some exercises daily</li>
                    <li>🍳 Take a healthy breakfast</li>
                    <li>🥗 Choose always healthy food for lunch & dinner</li>
                    <li>⚽ Involve in healthy sports activities</li>
                    <li>📚 Study health-related books</li>
                    <li>🌳 Live in a healthy environment</li>
                    <li>😴 Sleep early and on time</li>
                    <li>❤️ Love and respect all humanity</li>
                    <li>🏥 If facing health issues, always follow doctor's instructions</li>
                </ul>
            </div>
        </details>
    </div>
    """, unsafe_allow_html=True)

def render_goal_tips():
    """Render the goal format tips section"""
    st.markdown("""
    <div style='margin-top: 20px; margin-bottom: 20px;'>
        <details>
            <summary style='font-size: 20px; font-weight: bold; color: #4CAF50; cursor: pointer;'>
                💡 **Tip:** For best results, phrase your search like this:
            </summary>
            <div style='background-color: #f0f8ff; padding: 16px; border-radius: 5px; margin-t10px;'>
                <ul style='font-size: 20px; font-weight: bold; color: #2e7d32;'>
                    <li>---------------------------------------------------------</li>
                    <li>📞 "I need to speak to a human coach"</li>
                    <li>🧑‍🏫 "Is there a real trainer I can talk to?"</li>
                    <li>🆘 "Please escalate to a human help"</li>
                    <li>🙋 "Can I talk to someone directly?"</li>
                    <li>☎️ "I need real support from a human"</li>
                    <li>---------------------------------------------------------</li>
                    <li>🩸 "I have diabetes, what should I eat?"</li>
                    <li>⚠️ "I’m allergic to nuts, suggest alternatives"</li>
                    <li>❤️ "I have high blood pressure, recommend a diet"</li>
                    <li>🍽️ "Need help with diabetic meal planning"</li>
                    <li>🧬 "Nutrition advice for medical condition"</li>
                    <li>🌡️ "I’m allergic and need special food plan"</li>
                    <li>---------------------------------------------------------</li>
                    <li>🤕 "I have an injury, what workout can I do?"</li>
                    <li>🏥 "Pain in my knee — suggest safe exercises"</li>
                    <li>🦽 "I have a disability, need fitness guidance"</li>
                    <li>🦴 "I’m recovering from injury, help with routine"</li>
                    <li>🚧 "Physical limitation — need adapted workout"</li>
                    <li>---------------------------------------------------------</li>
                    <li>📈 "I want to gain 5 kg in 3 months"</li>
                    <li>📉 "I want to lose 10 kg in 4 months"</li>
                    <li>💪 "I want to build muscle in 4 months"</li>
                    <li>🏃 "My fitness in 2 months"</li>
                    <li>🌱 "General fitness in 2 months"</li>
                    <li>⚖️ "I want to maintain my weight and get fit"</li>
                    <li>🥵 "Lose belly fat in 6 weeks"</li>
                    <li>🍱 "Suggest a balanced meal for lunch"</li>
                    <li>🥗 "I need a vegetarian meal plan"</li>
                    <li>🍳 "What should I eat for breakfast?"</li>
                    <li>🥩 "Looking for high protein dinners"</li>
                    <li>🧁 "Low sugar snack ideas please"</li>
                    <li>🥘 "Weekly food plan for keto diet"</li>
                    <li>🍓 "Give me meals using strawberries"</li>
                    <li>🧾 "Find a recipe for dinner tonight"</li>
                    <li>---------------------------------------------------------</li>
                    <li>🏋️ "Give me a beginner workout plan"</li>
                    <li>🤸 "I want to start home exercises"</li>
                    <li>🚴 "Best cardio workout for weight loss"</li>
                    <li>🧘 "Yoga routine for daily flexibility"</li>
                    <li>🏃 "Running plan for 5k training"</li>
                    <li>💪 "Strength training ideas for muscle gain"</li>
                    <li>🗓️ "Suggest a 7-day workout routine"</li>
                    <li>🔥 "Intense HIIT workout for fat burning"</li>
                    <li>---------------------------------------------------------</li>
                    <li>📊 "Show me my fitness progress"</li>
                    <li>✅ "Track my completed workouts"</li>
                    <li>🎯 "How much have I achieved so far?"</li>
                    <li>📅 "Weekly progress update please"</li>
                    <li>🏁 "What’s my current milestone?"</li>
                    <li>📈 "How am I doing with my goals?"</li>
                    <li>---------------------------------------------------------</li>
                    <li>⏰ "Set a weekly check-in reminder"</li>
                    <li>🗓️ "Schedule my next progress update"</li>
                    <li>🔔 "Remind me to exercise tomorrow"</li>
                    <li>📆 "Plan a monthly fitness check"</li>
                    <li>📍 "Add a calendar entry for my diet review"</li>
                    <li>🕒 "Set a bi-weekly health appointment"</li>
                    <li>---------------------------------------------------------</li>
                </ul>
            </div>
        </details>
    </div>
    """, unsafe_allow_html=True)

def render_chat_history():
    """Render existing chat messages"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(f"<div style='font-size:25px;color:#f0f0f0'>{message['content']}</div>", unsafe_allow_html=True)

async def process_user_input(prompt: str):
    """Process user input and generate response"""
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(f"<div style='font-size:25px; color:orange'>{prompt}</div>", unsafe_allow_html=True)
    
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        streamer = StreamlitStreamer(response_placeholder)
        try:
            search_start = time.time()
            response = await st.session_state.agent.process_message(
                prompt,
                st.session_state.context,
                streamer
            )
            
            # 🆕 Update UI flags based on content of the response
            if "Goal Analyzed Successfully!" in response:
                st.session_state.goal_updated = True
            elif "Workout Plan Created!" in response:
                # Extract workout plan info from response
                st.session_state.current_workout_plan = {
                    "created_at": time.strftime("%Y-%m-%d %H:%M"),
                    "prompt": prompt,
                    "response": response
                }
            elif "Progress logged successfully!" in response:
                # Add progress entry
                st.session_state.progress_entries.append({
                    "date": time.strftime("%Y-%m-%d"),
                    "time": time.strftime("%H:%M"),
                    "activity": prompt,
                    "response": response
                })
            
            # Add assistant response
            search_end = time.time()
            duration = round(search_end - search_start, 2)
            st.session_state.messages.append({
                "role": "assistant",
                "content": response
            })
            
            # Show how long the search took, display it
            st.markdown("---")
            st.markdown("### 🔍 <span style='color:#61dafb'>Health Agent Search Duration</span>", unsafe_allow_html=True)
            st.markdown(f"✅ <span style='color:lightgreen; font-size:25px;'>Search result completed in {duration}s</span>", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"I encountered an error: {str(e)}"
            })

# 🧍 Sidebar Section: User Profile
def render_user_profile_section():
    """Render user profile section in sidebar"""
    st.markdown("<div style='color:blue;font-size:35px;font-weight:bold;'>🧑‍🏫 User Profile</div>", unsafe_allow_html=True)
    name = st.text_input("🧑‍🏫 Name", value=st.session_state.context.name)
    if name != st.session_state.context.name:
        st.session_state.context.name = name
    return name

# 🎯 Sidebar Section: Goals
def render_goals_section():
    """Render current goals section in sidebar"""
    st.markdown("<div style='color:orange;font-size:25px;font-weight:bold;'>📊 Current Goals</div>", unsafe_allow_html=True)
    if st.session_state.context.goal:
        st.json(st.session_state.context.goal)
    else:
        st.markdown("💡 Set a goal like: *'I want to lose 5kg in 2 months'*")

# 🍽️ Sidebar Section: Diet Preferences
def _update_diet_preferences(diet_type: str, allergies: list, meal_prefs: list, calorie_goal: int):
    """Update diet preferences in context"""
    st.session_state.context.diet_preferences = {
        "diet_type": diet_type if diet_type != NONE_SELECTED else None,
        "allergies": allergies,
        "meal_preferences": meal_prefs,
        "calorie_goal": calorie_goal
    }

def _show_diet_preferences():
    """Show current diet preferences"""
    st.success("✅ Preferences saved!")
    with st.expander("View your preferences"):
        prefs = st.session_state.context.diet_preferences
        if prefs.get("diet_type"):
            st.write(f"🥗 Diet: {prefs['diet_type']}")
        if prefs.get("allergies"):
            st.write(f"🚫 Allergies: {', '.join(prefs['allergies'])}")
        if prefs.get("meal_preferences"):
            st.write(f"⭐ Preferences: {', '.join(prefs['meal_preferences'])}")
        st.write(f"🔥 Calorie Goal: {prefs['calorie_goal']}")

def render_diet_preferences_section():
    """Render active diet preferences section in sidebar"""
    st.markdown("<div style='color:mediumpurple;font-size:25px;font-weight:bold;'>🍽️ Diet Preferences</div>", unsafe_allow_html=True)
    
    # Diet Type Selection
    diet_type = st.selectbox(
        "Select your diet type:",
        [NONE_SELECTED, "Vegetarian", "Vegan", "Keto", "Paleo", "Mediterranean", "DASH", "Low Carb", "High Protein", "Gluten-Free", "Dairy-Free"],
        index=0
    )
    
    # Food Allergies/Restrictions
    allergies = st.multiselect(
        "Food allergies/restrictions:",
        ["Nuts", "Dairy", "Gluten", "Shellfish", "Eggs", "Soy", "Fish", "Sesame"],
        default=[]
    )
    
    # Meal Preferences
    meal_prefs = st.multiselect(
        "Meal preferences:",
        ["Quick meals (under 30 min)", "Meal prep friendly", "One-pot meals", "Raw foods", "Smoothies", "High fiber", "Low sodium"],
        default=[]
    )
    
    # Calorie Goal
    calorie_goal = st.number_input("Daily calorie goal (optional):", min_value=1000, max_value=4000, value=2000, step=100)
    
    # Update context when preferences change
    if diet_type != NONE_SELECTED or allergies or meal_prefs:
        _update_diet_preferences(diet_type, allergies, meal_prefs, calorie_goal)
        
        # Show current preferences
        if st.session_state.context.diet_preferences:
            _show_diet_preferences()
    else:
        st.markdown("💡 Select your dietary preferences above")

# 🏋️ Sidebar Section: Workout Planner
def render_workout_plan_section():
    """✅ NEW: Enhanced interactive workout plan section"""
    st.markdown("<div style='color:lightgreen;font-size:25px;font-weight:bold;'>💪 Workout Plan</div>", unsafe_allow_html=True)
    
    # Quick action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🏃 Get Beginner Plan", key="beginner_workout"):
            st.session_state.workout_request = "I'm a beginner, suggest exercises"
            st.rerun()
    with col2:
        if st.button("💪 Get Advanced Plan", key="advanced_workout"):
            st.session_state.workout_request = "I'm advanced, suggest workout"
            st.rerun()
    
    # Experience level selector
    experience = st.selectbox(
        "Your fitness level:",
        ["Beginner", "Intermediate", "Advanced"],
        key="fitness_level"
    )
    
    if st.button(f"📋 Get {experience} Workout Plan", key="custom_workout"):
        st.session_state.workout_request = f"I'm {experience.lower()}, create workout plan"
        st.rerun()
    
    # Show current workout plan if exists
    if st.session_state.current_workout_plan:
        st.markdown("### 📋 Current Workout Plan")
        with st.expander("View Current Plan", expanded=True):
            plan = st.session_state.current_workout_plan
            st.markdown(f"**Created:** {plan['created_at']}")
            st.markdown(f"**Request:** {plan['prompt']}")
            st.markdown("**Plan Details:**")
            # Extract key info from response
            if "Exercises:" in plan['response']:
                exercises_part = plan['response'].split("Exercises:")[1].split("Duration:")[0].strip()
                st.markdown(f"🏋️ **Exercises:** {exercises_part}")
    else:
        st.markdown("💡 **Defining, how to use:**")
        st.markdown("• Click buttons above for quick plans")
        st.markdown("• Or type: *'I'm a beginner, suggest exercises'*")
        st.markdown("• Or type: *'Create workout plan for weight loss'*")

# 📈 Sidebar Section: Progress Tracking
def render_progress_tracking_section():
    """✅ NEW: Enhanced interactive progress tracking section"""
    st.markdown("<div style='color:deeppink;font-size:25px;font-weight:bold;'>📈 Progress Tracking</div>", unsafe_allow_html=True)
    
    # Quick log buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Log Workout", key="log_workout"):
            st.session_state.progress_request = "I completed my workout today"
            st.rerun()
    with col2:
        if st.button("📊 Check Progress", key="check_progress"):
            st.session_state.progress_request = "what is my progress"
            st.rerun()
    
    # Custom progress entry
    activity_type = st.selectbox(
        "Activity type:",
        ["Workout", "Cardio", "Strength Training", "Yoga", "Walking", "Other"],
        key="activity_type"
    )
    
    if st.button(f"📝 Log {activity_type}", key="log_custom"):
        st.session_state.progress_request = f"I completed {activity_type.lower()} today"
        st.rerun()
    
    # Show recent progress entries
    if st.session_state.progress_entries:
        st.markdown("### 📊 Recent Progress")
        with st.expander("View Progress History", expanded=True):
            # Show last 5 entries
            recent_entries = st.session_state.progress_entries[-5:]
            for entry in reversed(recent_entries):
                st.markdown(f"**{entry['date']} {entry['time']}**")
                st.markdown(f"Activity: {entry['activity']}")
                st.markdown("---")
    else:
        st.markdown("💡 **How to use:**")
        st.markdown("• Click buttons above to log activities")
        st.markdown("• Or type: *'I completed my workout today'*")
        st.markdown("• Or type: *'I finished 30 minutes of cardio'*")
        st.markdown("• Or type: *'what is my progress'*")

# 📅 Sidebar Section: Scheduler
def render_scheduler_section():
    """✅ NEW: Interactive scheduler section"""
    st.markdown("<div style='color:orange;font-size:25px;font-weight:bold;'>📅 Schedule & Reminders</div>", unsafe_allow_html=True)
    
    # Quick schedule buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⏰ Weekly Check-in", key="weekly_schedule"):
            st.session_state.schedule_request = "schedule weekly check-in"
            st.rerun()
    with col2:
        if st.button("🗓️ Monthly Review", key="monthly_schedule"):
            st.session_state.schedule_request = "schedule monthly review"
            st.rerun()
    
    # Custom frequency
    frequency = st.selectbox(
        "Check-in frequency:",
        ["Weekly", "Bi-weekly", "Monthly"],
        key="checkin_frequency"
    )
    
    if st.button(f"⏰ Set {frequency} Reminders", key="custom_schedule"):
        st.session_state.schedule_request = f"schedule {frequency.lower()} check-in"
        st.rerun()
    
    st.markdown("💡 **How to use:**")
    st.markdown("• Click buttons above for quick scheduling")
    st.markdown("• Or type: *'remind me weekly'*")
    st.markdown("• Or type: *'schedule monthly check-in'*")

# 🧹 Sidebar Section: Clear Chat History
def render_clear_chat_section(name: str):
    """Render clear chat section in sidebar"""
    st.markdown("<div style='color:red;font-size:25px;font-weight:bold;'>🗑️🧹 Clear Chat History</div>", unsafe_allow_html=True)
    if st.button("🧹 Clear Chat History"):
        st.session_state.messages = []
        st.session_state.context = UserSessionContext(name=name, uid=1)
        st.session_state.goal_updated = False
        # ✅ NEW: Also clear workout and progress data
        st.session_state.current_workout_plan = None
        st.session_state.progress_entries = []
        st.rerun()

# 📜👣 Footer
def render_footer():
    """👣 Render footer section"""
    st.markdown("---")
    st.markdown("👨‍🏫 <span style='font-size:25px'>Mentor: <b style='color:#ffaa00'>Aneeq Khatri</b></span>", unsafe_allow_html=True)
    st.markdown("🧑‍💻 <span style='font-size:25px'>Author: <b style='color:#33ddff'>Azmat Ali</b></span>", unsafe_allow_html=True)

# 🧠 Sidebar Request Handler (automated logic trigger)
async def handle_sidebar_requests():
    """🚀 Trigger action based on which sidebar button was pressed"""
    if hasattr(st.session_state, 'workout_request'):
        await process_user_input(st.session_state.workout_request)
        del st.session_state.workout_request
    
    if hasattr(st.session_state, 'progress_request'):
        await process_user_input(st.session_state.progress_request)
        del st.session_state.progress_request
    
    if hasattr(st.session_state, 'schedule_request'):
        await process_user_input(st.session_state.schedule_request)
        del st.session_state.schedule_request

# 🚀 Main App Runner
async def main():
    """Main application function - enhanced with interactive sidebar"""
    # Initialize session state
    initialize_session_state()
    
    # Handle sidebar button requests first
    await handle_sidebar_requests()
    
    # Render header sections
    render_header()
    render_health_tips()
    render_goal_tips()
    
    # Render chat input and history
    chat_container = st.container()
    with chat_container:
        render_chat_history()
        st.markdown("### 🧠 <span style='color:blue'>Tell me about your health goals...</span>", unsafe_allow_html=True)
        prompt = st.chat_input("Type your health goal here...")
        if prompt:
            await process_user_input(prompt)
    
    # ✅ Render: Interactive sidebar sections
    with st.sidebar:
        name = render_user_profile_section()
        render_goals_section()
        render_diet_preferences_section()
        render_workout_plan_section()  # Enhanced
        render_progress_tracking_section()  # Enhanced
        render_scheduler_section()  # New
        render_clear_chat_section(name)
        
        # Reset the flag after sidebar is rendered
        if st.session_state.goal_updated:
            st.session_state.goal_updated = False
    
    # Footer
    render_footer()

if __name__ == "__main__":
    asyncio.run(main())

