
from datetime import datetime

from pydantic import BaseModel, Field


class WeatherData(BaseModel):
    """Weather data model."""

    location: str = Field(..., description="Location name")
    temperature: float = Field(..., description="Temperature in Celsius")
    feels_like: float = Field(..., description="Feels like temperature in Celsius")
    humidity: int = Field(..., description="Humidity percentage")
    wind_speed: float = Field(..., description="Wind speed in km/h")
    description: str = Field(..., description="Weather description")
    conditions: list[str] = Field(..., description="Weather conditions")
    timestamp: datetime = Field(..., description="Timestamp of the weather data")


class PersonalClothingItem(BaseModel):
    """Personal clothing item in the wardrobe."""

    id: str | None = Field(None, description="Unique identifier for the item")
    name: str = Field(..., description="Name of the clothing item")
    category: str = Field(
        ..., description="Category (top, bottom, footwear, outerwear, accessory)"
    )
    subcategory: str = Field(
        ..., description="Specific type (shirt, jeans, sneakers, etc.)"
    )
    material: str = Field(..., description="Primary material")
    color: str = Field(..., description="Primary color")
    secondary_colors: list[str] = Field(
        default_factory=list, description="Additional colors"
    )
    warmth_level: int = Field(
        ..., description="Warmth level (1-5, 1=very light, 5=very warm)"
    )
    formality: int = Field(
        ..., description="Formality level (1-5, 1=very casual, 5=very formal)"
    )
    weather_suitability: list[str] = Field(
        default_factory=list, description="Suitable weather conditions"
    )
    season: list[str] = Field(default_factory=list, description="Suitable seasons")
    brand: str | None = Field(None, description="Brand name")
    size: str | None = Field(None, description="Size")
    description: str = Field("", description="Detailed description of the item")
    tags: list[str] = Field(default_factory=list, description="Tags for categorization")
    last_worn: datetime | None = Field(
        None, description="Last time this item was worn"
    )


class WardrobeSelection(BaseModel):
    """Selected items from the wardrobe based on weather and preferences."""

    available_tops: list[PersonalClothingItem] = Field(
        default_factory=list, description="Available tops"
    )
    available_bottoms: list[PersonalClothingItem] = Field(
        default_factory=list, description="Available bottoms"
    )
    available_footwear: list[PersonalClothingItem] = Field(
        default_factory=list, description="Available footwear"
    )
    available_outerwear: list[PersonalClothingItem] = Field(
        default_factory=list, description="Available outerwear"
    )
    available_accessories: list[PersonalClothingItem] = Field(
        default_factory=list, description="Available accessories"
    )
    selection_reasoning: str = Field(
        ..., description="Reasoning for the wardrobe selection"
    )


class OutfitRecommendation(BaseModel):
    """Final outfit recommendation with selected items and styling advice."""

    selected_top: PersonalClothingItem | None = Field(
        None, description="Selected top item"
    )
    selected_bottom: PersonalClothingItem | None = Field(
        None, description="Selected bottom item"
    )
    selected_footwear: PersonalClothingItem | None = Field(
        None, description="Selected footwear"
    )
    selected_outerwear: PersonalClothingItem | None = Field(
        None, description="Selected outerwear (if needed)"
    )
    selected_accessories: list[PersonalClothingItem] = Field(
        default_factory=list, description="Selected accessories"
    )

    outfit_description: str = Field(
        ..., description="Description of the complete outfit"
    )
    styling_advice: str = Field(..., description="Styling tips and advice")
    weather_appropriateness: str = Field(
        ..., description="How the outfit suits the weather"
    )
    formality_match: str = Field(
        ..., description="How the outfit matches the context/formality needed"
    )


class WeatherAnalysis(BaseModel):
    """Structured weather analysis from the weather agent."""
    
    weather_analysis: str = Field(..., description="Analysis of current weather conditions")
    comfort_level: int = Field(..., description="Comfort level from 1-5 for outdoor activities")
    key_factors: list[str] = Field(..., description="Key weather factors to consider for clothing")
    temperature_category: str = Field(..., description="Temperature category: cold, cool, mild, warm, hot")
    precipitation_risk: str = Field(..., description="Precipitation risk: none, low, moderate, high")
    wind_factor: str = Field(..., description="Wind consideration: calm, breezy, windy, very_windy")
    recommendations: str = Field(..., description="Weather-specific clothing recommendations")


class SupervisorPlan(BaseModel):
    """Supervisor agent's analysis and routing plan."""
    
    action: str = Field(..., description="Action to take: full_recommendation, weather_only, wardrobe_only, conversation_only")
    location: str | None = Field(None, description="Extracted location from user message")
    followup_context: str | None = Field(None, description="Additional context for the request")
    original_message: str = Field(..., description="Original user message")
    reasoning: str = Field(..., description="Reasoning for the chosen action")
    confidence: float = Field(..., description="Confidence in the analysis (0.0-1.0)")


class ConversationResponse(BaseModel):
    """Final response from the conversation agent."""
    
    response: str = Field(..., description="Natural language response to the user")
    response_type: str = Field(..., description="Type of response: outfit_recommendation, weather_info, general_chat")
    confidence: float = Field(..., description="Confidence in the response quality (0.0-1.0)")
    suggestions: list[str] = Field(default_factory=list, description="Follow-up suggestions for the user")
