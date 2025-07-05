<<<<<<< HEAD
# Health & Wellness Planner Agent

An AI-powered Health & Wellness Planner Agent built with OpenAI and Streamlit.

## Features

- 🎯 **Goal Analysis**: Converts natural language goals into structured plans
- 🍽️ **Meal Planning**: Generates personalized 7-day meal plans
- 💪 **Workout Recommendations**: Creates custom workout plans based on goals
- 📅 **Progress Tracking**: Monitors and tracks user progress
- 🤝 **Specialized Agents**: Handoffs to nutrition experts, injury support, and escalation agents
- 🔒 **Guardrails**: Input/output validation for safety and accuracy
- 📱 **Real-time Streaming**: Live response streaming for better user experience

# Create .env file and add your OpenAI API key
echo "OPENAI_API_KEY=your_key_here" > .env

# Run the Streamlit app
uv run streamlit run main.py

# Or with regular Python
streamlit run main.py


## Project Structure

health_wellness_agent/
├── main.py                 # Streamlit app entry point
├── agent.py               # Main agent logic
├── context.py             # User session context
├── guardrails.py          # Input/output validation
├── hooks.py               # Lifecycle hooks for logging
├── tools/                 # Individual tools
│   ├── goal_analyzer.py
│   ├── meal_planner.py
│   ├── workout_recommender.py
│   ├── scheduler.py
│   └── tracker.py
├── agents/                # Specialized agents
│   ├── escalation_agent.py
│   ├── nutrition_expert_agent.py
│   └── injury_support_agent.py
├── utils/                 # Utilities
│   └── streaming.py
└── README.md


## Example Usage

1. **Set Goals**: "I want to lose 5kg in 2 months"
2. **Get Meal Plan**: "I'm vegetarian, can you create a meal plan?"
3. **Workout Plan**: "I'm a beginner, what exercises should I do?"
4. **Track Progress**: "I completed my workout today"
5. **Specialized Help**: "I have knee pain" (triggers injury support agent)

## Environment Variables
Create a `.env` file with:

OPENAI_API_KEY=your_openai_api_key_here



# requirements.txt
openai>=1.0.0
streamlit>=1.28.0
pydantic>=2.0.0
python-dotenv>=1.0.0
pandas>=2.0.0
asyncio

# -------------------------------------------------------------------------------
# goal analyzer
“I want to lose 5kg in 2 months”
“I want to gain 4 pounds in 4 weeks”
“I want to build muscle”

# Meal Plan Generation:
"Create a vegetarian meal plan for weight loss" 🥗

"Generate a keto meal plan with 1500 calories" 🥑

"I need a gluten-free meal plan for the week" 🌾

Ingredient Search:
"Find meals containing chicken and broccoli" 🍗🥦

"Show me recipes with avocado" 🥑

"What can I make with salmon and asparagus?" 🐟🌱

Dietary Preference Search:
"Find high-protein vegan meals" 💪🌱

"Show me low-carb dinner options" 🍽️

"What are some gluten-free breakfast ideas?" ☀️

Nutritional Search:
"Find meals under 500 calories" 🔢

"Show me high-protein lunch options" 🏋️

"What are some low-fat snack ideas?" 🍏

Meal Type Search:
"Suggest quick breakfast options" ⏰

"Find easy meal prep lunches" 🍱

"Show me fancy dinner recipes" 🎩


"I have knee pain"
"My back hurts"
"shoulder injury"
"I'm injured"
"physical limitation"

# -----------------------------------------



# **COMPLETE SEARCH KEYWORDS GUIDE**

## **SPECIALIZED AGENTS**(Files: `agents/`)

### **Escalation Agent**(`escalation_agent.py`)

**Keywords:** `human coach`, `real trainer`, `speak to someone`, `human help`
**Test Examples:**

- "I need human coach"
- "speak to someone"
- "real trainer help"


# **COMPLETE SEARCH KEYWORDS GUIDE**

## **SPECIALIZED AGENTS**(Files: `agents/`)

### **Escalation Agent**(`escalation_agent.py`)

