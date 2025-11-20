"""
Indexing API endpoint for RAG backend.
"""

from fastapi import APIRouter, BackgroundTasks, HTTPException
from typing import List, Dict, Any
import logging
from app.common.models import IndexingRequest, IndexingResponse, ErrorResponse
from app.indexing.orchestrator import IndexingOrchestrator
from pathlib import Path
import uuid

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/rag", tags=["indexing"])

# Global indexing orchestrator instance
indexing_orchestrator = IndexingOrchestrator()


@router.post("/indexing", response_model=IndexingResponse, responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def trigger_indexing(request: IndexingRequest, background_tasks: BackgroundTasks):
    """
    Trigger document indexing process.

    Args:
        request: Indexing request with document URLs and collection name
        background_tasks: FastAPI background tasks for async processing

    Returns:
        Indexing response with job ID and status
    """
    try:
        logger.info(f"Received indexing request for {len(request.document_urls)} documents")

        # Generate job ID
        job_id = str(uuid.uuid4())

        # Add indexing task to background tasks
        background_tasks.add_task(
            background_indexing_task,
            job_id,
            request.document_urls,
            request.collection_name
        )

        # Return immediate response
        return IndexingResponse(
            job_id=job_id,
            status="started"
        )

    except Exception as e:
        logger.error(f"Error triggering indexing: {e}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error=str(e),
                code="INDEXING_TRIGGER_ERROR"
            ).dict()
        )


async def background_indexing_task(job_id: str, document_urls: List[str], collection_name: str):
    """
    Background task to perform document indexing.

    Args:
        job_id: ID of the indexing job
        document_urls: List of document URLs to index
        collection_name: Name of the collection to index into
    """
    try:
        logger.info(f"Starting background indexing task {job_id} for {len(document_urls)} documents")

        # Convert URLs to file paths (simplified - in reality, you'd need to download files)
        document_paths = [Path(url) for url in document_urls]

        # Index documents
        results = await indexing_orchestrator.batch_index_documents(document_paths, collection_name)

        logger.info(f"Completed indexing task {job_id} with {len(results)} results")
        # In a real implementation, you would store the results somewhere
        # accessible by the client, such as a database or cache

    except Exception as e:
        logger.error(f"Error in background indexing task {job_id}: {e}")
        # In a real implementation, you would update the job status to "failed"
        # and store the error information for the client to retrieve


@router.get("/indexing/{job_id}", response_model=Dict[str, Any])
async def get_indexing_status(job_id: str):
    """
    Get the status of an indexing job.

    Args:
        job_id: ID of the indexing job

    Returns:
        Dictionary with job status and results
    """
    try:
        # In a real implementation, you would retrieve the job status from
        # a database or cache where background tasks store their results
        return {
            "job_id": job_id,
            "status": "processing",  # Simplified - in reality, check actual status
            "message": "Indexing job is in progress"
        }

    except Exception as e:
        logger.error(f"Error getting indexing status for job {job_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error=str(e),
                code="INDEXING_STATUS_ERROR"
            ).dict()
        )