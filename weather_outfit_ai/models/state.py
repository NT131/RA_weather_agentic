

from pydantic import BaseModel, Field

from weather_outfit_ai.models.schemas import (
    OutfitRecommendation,
    WardrobeSelection,
    WeatherData,
)


class AgentState(BaseModel):
    """Simplified agent state for the outfit recommendation flow."""

    location: str | None = Field(None, description="Location for weather data")
    followup_context: str | None = Field(
        None, description="Additional context (e.g., 'business meeting')"
    )

    weather_data: WeatherData | None = Field(None, description="Weather information")
    wardrobe_selection: WardrobeSelection | None = Field(
        None, description="Available wardrobe items"
    )
    final_recommendation: OutfitRecommendation | None = Field(
        None, description="Final outfit recommendation"
    )
    response: str | None = Field(
        None, description="Final conversational response to user"
    )
    conversation_history: list[str] = Field(
        default_factory=list, description="Conversation history"
    )
    errors: list[str] = Field(
        default_factory=list, description="Any errors that occurred"
    )
    metadata: dict = Field(default_factory=dict, description="Additional metadata")
