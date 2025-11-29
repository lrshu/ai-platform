### 模块设计文档：Provider (模型供应商模块)

#### 9.1 模块介绍

Provider 模块实现了 **Model-as-a-Service**。它将 LLM（大语言模型）、Embedding 模型、Rerank 模型以及 **文档解析 (Document Parsing)** 的调用逻辑与业务逻辑完全解耦。通过适配器模式，系统可以在 OpenAI、Anthropic、Ollama、Cohere、Unstructured、AWS Textract 等多家厂商之间自由切换，同时为 Indexing、Post-Retrieval、Retrieval 等模块提供统一的文本生成、向量、重排序与解析能力。

#### 9.2 业务流程说明

1. **工厂初始化**: 根据配置（`LLM_PROVIDER`、`EMBEDDING_PROVIDER`、`RERANK_PROVIDER`、`PARSER_PROVIDER`），工厂类实例化对应的 Client，并缓存单例。
2. **统一参数**: 上层传入标准化的消息或文档对，Provider 负责转换为特定厂商 API 需要的格式（如 Anthropic Messages、OpenAI ChatCompletion、Cohere Rerank 请求、Unstructured/Textract 解析请求等）。
3. **调用与重试**: 执行 API 调用，内置指数退避重试与超时控制，确保在网络抖动或速率限制下保持稳定。
4. **统一输出**: 将厂商返回的复杂 JSON 响应统一清洗为标准的 `str`、`Generator`、`List[float]`、`List[float] scores`、`ParsedDocument` 等结构，并补齐 metadata（模型名、耗时、token/page 计数）。
5. **多模态解析支持**: 当接收到 PDF、DOCX、Image 等文件时，ParserClient 负责调用解析厂商 API，返回结构化文本块（包含段落、表格、版面信息），供 Indexing 模块直接消费。

#### 9.3 对外接口说明

- **`LLMClient.chat(messages: List[dict], stream: bool = True) -> Generator | str`**
  - 文本生成，支持流式。
- **`EmbeddingClient.embed_documents(texts: List[str]) -> List[List[float]]`**
  - 批量向量化文档。
- **`EmbeddingClient.embed_query(text: str) -> List[float]`**
  - 单句向量化查询。
- **`RerankClient.score(query: str, documents: List[str], top_n: int = 5) -> List[RerankResult]`**
  - 对查询与候选文档进行交互式打分，返回排序后的 Top-N 结果。
- **`ParserClient.parse(document: RawDocument, strategy: ParseStrategy) -> ParsedDocument`**
  - 对 PDF/DOCX/HTML/Image 等文档执行解析，返回结构化的 `ParsedDocument`，包含段落、表格、版面块、metadata。
- **`ParserClient.batch_parse(documents: List[RawDocument]) -> List[ParsedDocument]`**
  - 支持批量解析或多页解析，结合并发与速率控制。

#### 9.4 集成测试用例

- **Case 1: 模型切换**
  - **操作**: 将 `LLM_PROVIDER` 从 OpenAI 改为 MockLLM，调用 `chat`。
  - **期望**: 无需改代码，返回 Mock 的固定结果。
- **Case 2: Embedding 维度检查**
  - **操作**: 调用 `embed_query("hello")`。
  - **期望**: 返回列表长度等于配置 `EMBEDDING_DIM` (如 1536)。
- **Case 3: Rerank 输出一致性**
  - **操作**: 调用 `RerankClient.score`，传入固定 query/docs。
  - **期望**: 返回结果包含 `doc_id`, `score`，排序与厂商接口一致。
- **Case 4: 流式输出完整性**
  - **操作**: 调用 `chat(stream=True)`，拼接所有 yield 的字符。
  - **期望**: 拼接后的完整字符串与非流式调用结果语义一致。
- **Case 5: 文档解析一致性**
  - **操作**: 调用 `ParserClient.parse` 解析带有表格的 PDF。
  - **期望**: 返回 `ParsedDocument` 中的 `blocks` 按页/区域排序，表格以结构化 JSON 表示，包含行列坐标。
- **Case 6: 批量解析速率控制**
  - **操作**: `ParserClient.batch_parse` 同时处理多份文档。
  - **期望**: 遵循厂商速率限制，失败任务自动重试。

#### 9.5 技术栈选型

- **LiteLLM**: 统一调度 OpenAI, Azure, Anthropic, Ollama, Cohere 等 100+ 模型厂商。
- **Tenacity**: 指数退避重试。
- **Cohere Rerank / BAAI BGE-Reranker / Jina Rerank API**: 可插拔的 Rerank 实现。

#### 9.6 需要的配置定义

- `LLM_PROVIDER`, `LLM_MODEL_NAME`, `API_KEY`, `API_BASE_URL`
- `EMBEDDING_PROVIDER`, `EMBEDDING_MODEL_NAME`
- `RERANK_PROVIDER` (cohere / jina / local)
- `RERANK_MODEL_NAME` 或 `RERANK_MODEL_PATH`
- `RERANK_TOP_N`: 默认返回数量
- `PARSER_PROVIDER` (unstructured / textract / local)
- `PARSER_MODEL_NAME` or `PARSER_CONFIG`
- `PARSER_STRATEGY`: `fast / high_quality / layout_preserve`
- `PARSER_MAX_PAGE_PARALLELISM`: 控制并发解析页数
- `PARSER_CACHE_TTL`: 解析结果缓存时长
- `MAX_FILE_SIZE_MB`: 解析接口允许的最大文件
- `SUPPORTED_MIME_TYPES`: 白名单 MIME，前置校验

#### 9.7 项目目录结构

```text
provider/
├── __init__.py
├── config.py
├── factory.py              # 工厂模式入口
├── llm/                    # LLM 适配器
│   ├── __init__.py
│   ├── base.py
│   └── litellm_wrapper.py
├── embedding/              # Embedding 适配器
│   ├── __init__.py
│   ├── base.py
│   └── openai_embedding.py
└── rerank/                 # Rerank 适配器
    ├── __init__.py
    ├── base.py             # 抽象 RerankClient
    ├── cohere_rerank.py
    └── local_bge_rerank.py
```

#### 9.8 每个目录下 py 文件说明

- **`provider/factory.py`**
  - `get_llm_client()`, `get_embedding_client()`, `get_rerank_client()`：读取配置并缓存单例。
- **`provider/llm/base.py`**
  - `class BaseLLM`: 定义 `chat` 抽象接口。
- **`provider/llm/litellm_wrapper.py`**
  - `invoke(messages, stream)`: 调用 `litellm.completion(...)` 并处理异常。
- **`provider/rerank/base.py`**
  - `class BaseRerankClient`: 定义 `score(query, documents, top_n)`。
- **`provider/rerank/cohere_rerank.py`**
  - 组装 Cohere API 请求体，返回 `RerankResult`，支持多语言、批量。
- **`provider/rerank/local_bge_rerank.py`**
  - 加载本地 Cross-Encoder（如 `BAAI/bge-reranker-large`），在 CPU/GPU 上执行批量打分。
