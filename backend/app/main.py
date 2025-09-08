"""
VitaeAgent FastAPI Backend
The main FastAPI application that exposes the VitaeAgent's capabilities
through a REST API interface.
"""

import os
import logging
from typing import Dict, Any, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from .agent import get_agent

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    query: str = Field(..., description="The user's question or message")
    language: str = Field(default="en", description="Target language for response (ISO 639-1 code)")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str = Field(..., description="The agent's response")
    sources: List[Dict[str, Any]] = Field(default_factory=list, description="Source documents used")
    original_query: str = Field(..., description="Original user query")
    processed_query: str = Field(..., description="Query processed by the agent")
    language: str = Field(..., description="Response language")
    source_count: int = Field(..., description="Number of sources referenced")


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str = Field(..., description="Overall health status")
    components: Dict[str, Any] = Field(..., description="Status of individual components")
    version: str = Field(default="1.0.0", description="API version")


class SuggestedQuestionsResponse(BaseModel):
    """Response model for suggested questions."""
    questions: List[str] = Field(..., description="List of suggested questions")


# Global agent instance
agent = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI app."""
    global agent
    try:
        logger.info("Initializing VitaeAgent...")
        agent = get_agent()
        logger.info("VitaeAgent initialized successfully")
        yield
    except Exception as e:
        logger.error(f"Failed to initialize VitaeAgent: {e}")
        raise
    finally:
        logger.info("Shutting down VitaeAgent...")


# Create FastAPI app
app = FastAPI(
    title="VitaeAgent API",
    description="An intelligent conversational interface for professional background information",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with basic API information."""
    return {
        "message": "Welcome to VitaeAgent API",
        "description": "An intelligent digital professional persona",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint for conversing with the VitaeAgent.
    
    This endpoint processes user queries and returns intelligent responses
    based on the agent's knowledge base, complete with source citations.
    """
    global agent
    
    if agent is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="VitaeAgent is not initialized"
        )
    
    try:
        # Validate input
        if not request.query.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Query cannot be empty"
            )
        
        # Process the chat request
        logger.info(f"Processing chat request: {request.query[:100]}...")
        result = agent.chat(request.query, request.language)
        
        # Check for errors in the result
        if "error" in result:
            logger.error(f"Agent error: {result['error']}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while processing your request"
            )
        
        return ChatResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint to verify the status of all components.
    
    Returns the status of the agent, database, LLM, and other components.
    """
    global agent
    
    try:
        if agent is None:
            return HealthResponse(
                status="unhealthy",
                components={"agent": "not_initialized"},
                version="1.0.0"
            )
        
        # Perform comprehensive health check
        health_data = agent.health_check()
        
        # Determine overall status
        overall_status = "healthy"
        if not health_data.get("retriever_ready", False) or not health_data.get("llm_ready", False):
            overall_status = "degraded"
        if "error" in health_data:
            overall_status = "unhealthy"
        
        return HealthResponse(
            status=overall_status,
            components=health_data,
            version="1.0.0"
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            components={"error": str(e)},
            version="1.0.0"
        )


@app.get("/suggestions", response_model=SuggestedQuestionsResponse)
async def get_suggested_questions():
    """
    Get suggested questions to help users start conversations with the agent.
    
    Returns a list of example questions that showcase the agent's capabilities.
    """
    global agent
    
    if agent is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="VitaeAgent is not initialized"
        )
    
    try:
        questions = agent.get_suggested_questions()
        return SuggestedQuestionsResponse(questions=questions)
        
    except Exception as e:
        logger.error(f"Error getting suggestions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve suggested questions"
        )


@app.get("/stats", response_model=Dict[str, Any])
async def get_stats():
    """
    Get statistics about the agent's knowledge base.
    
    Returns information about the number of documents, sources, and other metadata.
    """
    global agent
    
    if agent is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="VitaeAgent is not initialized"
        )
    
    try:
        # Get basic stats from the health check
        health_data = agent.health_check()
        
        stats = {
            "knowledge_base_size": health_data.get("database_count", 0),
            "retriever_status": "ready" if health_data.get("retriever_ready", False) else "not_ready",
            "llm_status": "ready" if health_data.get("llm_ready", False) else "not_ready",
            "translation_available": health_data.get("translator_available", False),
            "api_version": "1.0.0"
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve statistics"
        )


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions with consistent format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.detail,
                "status_code": exc.status_code,
                "timestamp": str(request.url)
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "message": "An unexpected error occurred",
                "status_code": 500,
                "timestamp": str(request.url)
            }
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("BACKEND_HOST", "0.0.0.0")
    port = int(os.getenv("BACKEND_PORT", "8000"))
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )