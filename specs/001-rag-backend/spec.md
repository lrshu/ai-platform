# Feature Specification: RAG Backend Implementation

**Feature Branch**: `001-rag-backend`
**Created**: 2025-11-20
**Status**: Draft
**Input**: User description: "create feature for rag backend

2. Integrated Functional Specifications (综合功能规格)

2.1 Core Infrastructure (基础架构层)

目标: 建立系统的骨架，定义所有交互的标准协议。
• 接口定义 (app/common/interfaces/):
◦ 必须建立独立的 Python 包。
◦ 包含纯抽象类：IDatabase, ITextGenerator, IEmbedder, IReranker, IDocumentParser。
• 数据模型 (app/common/models.py):
◦ SearchRequest: 包含查询 query 及动态开关 (use_hyde, use_rerank, top_k)。
◦ Chunk: 包含 content, embedding, metadata。
◦ DocumentMetadata: 必须包含 溯源信息 (document_id, start_index, end_index, parent_id)。
• 配置管理 (app/common/config_loader.py):
◦ 加载 config.json5，支持注释。
◦ 支持环境变量覆盖敏感信息 (API Keys)。

示例配置 (config.json5):

```json
// 应用配置示例 (使用 JSON5 格式，支持注释)
{
  // 数据库配置
  "database": {
    "uri": "bolt://localhost:7687",
    "user": "memgraph",
    "password": "password"
  },

  // 核心 RAG 流水线能力配置 (定义每个能力使用的 Provider 和 Model/Version)
  "pipeline_capabilities": {
    // Embedding 能力配置
    "embedder": {
      "provider": "Qwen",
      "name": "text-embedding-v4" // 统一键名
    },
    // LLM Generator/HyDE/Expansion 能力配置
    "generator": {
      "provider": "Qwen",
      "name": "qwen-plus" // 统一键名
    },
    // Rerank 能力配置
    "reranker": {
      "provider": "Qwen",
      "name": "gte-rerank" // 统一键名
    },
    // 文档解析能力配置
    "parser": {
      "provider": "Mineru",
      "name": "v1" // 统一键名 (原 api_version)
    }
  },

  // 具体的 Provider 实现类映射 (用于运行时反射实例化)
  "provider_map": {
    // 路径已更新，指向 app/providers 模块
    "Qwen": "app.providers.qwen_provider.QwenProvider",
    "Mineru": "app.providers.mineru_provider.MineruProvider"
  }

  // 注意: 'module_toggles' 已移除，该配置由 API 请求动态传入
}
```

2.2 Implementation Layer (实现层)

目标: 实现具体的业务能力，隔离外部依赖。
• Capability Providers (app/providers/):
◦ QwenProvider: 封装 DashScope API，实现 Generator, Embedder, Reranker 三个接口。需处理 name 参数以支持不同模型 (qwen-plus vs qwen-max)。
◦ MineruProvider: 封装 Mineru API，实现 DocumentParser 接口。
• Database (app/database/):
◦ MemgraphDB: 使用 python-memgraph 实现 IDatabase。
◦ 功能:
▪ Vector Search (基于 Memgraph MAGE)。
▪ Keyword Search (基于 Memgraph Fulltext Index)。
▪ Graph Storage (Nodes/Edges) & Traversal。

2.3 RAG Logic Pipeline (业务逻辑层)

目标: 实现 RAG 的核心处理流程，模块间松耦合。
• Indexing Module (app/indexing/):
◦ Small-to-Big: 切分 Parent Chunk ($\sim 1000t$) 和 Child Chunk ($\sim 200t$)。
◦ Graph Extraction: 利用 LLM 提取实体关系写入图库。
◦ Persistence: Child Chunks $\rightarrow$ Vector Index; Entities $\rightarrow$ Graph.

• Pre-Retrieval (检索前): 查询理解与重写 (HyDE, Query Expansion)。
◦ HyDE:目标: 生成假设性回答，增强查询理解。
◦ Query Expansion:目标: 将复杂问题分解为子问题，提高检索召回率。

• Retrieval Module (app/retrieval/):
◦ HyDE: 向量化 $\rightarrow$ 检索。
◦ Search: 执行 Vector + Keyword + Graph Search，并合并结果。

• Post-Retrieval (app/post_retrieval/):
◦ Rerank: 对检索结果进行截断和重排序。
◦ Context Recall: 关键步骤，根据 Child Chunk 的 parent_id 从 DB 召回完整的 Parent Chunk。

• Generation Module (app/generation/):
◦ LLM Inference: 组装 Prompt 并执行生成。

2.4 Application Layer (应用层)

目标: 编排流程并对外服务。
• Orchestration (app/orchestration/):
◦ RAGPipeline: 核心类。构造函数接收所有 Logic Modules 的实例（依赖注入）。
◦ Dynamic Run: run(request: SearchRequest) 方法根据 Request 中的开关 (use_hyde 等) 动态决定数据流向（例如：跳过 HyDE，直接检索）。
• API Gateway (app/api/):
◦ Endpoint: POST /api/rag/search：Streaming: 使用 SSE (StreamingResponse) 流式返回 LLM 生成的 Token。
◦ Endpoint: POST /api/rag/indexing：触发 Indexing 流程， 指定要索引的文档地址。
◦ Error Handling: 捕获 Pipeline 异常并返回标准 HTTP 错误。"

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.

  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently

  For RAG backend features, ensure stories align with the six pipeline stages:
  1. Indexing: Parse → Split → Embed → Store (Graph + Vector)
  2. Pre-Retrieval: Query understanding and rewriting (HyDE, Query Expansion)
  3. Retrieval: Multi-path recall (Hybrid Search)
  4. Post-Retrieval: Context optimization (Rerank, Selection)
  5. Generation: Prompt assembly and LLM inference
  6. Orchestration: Dynamic module scheduling controlled by user requests
