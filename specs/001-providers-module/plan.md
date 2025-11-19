# Implementation Plan: Providers Module (External Capabilities)

**Branch**: `001-providers-module` | **Date**: 2025-11-19 | **Spec**: [/Users/zhengliu/Desktop/workspace/work/study/ai-platform/specs/001-providers-module/spec.md](file:///Users/zhengliu/Desktop/workspace/work/study/ai-platform/specs/001-providers-module/spec.md)

**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

## Summary

The Providers Module is responsible for implementing all I*Capability interfaces to provide external service capabilities while isolating API call details, authentication, and error handling from the core RAG logic. This module acts as a firewall between the RAG core logic and external services. The implementation includes QwenProvider for text generation, embedding, and reranking capabilities, and MineruProvider for document parsing capabilities.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: FastAPI, Pydantic V2, python-json5, requests, python-memgraph, uvicorn
**Storage**: Memgraph (Vector + Graph database)
**Testing**: pytest
**Target Platform**: Linux server
**Project Type**: Web application (backend)
**Performance Goals**: Text generation response time under 2 seconds for 95% of requests
**Constraints**: Core RAG logic must dynamically obtain required capability provider instances and specific model names through configuration
**Scale/Scope**: Support for multiple external service providers with configurable models

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Based on the Modular RAG AI Knowledge Base Platform Constitution (v1.2.0):

1. **Pipeline Architecture Compliance**:
   - Implementation MUST follow the six-stage pipeline with specific responsibilities:
     * Indexing: Parse → Chunk → Embed → Store (Graph + Vector)
     * Pre-Retrieval: Query understanding and rewriting (HyDE, Query Expansion)
     * Retrieval: Multi-path recall (Hybrid Search)
     * Post-Retrieval: Context optimization (Rerank, Selection)
     * Generation: Prompt assembly and LLM reasoning
     * Orchestration: Dynamic module scheduling controlled by user requests
   - Direct calls to underlying logic that bypass core abstractions are PROHIBITED
   - Each stage MUST be independently testable with clear boundaries

2. **Technology Stack Compliance**:
   - Runtime: Python 3.12+ MUST be used
   - Dependency Manager: uv MUST be used
   - Web Framework: FastAPI 全异步模式 with async/await MUST be used
   - Data Validation: Pydantic V2 MUST be used
   - Database (Vector + Graph): Memgraph MUST be used
   - Model Provider (Primary): Aliyun Bailian (Qwen/DashScope) MUST be used
   - LLM Models: Qwen-Turbo/Plus/Max MUST be used
   - Embedding Model: text-embedding-v4 MUST be used
   - Rerank Model: gte-rerank MUST be used
   - Doc Parsing Provider: Mineru API MUST be used

3. **Provider Abstraction and Modular Design Compliance**:
   - External services MUST be defined as capability providers implementing specific capability interfaces
   - Capability Interfaces: ITextGenerator, IEmbedder, IReranker, IDocumentParser
   - Each pipeline stage MUST be encapsulated as an independent class following the single responsibility principle
   - Components MUST be orchestrated through a central Orchestrator
   - Direct coupling between stages is PROHIBITED

4. **Documentation First Compliance**:
   - Core functions MUST include Google-style docstrings with comprehensive type hints
   - Public APIs and service interfaces MUST be documented with clear examples

5. **Configuration Management Compliance**:
   - All configuration MUST be loaded through a config.json5 file
   - Sensitive API Keys MUST be overridden or loaded through environment variables at runtime
   - Core RAG logic MUST dynamically obtain required capability provider instances through configuration

## Project Structure

### Documentation (this feature)

```text
specs/001-providers-module/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── api/
│   ├── common/             # 共用的接口、配置加载、工具类、日志等
│   │   ├── interfaces.py   # 统一存放 IDatabase 和 I*Capability 接口定义
│   │   ├── config_loader.py # 配置加载与运行时配置注入逻辑
│   │   ├── utils.py        # 工具类和日志
│   ├── database/           # 数据库实现模块
│   │   ├── memgraph_impl.py
│   ├── indexing/           # 索引模块
│   ├── retrieval/          # 检索模块
│   ├── post_retrieval/     # 检索后处理模块
│   ├── generation/         # 生成模块
│   ├── providers/          # 外部能力提供者实现
│   │   ├── qwen_provider.py
│   │   ├── mineru_provider.py
│   ├── orchestration/      # RAG 流程编排与动态调度
├── config.json5             # 项目主配置文件
├── pyproject.toml
└── main.py
```

**Structure Decision**: The project follows a modular backend structure with separate directories for each RAG pipeline stage and providers. The providers directory contains implementations for external service providers (Qwen and Mineru).

## Complexity Tracking

No violations of the Constitution principles identified. All implementation will follow the required technology stack and architectural patterns.