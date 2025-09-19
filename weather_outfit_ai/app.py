"""
FastAPI application for Weather Outfit AI.
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from weather_outfit_ai.config import config
from weather_outfit_ai.graph.graph import create_outfit_graph
from weather_outfit_ai.models.state import AgentState

# Configure logging
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL))
logger = logging.getLogger(__name__)

# Global graph instance
graph = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global graph
    
    # Startup
    logger.info("Starting Weather Outfit AI application...")
    try:
        config.validate()
        graph = create_outfit_graph()
        logger.info("Graph initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Weather Outfit AI application...")


# Create FastAPI app
app = FastAPI(
    title="Weather Outfit AI",
    description="An agentic AI system that provides personalized outfit recommendations based on weather and context",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class OutfitRequest(BaseModel):
    message: str
    location: Optional[str] = None
    context: Optional[str] = None
    conversation_history: Optional[List[str]] = None


class OutfitResponse(BaseModel):
    success: bool
    response: str
    location: Optional[str] = None
    weather_data: Optional[dict] = None
    final_recommendation: Optional[dict] = None
    errors: Optional[List[str]] = None
    conversation_history: Optional[List[str]] = None


class HealthResponse(BaseModel):
    status: str
    message: str


@app.get("/", response_model=dict)
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Weather Outfit AI",
        "version": "0.1.0",
        "endpoints": {
            "health": "/health",
            "recommend": "/recommend",
            "chat": "/chat",
            "docs": "/docs"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        # Validate configuration
        config.validate()
        
        # Check if graph is initialized
        if graph is None:
            raise Exception("Graph not initialized")
        
        return HealthResponse(
            status="healthy",
            message="Weather Outfit AI is running properly"
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {e}")


@app.post("/recommend", response_model=OutfitResponse)
async def get_outfit_recommendation(request: OutfitRequest):
    """Get a single outfit recommendation."""
    try:
        if graph is None:
            raise HTTPException(status_code=503, detail="Service not initialized")
        
        # Enhance message with optional parameters
        message = request.message
        if request.location:
            message = f"{message} in {request.location}"
        if request.context:
            message = f"{message} for {request.context}"
        
        # Initialize the agent state
        initial_state = AgentState(
            conversation_history=request.conversation_history or [],
            metadata={"user_message": message}
        )
        
        # Run the graph
        config_dict = {"configurable": {"thread_id": f"api-session"}}
        
        logger.info(f"Processing outfit request: {message}")
        result = await graph.ainvoke(initial_state, config=config_dict)
        
        # Convert result to response format
        weather_data = None
        if result.weather_data:
            weather_data = {
                "location": result.weather_data.location,
                "temperature": result.weather_data.temperature,
                "feels_like": result.weather_data.feels_like,
                "description": result.weather_data.description,
                "conditions": result.weather_data.conditions,
                "humidity": result.weather_data.humidity,
                "wind_speed": result.weather_data.wind_speed,
            }
        
        final_recommendation = None
        if result.final_recommendation:
            outfit = result.final_recommendation
            final_recommendation = {
                "outfit_description": outfit.outfit_description,
                "styling_advice": outfit.styling_advice,
                "weather_appropriateness": outfit.weather_appropriateness,
                "formality_match": outfit.formality_match,
                "selected_items": {
                    "top": {
                        "name": outfit.selected_top.name,
                        "color": outfit.selected_top.color,
                        "material": outfit.selected_top.material
                    } if outfit.selected_top else None,
                    "bottom": {
                        "name": outfit.selected_bottom.name,
                        "color": outfit.selected_bottom.color,
                        "material": outfit.selected_bottom.material
                    } if outfit.selected_bottom else None,
                    "footwear": {
                        "name": outfit.selected_footwear.name,
                        "color": outfit.selected_footwear.color,
                        "material": outfit.selected_footwear.material
                    } if outfit.selected_footwear else None,
                    "outerwear": {
                        "name": outfit.selected_outerwear.name,
                        "color": outfit.selected_outerwear.color,
                        "material": outfit.selected_outerwear.material
                    } if outfit.selected_outerwear else None,
                    "accessories": [
                        {
                            "name": acc.name,
                            "color": acc.color,
                            "material": acc.material
                        } for acc in outfit.selected_accessories
                    ] if outfit.selected_accessories else []
                }
            }
        
        return OutfitResponse(
            success=True,
            response=result.response or "Here's your outfit recommendation!",
            location=result.location,
            weather_data=weather_data,
            final_recommendation=final_recommendation,
            errors=result.errors,
            conversation_history=result.conversation_history
        )
        
    except Exception as e:
        logger.error(f"Error processing outfit request: {e}")
        return OutfitResponse(
            success=False,
            response="Sorry, I encountered an error processing your request.",
            errors=[str(e)]
        )


@app.post("/chat", response_model=OutfitResponse)
async def chat_interaction(request: OutfitRequest):
    """Chat interaction endpoint for conversational interface."""
    # For now, this is the same as recommend, but could be extended
    # for more interactive features like session management
    return await get_outfit_recommendation(request)


@app.get("/config", response_model=dict)
async def get_config():
    """Get current configuration (non-sensitive parts)."""
    try:
        settings = config.get_all_settings()
        # Remove sensitive information
        safe_settings = {k: v for k, v in settings.items() if not k.endswith("_KEY")}
        return {"config": safe_settings}
    except Exception as e:
        logger.error(f"Error getting config: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving configuration")


if __name__ == "__main__":
    import uvicorn
    
    # Validate config before starting
    config.validate()
    
    uvicorn.run(
        "weather_outfit_ai.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=config.LOG_LEVEL.lower()
    )

