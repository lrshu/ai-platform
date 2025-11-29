### 模块设计文档：Pre-Retrieval (检索前处理模块)

#### 6.1 模块介绍

Pre-Retrieval 模块致力于优化用户的原始查询（Query）。用户的提问往往是口语化的、含糊的，或者依赖于历史对话上下文的（如使用代词“它”）。本模块通过 **查询重写（Query Rewriting）**、**查询扩展（Query Expansion）** 和 **意图识别（Intent Recognition）** 等技术，将用户的自然语言转换为更适合机器检索的形式。

#### 6.2 业务流程说明

1. **接收输入**: 接收用户原始 Query 和历史对话记录 History。
2. **指代消解 (Coreference Resolution)**: 如果 History 存在，利用 LLM 结合上下文将 Query 中的代词（如“它”、“这个”）替换为具体实体（如“上个问题提到的 iPhone 15”）。
3. **查询扩展 (Expansion)** (可选):
   - **同义词扩展**: 生成查询关键词的同义词。
   - **子问题拆解**: 将复杂问题拆解为多个简单的子查询（Sub-queries）。
4. **格式化输出**: 输出一个或多个优化后的查询字符串，供 Orchestration 调用 Retrieval 模块。

#### 6.3 对外接口说明

- **`optimize(query: str, history: List[Message], method: str = "rewrite") -> List[str]`**
  - **功能**: 核心优化接口。
  - **参数**:
    - `query`: 用户原始问题。
    - `history`: 对话历史（用于补充上下文）。
    - `method`: 优化策略 (`rewrite` | `expand` | `hybrid`)。
  - **返回**: 优化后的查询列表（通常情况下是一个重写后的 Query，若是扩展策略则可能是多个）。

#### 6.4 集成测试用例

- **Case 1: 历史上下文补全**
  - **输入**: History=[User: "介绍一下 Docker"], Query="它的核心组件有哪些？"
  - **期望**: 输出 `["Docker 的核心组件有哪些？"]`。
- **Case 2: 独立问题保持不变**
  - **输入**: History=[], Query="北京天气如何？"
  - **期望**: 输出 `["北京天气如何？"]`（无变化或仅微调）。
- **Case 3: 多角度扩展 (Expansion)**
  - **输入**: Query="如何学习 Python"
  - **期望**: 输出 `["如何学习 Python", "Python 学习路线图", "Python 初学者教程"]`。

#### 6.5 技术栈选型

- **LLM (Prompt Engineering)**: 目前效果最好的重写方式是直接调用 LLM（如 GPT-3.5-turbo），通过 Prompt 指令让模型补全上下文。
- **NLTK / SpaCy**: 用于传统的关键词提取（作为轻量级备选方案）。

#### 6.6 需要的配置定义

- `PRE_RETRIEVAL_ENABLED`: 全局开关。
- `REWRITE_MODEL_ID`: 用于重写的模型 ID（通常用快且便宜的模型）。
- `MAX_HISTORY_ROUNDS`: 重写时参考的历史对话轮数（如最近 3 轮）。

#### 6.7 项目目录结构

```text
pre_retrieval/
├── __init__.py
├── config.py
├── service.py              # 对外 Facade
├── rewritters/             # 重写器实现
│   ├── __init__.py
│   ├── base.py
│   └── llm_rewriter.py     # 基于 LLM 的重写
└── expanders/              # 扩展器实现
    ├── __init__.py
    └── generated_queries.py
```

#### 6.8 每个目录下 py 文件说明

- **`pre_retrieval/rewritters/llm_rewriter.py`**:
  - `class LLMRewriter`:
    - `rewrite(query, history)`:
      - **逻辑**: 构建 Prompt（例如：“基于以下历史对话，将用户最新的问题改写为独立、完整的句子...”），调用 `Provider` 的 LLM 接口，解析返回文本。
- **`pre_retrieval/service.py`**:
  - `optimize(...)`:
    - **逻辑**: 根据配置判断是否开启优化。若关闭，直接返回 `[query]`。若开启，实例化 `LLMRewriter` 并执行。
