# Data Model: RAG Backend System

## Overview

This document describes the data model for the RAG backend system, including entities, relationships, and validation rules.

## Entities

### DocumentCollection

Represents a named grouping of related documents.

**Fields**:
- `id` (string, primary key): Unique identifier for the collection
- `name` (string): User-provided name for the collection
- `created_at` (datetime): Timestamp when the collection was created
- `updated_at` (datetime): Timestamp when the collection was last updated

**Validation Rules**:
- `name` must be unique
- `name` must be between 1 and 100 characters
- `created_at` and `updated_at` must be valid datetime values

### Document

Represents a single document that has been indexed.

**Fields**:
- `id` (string, primary key): Unique identifier for the document
- `collection_id` (string, foreign key): Reference to the DocumentCollection
- `file_path` (string): Path to the original document file
- `title` (string): Title of the document (extracted from metadata or filename)
- `created_at` (datetime): Timestamp when the document was indexed
- `updated_at` (datetime): Timestamp when the document was last updated

**Validation Rules**:
- `collection_id` must reference an existing DocumentCollection
- `file_path` must be a valid file path
- `title` must be between 1 and 200 characters

### DocumentChunk

Represents a segment of text extracted from a document.

**Fields**:
- `id` (string, primary key): Unique identifier for the chunk
- `document_id` (string, foreign key): Reference to the Document
- `content` (text): The extracted text content of the chunk
- `position` (integer): Position of the chunk within the document
- `metadata` (JSON): Additional metadata about the chunk
- `created_at` (datetime): Timestamp when the chunk was created

**Validation Rules**:
- `document_id` must reference an existing Document
- `content` must not be empty
- `position` must be a non-negative integer

### VectorEmbedding

Represents the numerical vector representation of a document chunk.

**Fields**:
- `id` (string, primary key): Unique identifier for the embedding
- `chunk_id` (string, foreign key): Reference to the DocumentChunk
- `vector` (array of floats): The vector embedding values
- `model_name` (string): Name of the model used to generate the embedding
- `created_at` (datetime): Timestamp when the embedding was generated

**Validation Rules**:
- `chunk_id` must reference an existing DocumentChunk
- `vector` must be an array of floating-point numbers
- `model_name` must not be empty

### KnowledgeGraphNode

Represents an entity extracted from document content.

**Fields**:
- `id` (string, primary key): Unique identifier for the node
- `chunk_id` (string, foreign key): Reference to the DocumentChunk
- `entity_type` (string): Type of entity (e.g., person, place, organization)
- `name` (string): Name of the entity
- `description` (text): Description of the entity
- `created_at` (datetime): Timestamp when the node was created

**Validation Rules**:
- `chunk_id` must reference an existing DocumentChunk
- `entity_type` must not be empty
- `name` must be between 1 and 200 characters

### KnowledgeGraphRelationship

Represents a relationship between two entities.

**Fields**:
- `id` (string, primary key): Unique identifier for the relationship
- `source_node_id` (string, foreign key): Reference to the source KnowledgeGraphNode
- `target_node_id` (string, foreign key): Reference to the target KnowledgeGraphNode
- `relationship_type` (string): Type of relationship (e.g., "works_at", "located_in")
- `description` (text): Description of the relationship
- `created_at` (datetime): Timestamp when the relationship was created

**Validation Rules**:
- `source_node_id` and `target_node_id` must reference existing KnowledgeGraphNodes
- `relationship_type` must not be empty
- A relationship cannot have the same source and target node

### Query

Represents a user-provided question or search term.

**Fields**:
- `id` (string, primary key): Unique identifier for the query
- `content` (text): The query text
- `created_at` (datetime): Timestamp when the query was submitted

**Validation Rules**:
- `content` must not be empty

### RetrievalResult

Represents a document chunk identified as relevant to a query.

**Fields**:
- `id` (string, primary key): Unique identifier for the result
- `query_id` (string, foreign key): Reference to the Query
- `chunk_id` (string, foreign key): Reference to the DocumentChunk
- `relevance_score` (float): Score indicating relevance to the query
- `rank` (integer): Rank of this result in the result set
- `created_at` (datetime): Timestamp when the result was generated

**Validation Rules**:
- `query_id` must reference an existing Query
- `chunk_id` must reference an existing DocumentChunk
- `relevance_score` must be between 0.0 and 1.0
- `rank` must be a non-negative integer

### ConversationContext

Represents the history of previous questions and answers in a chat session.

**Fields**:
- `id` (string, primary key): Unique identifier for the conversation
- `session_id` (string): Identifier for the chat session
- `query_id` (string, foreign key): Reference to the Query
- `response` (text): The generated response to the query
- `created_at` (datetime): Timestamp when the conversation entry was created

**Validation Rules**:
- `session_id` must not be empty
- `query_id` must reference an existing Query
- `response` must not be empty

## Relationships

1. **DocumentCollection** 1 → N **Document**
2. **Document** 1 → N **DocumentChunk**
3. **DocumentChunk** 1 → 1 **VectorEmbedding**
4. **DocumentChunk** 1 → N **KnowledgeGraphNode**
5. **KnowledgeGraphNode** N → N **KnowledgeGraphRelationship** (source and target)
6. **Query** 1 → N **RetrievalResult**
7. **DocumentChunk** 1 → N **RetrievalResult**
8. **Query** 1 → N **ConversationContext**
9. **DocumentChunk** 1 → N **KnowledgeGraphNode**

## Indexes

- Primary keys on all `id` fields
- Index on `DocumentCollection.name` for fast lookup
- Index on `Document.collection_id` for efficient collection queries
- Index on `DocumentChunk.document_id` for efficient document queries
- Index on `VectorEmbedding.chunk_id` for efficient vector lookups
- Index on `KnowledgeGraphNode.chunk_id` for efficient chunk-entity lookups
- Index on `KnowledgeGraphRelationship.source_node_id` and `target_node_id` for efficient relationship queries
- Index on `RetrievalResult.query_id` for efficient result retrieval
- Index on `ConversationContext.session_id` for efficient session lookups

## Constraints

- Foreign key constraints to maintain referential integrity
- Unique constraint on `DocumentCollection.name`
- Check constraints on score ranges and non-negative values