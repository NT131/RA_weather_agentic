"""
Pure Pydantic-based Outfit Recommendation Orchestrator

This module replaces LangGraph with a simple, type-safe Pydantic orchestration system.
"""

import asyncio
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from weather_outfit_ai.models.state import AgentState
from weather_outfit_ai.models.schemas import SupervisorPlan
from weather_outfit_ai.agents.supervisor_agent import SupervisorAgent
from weather_outfit_ai.agents.weather_agent import WeatherAgent
from weather_outfit_ai.agents.wardrobe_agent import WardrobeAgent
from weather_outfit_ai.agents.design_agent import DesignAgent
from weather_outfit_ai.agents.conversation_agent import ConversationAgent
from weather_outfit_ai.services.wardrobe_service import WardrobeService
from weather_outfit_ai.config import config
from langchain_openai import ChatOpenAI


class OutfitOrchestrator(BaseModel):
    """Pure Pydantic orchestrator for outfit recommendations."""
    
    model_config = {"arbitrary_types_allowed": True}
    
    # Agents
    supervisor_agent: SupervisorAgent = Field(default_factory=SupervisorAgent)
    weather_agent: WeatherAgent = Field(default=None)
    wardrobe_agent: WardrobeAgent = Field(default=None)
    design_agent: DesignAgent = Field(default=None)
    conversation_agent: ConversationAgent = Field(default=None)
    
    # Services
    wardrobe_service: WardrobeService = Field(default_factory=WardrobeService)
    
    # Memory for conversation
    conversation_memory: Dict[str, list] = Field(default_factory=dict)
    
    def __init__(self, **data):
        super().__init__(**data)
        
        # Initialize LLM
        llm = ChatOpenAI(
            model=config.OPENAI_MODEL,
            api_key=config.OPENAI_API_KEY,
            temperature=config.OPENAI_TEMPERATURE
        )
        
        # Initialize agents that need LLM and services
        self.weather_agent = WeatherAgent(llm=llm)
        self.wardrobe_agent = WardrobeAgent(llm=llm, wardrobe_service=self.wardrobe_service)
        self.design_agent = DesignAgent(llm=llm)
        self.conversation_agent = ConversationAgent(llm=llm)
    
    async def process_request(
        self, 
        user_message: str, 
        thread_id: str = "default",
        conversation_history: Optional[list] = None
    ) -> AgentState:
        """
        Process a user request and return the complete outfit recommendation.
        
        Args:
            user_message: The user's message/request
            thread_id: Unique identifier for conversation thread
            conversation_history: Optional conversation history
            
        Returns:
            AgentState with complete recommendation
        """
        
        # Initialize state
        state = AgentState(
            conversation_history=conversation_history or [],
            metadata={"user_message": user_message}
        )
        
        try:
            # Step 1: Supervisor analysis
            state = await self._run_supervisor(state)
            
            # Step 2: Route based on supervisor decision
            action = state.metadata.get("action", "full_recommendation")
            
            if action == "full_recommendation":
                state = await self._run_full_recommendation_flow(state)
            elif action == "weather_only":
                state = await self._run_weather_only_flow(state)
            elif action == "wardrobe_only":
                state = await self._run_wardrobe_only_flow(state)
            elif action == "conversation_only":
                state = await self._run_conversation_only_flow(state)
            else:
                # Default to full recommendation
                state = await self._run_full_recommendation_flow(state)
                
            # Update conversation memory
            self._update_conversation_memory(thread_id, user_message, state.response or "")
            
        except Exception as e:
            error_msg = f"Error processing request: {str(e)}"
            state.errors.append(error_msg)
            state.response = "I apologize, but I encountered an error processing your request. Please try again."
            
        return state
    
    async def _run_supervisor(self, state: AgentState) -> AgentState:
        """Run supervisor agent to analyze intent and plan routing."""
        user_message = state.metadata.get("user_message", "")
        
        # Extract conversation history for context
        history = []
        for i in range(0, len(state.conversation_history), 2):
            if i + 1 < len(state.conversation_history):
                user_msg = state.conversation_history[i].replace("User: ", "")
                bot_msg = state.conversation_history[i + 1].replace("Bot: ", "")
                history.append({"user": user_msg, "bot": bot_msg})
        
        # Get planning result from supervisor
        plan_result = await self.supervisor_agent.plan(user_message, history)
        
        if plan_result:
            # Update state with supervisor's analysis
            state.location = plan_result.get("location")
            state.followup_context = plan_result.get("followup_context")
            state.metadata.update({
                "action": plan_result.get("action", "full_recommendation"),
                "user_message": plan_result.get("original_message", user_message),
                "supervisor_reasoning": plan_result
            })
        else:
            # Fallback if supervisor fails
            state.metadata.update({
                "action": "full_recommendation",
                "user_message": user_message
            })
        
        return state
    
    async def _run_full_recommendation_flow(self, state: AgentState) -> AgentState:
        """Run the complete recommendation flow: Weather -> Wardrobe -> Design -> Conversation."""
        # Step 1: Weather analysis
        state = await self.weather_agent.run(state)
        
        # Step 2: Wardrobe selection
        state = await self.wardrobe_agent.run(state)
        
        # Step 3: Design outfit
        state = await self.design_agent.run(state)
        
        # Step 4: Generate conversation response
        state = await self.conversation_agent.run(state)
        
        return state
    
    async def _run_weather_only_flow(self, state: AgentState) -> AgentState:
        """Run weather-only flow."""
        # Get weather data
        state = await self.weather_agent.run(state)
        
        # Generate conversation response
        state = await self.conversation_agent.run(state)
        
        return state
    
    async def _run_wardrobe_only_flow(self, state: AgentState) -> AgentState:
        """Run wardrobe-only flow."""
        # Get wardrobe selection (may need minimal weather context)
        state = await self.wardrobe_agent.run(state)
        
        # Generate conversation response
        state = await self.conversation_agent.run(state)
        
        return state
    
    async def _run_conversation_only_flow(self, state: AgentState) -> AgentState:
        """Run conversation-only flow for general chat."""
        # Skip to conversation response
        state = await self.conversation_agent.run(state)
        
        return state
    
    def _update_conversation_memory(self, thread_id: str, user_message: str, response: str):
        """Update conversation memory for the thread."""
        if thread_id not in self.conversation_memory:
            self.conversation_memory[thread_id] = []
        
        self.conversation_memory[thread_id].extend([
            f"User: {user_message}",
            f"Bot: {response}"
        ])
        
        # Keep only last 10 exchanges (20 messages)
        if len(self.conversation_memory[thread_id]) > 20:
            self.conversation_memory[thread_id] = self.conversation_memory[thread_id][-20:]
    
    def get_conversation_history(self, thread_id: str) -> list:
        """Get conversation history for a thread."""
        return self.conversation_memory.get(thread_id, [])


# Global orchestrator instance
_orchestrator_instance = None

def get_orchestrator() -> OutfitOrchestrator:
    """Get or create the global orchestrator instance."""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = OutfitOrchestrator()
    return _orchestrator_instance


async def process_outfit_request(
    user_message: str, 
    thread_id: str = "default",
    conversation_history: Optional[list] = None
) -> AgentState:
    """
    Convenience function to process an outfit request.
    
    Args:
        user_message: The user's message/request
        thread_id: Unique identifier for conversation thread
        conversation_history: Optional conversation history
        
    Returns:
        AgentState with complete recommendation
    """
    orchestrator = get_orchestrator()
    return await orchestrator.process_request(user_message, thread_id, conversation_history)
