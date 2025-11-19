# Data Model: Providers Module

## Entities

### ProviderConfiguration
Configuration parameters for external service access

**Fields**:
- provider_name: str - Name of the provider (e.g., "Qwen", "Mineru")
- model_name: str - Name of the specific model to use
- api_key: str - API key for authentication (loaded from environment variables)
- api_endpoint: str - Base URL for the API
- timeout: int - Request timeout in seconds (default: 30)
- retry_attempts: int - Number of retry attempts for failed requests (default: 3)

**Validation Rules**:
- provider_name must be one of the supported providers
- model_name must be a valid model for the specified provider
- api_endpoint must be a valid URL
- timeout must be positive
- retry_attempts must be non-negative

### ServiceCallLog
Record of interactions with external services for monitoring and debugging

**Fields**:
- timestamp: datetime - When the call was made
- provider_name: str - Name of the provider that was called
- method: str - HTTP method used (GET, POST, etc.)
- endpoint: str - Specific endpoint that was called
- request_data: dict - Data sent in the request (sanitized for sensitive information)
- response_status: int - HTTP status code of the response
- response_time: float - Time taken for the request in seconds
- error_message: str - Error message if the call failed (optional)

**Validation Rules**:
- timestamp must be a valid datetime
- provider_name must not be empty
- method must be a valid HTTP method
- endpoint must not be empty
- response_status must be a valid HTTP status code
- response_time must be non-negative

### TextGenerationRequest
Request for text generation from LLM

**Fields**:
- prompt: str - The prompt to send to the LLM
- max_tokens: int - Maximum number of tokens to generate (default: 1000)
- temperature: float - Sampling temperature (default: 0.7)
- top_p: float - Top-p sampling parameter (default: 0.9)

**Validation Rules**:
- prompt must not be empty
- max_tokens must be positive
- temperature must be between 0 and 1
- top_p must be between 0 and 1

### TextGenerationResponse
Response from text generation

**Fields**:
- generated_text: str - The generated text
- finish_reason: str - Reason why generation stopped
- usage: dict - Information about token usage

**Validation Rules**:
- generated_text must not be None
- finish_reason must be a valid finish reason

### EmbeddingRequest
Request for text embedding

**Fields**:
- text: str - The text to embed
- model: str - The model to use for embedding

**Validation Rules**:
- text must not be empty
- model must be a valid embedding model

### EmbeddingResponse
Response from text embedding

**Fields**:
- embeddings: list - List of embedding vectors
- model: str - The model used for embedding
- usage: dict - Information about token usage

**Validation Rules**:
- embeddings must be a list of numbers
- model must not be empty

### RerankRequest
Request for result reranking

**Fields**:
- query: str - The original query
- documents: list - List of documents to rerank
- top_n: int - Number of top results to return

**Validation Rules**:
- query must not be empty
- documents must be a list of strings
- top_n must be positive

### RerankResponse
Response from result reranking

**Fields**:
- results: list - List of reranked results with scores
- model: str - The model used for reranking

**Validation Rules**:
- results must be a list of dictionaries with 'document' and 'score' keys
- model must not be empty

### DocumentParseRequest
Request for document parsing

**Fields**:
- document_content: bytes - The document content to parse
- document_type: str - The type of document (PDF, image, etc.)

**Validation Rules**:
- document_content must not be empty
- document_type must be a supported document type

### DocumentParseResponse
Response from document parsing

**Fields**:
- extracted_text: str - The text extracted from the document
- metadata: dict - Additional metadata about the document

**Validation Rules**:
- extracted_text must not be None
- metadata must be a dictionary

## Relationships

- ProviderConfiguration is used by QwenProvider and MineruProvider
- ServiceCallLog is created by QwenProvider and MineruProvider for each external call
- TextGenerationRequest is processed by QwenProvider's ITextGenerator implementation
- TextGenerationResponse is returned by QwenProvider's ITextGenerator implementation
- EmbeddingRequest is processed by QwenProvider's IEmbedder implementation
- EmbeddingResponse is returned by QwenProvider's IEmbedder implementation
- RerankRequest is processed by QwenProvider's IReranker implementation
- RerankResponse is returned by QwenProvider's IReranker implementation
- DocumentParseRequest is processed by MineruProvider's IDocumentParser implementation
- DocumentParseResponse is returned by MineruProvider's IDocumentParser implementation

## State Transitions

No explicit state transitions for the data entities in this module.