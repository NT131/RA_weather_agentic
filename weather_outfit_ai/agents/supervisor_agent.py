
import json
from typing import Any

from langchain_openai import ChatOpenAI

from weather_outfit_ai.prompts import Prompts


class SupervisorAgent:

    def __init__(self, model_name: str = "gpt-4o-mini") -> None:
        """
        Initialize the supervisor agent.

        Args:
            model_name: OpenAI model to use for intent detection
        """
        self.llm = ChatOpenAI(model=model_name, temperature=0.3)
        self.system_prompt = Prompts.supervisor_agent()

    async def plan(
        self, message: str, history: list[dict[str, str]] | None = None
    ) -> dict[str, Any]:
        """
        Analyze user message and determine the appropriate action.

        Args:
            message: User's message
            history: Conversation history

        Returns:
            Dictionary with action, location, followup_context, and original_message
        """
        
        messages = [
            {"role": "system", "content": self.system_prompt},
        ]
        if history:
            for turn in history:
                if turn.get("user"):
                    messages.append({"role": "user", "content": turn["user"]})
                if turn.get("bot"):
                    messages.append({"role": "assistant", "content": turn["bot"]})
                    
        messages.append({"role": "user", "content": message})
        
        response = await self.llm.ainvoke(messages)
        
        if isinstance(response.content, str):
            data: dict[str, Any] = json.loads(response.content)
            for key in ["action", "location", "followup_context", "original_message"]:
                if key not in data:
                    data[key] = None
            
            print(f"SupervisorAgent: Intent detected - Action: {data.get('action')}, Location: {data.get('location')}")
            return data
        
        return None
