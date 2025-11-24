"""Orchestration module for RAG backend system."""

import os
from typing import List, Dict
from dotenv import load_dotenv

from indexing import Indexing
from pre_retrieval import PreRetrieval
from retrieval import Retrieval
from post_retrieval import PostRetrieval
from generation import Generation

# Load environment variables
load_dotenv()

class Orchestration:
    """Handles orchestration of the RAG pipeline."""

    def __init__(self):
        """Initialize orchestration module."""
        self.indexing = Indexing()
        self.pre_retrieval = PreRetrieval()
        self.retrieval = Retrieval()
        self.post_retrieval = PostRetrieval(api_key=os.getenv("QWEN_API_KEY"))
        self.generation = Generation()

    def index_document(self, name: str, file_path: str) -> Dict:
        """
        Orchestrate document indexing.

        Args:
            name: Name identifier for the document.
            file_path: Path to the PDF file.

        Returns:
            Dict: Indexing result with document ID.

        Raises:
            Exception: If indexing fails.
        """
        try:
            # Step 1: Parse PDF to Markdown
            md_content = self.indexing.parse_pdf(file_path)

            # Step 2: Split content into chunks
            chunks = self.indexing.split_content(md_content)

            # Step 3: Generate embeddings
            chunks_with_embeddings = self.indexing.generate_embeddings(chunks)

            # Step 4: Extract knowledge graph
            chunks_with_kg = self.indexing.extract_knowledge_graph(chunks_with_embeddings)

            # Step 5: Store in Memgraph
            document_id = self.indexing.store_content(name, chunks_with_kg, file_path)

            return {
                "success": True,
                "document_id": document_id,
                "message": f"Document '{name}' indexed successfully",
                "chunk_count": len(chunks)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def retrieve_results(self, name: str, question: str, options: Dict = None) -> Dict:
        """
        Orchestrate content retrieval.

        Args:
            name: Name identifier of the document to search.
            question: User question.
            options: Retrieval options.

        Returns:
            Dict: Retrieval result with reranked results.

        Raises:
            Exception: If retrieval fails.
        """
        # Set default options
        default_options = {
            "top_k": 5,
            "expand_query": True,
            "rerank": True,
            "vector_retrieval": True,
            "graph_retrieval": True
        }
        options = {**default_options, **(options or {})}

        try:
            # Step 1: Pre-retrieval processing
            pre_processed = self.pre_retrieval.pre_retrieval_process(question, expand=options["expand_query"])

            # Step 2: Retrieval
            results = self.retrieval.retrieve(
                name,
                pre_processed["original_question"],
                pre_processed["processed_question"],
                top_k=options["top_k"]
            )

            # Step 3: Post-retrieval (reranking)
            if options["rerank"] and results:
                reranked_results = self.post_retrieval.rerank(
                    pre_processed["original_question"],
                    results,
                    top_k=options["top_k"]
                )
            else:
                # No reranking, just add final_score field
                reranked_results = []
                for result in results:
                    reranked_result = {**result, "final_score": result["score"]}
                    reranked_results.append(reranked_result)

            return {
                "success": True,
                "question": pre_processed["original_question"],
                "processed_question": pre_processed["processed_question"],
                "expanded_queries": pre_processed["expanded_queries"],
                "results": reranked_results,
                "options": options
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def generate_response(self, name: str, question: str, options: Dict = None) -> Dict:
        """
        Orchestrate answer generation.

        Args:
            name: Name identifier of the document to use.
            question: User question.
            options: Generation options.

        Returns:
            Dict: Generation result with answer and sources.

        Raises:
            Exception: If generation fails.
        """
        # Retrieve results first
        retrieval_result = self.retrieve_results(name, question, options)

        if not retrieval_result["success"]:
            return retrieval_result

        try:
            # Step: Generate answer
            generation_result = self.generation.generate_answer(
                question,
                retrieval_result["results"]
            )

            return {
                "success": True,
                "question": retrieval_result["question"],
                "answer": generation_result["answer"],
                "sources": generation_result["sources"],
                "options": retrieval_result["options"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

if __name__ == "__main__":
    # Example usage
    orchestration = Orchestration()
    # # Index a document
    # index_result = orchestration.index_document("rag_doc", "rag_overview.pdf")
    # print(index_result)
    #
    # # Retrieve results
    # retrieve_result = orchestration.retrieve_results("rag_doc", "What are RAG systems?")
    # print(f"Retrieved {len(retrieve_result['results'])} results")
    #
    # # Generate answer
    # generate_result = orchestration.generate_response("rag_doc", "What are RAG systems?")
    # print(f"Answer: {generate_result['answer']}")