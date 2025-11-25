# 安装 spec-kit 工具

uv tool install specify-cli --from git+https://github.com/github/spec-kit.git

# 安装 Claude Code

npm install -g @anthropic-ai/claude-code

# 我要实现一个 RAG 开发平台

```
proxy
specify init ai-platform
cd ai-platform
uv init
uv sync
source .venv/bin/activate
```

# 启动对应的 cli

```
claude --dangerously-skip-permissions
ccr code --dangerously-skip-permissions
gemini --yolo
codex  --dangerously-bypass-approvals-and-sandbox
```

# 在 claude code 中执行

```
/speckit.constitution

```

# openrouter claude code route config

```json
"Router": {
    "default": "openrouter,anthropic/claude-sonnet-4.5",
    "background": "openrouter,anthropic/claude-sonnet-4.5",
    "think": "openrouter,anthropic/claude-opus-4.1",
    "longContext": "openrouter,anthropic/claude-sonnet-4.5",
    "webSearch": "openrouter,anthropic/claude-haiku-4.5"
  }
```

# 各 AI 编码开发智能体生成效果对比

我正在使用 AI 智能体： claude code with doubao-code, claude code with glm4.6, claude code with qwen-coder-plus, claude code with sonnet4.5, codex cli with chat-gpt5.1 来生成代码，使用的 githu spec-kit 代码规范来生成代码，代码在对应的子文件夹下，生成代码文档要求来自 prompts/prompts.md。
请分析各子文件夹下生成的代码， 给出一个评估报告， 将评估结果输出到 eval.md 文件中。
评估结果包括：生成的代码行数量级，与文档要求的匹配度，代码质量，测试代码，可读性， 实现复杂度， 安全性，功能完善性，可维护性等方面，每个指标的得分范围为 0-10 分。
以表格形式输出各智能体的评估指标后，在 eval.md 文档后面，给出每个智能体的每个指标得分的原因。
