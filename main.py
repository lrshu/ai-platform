"""
Main application file for RAG backend.
"""

from fastapi import FastAPI
from app.api.indexing import router as indexing_router
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="RAG Backend API",
    description="API for Retrieval-Augmented Generation backend system",
    version="1.0.0"
)

# Include routers
app.include_router(indexing_router)

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "RAG Backend API is running"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
