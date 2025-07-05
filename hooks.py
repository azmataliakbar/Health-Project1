from typing import Dict, Any, Optional
from context import UserSessionContext
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RunHooks:
    """Global hooks for tracking agent and tool usage"""
    
    def __init__(self):
        self.tool_usage_count = {}
        self.agent_usage_count = {}
        self.handoff_count = 0
    
    def on_agent_start(self, agent_name: str, context: UserSessionContext):
        """Called when an agent starts processing"""
        logger.info(f"Agent started: {agent_name}")
        self.agent_usage_count[agent_name] = self.agent_usage_count.get(agent_name, 0) + 1
    
    def on_agent_end(self, agent_name: str, context: UserSessionContext):
        """Called when an agent finishes processing - FIXED: removed unused result parameter"""
        logger.info(f"Agent completed: {agent_name}")
    
    def on_tool_start(self, tool_name: str, context: UserSessionContext):
        """Called when a tool starts executing - FIXED: removed unused input_data parameter"""
        logger.info(f"Tool started: {tool_name}")
        self.tool_usage_count[tool_name] = self.tool_usage_count.get(tool_name, 0) + 1
    
    def on_tool_end(self, tool_name: str, context: UserSessionContext):
        """Called when a tool finishes executing"""
        logger.info(f"Tool completed: {tool_name}")
    
    def on_handoff(self, from_agent: str, to_agent: str, context: UserSessionContext, reason: str):
        """Called when a handoff occurs"""
        logger.info(f"Handoff: {from_agent} -> {to_agent} (Reason: {reason})")
        self.handoff_count += 1
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        return {
            "tool_usage": self.tool_usage_count,
            "agent_usage": self.agent_usage_count,
            "total_handoffs": self.handoff_count
        }

class AgentHooks:
    """Agent-specific hooks"""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.start_times = {}
    
    def on_start(self, context: UserSessionContext):
        """Called when this agent starts"""
        logger.info(f"{self.agent_name} agent started")
        self.start_times[context.uid] = time.time()
    
    def on_end(self, context: UserSessionContext, result: Any):
        """Called when this agent ends"""
        logger.info(f"{self.agent_name} agent completed with result: {str(result)[:100]}")
        if context.uid in self.start_times:
            duration = time.time() - self.start_times[context.uid]
            logger.info(f"{self.agent_name} agent completed in {duration:.2f}s")
    
    def on_tool_start(self, tool_name: str, context: UserSessionContext):
        """Called when this agent starts using a tool"""
        logger.info(f"{self.agent_name} using tool: {tool_name}")
    
    def on_tool_end(self, tool_name: str, context: UserSessionContext):
        """Called when this agent finishes using a tool"""
        logger.info(f"{self.agent_name} finished using tool: {tool_name}")
    
    def on_handoff(self, to_agent: str, context: UserSessionContext, reason: str):
        """Called when this agent hands off to another"""
        logger.info(f"{self.agent_name} handing off to {to_agent}: {reason}")
