
import json

from langchain_openai import ChatOpenAI

from weather_outfit_ai.models.schemas import ConversationResponse
from weather_outfit_ai.models.state import AgentState
from weather_outfit_ai.prompts import Prompts


class ConversationAgent:

    def __init__(self, llm: ChatOpenAI) -> None:
        """
        Initialize the conversation agent.

        Args:
            llm: OpenAI language model instance
        """
        self.llm = llm
        self.system_prompt = Prompts.conversation_agent()

    async def run(self, state: AgentState) -> AgentState:
        
        user_message = state.metadata.get("user_message", "")
        action = state.metadata.get("action", "full_recommendation")

        history = []
        for i in range(0, len(state.conversation_history), 2):
            if i + 1 < len(state.conversation_history):
                user_msg = state.conversation_history[i].replace("User: ", "")
                bot_msg = state.conversation_history[i + 1].replace("Bot: ", "")
                history.append({"user": user_msg, "bot": bot_msg})

        agent_results = {
            "location": state.location,
            "weather_data": (
                {
                    "temperature": state.weather_data.temperature,
                    "description": state.weather_data.description,
                    "conditions": state.weather_data.conditions,
                    "feels_like": state.weather_data.feels_like,
                    "humidity": state.weather_data.humidity,
                    "wind_speed": state.weather_data.wind_speed,
                }
                if state.weather_data
                else None
            ),
            "wardrobe_selection": state.wardrobe_selection,
            "final_recommendation": state.final_recommendation,
            "action": action,
            "followup_context": state.followup_context,
            "errors": state.errors,
        }

        response = await self.respond(
            user_message=user_message,
            agent_results=agent_results,
            history=history,
            initial=(action == "full_recommendation"),
        )
        state.response = response
        
        return state

    async def respond(
        self,
        user_message: str,
        agent_results: dict,
        history: list[dict[str, str]] | None = None,
        initial: bool = False,
    ) -> str:
        messages = [
            {"role": "system", "content": self.system_prompt},
        ]

        if history:
            for turn in history:
                if turn.get("user"):
                    messages.append({"role": "user", "content": turn["user"]})
                if turn.get("bot"):
                    messages.append({"role": "assistant", "content": turn["bot"]})

        messages.append({"role": "user", "content": user_message})

        context = f"Agent results: {json.dumps(agent_results, default=str, indent=2)}"
        if initial:
            context += "\n\nThis is an initial recommendation request - provide a comprehensive response."
        messages.append({"role": "system", "content": context})

        # Use structured output with Pydantic model
        structured_llm = self.llm.with_structured_output(ConversationResponse)
        
        try:
            response_obj = await structured_llm.ainvoke(messages)
            # Store the structured response in state metadata for potential use
            return response_obj.response
        except Exception as e:
            print(f"ConversationAgent structured output error: {e}")
            # Fallback to unstructured response
            response = await self.llm.ainvoke(messages)
            response_content = response.content
            if isinstance(response_content, str):
                return response_content.strip()
            else:
                return "I apologize, but I couldn't generate a proper response. Please try again."
