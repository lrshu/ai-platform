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
