"""Generation module for RAG backend system."""

import os
from typing import List, Dict
from dotenv import load_dotenv
from dashscope import Generation as DashScopeGeneration

class Qwen3:
    def __init__(self, api_key, base_url):
        self.api_key = api_key
        self.base_url = base_url

    def __call__(self, prompt):
        response = DashScopeGeneration.call(
            model="qwen3-max",
            prompt=prompt,
            api_key=self.api_key
        )
        return response.output['text']

# Load environment variables
load_dotenv()

class Generation:
    """Handles answer generation operations."""

    def __init__(self):
        """Initialize generation module with required configurations."""
        self.llm = Qwen3(
            api_key=os.getenv("QWEN_API_KEY"),
            base_url=os.getenv("QWEN_API_BASE")
        )

    def assemble_prompt(self, question: str, context: List[Dict]) -> str:
        """
        Assemble a prompt for answer generation.

        Args:
            question: User question.
            context: Retrieved context chunks.

        Returns:
            str: Assembled prompt.
        """
        # Format context
        context_text = "\n\n".join([chunk["content"] for chunk in context])

        # Prompt template
        prompt = f"""
        You are a helpful assistant. Answer the following question based on the provided context only.
        If the answer cannot be found in the context, say "I don't have enough information to answer that."

        Context:
        {context_text}

        Question:
        {question}

        Answer:
        """
        return prompt.strip()

    def generate_answer(self, question: str, retrieval_results: List[Dict]) -> Dict:
        """
        Generate an answer based on retrieval results.

        Args:
            question: User question.
            retrieval_results: Reranked retrieval results.

        Returns:
            Dict: Generated answer with sources.

        Raises:
            Exception: If generation fails.
        """
        try:
            # Assemble prompt
            prompt = self.assemble_prompt(question, retrieval_results)

            # Generate answer
            response = self.llm(prompt)

            # Prepare sources
            sources = [
                {
                    "chunk_id": result["chunk_id"],
                    "content": result["content"],
                    "score": result["final_score"]
                }
                for result in retrieval_results
            ]

            return {
                "answer": response.strip(),
                "sources": sources
            }
        except Exception as e:
            raise Exception(f"Answer generation failed: {str(e)}")

if __name__ == "__main__":
    # Example usage
    generation = Generation()
    example_results = [
        {"chunk_id": "1", "content": "RAG systems retrieve relevant documents and generate answers based on that context.", "final_score": 0.95},
        {"chunk_id": "2", "content": "Vector embeddings help find similar text chunks for RAG systems.", "final_score": 0.8}
    ]
    question = "What are RAG systems?"
    answer = generation.generate_answer(question, example_results)
    print(f"Answer: {answer['answer']}")
    print(f"\nSources ({len(answer['sources'])}):")
    for i, source in enumerate(answer['sources']):
        print(f"\nSource {i+1} (Score: {source['score']:.4f}):")
        print(f"Content: {source['content']}")