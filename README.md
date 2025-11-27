# AI-Platform: 编码开发智能体评测

本仓库旨在评测和比较不同 AI 编码智能体在 **规格驱动开发 (Specification-Driven Development, SDD)** 模式下的代码生成能力。所有项目均使用 [GitHub Spec Kit](https://github.com/github/spec-kit) 工具链，遵循预设的“宪法”和功能规格，从零开始生成一个 RAG (Retrieval-Augmented Generation) 后端应用。

---

## 1. 评测结果总结

我们对五个不同的 AI 智能体组合进行了评估，涵盖代码质量、功能完整性、可维护性等九个维度。

### 评估结果汇总

| 智能体 (Agent)                     | 代码行数 (10) | 需求匹配度 (10) | 代码质量 (10) | 测试代码 (10) | 可读性 (10) | 实现复杂度 (10) | 安全性 (10) | 功能完善性 (10) | 可维护性 (10) | **总分 (90)** |
| ---------------------------------- | :-----------: | :-------------: | :-----------: | :-----------: | :---------: | :-------------: | :---------: | :---------------: | :-------------: | :-------------: |
| claude code with doubao-code       |       9       |        5        |       4       |       2       |      5      |        8        |      7      |         4         |        3        |     **47**      |
| claude code with glm4.6            |       7       |        7        |       7       |       5       |      7      |        7        |      7      |         6         |        7        |     **59**      |
| **claude code with qwen-coder-plus**   |       **6**       |        **9**        |       **9**       |       **8**       |      **8**      |        **6**        |      **8**      |         **9**         |        **9**        |     **72**      |
| claude code with sonnet4.5         |       6       |        8        |       8       |       7       |      8      |        7        |      8      |         8         |        8        |     **68**      |
| codex cli with chat-gpt5.1         |       7       |        8        |       8       |       6       |      7      |        6        |      8      |         7         |        7        |     **64**      |

**核心结论：**

**`claude code with qwen-coder-plus`** 在本次评测中综合表现最佳，生成了质量最高、功能最完善且可维护性最好的项目。它不仅精准地实现了规格要求，还额外提供了 Docker 支持和完善的工具链配置。

> 详细的各项指标得分原因请参阅 [**AI 智能体代码生成评估报告 (eval-ai-rag.md)**](./eval-ai-rag.md)。

---

## 2. 核心方法论：规格驱动开发 (SDD)

本项目遵循 **规格驱动开发 (SDD)** 的理念，其核心思想是“代码服务于规格”，而非反之。

- **规格 (Specification)**: 成为真理的唯一来源。
- **代码 (Code)**: 成为规格的自动化产物。
- **调试 (Debugging)**: 意味着修复产生错误代码的规格。

### SDD 工作流

整个开发过程由一系列结构化的指令驱动，确保意图与实现之间的完美对齐。

1.  **`/speckit.specify`**: 将自然语言描述的需求转化为结构化的、可执行的 **功能规格 (Spec)**。
2.  **`/speckit.plan`**: 基于功能规格，并遵循项目“宪法” (`constitution.md`)，生成详细的 **技术实施计划 (Plan)**。
3.  **`/speckit.tasks`**: 将技术计划分解为原子化的、可并行执行的 **开发任务 (Tasks)**。
4.  **Implementation**: AI 编码智能体根据任务列表自动生成或修改代码。

> 更多关于 SDD 的理念、原则和适用场景，请参阅：
> - [**1. Spec Kit 理念与使用说明.md**](./docs/1.Spec%20Kit%20理念与使用说明.md)
> - [**2. Spec Kit 的适用性说明.md**](./docs/2.Spec%20Kit%20的适用性说明.md)

---

## 3. 开发环境搭建

### 3.1. 安装核心工具

1.  **Spec Kit**:
    ```bash
    uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
    ```

2.  **Claude Code**:
    ```bash
    npm install -g @anthropic-ai/claude-code
    ```

### 3.2. 初始化项目环境

```bash
# 1. 初始化 spec-kit (由于是多项目仓库，使用 --no-git)
specify init ai-platform --no-git
cd ai-platform

# 2. 初始化 Python 虚拟环境并安装依赖
uv init
uv add --dev ruff pyright pytest
uv sync

# 3. 激活虚拟环境
source .venv/bin/activate
```

### 3.3. 启动 AI 智能体

根据你选择的后端模型，启动对应的 CLI 工具：

```bash
# Claude Code (推荐, 需配合模型配置)
claude --dangerously-skip-permissions

# Claude Code (旧版)
ccr code --dangerously-skip-permissions

# Gemini
gemini --yolo

# Codex
codex --dangerously-bypass-approvals-and-sandbox
```

---

## 4. AI 智能体配置 (国内网络环境)

由于网络限制，直接连接 Anthropic, Google, OpenAI 的 API 可能受阻。以下是 `claude-code` 工具通过配置环境变量使用国内可用模型或代理的方案。

### 4.1. 阿里通义千问 (Qwen)

```bash
# 使用 qwen3-coder-plus 模型
export ANTHROPIC_BASE_URL=https://dashscope.aliyuncs.com/apps/anthropic
export ANTHROPIC_AUTH_TOKEN="sk-..." # 替换为你的 DashScope API Key
export ANTHROPIC_MODEL="qwen3-coder-plus"
claude
```

### 4.2. 智谱 (GLM)

```bash
# 使用 GLM-4.6 模型
export ANTHROPIC_BASE_URL=https://open.bigmodel.cn/api/anthropic
export ANTHROPIC_AUTH_TOKEN="..." # 替换为你的 Zhipu API Key
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC="1" # 禁用不必要的网络请求
claude
```

### 4.3. 字节豆包 (Doubao)

```bash
export ANTHROPIC_BASE_URL="https://ark.cn-beijing.volces.com/api/coding"
export ANTHROPIC_AUTH_TOKEN="..." # 替换为你的火山方舟 Key
export ANTHROPIC_MODEL="doubao-seed-code-preview-latest"
claude
```

### 4.4. OpenRouter (通用中转)

通过 OpenRouter 可以使用包括 `gpt-5.1-codex` 在内的多种模型。

```json
// 在 claude code 的配置文件中设置 Router
"Router": {
    "default": "openrouter,anthropic/claude-sonnet-4.5",
    "background": "openrouter,anthropic/claude-sonnet-4.5",
    "think": "openrouter,anthropic/claude-opus-4.1",
    "longContext": "openrouter,anthropic/claude-sonnet-4.5",
    "webSearch": "openrouter,anthropic/claude-haiku-4.5"
}
```
> **注意**: 切换使用 `openai/gpt-5.1-codex` 时，建议关闭 `claude code` 的 thinking 模式，否则执行速度可能很慢。

---

## 5. 使用说明与技巧

### 5.1. Spec-Kit 使用注意

- **多项目仓库**: 在一个已存在的 Git 仓库下使用 `specify init` 时，务必添加 `--no-git` 参数，避免 Git 分支混乱。
- **功能变更**: 始终遵循 **Spec → Plan → Tasks** 的流程。不要直接修改代码，而应先更新规格文档，再驱动后续环节的变更。详情请见 [**功能变更使用说明**](./docs/3.Spec%20Kit功能变更使用说明.md)。
- **模型中断问题**: 使用 `GPT-5.1` 或 `Gemini-3-Pro` 时，`/speckit.implement` 可能会因模型“深度思考”或“懒惰”而中断，需要手动继续。

### 5.2. 高效提示词技巧

- **提供示例**: 给出“输入 -> 输出”的样本，比单纯描述更有效。
- **明确上下文**: 指定语言、版本、库和命名风格。
- **拆解步骤**: 对复杂问题，要求模型“一步步思考”。
- **定义格式**: 明确要求输出 Markdown、纯代码块、JSON 等。

> **差**: “用 Python 写个爬虫。”
>
> **好**: “使用 **Python 3.10** 和 **BeautifulSoup4**。编写一个脚本解析 `data.html`，提取所有 `<div class='price'>` 中的文本，并保存为 **CSV 文件**。不要包含 markdown 解释，直接给代码。”

更多技巧请参阅 [**编码开发中的提示词说明**](./docs/5.编码开发中的提示词说明.md)。

---

## 6. 项目结构

```
/
├───docs/                  # 存放 SDD 方法论、工具指南等核心文档
├───prompts/               # 存放用于生成代码的原始需求提示
├───eval-ai-rag.md         # AI 智能体详细评估报告
├───README.md              # 本文档
│
├───agent-claude-qwen3/    # qwen-coder-plus 生成的项目 (表现最佳)
├───agent-claude-gpt51/
├───agent-gemini3/
├───arg-claude-dbcode/     # doubao-code 生成的项目
├───arg-claude-glm46/      # glm4.6 生成的项目
├───arg-claude-sonnet45/   # sonnet4.5 生成的项目
└───arg-codex-gpt51/       # gpt-5.1-codex 生成的项目
```