"""LangChain core components setup."""

from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_core.output_parsers import StrOutputParser


def create_basic_prompt(template: str, input_variables: list) -> PromptTemplate:
    """
    Create a basic prompt template.

    Args:
        template (str): Template string with placeholders
        input_variables (list): List of input variable names

    Returns:
        PromptTemplate: Configured prompt template
    """
    return PromptTemplate(
        template=template,
        input_variables=input_variables
    )


def create_runnable_chain(prompt: PromptTemplate, llm) -> RunnableSequence:
    """
    Create a runnable chain with prompt and LLM.

    Args:
        prompt (PromptTemplate): Prompt template
        llm: Language model instance

    Returns:
        RunnableSequence: Configured runnable chain
    """
    return prompt | llm | StrOutputParser()


def split_text_by_tokens(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> list:
    """
    Split text into chunks based on token count.

    Args:
        text (str): Text to split
        chunk_size (int): Maximum chunk size in tokens
        chunk_overlap (int): Overlap between chunks in tokens

    Returns:
        list: List of text chunks
    """
    # This is a simple implementation - in practice, you might want to use
    # a more sophisticated tokenizer
    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size - chunk_overlap):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)

    return chunks