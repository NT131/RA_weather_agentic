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
        model="gpt-4o-mini", api_key=config.OPENAI_API_KEY, temperature=0.7
    )

    wardrobe_service = WardrobeService()

    supervisor_agent = SupervisorAgent()
    weather_agent = WeatherAgent(llm=llm)
    wardrobe_agent = WardrobeAgent(llm=llm, wardrobe_service=wardrobe_service)
    design_agent = DesignAgent(llm=llm)
    conversation_agent = ConversationAgent(llm=llm)
