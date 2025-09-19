
import json
from typing import Any

from langchain_openai import ChatOpenAI

from weather_outfit_ai.config import config
from weather_outfit_ai.models.schemas import SupervisorPlan
from weather_outfit_ai.prompts import Prompts


class SupervisorAgent:

    def __init__(self, model_name: str | None = None) -> None:
        """
        Initialize the supervisor agent.

        Args:
            model_name: OpenAI model to use for intent detection (defaults to config.OPENAI_MODEL)
        """
        self.llm = ChatOpenAI(
            model=model_name or config.OPENAI_MODEL, 
            temperature=0.3
        )
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
        
        # Use structured output with Pydantic model
        structured_llm = self.llm.with_structured_output(SupervisorPlan)
        
        try:
            plan = await structured_llm.ainvoke(messages)
            print(f"SupervisorAgent: Intent detected - Action: {plan.action}, Location: {plan.location}")
            return plan.model_dump()
        except Exception as e:
            print(f"SupervisorAgent structured output error: {e}")
            # Fallback to unstructured response
            response = await self.llm.ainvoke(messages)
            
            if isinstance(response.content, str):
                try:
                    data: dict[str, Any] = json.loads(response.content)
                    for key in ["action", "location", "followup_context", "original_message"]:
                        if key not in data:
                            data[key] = None
                    
                    print(f"SupervisorAgent: Intent detected - Action: {data.get('action')}, Location: {data.get('location')}")
                    return data
                except json.JSONDecodeError as e:
                    print(f"SupervisorAgent JSON parse error: {e}")
        
        # Final fallback
        return {
            "action": "full_recommendation",
            "location": None,
            "followup_context": None,
            "original_message": message,
            "reasoning": "Fallback to full recommendation due to parsing error",
            "confidence": 0.5
        }
