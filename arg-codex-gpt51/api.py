from fastapi import FastAPI, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel

from src import orchestration
from src.models import RetrievalResult, GenerationResult

app = FastAPI(title="RAG Backend API", description="API for search and chat functionalities")

# Request models
class SearchRequest(BaseModel):
    name: str
    question: str
    top_k: Optional[int] = 5
    expand_query: Optional[bool] = True
    rerank: Optional[bool] = True
    use_vector: Optional[bool] = True
    use_keyword: Optional[bool] = False
    use_graph: Optional[bool] = True

class ChatRequest(BaseModel):
    name: str
    question: str
    top_k: Optional[int] = 5
    expand_query: Optional[bool] = True
    rerank: Optional[bool] = True
    use_vector: Optional[bool] = True
    use_keyword: Optional[bool] = False
    use_graph: Optional[bool] = True

# Response models
class SearchResult(RetrievalResult):
    pass

class ChatResponse(GenerationResult):
    pass

@app.post("/search", response_model=List[SearchResult])
async def search(request: SearchRequest):
    """
    Search for relevant documents based on the question
    """
    try:
        options = orchestration.SearchOptions(
            top_k=request.top_k,
            expand_query=request.expand_query,
            rerank=request.rerank,
            use_vector=request.use_vector,
            use_keyword=request.use_keyword,
            use_graph=request.use_graph
        )

        results = orchestration.search(request.name, request.question, options)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with the system based on the question and retrieved context
    """
    try:
        options = orchestration.SearchOptions(
            top_k=request.top_k,
            expand_query=request.expand_query,
            rerank=request.rerank,
            use_vector=request.use_vector,
            use_keyword=request.use_keyword,
            use_graph=request.use_graph
        )

        result = orchestration.chat(request.name, request.question, options)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)