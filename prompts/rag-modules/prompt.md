### 系统架构总览

在深入模块之前，确认模块间的依赖关系：

- **Api**: 依赖 Orchestration。
- **Orchestration**: 编排 Indexing, Retrieval, Generation 等。
- **Indexing**: 依赖 Storage (存向量/元数据), Common (工具类), Provider (Embedding 模型)。

---

### 模块设计文档索引

以下模块设计文档已拆分至独立文件，便于维护与查阅：

1. [Indexing 模块设计](./indexing-specify.md) — 覆盖解析、切分、向量化与入库流程。
2. [Api 模块设计](./api-specify.md) — 介绍 RESTful 网关、路由与校验逻辑。
3. [Retrieval 模块设计](./retrieval-specify.md) — 说明向量/关键词检索与策略引擎。
4. [Generation 模块设计](./generation-specify.md) — 描述 Prompt 构建与 LLM 调用流程。
5. [Orchestration 模块设计](./orchestration-specify.md) — 展示端到端 RAG 编排与工作流。
6. [Pre-Retrieval 模块设计](./pre-retrieval-specify.md) — 解析查询重写、扩展与意图识别。
7. [Post-Retrieval 模块设计](./post-retrieval-specify.md) — 细化 Rerank、过滤与窗口适配逻辑。
8. [Storage 模块设计](./storage-specify.md) — 介绍双模态数据存储与 Repository 封装。
9. [Provider 模块设计](./provider-specify.md) — 说明模型适配、工厂与重试机制。
10. [Common 模块设计](./common-specify.md) — 汇总通用常量、异常、日志与工具集。

> 更新模块设计请在对应 `{name}-specify.md` 文件中维护，并在此索引中新增链接或注释。

更新 storage 模块设计文档, 增加知识图谱 graph 的存储， 并更新其他模块，增加对 graph 的检索支持
更新 provider 模块设计文档, 增加对 rerank 的支持，并更新 post retrieval 模块，替换为对 provider 中 rerank 的调用
更新 api 模块设计文档, datasets 和 documents 应该有 CRUD 4 种接口，分别是：

- POST /datasets: 创建数据集
- GET /datasets: 获取所有数据集
- GET /datasets/{dataset_id}: 获取指定数据集
- DELETE /datasets/{dataset_id}: 删除指定数据集

- POST /documents: 创建文档
- GET /documents: 获取所有文档
- GET /documents/{document_id}: 获取指定文档
- DELETE /documents/{document_id}: 删除指定文档

# 请检查所有的 \*-specify.md 文件，确认是否有遗漏或错误

# 修改 storage-specify.md 文件，增加所有实体结构的定义

# provider-specify.md 文件，增加文档解析的支持， 在 indexing-specify.md 文件中, 直接使用 provider 提供的解析接口完成文档 loader 的调用
