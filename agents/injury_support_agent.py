from typing import Dict, Any
from context import UserSessionContext
import asyncio

class InjurySupportAgent:
    """Specialized agent for injury-related fitness modifications"""
    
    def __init__(self):
        self.injury_modifications = {
            "knee": {
                "avoid": ["Running", "Jumping", "Deep squats", "Lunges"],
                "alternatives": ["Swimming", "Upper body strength1", "Chair exercises", "Gentle yoga"],
                "tips": ["Use ice after activity", "Elevate when resting", "Avoid high-impact activities"]
            },
            "back": {
                "avoid": ["Heavy lifting", "Twisting motions", "High-impact activities"],
                "alternatives": ["Walking", "Swimming", "Soft stretching", "Core strengthening"],
                "tips": ["Maintain good posture", "Use proper lifting technique", "Sleep with pillow support"]
            },
            "shoulder": {
                "avoid": ["Overhead movements", "Heavy pushing/pulling", "Contact sports"],
                "alternatives": ["Lower body exercises", "Gentle arm movements", "Walking", "Light cardio"],
                "tips": ["Apply ice after activity", "Avoid sleeping on injured side", "Gentle range of motion"]
            },
            "ankle": {
                "avoid": ["Running", "Jumping", "High-impact sports", "Uneven surfaces"],
                "alternatives": ["Upper body strength", "Swimming", "Seated exercises", "Gentle stretching1"],
                "tips": ["Use RICE protocol", "Wear supportive footwear", "Avoid walking on uneven ground"]
            },
            "foot": {
                "avoid": ["Running", "Jumping", "High-impact sports", "Long walks on hard surfaces"],
                "alternatives": ["Upper body strength", "Swimming", "Seated exercises", "Gentle stretching"],
                "tips": ["Use RICE protocol", "Wear supportive footwear", "Avoid walking on uneven ground", "Consider arch support"]
            },
            "wrist": {
                "avoid": ["Heavy lifting", "Push-ups", "Weight-bearing on hands", "Repetitive motions"],
                "alternatives": ["Lower body exercises", "Cardio machines", "Gentle stretching", "Walking"],
                "tips": ["Use wrist supports", "Apply ice after activity", "Avoid repetitive gripping"]
            }
        }

    async def process_message(self, message: str, context: UserSessionContext, streamer=None) -> str:
        """Process injury-related fitness concerns"""
        print("🏥 Injury Support Agent - User said:", message)
        
        try:
            context.add_handoff_log("main", "injury_support", f"Physical limitation consultation: {message[:50]}...")
        except Exception as e:
            print(f"Warning: Could not add handoff log: {e}")
        
        # ✅ FIXED: Safely initialize injury_notes
        try:
            if not hasattr(context, 'injury_notes') or context.injury_notes is None:
                context.injury_notes = []
            context.injury_notes.append(message)
        except Exception as e:
            print(f"Warning: Could not update injury notes: {e}")
            # Continue without injury notes if there's an issue
        
        # Identify injury type
        injury_type = self._identify_injury_type(message)
        
        if injury_type and injury_type != "unknown":
            response = self._generate_injury_specific_advice(injury_type, context)
        else:
            response = self._generate_general_injury_advice(context)
        
        # Handle streaming
        if streamer:
            try:
                await streamer.update(response)
                print("✅ Injury support response streamed successfully")
            except Exception as e:
                print(f"❌ Injury streaming error: {e}")
        
        print(f"✅ Injury support returning response: {len(response)} characters")
        return response

    def _identify_injury_type(self, message: str) -> str:
        """Identify type of injury from message"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["knee", "kneecap", "patella"]):
            return "knee"
        elif any(word in message_lower for word in ["back", "spine", "lower back", "upper back"]):
            return "back"
        elif any(word in message_lower for word in ["shoulder", "rotator cuff", "arm"]):
            return "shoulder"
        elif any(word in message_lower for word in ["ankle"]):
            return "ankle"
        elif any(word in message_lower for word in ["foot", "feet", "toe", "heel"]):
            return "foot"
        elif any(word in message_lower for word in ["wrist", "hand"]):
            return "wrist"
        
        return "unknown"

    def _generate_injury_specific_advice(self, injury_type: str, context: UserSessionContext) -> str:
        """Generate advice for specific injury types"""
        
        if injury_type not in self.injury_modifications:
            return self._generate_general_injury_advice(context)
        
        injury_info = self.injury_modifications[injury_type]
        
        response = f"""🏥 **{injury_type.upper()} INJURY SUPPORT & RECOVERY**

