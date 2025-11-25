import fitz  # PyMuPDF
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from . import config

def parse_pdf(file_path: str) -> str:
    """
    Parses a PDF file and returns its text content.
    """
    try:
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        print(f"Failed to parse PDF: {e}")
        return ""

def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> list[str]:
    """
    Splits a long text into smaller chunks.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    chunks = text_splitter.split_text(text)
    return chunks

def get_embeddings(chunks: list[str]) -> list[list[float]]:
    """
    Generates vector embeddings for a list of text chunks.
    """
    embeddings = DashScopeEmbeddings(
        model="text-embedding-v4",
        dashscope_api_key=config.DASHSCOPE_API_KEY
    )
    return embeddings.embed_documents(chunks)

class Graph(BaseModel):
    """Represents a knowledge graph."""
    nodes: list[str] = Field(description="List of nodes in the graph")
    edges: list[tuple[str, str, str]] = Field(description="List of edges in the graph, as (source, target, relationship) tuples")

def get_knowledge_graph(chunks: list[str]) -> Graph:
    """
    Extracts a knowledge graph from a list of text chunks.
    """
    llm = ChatTongyi(
        model="qwen-max",
        dashscope_api_key=config.DASHSCOPE_API_KEY
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful assistant that extracts knowledge graphs from text.",
            ),
            ("human", "Extract a knowledge graph from the following text: {text}"),
        ]
    )

    structured_llm = llm.with_structured_output(Graph)
    chain = prompt | structured_llm
    return chain.invoke({"text": "\n".join(chunks)})
