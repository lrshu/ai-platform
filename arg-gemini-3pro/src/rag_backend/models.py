from gqlalchemy import Node, Relationship
from datetime import datetime

class KnowledgeBase(Node):
    name: str
    created_at: datetime

class Document(Node):
    id: str
    knowledge_base_name: str
    file_name: str
    indexed_at: datetime

class TextChunk(Node):
    id: str
    document_id: str
    text: str
    vector: list[float]

class Entity(Node):
    name: str

class Contains(Relationship):
    pass
