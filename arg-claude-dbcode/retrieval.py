"""Retrieval module for RAG backend system."""

import os
from typing import List, Dict
from dotenv import load_dotenv
from dashscope import TextEmbedding

class QwenEmbeddings:
    def __init__(self):
        self.model = "text-embedding-v1"

    def embed_query(self, text):
        response = TextEmbedding.call(
            model=self.model,
            input=[text]
        )
        return response.output['embeddings'][0]['embedding']
from langchain_community.graphs import Neo4jGraph

# Load environment variables
load_dotenv()

class Retrieval:
    """Handles retrieval operations."""

    def __init__(self):
        """Initialize retrieval module with required configurations."""
        self.embeddings = QwenEmbeddings()
        self.graph = Neo4jGraph(
            url=os.getenv("DATABASE_URL"),
            username=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD")
        )

    def get_query_embedding(self, original_question: str, processed_question: str) -> List[float]:
        """
        Generate embedding for the processed question.

        Args:
            original_question: Original user question.
            processed_question: Processed/expanded question.

        Returns:
            List[float]: Query embedding.
        """
        # Use processed question for embedding
        return self.embeddings.embed_query(processed_question)

    def hybrid_search(self, name: str, question: str, query_embedding: List[float], top_k: int = 5) -> List[Dict]:
        """
        Perform hybrid vector + graph search.

        Args:
            name: Name identifier of the document to search.
            question: User question.
            query_embedding: Embedding of the processed question.
            top_k: Number of top results to return.

        Returns:
            List[Dict]: Merged search results.
        """
        # Step 1: Vector search
        vector_query = """
        MATCH (d:Document {document_name: $name})-[:HAS_CHUNK]->(c:TextChunk)
        WITH c, vector.similarity_cosine(c.embedding, $query_embedding) AS similarity
        WHERE similarity > 0.7
        RETURN c.chunk_id AS chunk_id, c.content AS content, similarity AS score, 'vector' AS type
        ORDER BY similarity DESC
        LIMIT $top_k
        """
        vector_results = self.graph.query(
            vector_query,
            {"name": name, "query_embedding": query_embedding, "top_k": top_k}
        )

        # Step 2: Graph search (entity-based)
        # Extract entities from question (simplified)
        import re
        entities = re.findall(r'\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\b', question)
        unique_entities = list(set(entities))

        graph_results = []
        if unique_entities:
            # Search for chunks mentioning these entities
            entity_placeholders = ", ".join([f"'{entity}'" for entity in unique_entities])
            graph_query = f"""
            MATCH (d:Document {{document_name: $name}})-[:HAS_CHUNK]->(c:TextChunk)-[:MENTIONS]->(e:Entity)
            WHERE e.entity_name IN [{entity_placeholders}]
            WITH c.chunk_id AS chunk_id, c.content AS content, count(e) AS entity_count
            RETURN chunk_id, content, toFloat(entity_count) AS score, 'graph' AS type
            ORDER BY entity_count DESC
            LIMIT $top_k
            """
            try:
                graph_results = self.graph.query(
                    graph_query,
                    {"name": name, "top_k": top_k}
                )
            except Exception as e:
                print(f"Graph search error: {str(e)}")

        # Step 3: Merge results
        merged_results = {}

        # Add vector results
        for result in vector_results:
            chunk_id = result["chunk_id"]
            if chunk_id not in merged_results:
                merged_results[chunk_id] = {
                    "chunk_id": chunk_id,
                    "content": result["content"],
                    "vector_score": result["score"],
                    "graph_score": 0,
                    "type": [result["type"]]
                }

        # Add graph results
        for result in graph_results:
            chunk_id = result["chunk_id"]
            if chunk_id in merged_results:
                merged_results[chunk_id]["graph_score"] = result["score"]
                if result["type"] not in merged_results[chunk_id]["type"]:
                    merged_results[chunk_id]["type"].append(result["type"])
            else:
                merged_results[chunk_id] = {
                    "chunk_id": chunk_id,
                    "content": result["content"],
                    "vector_score": 0,
                    "graph_score": result["score"],
                    "type": [result["type"]]
                }

        # Calculate combined score and prepare final results
        final_results = []
        for chunk_id, data in merged_results.items():
            # Combine scores (equal weight for vector and graph)
            combined_score = data["vector_score"] + data["graph_score"]
            final_results.append({
                "chunk_id": data["chunk_id"],
                "content": data["content"],
                "score": combined_score,
                "vector_score": data["vector_score"],
                "graph_score": data["graph_score"],
                "match_type": data["type"]
            })

        # Sort by combined score and take top_k
        final_results.sort(key=lambda x: x["score"], reverse=True)
        return final_results[:top_k]

    def retrieve(self, name: str, original_question: str, processed_question: str, top_k: int = 5) -> List[Dict]:
        """
        Execute retrieval process.

        Args:
            name: Name identifier of the document to search.
            original_question: Original user question.
            processed_question: Processed/expanded question.
            top_k: Number of top results to return.

        Returns:
            List[Dict]: Retrieval results.
        """
        # Generate query embedding
        query_embedding = self.get_query_embedding(original_question, processed_question)

        # Perform hybrid search
        return self.hybrid_search(name, original_question, query_embedding, top_k=top_k)

if __name__ == "__main__":
    # Example usage
    retrieval = Retrieval()
    original_question = "Explain RAG systems?"
    processed_question = "Explain RAG systems? Describe RAG systems? What is RAG systems? How does RAG systems?"
    results = retrieval.retrieve("example_doc", original_question, processed_question)
    print(f"Retrieved {len(results)} results:")
    for i, result in enumerate(results):
        print(f"\nResult {i+1} (Score: {result['score']:.4f}):")
        print(f"Match types: {result['match_type']}")
        print(f"Content: {result['content'][:100]}...")