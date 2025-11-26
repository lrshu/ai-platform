# 安装 spec-kit 工具

uv tool install specify-cli --from git+https://github.com/github/spec-kit.git

# 安装 Claude Code

npm install -g @anthropic-ai/claude-code

# 初始化开发环境，准备好测试和代码检查的依赖

```
proxy
specify init ai-platform --no-git
cd ai-platform
uv init
uv add --dev ruff
uv add --dev pyright
uv add --dev pytest
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

切换使用 openai/gpt-5.1-codex 时，建议关闭 claude code 的 thinking 模式， 否则执行太慢
当前还无法使用 google/gemini-3-pro-preview

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

每个指标的得分范围为 0-10 分,评估指标包括：

1. 生成的代码行数量级: 行数越少，得分越高
2. 与文档要求的匹配度: 越匹配，得分越高
3. 代码质量： 质量越高，得分越高
4. 测试代码： 测试越全，得分越高
5. 可读性： 注释和调理越清晰，得分越高
6. 实现复杂度： 复杂度越低，得分越高
7. 安全性： 安全性越高， 得分越高
8. 功能完善性： 越完善，得分越高
9. 可维护性：维护性越高，得分越高

以表格形式输出各智能体的评估指标后，在 eval.md 文档后面，给出每个智能体的每个指标得分的原因。

# spec-kit 使用注意问题

1. 一个 git 仓库下使用多个工程时，添加--no-git 参数，否则 git 分支可能混乱
2. 使用 chatgpt5.1、gemini3 时， /speckit.implement 执行总是中断，需要一直守着，继续执行,有时无法继续，可能原因如下：
   1. GPT-5.1：倾向于进行深度思考（Extended Thinking），这会导致它花费大量时间在“思考”阶段，从而导致前端等待超时。如果任务过于复杂，它可能会陷入循环调试，最终导致连接断开。
   2. Gemini 3-Pro：目前的预览版被指出存在“懒惰（Laziness）”问题。为了节省计算资源，它在生成长代码块时倾向于中断，或者只生成部分代码（例如只写注释 // ...rest of the code），导致 Spec Kit 无法解析完整的变更，从而抛出错误或中断进程。
