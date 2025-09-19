"""
DEPRECATED: This file contains the original LangGraph-based implementation.

The LangGraph-based orchestration has been replaced with a pure Pydantic approach.
See weather_outfit_ai/orchestrator/outfit_orchestrator.py for the new implementation.

This file is kept for reference only and will be removed in a future version.
"""

from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from weather_outfit_ai.agents.conversation_agent import ConversationAgent
from weather_outfit_ai.agents.design_agent import DesignAgent
from weather_outfit_ai.agents.supervisor_agent import SupervisorAgent
from weather_outfit_ai.agents.wardrobe_agent import WardrobeAgent
from weather_outfit_ai.agents.weather_agent import WeatherAgent
from weather_outfit_ai.config import config
from weather_outfit_ai.models.state import AgentState
from weather_outfit_ai.services.wardrobe_service import WardrobeService


def create_outfit_graph():
    llm = ChatOpenAI(
        model=config.OPENAI_MODEL, 
        api_key=config.OPENAI_API_KEY, 
        temperature=config.OPENAI_TEMPERATURE
    )

    wardrobe_service = WardrobeService()

    # Instantiate all agents
    supervisor_agent = SupervisorAgent()
    weather_agent = WeatherAgent(llm=llm)
    wardrobe_agent = WardrobeAgent(llm=llm, wardrobe_service=wardrobe_service)
    design_agent = DesignAgent(llm=llm)
    conversation_agent = ConversationAgent(llm=llm)

    # Define node functions
    async def supervisor_node(state: AgentState) -> AgentState:
        """Supervisor node that analyzes user intent and sets routing information."""
        user_message = state.metadata.get("user_message", "")
        
        # Extract conversation history for context
        history = []
        for i in range(0, len(state.conversation_history), 2):
            if i + 1 < len(state.conversation_history):
                user_msg = state.conversation_history[i].replace("User: ", "")
                bot_msg = state.conversation_history[i + 1].replace("Bot: ", "")
                history.append({"user": user_msg, "bot": bot_msg})
        
        # Get planning result from supervisor
        plan_result = await supervisor_agent.plan(user_message, history)
        
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

    async def weather_node(state: AgentState) -> AgentState:
        """Weather node that fetches and analyzes weather data."""
        return await weather_agent.run(state)

    async def wardrobe_node(state: AgentState) -> AgentState:
        """Wardrobe node that selects appropriate clothing items."""
        return await wardrobe_agent.run(state)

    async def design_node(state: AgentState) -> AgentState:
        """Design node that creates the final outfit recommendation."""
        return await design_agent.run(state)

    async def conversation_node(state: AgentState) -> AgentState:
        """Conversation node that generates the final response to user."""
        return await conversation_agent.run(state)

    # Router function for conditional edges
    def route_after_supervisor(state: AgentState) -> str:
        """Router that determines the next step based on supervisor's action decision."""
        action = state.metadata.get("action", "full_recommendation")
        
        # Route based on the action determined by supervisor
        if action == "full_recommendation":
            return "weather"
        elif action == "weather_only":
            return "weather_direct"
        elif action == "wardrobe_only":
            return "wardrobe_direct"
        elif action == "conversation_only":
            return "conversation"
        else:
            # Default to full recommendation flow
            return "weather"

    # Create the state graph
    workflow = StateGraph(AgentState)

    # Add all nodes
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("weather", weather_node)
    workflow.add_node("wardrobe", wardrobe_node)
    workflow.add_node("design", design_node)
    workflow.add_node("conversation", conversation_node)
    
    # Add specialized nodes for direct routing
    workflow.add_node("weather_direct", weather_node)
    workflow.add_node("wardrobe_direct", wardrobe_node)

    # Set entry point
    workflow.set_entry_point("supervisor")

    # Add conditional edge from supervisor based on action
    workflow.add_conditional_edges(
        "supervisor",
        route_after_supervisor,
        {
            "weather": "weather",
            "weather_direct": "weather_direct", 
            "wardrobe_direct": "wardrobe_direct",
            "conversation": "conversation"
        }
    )

    # Main flow: Weather -> Wardrobe -> Design -> Conversation -> END
    workflow.add_edge("weather", "wardrobe")
    workflow.add_edge("wardrobe", "design")
    workflow.add_edge("design", "conversation")
    workflow.add_edge("conversation", END)

    # Direct routes that skip to conversation
    workflow.add_edge("weather_direct", "conversation")
    workflow.add_edge("wardrobe_direct", "conversation")

    # Compile the graph with memory
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    
    return app
