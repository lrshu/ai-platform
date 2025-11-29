### 模块设计文档：Storage (存储模块)

#### 8.1 模块介绍

Storage 模块负责系统所有持久化数据的管理。RAG 系统现在需要同时管理 **关系型数据**（如知识库信息、文档状态、聊天记录、用户权限）、**向量数据**（如文档切片的 Embedding 向量）以及 **知识图谱数据**（实体与关系的图结构）。模块通过 **Repository 模式** 封装 SQL 数据库（PostgreSQL/MySQL）、向量数据库（Chroma/Milvus/PgVector）以及图数据库（Neo4j/NebulaGraph/AWS Neptune），让上层业务无需关心底层实现细节。

#### 8.2 业务流程说明

该模块主要是被动响应调用，核心流程为 **CRUD 操作** 和 **连接池管理**：

1. **连接初始化**: 系统启动时，分别建立 SQL、向量库、图数据库连接/会话。
2. **事务管理**: 对关系型、图数据库提供 Session/Transaction 管理，确保跨存储的数据一致性（必要时采用两阶段提交或业务补偿）。
3. **向量操作封装**: 将 `add`, `delete`, `search` 等操作转化为特定向量库的 API 调用。
4. **图谱操作封装**: 提供实体/关系的 Upsert、批量写入、子图检索、最短路径查询等能力，供 Retrieval/Orchestration 模块复用。
5. **混合查询支持**: 支持通过 Dataset/Document ID 将 SQL 元数据、向量结果与图谱节点关联，实现“语义 + 图谱”联合查询。

#### 8.3 对外接口说明

- **`VectorStore.add(dataset_id: str, texts: List[str], embeddings: List[List[float]], metadatas: List[dict]) -> bool`**
  - **功能**: 批量存入向量。
- **`VectorStore.search(dataset_id: str, query_vector: List[float], top_k: int) -> List[SearchResult]`**
  - **功能**: 向量相似度搜索。
- **`GraphStore.upsert_entities(dataset_id: str, nodes: List[GraphNode]) -> bool`**
  - **功能**: 批量写入或更新实体节点。
- **`GraphStore.upsert_edges(dataset_id: str, edges: List[GraphEdge]) -> bool`**
  - **功能**: 批量写入/更新关系边，维护双向引用和属性。
- **`GraphStore.query_subgraph(dataset_id: str, query: GraphQuery, max_hops: int = 3) -> GraphResult`**
  - **功能**: 返回与查询实体相关的子图（节点 + 边），供 Retrieval 模块做知识图谱召回。
- **`DB.chat_history_repo.add_message(session_id: str, role: str, content: str)`**
  - **功能**: 记录一条对话历史。
- **`DB.document_repo.update_status(doc_id: str, status: str)`**
  - **功能**: 更新文档处理状态（如 `processing` -> `completed`）。

#### 8.4 集成测试用例

- **Case 1: 向量存取一致性**
  - **操作**: 存入向量 A (content="test"), 执行搜索。
  - **期望**: 搜索结果包含 A，且 metadata 正确。
- **Case 2: 关系型数据事务**
  - **操作**: 创建 Dataset 记录，但在关联 Document 记录时抛出异常。
  - **期望**: 数据库回滚，Dataset 记录不应存在（原子性）。
- **Case 3: Dataset 隔离**
  - **操作**: 向 Dataset A 存入向量，在 Dataset B 中搜索。
  - **期望**: 搜索结果为空。
- **Case 4: 知识图谱 Upsert + 检索**
  - **操作**: Upsert `设备A -> 属于 -> 机房1` 边，随后查询“设备A 所属机房”。
  - **期望**: `GraphStore.query_subgraph` 返回节点与关系正确，供 Retrieval 继续处理。
- **Case 5: 语义 + 图谱联合查询**
  - **操作**: 向量检索命中文档后，通过 GraphStore 查询其关联实体。
  - **期望**: 返回的 metadata 包含图谱节点 ID，方便 Orchestration 聚合。

#### 8.5 技术栈选型

- **SQLAlchemy (Async)**: 关系型 ORM，支持异步会话。
- **Alembic**: 数据库版本迁移工具。
- **ChromaDB / Milvus / PGVector**: 向量数据库客户端。
- **Neo4j / NebulaGraph / AWS Neptune**: 图数据库实现；可使用 `py2neo`、`nebula3-python` 或官方 SDK。

#### 8.6 需要的配置定义

