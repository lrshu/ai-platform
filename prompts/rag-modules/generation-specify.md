### 模块设计文档：Generation (生成模块)

#### 4.1 模块介绍

Generation 模块负责“组装”最终回复。它不直接检索知识，而是接收检索到的上下文（Context），结合系统提示词（System Prompt）和用户问题，构建完整的 Prompt，并调用大模型（LLM）获取回复。支持流式（Streaming）和非流式输出。

#### 4.2 业务流程说明

1. **Prompt 构建**: 根据任务类型（聊天、摘要、翻译），选择对应的 Prompt 模板。
2. **上下文注入**: 将检索到的文档片段（由 Orchestration 传入）填充到 Prompt 的 `{context}` 占位符中。
3. **Token 计算**: (可选) 检查构建后的 Prompt 是否超过模型最大 Token 限制，若超过则截断上下文。
4. **模型调用**: 调用 `Provider` 模块的 LLM 接口。
5. **结果处理**: 处理流式生成器或一次性文本，返回给调用方。

#### 4.3 对外接口说明

- **`generate(query: str, context: List[str], history: List[Message], parameters: dict) -> Generator`**
  - **功能**: 生成回复的核心函数。
  - **参数**: 用户问题、检索到的上下文中列表、历史对话记录、生成参数（temp 等）。
  - **返回**: Python Generator (yield str) 以支持流式输出。

#### 4.4 集成测试用例

- **Case 1: 基于上下文回答**
  - **输入**: Context=["天空是蓝色的"], Query="天空什么颜色?"
  - **期望**: 模型回答包含“蓝色”，且不产生幻觉。
- **Case 2: 拒答测试**
  - **输入**: Context=[], Query="公司 CEO 的私钥是多少?" (且 Prompt 设定若不知则拒答)。
  - **期望**: 模型回答“根据已知信息无法回答...”。
- **Case 3: Prompt 渲染**
  - **测试点**: 验证模板变量 `{context}` 和 `{query}` 是否被正确替换，没有格式错误。

#### 4.5 技术栈选型

- **Jinja2**: 比 f-string 更强大的模板引擎，用于管理复杂的 Prompt 模板（支持条件判断、循环）。
- **LiteLLM / OpenAI SDK**: 虽然 `Provider` 模块负责底层调用，但 Generation 模块需处理 `SystemMessage`, `HumanMessage` 等结构构建。

#### 4.6 需要的配置定义

- `MAX_CONTEXT_TOKENS`: 上下文窗口限制 (如 4096)。
- `DEFAULT_TEMPLATE_ID`: 默认使用的 Prompt 模板 ID。

#### 4.7 项目目录结构

```text
generation/
├── __init__.py
├── prompt_manager.py      # Prompt 模板管理
├── context_builder.py     # 上下文组装逻辑
├── llm_wrapper.py         # LLM 调用封装
└── templates/             # 预置 Prompt 模板文件
    ├── default_chat.jinja2
    └── summary.jinja2
```

#### 4.8 每个目录下 py 文件说明

- **`generation/prompt_manager.py`**:
  - `load_template(template_name)`: 读取 jinja2 文件。
  - `render(template_name, **kwargs)`: 返回渲染后的最终 Prompt 字符串。
- **`generation/context_builder.py`**:
  - `format_context(retrieval_results)`: 将检索结果列表拼接成一个字符串，可能包含引用标记（如 `[Doc 1]: ...`）。
- **`generation/llm_wrapper.py`**:
  - `invoke_llm(prompt_messages, stream=True)`: 调用 `Provider` 模块，返回迭代器。
