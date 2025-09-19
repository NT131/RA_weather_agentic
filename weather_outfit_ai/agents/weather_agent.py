
import datetime
import json
from typing import Any

from langchain_openai import ChatOpenAI

from weather_outfit_ai.models.schemas import WeatherData, WeatherAnalysis
from weather_outfit_ai.models.state import AgentState
from weather_outfit_ai.prompts import Prompts
from weather_outfit_ai.services.weather_service import WeatherService


class WeatherAgent:

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.system_prompt = Prompts.weather_agent()
        self.weather_service = WeatherService()

    async def run(self, state: AgentState) -> AgentState:
        if not state.location:
            return state

        weather_data = await self.weather_service.get_weather(state.location)
        state.weather_data = weather_data

        analysis = await self._analyze_weather(weather_data)
        state.metadata.update(analysis)

        return state

    async def _analyze_weather(self, weather_data: WeatherData) -> dict[str, Any]:
        """Analyze weather data and return structured analysis."""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {
                "role": "user",
                "content": f"""
                    Analyze this weather data for clothing recommendations:
                    Location: {weather_data.location}
                    Temperature: {weather_data.temperature}°C (feels like {weather_data.feels_like}°C)
                    Humidity: {weather_data.humidity}%
                    Wind Speed: {weather_data.wind_speed} km/h
                    Conditions: {', '.join(weather_data.conditions)}
                    Description: {weather_data.description}
                    
                    Return a structured analysis in JSON format with:
                    - weather_analysis: detailed analysis
                    - comfort_level: 1-5 rating
                    - key_factors: list of important factors
                    - temperature_category: cold/cool/mild/warm/hot
                    - precipitation_risk: none/low/moderate/high  
                    - wind_factor: calm/breezy/windy/very_windy
                    - recommendations: specific clothing suggestions
                """,
            },
        ]

        # Use structured output with Pydantic model
        structured_llm = self.llm.with_structured_output(WeatherAnalysis)
        
        try:
            analysis = await structured_llm.ainvoke(messages)
            return analysis.model_dump()
        except Exception as e:
            print(f"WeatherAgent structured output error: {e}")
            # Fallback to unstructured response
            response = await self.llm.ainvoke(messages)
            
            if isinstance(response.content, str) and response.content.strip():
                try:
                    return json.loads(response.content.strip())
                except json.JSONDecodeError as e:
                    print(f"WeatherAgent JSON parse error: {e}")
                    print(f"Response content: '{response.content}'")
            
            # Final fallback with minimal structure
            return {
                "weather_analysis": f"Weather in {weather_data.location}: {weather_data.description}, {weather_data.temperature}°C",
                "comfort_level": 3,
                "key_factors": ["temperature", "conditions"],
                "temperature_category": "mild",
                "precipitation_risk": "low",
                "wind_factor": "calm",
                "recommendations": "Dress appropriately for the current conditions.",
            }
