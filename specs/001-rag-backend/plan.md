# Implementation Plan: RAG Backend Implementation

**Branch**: `001-rag-backend` | **Date**: 2025-11-20 | **Spec**: [/specs/001-rag-backend/spec.md](/specs/001-rag-backend/spec.md)
**Input**: Feature specification from `/specs/001-rag-backend/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

This plan outlines the implementation of a Retrieval-Augmented Generation (RAG) backend system that follows the Modular RAG paradigm with six standardized pipeline stages. The system will provide document indexing, search and retrieval capabilities, and answer generation using Qwen models and Memgraph for storage. The implementation will follow a modular architecture with provider abstractions for external services. The plan is organized into 5 key milestones that progressively build a complete RAG system from basic document processing to a production-ready solution with advanced features.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: FastAPI, Pydantic V2, Memgraph (python-memgraph), DashScope SDK, Mineru API client
**Storage**: Memgraph (Graph + Vector) with MAGE for vector search and Fulltext Index for keyword search
**Testing**: pytest with unit, integration, and contract tests
**Target Platform**: Linux server
**Project Type**: RAG backend (follows Modular RAG paradigm)
**Performance Goals**: Index 100 pages per minute with 95%+ entity extraction accuracy; Search queries return results in under 500ms for 95% of requests; Handle 100 concurrent search requests
**Constraints**: Must use configuration-driven architecture with environment variable overrides for sensitive data; Must implement Small-to-Big chunking strategy; Must support streaming responses
**Scale/Scope**: Initial implementation supporting PDF document indexing and search with Qwen-Turbo/Plus/Max models

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

For all RAG backend implementations, verify compliance with the [RAG Backend Platform Constitution](../../memory/constitution.md):

1. ✅ **Modular Architecture**: Does the design follow the six standardized pipeline stages?
2. ✅ **Provider Abstraction**: Are external services implemented as capability providers?
3. ✅ **Configuration-Driven**: Does the implementation use config.json5 for configuration?
4. ✅ **Documentation Standards**: Are Google-style Docstrings with Type Hints included?
5. ✅ **Directory Structure**: Does the implementation follow the prescribed directory structure?

## Project Structure

### Documentation (this feature)

```text
specs/001-rag-backend/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
app/
├── api/                 # API Gateway & Endpoints
├── common/              # Core Infrastructure
│   ├── interfaces/      # Abstract Base Classes
│   │   ├── database.py
│   │   ├── generator.py
│   │   ├── embedder.py
│   │   ├── reranker.py
│   │   ├── parser.py
│   ├── config_loader.py
│   ├── models.py        # Shared Pydantic Models
│   ├── utils.py
├── database/            # Memgraph Implementation
├── indexing/            # Indexing Logic
├── retrieval/           # Retrieval Logic (Pre & Core)
├── post_retrieval/      # Post-Retrieval Logic
├── generation/          # Generation Logic
├── providers/           # External Service Providers
├── orchestration/       # Pipeline & Orchestrator
tests/
├── contract/
├── integration/
└── unit/
config.json5             # Main Configuration
pyproject.toml
main.py
```

**Structure Decision**: RAG backend implementation following the prescribed directory structure from the constitution.

## Implementation Milestones

### 里程碑 1: 骨架构建 (基础设施与入库)
**目标**: 能够解析文档、生成嵌入并存储到 Memgraph 中。

**关键任务**:
- 项目初始化: 配置 uv 环境，建立目录结构和 config.json5
- 数据库实现: 完成 MemgraphDB 类，确保能连接并执行基础 Cypher 查询
- 基础索引流程: 实现简化的索引流：
  - 解析 (Mineru)
  - 简单切分 (暂不含 Parent/Child)
  - 嵌入 (Qwen)
  - 存储 (写入 Memgraph 向量索引)

### 里程碑 2: 大脑构建 (基础 RAG)
**目标**: 能够提问并基于存储的向量获得回答。

**关键任务**:
- Provider 集成: 完整实现 QwenProvider 的生成和嵌入功能
- 检索逻辑: 在 MemgraphRetriever 中实现基础向量搜索
- 编排器 V1: 创建线性流水线：查询 -> 嵌入 -> 向量搜索 -> 生成
- API V0.1: 实现一个基础的非流式接口以测试流程

### 里程碑 3: 肌肉增强 (高级特性)
**目标**: 实现模块化 RAG 特性以提高准确率。

**关键任务**:
- Small-to-Big: 重构索引模块以支持 Parent/Child 切分
- 上下文召回: 重构检索模块实现 Context Recall
- 重排序 (Reranking): 在检索后阶段集成 gte-rerank
- 查询预处理: 实现 HyDE 和查询扩展模块
- 动态编排: 更新 RAGPipeline 以支持用户参数控制 (use_hyde, use_rerank)

### 里程碑 4: 图增强 (知识图谱能力)
**目标**: 利用 Memgraph 的图能力。

**关键任务**:
- 实体提取: 实现 LLM Prompt 以在索引时提取实体
- 图存储: 更新索引模块以写入实体节点和关系
- 图检索: 更新 MemgraphRetriever 以执行图遍历或混合搜索 (Keyword + Vector + Graph)

### 里程碑 5: 生产化打磨
**目标**: 性能优化、流式输出与容器化。

**关键任务**:
- 流式输出: 将 API 改造为使用 SSE (StreamingResponse)
- 配置安全: 确保所有敏感 Key 通过环境变量加载，而非硬编码
- 文档: 为核心接口和编排器方法编写 Google 风格的 Docstrings
- Docker: 创建针对 Python 3.12 和 uv 优化的 Dockerfile

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |