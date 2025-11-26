# 入职引导智能体系统 (Agent-Gemini3)

这是一个基于 LangGraph 构建的入职引导智能体系统，用于自动化处理新员工入职流程。

## 项目概述

该系统通过多个专门的智能体节点协同工作，引导新员工完成整个入职流程：
1. 身份验证（身份证照片识别）
2. 个人信息收集
3. 权限申请（邮箱/git账号）
4. 最终入职介绍

## 技术架构

- **核心框架**: [LangGraph](https://langchain-ai.github.io/langgraph/)
- **语言模型**: Qwen系列（文本模型和视觉模型）
- **工具集成**: MCP (Model Control Protocol) 服务器
- **环境管理**: dotenv 配置文件

## 系统组件

### 智能体节点
- `supervisor`: 入职主管，负责流程规划和路由控制
- `first_chat`: 首次交互节点
- `id_verifier`: 身份验证节点，使用VL模型验证身份证照片
- `info_collector`: 信息收集节点
- `permissions_granted`: 权限申请节点
- `final_briefing`: 最终介绍节点
- `others`: 其他情况处理节点
- `query_checklist`: 检查列表查询节点

### 数据结构
- `AgentState`: 系统状态，包含消息历史、员工信息、检查列表等
- `EmployeeInfo`: 员工信息结构
- `Checklist`: 入职流程检查列表

## 环境要求

- Python >= 3.12
- Qwen API 密钥 (阿里云DashScope)
- MCP 服务器 (可选)

## 安装依赖

```bash
# 创建并激活虚拟环境（推荐）
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate  # Windows

# 安装项目依赖
pip install -e .
# 或安装开发依赖
pip install -e ".[dev]"
```

## 环境配置

创建 `.env` 文件并配置以下变量：

```env
# Qwen Configuration
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
OPENAI_API_KEY="your-api-key-here"
MCP_SERVER="http://127.0.0.1:9102/mcp"

# Langsmith (可选)
LANGSMITH_API_KEY="your-langsmith-api-key"
LANGSMITH_PROJECT="default"
```

## 启动开发服务器

```bash
langgraph dev --allow-blocking --debug-port 5678
```

## 项目结构

```
src/
├── agents/                 # 各个智能体节点实现
│   ├── supervisor.py       # 入职主管节点
│   ├── id_verifier.py      # 身份验证节点
│   ├── info_collector.py   # 信息收集节点
│   ├── permissions_granted.py  # 权限申请节点
│   ├── final_briefing.py   # 最终介绍节点
│   └── ...                 # 其他节点
├── graph.py               # 工作流图定义
├── state.py               # 状态数据结构
├── llm.py                 # LLM 配置和初始化
└── tools.py               # 工具函数和MCP集成
```

## 功能特性

1. **多模态身份验证**: 使用VL模型验证身份证照片并提取信息
2. **交互式信息收集**: 通过中断机制与用户交互获取必要信息
3. **权限自动申请**: 根据员工岗位自动申请相应系统权限
4. **流程状态跟踪**: 通过检查列表跟踪入职流程进度
5. **灵活的路由机制**: Supervisor节点动态决定下一步执行哪个节点

## 开发指南

### 添加新的智能体节点

1. 在 `src/agents/` 目录下创建新的节点文件
2. 实现异步函数节点逻辑
3. 在 `src/graph.py` 中注册新节点
4. 更新路由逻辑（如需要）

### 自定义LLM配置

在 `src/llm.py` 中可以修改模型配置：
- `get_llm()`: 获取文本模型实例
- `get_vl_llm()`: 获取视觉语言模型实例

## 测试

运行测试套件：

```bash
pytest
```

## 部署

构建项目：

```bash
langgraph build
```

## 许可证

MIT License