- `SQL_DATABASE_URI`: 关系型数据库连接串。
- `VECTOR_STORE_TYPE`: 向量库类型 (chroma / milvus / pgvector)。
- `VECTOR_STORE_PATH`: (Chroma) 本地存储路径。
- `VECTOR_STORE_URI`: (Milvus) 远程连接地址。
- `GRAPH_STORE_TYPE`: 图数据库类型 (neo4j / neptune / nebula)。
- `GRAPH_STORE_URI`: 图数据库连接地址。
- `GRAPH_MAX_HOPS`: 默认图谱检索深度。

#### 8.7 项目目录结构

```text
storage/
├── __init__.py
├── config.py
├── database.py             # SQL/向量/图数据库连接工厂
├── models/                 # ORM 模型定义 (SQL Table)
│   ├── __init__.py
│   ├── base.py
│   ├── dataset.py
│   └── chat_history.py
├── repositories/           # 关系型数据访问层 (CRUD)
│   ├── __init__.py
│   ├── dataset_repo.py
│   └── document_repo.py
├── vector_store/           # 向量库适配层
│   ├── __init__.py
│   ├── base.py
│   ├── chroma_store.py
│   └── milvus_store.py
└── graph_store/            # 图数据库适配层
    ├── __init__.py
    ├── base.py             # GraphStore 抽象接口
    ├── neo4j_store.py
    └── nebula_store.py
```

#### 8.8 每个目录下 py 文件说明

- **`storage/models/dataset.py`**: `class Dataset(Base)` 定义 `datasets` 表结构 (id, name, description, created_at)。
- **`storage/repositories/dataset_repo.py`**: `class DatasetRepo` 封装 `create/get_by_id/delete` 等操作。
- **`storage/vector_store/base.py`**: `class BaseVectorStore(ABC)` 定义 `add_vectors`, `delete_vectors`, `search` 抽象方法。
- **`storage/vector_store/chroma_store.py`**: `class ChromaVectorStore(BaseVectorStore)`，实现 ChromaDB 具体调用。
- **`storage/graph_store/base.py`**: `class BaseGraphStore(ABC)`，定义 `upsert_entities`, `upsert_edges`, `query_subgraph`。
- **`storage/graph_store/neo4j_store.py`**: 使用 `py2neo`/Bolt 协议实现图数据库读写，负责 Cypher 构造、批量提交与回溯。

#### 8.9 数据实体结构定义

存储模块需要分别管理 SQL 表、向量库集合以及图谱节点/边，所有实体都必须至少携带 `dataset_id` 以支撑 Dataset 隔离，并通过 `document_id`、`chunk_id`、`graph_id` 等键建立跨存储引用关系。

##### 8.9.1 关系型实体（SQL 数据库）

**Dataset (`datasets`)**

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | UUID | 数据集主键，供全模块引用。 |
| name | VARCHAR(128) | 数据集名称，唯一约束。 |
| description | TEXT | 描述信息。 |
| owner_id | VARCHAR(64) | 数据集归属者/租户 ID。 |
| config | JSONB | 索引策略、分块参数等配置快照。 |
| status | ENUM | `draft/indexing/ready/failed`。 |
| doc_count | INT | 文档数量，写入时增量维护。 |
| chunk_count | INT | 分块数量。 |
| embedding_dim | INT | 最近一次索引的向量维度。 |
| graph_node_count | INT | 关联图节点数量。 |
| last_indexed_at | TIMESTAMP | 最近完成索引时间。 |
| created_at / updated_at / deleted_at | TIMESTAMP | 生命周期字段，软删除保留 `deleted_at`。 |

**Document (`documents`)**

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | UUID | 文档主键。 |
| dataset_id | UUID | 归属数据集，外键 `datasets.id`。 |
| title | VARCHAR(256) | 文档标题或文件名。 |
| source_uri | TEXT | 原始文件路径/URL。 |
| source_type | ENUM | `upload/url/api`。 |
| language | VARCHAR(16) | 语言代码，供多语言检索。 |
| checksum | VARCHAR(64) | 文件内容哈希，支持去重。 |
| metadata | JSONB | 自定义标签（年份、作者等）。 |
| status | ENUM | `uploaded/indexing/ready/failed`。 |
| status_message | TEXT | 失败原因或进度说明。 |
| chunk_count | INT | 已生成的 Chunk 数量。 |
| embedding_model | VARCHAR(128) | 使用的向量模型名。 |
| graph_sync_state | ENUM | `pending/synced/failed`。 |
| created_at / updated_at | TIMESTAMP | 生命周期字段。 |

