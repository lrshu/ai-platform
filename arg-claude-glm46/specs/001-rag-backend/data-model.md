# Data Model: RAG Backend System

## Document

Represents a PDF file that has been indexed in the system.

**Fields**:
- id (string, primary key): Unique identifier for the document
- name (string): User-provided name for the document
- file_path (string): Path to the original PDF file
- created_at (datetime): Timestamp when document was indexed
- status (enum): Indexing status (pending, processing, completed, failed)
- chunk_count (integer): Number of chunks created from the document
- metadata (JSON): Additional document metadata (author, title, etc.)

## Chunk

Represents a segment of document content with associated embeddings and metadata.

**Fields**:
- id (string, primary key): Unique identifier for the chunk
- document_id (string, foreign key): Reference to the parent document
- content (text): The actual text content of the chunk
- position (integer): Position of chunk within the document
- embedding (vector): Numerical representation for similarity search
- metadata (JSON): Chunk-specific metadata
- created_at (datetime): Timestamp when chunk was created

**Relationships**:
- Belongs to one Document
- Can have multiple EntityMentions

## Entity

Represents a named entity extracted from document content.

**Fields**:
- id (string, primary key): Unique identifier for the entity
- name (string): Name of the entity
- type (string): Type of entity (person, organization, location, etc.)
- description (text): Description of the entity (optional)

## EntityMention

Represents a specific mention of an entity within a chunk.

**Fields**:
- id (string, primary key): Unique identifier for the entity mention
- entity_id (string, foreign key): Reference to the entity
- chunk_id (string, foreign key): Reference to the chunk containing the mention
- position_start (integer): Start position of mention within chunk
- position_end (integer): End position of mention within chunk
- confidence (float): Confidence score of entity recognition

**Relationships**:
- Belongs to one Entity
- Belongs to one Chunk

## Relationship

Represents a relationship between two entities extracted from document content.

**Fields**:
- id (string, primary key): Unique identifier for the relationship
- source_entity_id (string, foreign key): Reference to the source entity
- target_entity_id (string, foreign key): Reference to the target entity
- type (string): Type of relationship (works_for, located_in, etc.)
- description (text): Description of the relationship
- confidence (float): Confidence score of relationship extraction

**Relationships**:
- Belongs to one source Entity
- Belongs to one target Entity

## Query

Represents a user query processed by the system.

**Fields**:
- id (string, primary key): Unique identifier for the query
- content (text): The original query text
- expanded_content (text): Expanded query text after preprocessing
- created_at (datetime): Timestamp when query was processed
- user_id (string): Identifier for the user (if applicable)

## SearchResult

Represents a search result returned to the user.

**Fields**:
- id (string, primary key): Unique identifier for the search result
- query_id (string, foreign key): Reference to the query
- chunk_id (string, foreign key): Reference to the matched chunk
- relevance_score (float): Relevance score from search
- rank (integer): Rank position in result set
- reranked_score (float): Score after reranking (if applicable)

**Relationships**:
- Belongs to one Query
- Belongs to one Chunk

## Conversation

Represents a conversation session with context preservation.

**Fields**:
- id (string, primary key): Unique identifier for the conversation
- created_at (datetime): Timestamp when conversation started
- updated_at (datetime): Timestamp of last interaction
- context (JSON): Conversation context and history

## ConversationTurn

Represents a single turn in a conversation.

**Fields**:
- id (string, primary key): Unique identifier for the turn
- conversation_id (string, foreign key): Reference to the conversation
- query_id (string, foreign key): Reference to the query
- response (text): Generated response
- turn_number (integer): Sequential number of turn in conversation
- created_at (datetime): Timestamp when turn was processed

**Relationships**:
- Belongs to one Conversation
- Belongs to one Query