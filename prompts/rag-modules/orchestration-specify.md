### 模块设计文档：Orchestration (编排模块)

#### 5.1 模块介绍

Orchestration 是 RAG 系统的大脑。它不处理具体任务，而是将 Indexing, Retrieval, Generation 等模块串联起来，定义业务的工作流（Workflow）。它负责处理 API 层的请求，控制整个 RAG 流程的执行顺序和数据流转。

#### 5.2 业务流程说明

以最经典的 **Chat 流程**为例：

1. **接收请求**: 收到 Api 模块传来的 `chat(dataset_id, query)` 请求。
2. **查询预处理 (Pre-Retrieval)**: (调用 Pre-Retrieval 模块) 对用户 Query 进行重写或扩展（如将“它多少钱”重写为“iPhone 15 多少钱”）。
3. **执行检索 (Retrieval)**: 调用 `Retrieval.search()` 获取相关文档片段。
4. **检索后处理 (Post-Retrieval)**: (调用 Post-Retrieval 模块) 对检索结果进行重排序 (Rerank) 或去重。
5. **生成回复 (Generation)**: 将处理后的 Top-K 片段和 Query 传给 `Generation.generate()`。
6. **流式响应**: 将 Generation 返回的生成器逐个 yield 给 Api 层。
7. **异步记录**: 对话结束后，异步保存“问题-答案-引用源”到数据库（Storage），用于后续分析。

#### 5.3 对外接口说明

- **`chat_pipeline(dataset_id: str, query: str, history: list) -> AsyncGenerator`**
  - **功能**: RAG 对话主流程。
- **`search_pipeline(dataset_id: str, query: str) -> dict`**
  - **功能**: 纯检索流程（用于调试或知识库测试）。
  - **返回**: 包含检索到的文档列表及其分数。

#### 5.4 集成测试用例

- **Case 1: 标准 RAG 流程**
  - **操作**: 模拟各个子模块（Mock Retrieval 返回固定文档，Mock LLM 返回固定文本），运行 pipeline。
  - **期望**: 验证数据是否正确地从一个模块流向下一个模块，最终输出符合预期。
- **Case 2: 检索为空时的降级处理**
  - **操作**: Mock Retrieval 返回空列表。
  - **期望**: Pipeline 应能检测到空上下文，直接让 LLM 基于自身知识回答或返回预设话术（取决于配置）。

#### 5.5 技术栈选型

- **LangGraph / Custom Python Logic**: 对于复杂的编排（如 Agentic RAG），可以使用 LangGraph。对于当前标准 RAG，**纯 Python 代码**编写控制流（Controller）是最清晰、最易调试的。
- **Asyncio**: 必须全链路异步，保证高并发下的吞吐量。

#### 5.6 需要的配置定义

- `ENABLE_RERANK`: 是否开启重排序步骤 (True/False)。
- `ENABLE_QUERY_REWRITE`: 是否开启查询重写 (True/False)。

#### 5.7 项目目录结构

```text
orchestration/
├── __init__.py
├── workflows/             # 具体的工作流定义
│   ├── __init__.py
│   ├── base.py
│   ├── chat_flow.py       # 聊天工作流
│   └── search_flow.py     # 搜索工作流
└── service.py             # 对外暴露的 Service 类
```

#### 5.8 每个目录下 py 文件说明

- **`orchestration/workflows/chat_flow.py`**:
  - `class ChatFlow`:
    - `execute(query, dataset_id, history)`:
      ```python
      # 伪代码逻辑
      rewritten_query = PreRetrieval.process(query)
      raw_docs = Retrieval.search(dataset_id, rewritten_query)
      reranked_docs = PostRetrieval.process(raw_docs)
      response_stream = Generation.generate(query, reranked_docs, history)
      return response_stream
      ```
- **`orchestration/service.py`**:
  - `OrchestrationService`: 单例模式，被 Api 层依赖。
  - `chat(...)`: 实例化 `ChatFlow` 并运行。
  - `search(...)`: 实例化 `SearchFlow` 并运行。