-->

### User Story 1 - Document Indexing and Storage (Priority: P1)

As a system administrator, I want to index documents and store them in both vector and graph databases so that users can search through them later.

**Why this priority**: This is the foundational capability that enables all other RAG functionalities. Without proper indexing, no search or generation can occur.

**Independent Test**: Can be fully tested by uploading a test document, triggering the indexing process, and verifying that both vector embeddings and graph entities are correctly stored in their respective databases.

**Acceptance Scenarios**:

1. **Given** a document file, **When** the indexing API is called, **Then** the document is parsed, split into parent and child chunks, embedded, and stored in both vector and graph databases.
2. **Given** a successfully indexed document, **When** I query the databases directly, **Then** I can find both the vector embeddings of child chunks and the extracted graph entities.

---

### User Story 2 - Basic Search and Retrieval (Priority: P2)

As an end user, I want to search for information using natural language queries so that I can find relevant document content.

**Why this priority**: This is the core user-facing functionality that delivers immediate value. It enables users to retrieve information from indexed documents.

**Independent Test**: Can be tested by submitting a search query and verifying that relevant document chunks are returned with appropriate similarity scores.

**Acceptance Scenarios**:

1. **Given** indexed documents, **When** I submit a search query, **Then** the system returns relevant document chunks ranked by relevance.
2. **Given** a search with the HyDE toggle enabled, **When** I submit a query, **Then** the system generates a hypothetical answer before performing vector search.

---

### User Story 3 - Enhanced Answer Generation (Priority: P3)

As an end user, I want to receive coherent answers generated by an LLM based on retrieved document context so that I don't have to read through documents myself.

**Why this priority**: This enhances the user experience by providing synthesized answers rather than just relevant document snippets.

**Independent Test**: Can be tested by submitting a question and verifying that a coherent, contextually relevant answer is generated and streamed back to the user.

**Acceptance Scenarios**:

1. **Given** retrieved document context, **When** I submit a query, **Then** the system generates and streams back a coherent answer based on the context.
2. **Given** a query with reranking enabled, **When** I submit the query, **Then** the results are reranked before answer generation for improved relevance.

---

[Add more user stories as needed, each with an assigned priority]

### Edge Cases

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right edge cases.
-->

- What happens when the document parsing service is unavailable?
- How does system handle queries with no relevant results?
- What happens when the database connection is lost during indexing?
- How does the system handle very large documents that exceed processing limits?

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.

  For RAG backend features, ensure requirements align with the Provider Abstraction principle:
  - External services must be implemented as capability providers
  - Core RAG logic must be configuration-driven
  - All modules must follow Single Responsibility Principle
-->

### Functional Requirements

- **FR-001**: System MUST provide abstract interfaces for all external services (IDatabase, ITextGenerator, IEmbedder, IReranker, IDocumentParser).
- **FR-002**: System MUST implement concrete providers for Qwen (DashScope) and Mineru APIs.
- **FR-003**: System MUST support configuration-driven capability selection with environment variable overrides for sensitive data.
- **FR-004**: System MUST implement Small-to-Big chunking strategy with parent chunks (~1000 tokens) and child chunks (~200 tokens).
- **FR-005**: System MUST extract entities and relationships from documents using LLM and store them in a graph database.
- **FR-006**: System MUST support HyDE (Hypothetical Document Embeddings) for query understanding enhancement.
- **FR-007**: System MUST perform hybrid search combining vector, keyword, and graph search capabilities.
- **FR-008**: System MUST implement context recall to retrieve full parent chunks based on child chunk results.
- **FR-009**: System MUST provide streaming response for generated answers using SSE (Server-Sent Events).
- **FR-010**: System MUST implement dynamic pipeline orchestration based on request parameters.

*Example of marking unclear requirements:*

- **FR-011**: System MUST handle document indexing for [NEEDS CLARIFICATION: which document formats are supported - PDF, DOCX, TXT, HTML?]
- **FR-012**: System MUST retain indexed documents for [NEEDS CLARIFICATION: document retention period not specified - indefinite, 1 year, 5 years?]

### Key Entities *(include if feature involves data)*

- **SearchRequest**: Contains query text and dynamic switches (use_hyde, use_rerank, top_k) to control pipeline behavior.
- **Chunk**: Contains content, embedding vector, and metadata including parent-child relationships.
- **DocumentMetadata**: Contains溯源 information (document_id, start_index, end_index, parent_id) for tracking content origins.
- **Entity**: Extracted information from documents stored in the graph database with relationships to other entities.

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.

  For RAG backend features, consider metrics aligned with the pipeline stages:
  - Indexing throughput and accuracy
  - Query understanding effectiveness
  - Retrieval precision and recall
  - Reranking quality
  - Generation relevance and latency
  - Orchestration efficiency
-->

### Measurable Outcomes

- **SC-001**: System can index 100 pages of documents per minute with 95%+ accuracy in entity extraction.
- **SC-002**: Search queries return relevant results in under 500ms for 95% of requests.
- **SC-003**: Generated answers are rated as relevant and helpful by users 85% of the time.
- **SC-004**: System handles 100 concurrent search requests without degradation in performance.
- **SC-005**: Context recall successfully retrieves parent chunks for 99% of child chunk results.