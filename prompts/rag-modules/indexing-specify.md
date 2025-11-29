### 模块设计文档：Indexing (索引模块)

#### 1.1 模块介绍

Indexing 模块负责处理非结构化数据到结构化/向量数据的转换过程。它是 RAG 系统知识库构建的核心。主要功能包括文档解析（Parsing）、文本切片（Chunking）、向量化（Embedding）、知识图谱化（Knowledge Graphing）以及索引构建（Indexing）。

#### 1.2 业务流程说明

1. **接收输入**: 接收来自 API 或 Orchestration 传递的原始文档对象（文件路径或二进制流）。
2. **统一解析 (Provider Parser)**: 直接调用 Provider 模块的 `ParserClient.parse/batch_parse` 接口，根据文件类型（PDF, MD, TXT, DOCX、Image 等）获取标准化的 `ParsedDocument`（包含 blocks/layout/metadata）。
3. **数据清洗 (Cleaning)**: 对 `ParsedDocument.blocks` 提供的文本进行清洗，去除乱码、多余空格、不可见字符。
4. **文本切片 (Chunking)**: 根据配置（Chunk Size, Overlap）将清洗后的文本片段切分为 Chunk。
5. **向量化 (Embedding)**: 调用 `Provider` 模块的 Embedding 接口，将文本片段转换为向量。
6. **知识图谱化 (Knowledge Graphing)**: 基于文本片段抽取实体与关系，构建轻量级图结构供下游查询或推理使用。
7. **数据存储 (Persisting)**: 调用 `Storage` 模块，将“文本片段 + 向量/图谱节点 + 元数据”存入向量数据库、图数据库与关系型数据库。

> **说明**: Indexing 模块不再单独维护 Loader 层的解析器，而是复用 Provider 的 Parser 能力，确保所有模块对解析策略、重试、速率限制的处理保持一致。

> **并行处理**: 对多文件/多页场景，可直接调用 `ParserClient.batch_parse` 配合并发策略，解析结果沿用 `ParsedDocument` 标准结构。
#### 1.3 对外接口说明

该模块通常作为内部 Service 被 Orchestration 调用，不直接暴露 HTTP 接口（除非作为微服务）。

- **`index_document(dataset_id: str, document: DocumentObj) -> bool`**
  - **功能**: 对单个文档进行全流程索引。
  - **参数**: 数据集 ID，文档对象（包含内容、元数据）。
  - **返回**: 成功/失败布尔值。
- **`delete_document_index(dataset_id: str, doc_id: str) -> bool`**
  - **功能**: 从向量库中删除指定文档的所有切片。

#### 1.4 集成测试用例

- **Case 1: PDF 文档索引**
  - **输入**: 一个包含表格和文本的标准 PDF 文件。
  - **期望**: 解析出文本，切片数量符合预期（如 1000 字切为 3-4 段），向量库中查询到对应数量的向量。
- **Case 2: 脏数据处理**
  - **输入**: 包含乱码的 TXT 文件。
  - **期望**: 清洗后无乱码，成功入库。
- **Case 3: 更新文档**
  - **输入**: 对已存在的 `doc_id` 再次调用索引。
  - **期望**: 旧向量被删除，新向量写入。

#### 1.5 技术栈选型

- **LangChain / LlamaIndex (Core)**: 用于文档加载器（Loaders）和切分器（Splitters）的实现，生态丰富。
- **Unstructured**: 用于复杂格式（如 PDF 表格提取）的解析。
- **Pydantic**: 用于数据模型定义，保证类型安全。
- **Asyncio**: 这是一个 I/O 密集型模块（读文件、调 API、写库），必须全异步处理。

#### 1.6 需要的配置定义

- `CHUNK_SIZE`: 切片大小，默认 512 tokens。
- `CHUNK_OVERLAP`: 切片重叠，默认 50 tokens。
- `EMBEDDING_MODEL_ID`: 使用的模型 ID（对应 Provider 模块配置）。
- `PARSER_STRATEGY`: 解析策略（Fast/HighQuality）。

#### 1.7 项目目录结构

```text
indexing/
├── __init__.py
├── config.py           # 模块配置
├── manager.py          # 模块入口，对外暴露的 Facade
├── loaders/            # 文档加载器（薄封装 Provider Parser）
│   ├── __init__.py
│   ├── base.py
│   └── provider_loader.py
├── splitters/          # 文本切分器
│   ├── __init__.py
│   └── text_splitter.py
└── processors/         # 核心处理流程
    ├── __init__.py
    └── pipeline.py
```

#### 1.8 每个目录下 py 文件说明

**1. `indexing/config.py`**

- **作用**: 定义 Indexing 模块的配置类。
- **函数**: 无，主要是 Pydantic Model 定义。
  - `IndexingConfig`: 包含 chunk_size, embedding_model 等字段。

**2. `indexing/loaders/base.py`**

- **作用**: 定义 Loader 抽象基类，统一对 Provider Parser 的调用。
- **类/函数**:
  - `class BaseLoader`:
    - `parse(document: DocumentInput) -> ParsedDocument`: 抽象方法，直接返回 Provider 标准化结构。

**3. `indexing/loaders/provider_loader.py`**

- **作用**: 对 `ParserClient` 的薄封装，实现通用文档解析。
- **函数**:
  - `parse(document, strategy)`:
    - **逻辑**: 根据配置选择 `parse` 或 `batch_parse`，传递必要的 metadata（dataset_id、checksum、parser_strategy），将结果交给下游 Splitter。

**4. `indexing/splitters/text_splitter.py`**

- **作用**: 封装切分逻辑。
- **函数**:
  - `split_text(parsed_doc: ParsedDocument, chunk_size: int, overlap: int) -> List[Chunk]`:
    - **逻辑**: 遍历 `ParsedDocument.blocks`，组合文本后调用 LangChain 的 `RecursiveCharacterTextSplitter` 进行切分，同时保留 layout/metadata。

**5. `indexing/processors/pipeline.py`**

- **作用**: 串联 Parse -> Split -> Embed -> Store。
- **函数**:
  - `process_and_save(dataset_id, doc_id, document_input)`:
    - **逻辑**:
      1. `parsed = Loader.parse(document_input)` (调用 Provider Parser)
      2. `chunks = Splitter.split(parsed)`
      3. `vectors = Provider.embed(chunks)`
      4. `graph = GraphBuilder.build(chunks)`
      5. `Storage.save(vectors, graph, metadata)`

**6. `indexing/manager.py`**

- **作用**: 模块对外统一入口。
- **函数**:
  - `run_indexing_task(dataset_id, document_data)`:
    - **逻辑**: 初始化 Pipeline，捕获异常，记录日志，调用 `process_and_save`。
    - **返回**: 任务状态（Success/Failed）。

> **迁移说明**: 历史上 Loader 直接依赖文件解析库（`pypdf`、`unstructured`），现在统一迁移到 Provider Parser，减少解析代码重复并继承 Provider 的重试、缓存与多模态解析能力。Splitters/Processors 中若需访问原始 layout，可通过 `ParsedDocument` 的 metadata 获取。