### 模块设计文档：Post-Retrieval (检索后处理模块)

#### 7.1 模块介绍

Post-Retrieval 模块负责在 Retrieval 粗召回之后进一步精排。当前方案完全依赖 Provider 模块暴露的 `RerankClient` 能力，对候选片段进行交互式打分、过滤与裁剪，并可选地补充知识图谱上下文。

#### 7.2 业务流程说明

1. **接收输入**: 接收 Retrieval 模块返回的文档列表（List of Nodes）、图谱节点信息以及用户 Query。
2. **去重 (Deduplication)**: 根据内容哈希或节点 ID 去除完全重复的文档/实体。
3. **知识图谱融合 (可选)**: 若节点带有 Graph metadata，调用 `Storage.GraphStore.query_subgraph` 拉取相关实体，拼接到候选文本中。
4. **Rerank 调用**: 将 `<query, document>` 或 `<query, graph snippet>` 对传入 `Provider.RerankClient.score`，获取交互式相关性得分。
5. **阈值过滤 + Top-N 截断**: 剔除分数低于 `SCORE_THRESHOLD` 的候选，保留得分最高的 N 个文档。
6. **窗口适配 (Optional)**: 计算累计 Token 数，确保总长度不超过 Generation 模块的上下文限制。

#### 7.3 对外接口说明

- **`process(nodes: List[Node], query: str, top_n: int = 4) -> List[Node]`**
  - **功能**: 对检索结果进行精修。
  - **参数**:
    - `nodes`: 原始检索结果列表，包含文本、score、graph metadata。
    - `query`: 用户查询（用于相关性打分）。
    - `top_n`: 最终保留的数量。
  - **返回**: 排序并截断后的节点列表，score 来源于 Provider Rerank。

#### 7.4 集成测试用例

- **Case 1: Provider Rerank 打分覆盖**
  - **操作**: Mock `RerankClient.score` 返回固定分数，执行 `process`。
  - **期望**: 输出顺序与 mock 得分一致。
- **Case 2: Graph metadata 融合**
  - **操作**: 节点包含 graph_id，触发子图查询。
  - **期望**: 拼接后的内容被一起传入 Rerank，最终结果包含 graph 注释。
- **Case 3: 阈值过滤**
  - **操作**: 设置 `SCORE_THRESHOLD=0.7`，模拟一个低分文档。
  - **期望**: 低分文档被过滤，返回列表长度缩短。
- **Case 4: 空输入**
  - **操作**: `nodes=[]`。
  - **期望**: 返回 []，不调用 Provider。

#### 7.5 技术栈选型

- **Provider.RerankClient**: 统一封装 Cohere、Jina、BGE-Reranker 等模型。
- **Storage.GraphStore**: 供可选的图谱上下文注入。

#### 7.6 需要的配置定义

- `RERANK_TOP_N`: 最终返回数量。
- `SCORE_THRESHOLD`: 过滤阈值。
- `ENABLE_GRAPH_CONTEXT`: 是否向 Rerank 注入图谱信息。

#### 7.7 项目目录结构

```text
post_retrieval/
├── __init__.py
├── config.py
├── service.py              # 对外 Facade
└── filters/
    ├── __init__.py
    └── deduplication.py
```

#### 7.8 关键文件说明

- **`post_retrieval/service.py`**
  - `process(...)`：核心入口，包含以下步骤：
    1. 调用 `deduplicate(nodes)`。
    2. 若开启图谱增强，调用 `GraphStore.query_subgraph` 拼接上下文。
    3. 构造文档文本数组，调用 `RerankClient.score(query, docs, top_n)`。
    4. 根据得分排序、阈值过滤、Top-N 截断，并返回最终节点列表。
- **`post_retrieval/filters/deduplication.py`**
  - 提供基于内容哈希或 graph_id 的去重工具。
