from context import UserSessionContext
import asyncio

class EscalationAgent:
    """Handles escalation to human coaches"""
    
    async def process_message(self, message: str, context: UserSessionContext, streamer=None) -> str:
        """Process escalation request - ASYNC and FIXED"""
        print("🔴 Escalation Agent - User said:", message)
        
        # Add handoff log
        context.add_handoff_log("main", "escalation", f"User requested human coach: {message[:50]}...")
        
        # Generate unique reference ID
        import time
        ref_id = f"HC-{context.uid}-{int(time.time())}"
        
        response = f"""🔴 CONNECTING YOU WITH HUMAN SUPPORT 🔴

I understand you'd like to speak with a human trainer! While I'm connecting you, here's what I can help you with in the meantime:

📞 What to expect:
• Contact within 24 hours
• Personalized advice from certified professionals
• Direct consultation with fitness experts

🆘 Emergency support:
🚨 ☎️ 800-111-222-333-4444 (24/7) ☎️

📝 **Reference ID:** {ref_id}

💬 **Your Request:** "{message}"

Is there anything specific you'd like me to note for the human coach?

⏰ **Estimated Response Time:** 2-4 hours during business hours
🕐 **Business Hours:** Mon-Fri 9AM-6PM EST

While you wait, I can still help you with:
• Meal planning and nutrition advice
• Workout recommendations
• Goal setting and tracking
• General health and wellness tips"""
        
        # ✅ Fixed streaming logic
        if streamer:
            try:
                await streamer.update(response)
                print("✅ Escalation response streamed successfully")
            except Exception as e:
                print(f"❌ Streaming error: {e}")
        
        print(f"✅ Escalation agent returning response: {len(response)} characters")
        return response

