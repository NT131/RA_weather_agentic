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
from weather_outfit_ai.orchestrator.outfit_orchestrator import get_orchestrator
from weather_outfit_ai.models.state import AgentState
from weather_outfit_ai.models.schemas import OutfitRequest, HealthResponse, OutfitRecommendationResponse

# Configure logging
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL))
logger = logging.getLogger(__name__)

# Global orchestrator instance
orchestrator = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global orchestrator
    
    # Startup
    logger.info("Starting Weather Outfit AI application...")
    try:
        config.validate()
        orchestrator = get_orchestrator()
        logger.info("Orchestrator initialized successfully")
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
    location: str
    style_preference: str = "casual"
    time_horizon: str = "now"


class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[str]] = None


class OutfitResponse(BaseModel):
    success: bool
    response: str
    location: Optional[str] = None
    weather_data: Optional[dict] = None
    final_recommendation: Optional[dict] = None
    errors: Optional[List[str]] = None
    conversation_history: Optional[List[str]] = None


class ChatResponse(BaseModel):
    response: str
    location: Optional[str] = None
    weather: Optional[dict] = None
    outfit_suggestion: Optional[str] = None


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
        
        # Check if orchestrator is initialized
        if orchestrator is None:
            raise Exception("Orchestrator not initialized")
        
        return HealthResponse(
            status="healthy",
            message="Weather Outfit AI is running properly"
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {e}")


@app.post("/outfit-recommendation", response_model=OutfitRecommendationResponse)
async def get_outfit_recommendation(request: OutfitRequest):
    """Get an outfit recommendation based on weather and preferences."""
    try:
        logger.info(f"Processing outfit request for {request.location}")
        
        # Convert request to our state format using the message
        user_message = f"I need an outfit recommendation for {request.location}. Style: {request.style_preference}. Time: {request.time_horizon}"
        
        # Process the request using the orchestrator
        result = await orchestrator.process_request(
            user_message=user_message,
            thread_id="frontend-form"
        )
        
        return OutfitRecommendationResponse(
            location=result.location or request.location,
            weather=result.weather_data if result.weather_data else {},
            outfit_suggestion=result.outfit_suggestion or result.response or "",
            style_preference=request.style_preference,
            additional_info=""
        )
    except Exception as e:
        logger.error(f"Error processing outfit recommendation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat", response_model=ChatResponse)
async def chat_interaction(request: ChatRequest):
    """Chat interaction endpoint for conversational interface."""
    try:
        logger.info(f"Processing chat message: {request.message[:100]}...")
        
        # Process the chat message using the orchestrator
        result = await orchestrator.process_request(
            user_message=request.message,
            thread_id="frontend-chat",
            conversation_history=request.conversation_history
        )
        
        return ChatResponse(
            response=result.response or "I couldn't generate a response.",
            location=result.location,
            weather=result.weather_data if result.weather_data else None,
            outfit_suggestion=result.outfit_suggestion if result.outfit_suggestion else None
        )
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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

