# Data Model: RAG Backend

## Entities

### SearchRequest
**Description**: Represents a search query with dynamic pipeline control parameters
**Fields**:
- query (string): The natural language query text
- use_hyde (boolean): Flag to enable/disable HyDE query expansion
- use_rerank (boolean): Flag to enable/disable reranking of results
- top_k (integer): Number of top results to return
- top_p (float): Nucleus sampling parameter for generation
- temperature (float): Temperature parameter for generation

### Chunk
**Description**: Represents a document chunk with content and embedding
**Fields**:
- id (string): Unique identifier for the chunk
- content (string): The text content of the chunk
- embedding (list[float]): Vector embedding of the chunk content
- metadata (DocumentMetadata): Metadata about the chunk's origin
- created_at (datetime): Timestamp when the chunk was created

### DocumentMetadata
**Description**: Metadata tracking the origin and position of content within a document
**Fields**:
- document_id (string): Identifier of the source document
- start_index (integer): Start position of the content in the document
- end_index (integer): End position of the content in the document
- parent_id (string): Reference to parent chunk for Small-to-Big strategy
- source_type (string): Type of source document (PDF, DOCX, etc.)
- title (string): Title of the document (if available)
- author (string): Author of the document (if available)

### Entity
**Description**: Extracted information from documents stored as graph nodes
**Fields**:
- id (string): Unique identifier for the entity
- name (string): Name of the entity
- type (string): Type/category of the entity
- description (string): Description of the entity
- created_at (datetime): Timestamp when the entity was created

### Relationship
**Description**: Relationships between entities stored as graph edges
**Fields**:
- id (string): Unique identifier for the relationship
- source_entity_id (string): ID of the source entity
- target_entity_id (string): ID of the target entity
- relationship_type (string): Type of relationship
- description (string): Description of the relationship
- confidence (float): Confidence score of the relationship extraction

### GenerationResponse
**Description**: Response from the LLM generation module
**Fields**:
- response_text (string): The generated text response
- sources (list[Chunk]): Chunks used as context for generation
- created_at (datetime): Timestamp when the response was generated

## Relationships

1. **Chunk** → **DocumentMetadata**: Each chunk has one metadata object describing its source
2. **Chunk** → **Chunk** (parent-child): Child chunks reference their parent chunk via parent_id
3. **Entity** ↔ **Entity**: Entities are connected via Relationship objects
4. **GenerationResponse** → **Chunk**: Generation responses reference the chunks used as context

## Validation Rules

1. **SearchRequest**:
   - query must not be empty
   - top_k must be between 1 and 100
   - top_p must be between 0 and 1
   - temperature must be between 0 and 2

2. **Chunk**:
   - content must not be empty
   - embedding must be a list of floats with consistent dimensions
   - metadata must reference a valid document

3. **DocumentMetadata**:
   - document_id must be a valid identifier
   - start_index and end_index must be non-negative
   - start_index must be less than end_index

4. **Entity**:
   - name must not be empty
   - type must be specified

5. **Relationship**:
   - source_entity_id and target_entity_id must reference existing entities
   - relationship_type must be specified

## State Transitions

N/A - Most entities are immutable once created. The system is primarily focused on creation and retrieval rather than state changes.