**Keywords:** `human coach`, `real trainer`, `speak to someone`, `human help`
**Test Examples:**

- "I need human coach"
- "speak to someone"
- "real trainer help"


### **Nutrition Expert**(`nutrition_expert_agent.py`)

**Keywords:** `diabetes`, `diabetic`, `allergy`, `allergic`, `medical condition`, `blood pressure`
**Test Examples:**

- "I have diabetes"
- "allergic to nuts"
- "blood pressure diet"


# **COMPLETE SEARCH KEYWORDS GUIDE**

## **SPECIALIZED AGENTS**(Files: `agents/`)

### **Escalation Agent**(`escalation_agent.py`)

**Keywords:** `human coach`, `real trainer`, `speak to someone`, `human help`
**Test Examples:**

- "I need human coach"
- "speak to someone"
- "real trainer help"


### **Nutrition Expert**(`nutrition_expert_agent.py`)

**Keywords:** `diabetes`, `diabetic`, `allergy`, `allergic`, `medical condition`, `blood pressure`
**Test Examples:**

- "I have diabetes"
- "allergic to nuts"
- "blood pressure diet"


### **Injury Support**(`injury_support_agent.py`)

**Keywords:** `injury`, `pain`, `hurt`, `injured`, `physical limitation`, `disability`
**Test Examples:**

- "knee injury"
- "back pain"
- "hurt shoulder"

# **COMPLETE SEARCH KEYWORDS GUIDE**

## **SPECIALIZED AGENTS**(Files: `agents/`)

### **Escalation Agent**(`escalation_agent.py`)

**Keywords:** `human coach`, `real trainer`, `speak to someone`, `human help`
**Test Examples:**

- "I need human coach"
- "speak to someone"
- "real trainer help"


### **Nutrition Expert**(`nutrition_expert_agent.py`)

**Keywords:** `diabetes`, `diabetic`, `allergy`, `allergic`, `medical condition`, `blood pressure`
**Test Examples:**

- "I have diabetes"
- "allergic to nuts"
- "blood pressure diet"


### **Injury Support**(`injury_support_agent.py`)

**Keywords:** `injury`, `pain`, `hurt`, `injured`, `physical limitation`, `disability`
**Test Examples:**

- "knee injury"
- "back pain"
- "hurt shoulder"


## ️ **TOOLS**(Files: `tools/`)

### **Goal Analyzer**(`goal_analyzer.py`)

**Keywords:** `gain`, `lose`, `build muscle`, `gain muscle`, `my fitness`, `general fitness`
**Test Examples:**

- "lose 5kg"
- "gain muscle"
- "build muscle in 3 months"

### **Meal Planner**(`meal_planner.py`)

**Keywords:** `meal`, `food`, `diet`, `eat`, `nutrition`, `recipe`, `breakfast`, `lunch`, `dinner`, `vegetarian`, `vegan`, `keto`
**Test Examples:**

- "meal plan"
- "vegetarian recipes"
- "breakfast ideas"
- "find meals with chicken"

### **Workout Recommender**(`workout_recommender.py`)

**Keywords:** `workout`, `exercise`, `training`, `gym`, `fitness`
**Test Examples:**

- "workout plan"
- "beginner exercise"
- "gym training"

### **rogress Tracker**(`tracker.py`)

**Keywords:** `progress`, `update`, `completed`, `finished`
**Test Examples:**

- "completed workout"
- "finished meal"
- "progress update"


# **COMPLETE SEARCH KEYWORDS GUIDE**

## **SPECIALIZED AGENTS**(Files: `agents/`)

### **Escalation Agent**(`escalation_agent.py`)

**Keywords:** `human coach`, `real trainer`, `speak to someone`, `human help`
**Test Examples:**

- "I need human coach"
- "speak to someone"
- "real trainer help"


### **Nutrition Expert**(`nutrition_expert_agent.py`)

**Keywords:** `diabetes`, `diabetic`, `allergy`, `allergic`, `medical condition`, `blood pressure`
**Test Examples:**

