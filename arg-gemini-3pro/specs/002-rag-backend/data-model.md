# Data Model: RAG Backend System

This document defines the key data entities for the RAG backend system.

## 1. KnowledgeBase

Represents a named collection of processed documents.

- **Attributes**:
    - `name`: `string` (Primary Key) - A unique name for the knowledge base.
    - `created_at`: `datetime` - The timestamp when the knowledge base was created.

## 2. Document

Represents a source document that has been indexed.

- **Attributes**:
    - `id`: `string` (Primary Key) - A unique identifier for the document.
    - `knowledge_base_name`: `string` (Foreign Key to KnowledgeBase)
    - `file_name`: `string` - The name of the original file.
    - `indexed_at`: `datetime` - The timestamp when the document was indexed.

## 3. TextChunk

Represents a chunk of text extracted from a document, stored in Memgraph. This will be a node in the graph.

- **Node Label**: `TextChunk`
- **Properties**:
    - `id`: `string` (Primary Key) - A unique identifier for the chunk.
    - `document_id`: `string` - The ID of the source document.
    - `text`: `string` - The text content of the chunk.
    - `vector`: `list[float]` - The vector embedding of the text.

## 4. Entity

Represents a named entity extracted from a text chunk. This will be a node in the graph.

- **Node Label**: `Entity`
- **Properties**:
    - `name`: `string` (Primary Key) - The name of the entity (e.g., "LangChain", "Python").

## 5. Relationship

Represents a relationship between two entities. This will be an edge in the graph.

- **Edge Type**: Dynamically named based on the relationship type (e.g., `IS_A`, `USES`).
- **Properties**:
    - `source`: `Entity` - The source entity.
    - `target`: `Entity` - The target entity.
    - `type`: `string` - The type of the relationship.

## Relationships between Nodes

- A `TextChunk` node can be linked to `Entity` nodes that are mentioned within it using a `CONTAINS` relationship.
- `Entity` nodes are connected to each other via various relationship types.
