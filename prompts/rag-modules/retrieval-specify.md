### 模块设计文档：Retrieval (检索模块)

#### 3.1 模块介绍

Retrieval 模块负责从存储层（Storage）中精准获取与用户查询最相关的文档片段（Chunks）。它是决定 RAG 系统回答准确性的关键瓶颈。它不仅支持简单的向量相似度搜索，通常还需支持关键词搜索（BM25）以及两者的混合检索（Hybrid Search）。

#### 3.2 业务流程说明

1. **查询向量化**: 接收用户 Query，调用 `Provider` 模块将 Query 转换为向量（Query Embedding）。
2. **构建检索条件**: 解析用户请求中的过滤参数（如：只检索某个特定 metadata 的文档）。
3. **执行检索**:
   - **向量检索 (Dense)**: 在向量数据库中查找相似度最高的 Top-K 片段。
   - **关键词检索 (Sparse)**: (可选) 在倒排索引中查找关键词匹配的片段。
4. **结果聚合**: 如果使用了混合检索，对多路召回的结果进行加权合并（如 Reciprocal Rank Fusion, RRF）。
5. **结果标准化**: 将存储层返回的原始数据转换为统一的 `RetrievalResult` 对象列表返回。

#### 3.3 对外接口说明

- **`search(dataset_id: str, query_text: str, top_k: int = 4, score_threshold: float = 0.5, filters: dict = None) -> List[Node]`**
  - **功能**: 执行核心检索逻辑。
  - **参数**:
    - `dataset_id`: 目标知识库 ID。
    - `query_text`: 用户查询文本。
    - `top_k`: 返回片段数量。
    - `score_threshold`: 相似度截断阈值。
    - `filters`: 元数据过滤条件（如 `{"source": "policy.pdf"}`）。
  - **返回**: 包含文本内容、元数据、相似度分数的节点列表。

#### 3.4 集成测试用例

- **Case 1: 语义检索**
  - **输入**: 知识库中有“苹果是水果”，查询“Apple 是什么类别”。
  - **期望**: 返回包含“苹果是水果”的片段，且 similarity score > 0.8。
- **Case 2: 过滤检索**
  - **输入**: 查询“合同条款”，filter=`{"year": 2023}`。
  - **期望**: 仅返回 metadata 中 year 为 2023 的文档，忽略 2022 的相关文档。
- **Case 3: 空结果处理**
  - **输入**: 查询完全无关的乱码字符串。
  - **期望**: 返回空列表，且不抛出异常。

#### 3.5 技术栈选型

- **Vector DB Clients**: 依赖 `Storage` 模块的统一接口，但内部逻辑需适配如 Chroma/Milvus/PGVector 的查询语法。
- **NumPy**: 用于本地进行简单的向量运算或分数处理（如果需要）。
- **Rank-BM25**: 如果数据库不支持原生混合检索，可在 Python 层实现简单的 BM25 算法作为补充。

#### 3.6 需要的配置定义

- `DEFAULT_TOP_K`: 默认检索数量 (4)。
- `DEFAULT_SCORE_THRESHOLD`: 默认相似度阈值 (0.0)。
- `RETRIEVAL_STRATEGY`: 检索策略 (dense, sparse, hybrid)。

#### 3.7 项目目录结构

```text
retrieval/
├── __init__.py
├── config.py
├── engine.py              # 检索主入口
├── strategies/            # 不同检索策略实现
│   ├── __init__.py
│   ├── base.py
│   ├── dense.py           # 纯向量检索
│   └── hybrid.py          # 混合检索
└── schemas.py             # 数据结构定义
```

#### 3.8 每个目录下 py 文件说明

- **`retrieval/schemas.py`**:
  - `RetrievalResult`: 定义返回的数据类，包含 `content`, `score`, `metadata`。
- **`retrieval/strategies/base.py`**:
  - `class BaseStrategy`: 定义 `retrieve(...)` 抽象方法。
- **`retrieval/strategies/dense.py`**:
  - `retrieve(...)`:
    1. 调用 `Provider.embed_query(query)`。
    2. 调用 `Storage.vector_store.search(vector, top_k, filters)`。
- **`retrieval/engine.py`**:
  - `search(...)`: 工厂模式入口。根据配置初始化对应的 Strategy (如 DenseStrategy)，执行检索并返回结果。