- "I have diabetes"
- "allergic to nuts"
- "blood pressure diet"


### **Injury Support**(`injury_support_agent.py`)

**Keywords:** `injury`, `pain`, `hurt`, `injured`, `physical limitation`, `disability`
**Test Examples:**

- "knee injury"
- "back pain"
- "hurt shoulder"


## ️ **TOOLS**(Files: `tools/`)

### **Goal Analyzer**(`goal_analyzer.py`)

**Keywords:** `gain`, `lose`, `build muscle`, `gain muscle`, `my fitness`, `general fitness`
**Test Examples:**

- "lose 5kg"
- "gain muscle"
- "build muscle in 3 months"


### ️ **Meal Planner**(`meal_planner.py`)

**Keywords:** `meal`, `food`, `diet`, `eat`, `nutrition`, `recipe`, `breakfast`, `lunch`, `dinner`, `vegetarian`, `vegan`, `keto`
**Test Examples:**

- "meal plan"
- "vegetarian recipes"
- "breakfast ideas"
- "find meals with chicken"


### ️ **Workout Recommender**(`workout_recommender.py`)

**Keywords:** `workout`, `exercise`, `training`, `gym`, `fitness`
**Test Examples:**

- "workout plan"
- "beginner exercise"
- "gym training"


### **Progress Tracker**(`tracker.py`)

**Keywords:** `progress`, `update`, `completed`, `finished`
**Test Examples:**

- "completed workout"
- "finished meal"
- "progress update"


### **Scheduler**(`scheduler.py`)

**Keywords:** `schedule`, `remind`, `check-in`, `weekly`
**Test Examples:**

- "schedule weekly"
- "remind me"
- "weekly check-in"


"I need human coach"
"speak to someone"
"real trainer help"
Nutrition Expert(nutrition_expert_agent.py)
Keywords: diabetes, diabetic, allergy, allergic, medical condition, blood pressure Test Examples:

"I have diabetes"
"allergic to nuts"
"blood pressure diet"
Injury Support(injury_support_agent.py)
Keywords: injury, pain, hurt, injured, physical limitation, disability Test Examples:

"knee injury"
"back pain"
"hurt shoulder"
️ TOOLS(Files: tools/)
Goal Analyzer(goal_analyzer.py)
Keywords: gain, lose, build muscle, gain muscle, my fitness, general fitness Test Examples:

"lose 5kg"
"gain muscle"
"build muscle in 3 months"
️ Meal Planner(meal_planner.py)
Keywords: meal, food, diet, eat, nutrition, recipe, breakfast, lunch, dinner, vegetarian, vegan, keto Test Examples:

"meal plan"
"vegetarian recipes"
"breakfast ideas"
"find meals with chicken"
️ Workout Recommender(workout_recommender.py)
Keywords: workout, exercise, training, gym, fitness Test Examples:

"workout plan"
"beginner exercise"
"gym training"
Progress Tracker(tracker.py)
Keywords: progress, update, completed, finished Test Examples:

"completed workout"
"finished meal"
"progress update"
Scheduler(scheduler.py)
Keywords: schedule, remind, check-in, weekly Test Examples:

"schedule weekly"
"remind me"
"weekly check-in"
WORKOUT PLAN & PROGRESS TRACKING SYNCHRONIZATION
How They Work Together:
1. Set Goal First:
"I want to build muscle in 3 months"
→ goal_analyzer.py creates goal → Saves to context.goal

2. Get Workout Plan:
"I'm a beginner, suggest exercises"
→ workout_recommender.py reads context.goal → Creates personalized plan → Saves to context.workout_plan

3. Track Progress:
"I completed my workout today"
→ tracker.py logs progress → Saves to context.progress_logs

4. Schedule Check-ins:
"schedule weekly check-ins"
→ scheduler.py creates reminders → Saves to context.schedule


Environment Variables (.env file):
OPENAI_API_KEY=your_openai_api_key_here
Run Command:
streamlit run main.py



=======
# Health-Project1
>>>>>>> 2de5145d476ccfe55da9b96f04bf6241b6220771
