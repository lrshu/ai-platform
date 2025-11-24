"""Post-retrieval module for RAG backend system."""

from typing import List, Dict
from dashscope import TextReRank

class PostRetrieval:
    """Handles post-retrieval operations."""

    def __init__(self, api_key: str):
        """
        Initialize post-retrieval module.

        Args:
            api_key: DashScope API key for reranking.
        """
        self.api_key = api_key

    def rerank(self, question: str, results: List[Dict], top_k: int = 5) -> List[Dict]:
        """
        Rerank retrieval results using DashScopeRerank.

        Args:
            question: User question.
            results: Retrieval results to rerank.
            top_k: Number of top results to return.

        Returns:
            List[Dict]: Reranked results.

        Raises:
            Exception: If reranking fails.
        """
        if not results:
            return []

        try:
            # Prepare inputs for reranking
            documents = [result["content"] for result in results]

            # Call DashScope Rerank API
            response = TextReRank.call(
                model="rerank-english-v2",  # Note: Use appropriate model
                query=question,
                documents=documents,
                top_n=top_k
            )

            # Process response
            reranked_results = []
            for i, match in enumerate(response.output["matches"]):
                original_result = results[match["index"]]
                reranked_results.append({
                    **original_result,
                    "rerank_score": match["score"],
                    "final_score": match["score"]  # Use rerank score as final score
                })

            # Sort by final score
            reranked_results.sort(key=lambda x: x["final_score"], reverse=True)
            return reranked_results
        except Exception as e:
            raise Exception(f"Reranking failed: {str(e)}")

if __name__ == "__main__":
    from dotenv import load_dotenv
    import os

    load_dotenv()
    api_key = os.getenv("QWEN_API_KEY")
    if not api_key:
        raise ValueError("QWEN_API_KEY not found in .env")

    post_retrieval = PostRetrieval(api_key=api_key)
    example_results = [
        {"chunk_id": "1", "content": "RAG systems retrieve relevant documents and generate answers.", "score": 0.9},
        {"chunk_id": "2", "content": "LLMs can generate text without external knowledge.", "score": 0.7},
        {"chunk_id": "3", "content": "Vector embeddings help find similar text chunks.", "score": 0.8}
    ]
    question = "What are RAG systems?"
    reranked = post_retrieval.rerank(question, example_results)
    print(f"Original results: {len(example_results)}")
    print(f"Reranked results: {len(reranked)}")
    for i, result in enumerate(reranked):
        print(f"\nResult {i+1} (Score: {result['final_score']:.4f}):")
        print(f"Content: {result['content']}")