**DocumentChunk (`document_chunks`)**

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | UUID | Chunk 主键，亦作为向量/图节点的引用 id。 |
| dataset_id | UUID | 冗余 dataset_id，便于过滤。 |
| document_id | UUID | 源文档 id。 |
| chunk_index | INT | 顺序号，配合分页渲染。 |
| content | TEXT | 纯文本内容。 |
| content_tokens | INT | Token 数，便于配额估算。 |
| start_offset / end_offset | INT | 在原文中的起止位置。 |
| section_path | TEXT | 章节层级（如 H1/H2）。 |
| metadata | JSONB | 如页面号、表格标记等。 |
| content_hash | VARCHAR(64) | 分块哈希，用于去重/加速更新。 |
| embedding_id | UUID | 指向向量存储中的记录。 |
| graph_node_ids | TEXT[] | 由 Chunk 衍生的实体节点 id 列表。 |
| created_at | TIMESTAMP | 创建时间。 |

**ChatHistory (`chat_histories`)**

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | UUID | 消息主键。 |
| session_id | VARCHAR(64) | 会话标识。 |
| dataset_id | UUID | 可为空；若绑定 Dataset 则用于审计。 |
| role | ENUM | `user/assistant/system/tool`。 |
| content | TEXT | 消息内容。 |
| content_tokens | INT | Token 数统计。 |
| metadata | JSONB | 包含引用的文档/Chunk ID。 |
| attachments | JSONB | 文件、图谱截图等。 |
| created_at | TIMESTAMP | 发送时间。 |

##### 8.9.2 向量实体（Vector Store）

向量数据库存储原始 embedding；SQL 中保存索引元数据以支持审计与跨存储 Join。

**EmbeddingRecord (`vector_entries`)**

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| embedding_id | UUID | 与向量库主键一致。 |
| dataset_id | UUID | 数据集作用域。 |
| document_id | UUID | 源文档。 |
| chunk_id | UUID | 关联 Chunk。 |
| provider_model | VARCHAR(128) | Embedding 模型名称（与 Provider 模块约定）。 |
| embedding_dim | INT | 维度，用于校验。 |
| embedding_version | VARCHAR(32) | 模型或超参版本。 |
| vector_ref | VARCHAR(128) | 向量库内的集合/namespace + id。 |
| vector_norm | FLOAT | 预计算范数，便于余弦归一化。 |
| metadata | JSONB | 过滤字段（语言、章节等）。 |
| created_at / deleted_at | TIMESTAMP | 创建及软删除时间。 |

##### 8.9.3 图谱实体（Graph Store）

GraphStore 以 `GraphNode`、`GraphEdge` 数据类与底层图数据库映射，以下字段必须在写入时补齐。

**GraphNode (`graph_nodes`)**

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| node_id | VARCHAR(64) | 图数据库节点 id / 自增主键。 |
| dataset_id | UUID | 数据集隔离键。 |
| document_id | UUID | 来源文档。 |
| chunk_id | UUID | 可为空；若由 Chunk 派生则写入以实现回溯。 |
| entity_type | VARCHAR(64) | 实体类别（人物、设备、概念等）。 |
| name | TEXT | 展示名称。 |
| canonical_name | TEXT | 规范化名，用于聚合。 |
| properties | JSON | 属性字典（key-value）。 |
| source_confidence | FLOAT | 信息可信度/打分。 |
| embeddings_ref | VARCHAR(128) | 若节点也写入向量库，记录其 id。 |
| created_at / updated_at | TIMESTAMP | 写入与更新时间。 |

**GraphEdge (`graph_edges`)**

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| edge_id | VARCHAR(64) | 边主键。 |
| dataset_id | UUID | 数据集隔离键。 |
| source_node_id | VARCHAR(64) | 起点 node。 |
| target_node_id | VARCHAR(64) | 终点 node。 |
| relation_type | VARCHAR(64) | 关系类型（属于、位于、依赖等）。 |
| direction | ENUM | `directed/undirected`。 |
| weight | FLOAT | 关系强度/置信度。 |
| properties | JSON | 关系属性，如时间区间。 |
| trace_info | JSON | 追踪来源的 chunk/document/graph pipeline。 |
| created_at / updated_at | TIMESTAMP | 写入与更新时间。 |

以上结构确保 SQL、向量库与图数据库之间可通过 ID 做互相引用，实现 8.2 中的混合查询与 8.4 集成测试所需的隔离、回滚与一致性保障。