I understand you're dealing with {injury_type} pain/injury. Here's your personalized modification plan:

❌ **Exercises to AVOID:**
{chr(10).join(f"• {exercise}" for exercise in injury_info["avoid"])}

✅ **SAFE Alternatives:**
{chr(10).join(f"• {exercise}" for exercise in injury_info["alternatives"])}

💡 **Recovery & Management Tips:**
{chr(10).join(f"• {tip}" for tip in injury_info["tips"])}

🔄 **Gradual Return Protocol:**
1. **Phase 1**: Pain-free range of motion
2. **Phase 2**: Gentle strengthening exercises  
3. **Phase 3**: Functional movement patterns
4. **Phase 4**: Gradual return to normal activities

⚠️ **IMPORTANT Safety Guidelines:**
• Stop immediately if you experience pain
• Ice for 15-20 minutes after activity
• Never push through sharp or increasing pain
• Consider anti-inflammatory foods (berries, leafy greens, fatty fish)

🏥 **When to Seek Professional Help:**
• Pain persists or worsens after 48-72 hours
• Swelling doesn't reduce with rest and ice
• You experience numbness or tingling
• You can't bear weight or use the injured area normally

📞 **Professional Resources:**
• Physical therapist for rehabilitation exercises
• Sports medicine doctor for diagnosis
• Massage therapist for muscle tension relief

Would you like me to create a specific modified workout plan that works around your {injury_type} injury? I can also suggest anti-inflammatory meal options to support your recovery."""

        return response

    def _generate_general_injury_advice(self, context: UserSessionContext) -> str:
        """Generate general injury advice"""
        return """🩹 **COMPREHENSIVE INJURY-SAFE FITNESS PLANNING**

I understand you're dealing with an injury or physical limitation. Your safety and recovery are the absolute top priorities.

🛡️ **Universal Safety Guidelines:**
• **Pain Rule**: Stop any activity that causes pain
• **Start Low**: Begin with gentle, low-impact exercises
• **Progress Slowly**: Increase intensity gradually over weeks
• **Listen to Your Body**: Rest when you need to rest

🏊 **Low-Impact Exercise Menu:**

**Cardiovascular Options:**
• Swimming or water walking (excellent for joint relief)
• Stationary bike (if lower body allows)
• Upper body ergometer (if legs are injured)
• Gentle walking on flat surfaces

**Strength Training Alternatives:**
• Chair-based resistance exercises
• Resistance bands (adjustable intensity)
• Isometric exercises (muscle contraction without movement)
• Upper body weights (if lower body is injured)

**Flexibility & Recovery:**
• Gentle stretching (pain-free range only)
• Deep breathing exercises
• Progressive muscle relaxation
• Gentle yoga or tai chi movements

🧠 **Mental Health During Recovery:**
• Set realistic, achievable goals
• Focus on what you CAN do, not limitations
• Maintain social connections through adapted activities
• Consider meditation or mindfulness practices

🍎 **Nutrition for Healing:**
• **Anti-inflammatory foods**: Berries, leafy greens, fatty fish
• **Protein for repair**: Lean meats, eggs, legumes, dairy
• **Vitamin C**: Citrus fruits, bell peppers, strawberries
• **Hydration**: 8+ glasses of water daily

⏰ **Recovery Timeline Expectations:**
• **Acute phase** (0-72 hours): Rest, ice, gentle movement
• **Subacute phase** (3 days - 6 weeks): Gradual activity increase
• **Chronic phase** (6+ weeks): Return to normal activities

🏥 **Professional Support Team:**
• **Primary care doctor**: Overall health assessment
• **Physical therapist**: Rehabilitation exercises
• **Sports medicine specialist**: Injury-specific treatment
• **Registered dietitian**: Nutrition for healing

📊 **Tracking Your Progress:**
• Daily pain levels (1-10 scale)
• Range of motion improvements
• Functional milestones (stairs, walking distance)
• Sleep quality and energy levels

Can you tell me more about your specific injury, pain location, or physical limitation? The more details you provide, the more targeted and helpful my recommendations can be.

Remember: This guidance is educational. Always consult healthcare professionals for proper diagnosis and treatment of injuries."""

