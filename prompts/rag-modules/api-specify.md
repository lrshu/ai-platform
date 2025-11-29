### 模块设计文档：Api (接口模块)

#### 2.1 模块介绍

Api 模块是系统的网关，基于 RESTful 规范对外暴露服务。它负责请求参数校验、鉴权（Auth）、路由分发以及响应格式化。它不包含核心业务逻辑，而是将请求转发给 **Orchestration**、**Storage**（包含知识图谱接口）或 **Common** 模块。

#### 2.2 业务流程说明

1. **请求接收**: 监听 HTTP 请求。
2. **中间件处理**: 处理 CORS、身份验证（JWT）、请求日志记录。
3. **参数校验**: 使用 Pydantic 模型校验 Request Body。
4. **业务转发**:
   - Datasets/Documents CRUD -> 调用 `Storage` Service。
   - Search/Chat 请求 -> 调用 `Orchestration` Service。
5. **异常处理**: 捕获全局异常，转换为标准 HTTP 错误响应（4xx, 5xx）。
6. **响应返回**: 统一封装 JSON 结构（`code`, `data`, `msg`）。

#### 2.3 对外接口说明 (RESTful)

##### Dataset CRUD

- `POST /api/datasets`
  - **功能**: 创建数据集。
  - **请求体**: `name`, `description`。
  - **响应**: 新建 dataset 详情。
- `GET /api/datasets`
  - **功能**: 获取所有数据集。
  - **响应**: dataset 列表，支持分页/过滤。
- `GET /api/datasets/{dataset_id}`
  - **功能**: 获取指定数据集。
  - **响应**: dataset 详情，包含统计数据。
- `DELETE /api/datasets/{dataset_id}`
  - **功能**: 删除指定数据集，并触发 Storage 清理向量与图谱关联。

##### Document CRUD

- `POST /api/documents`
  - **功能**: 上传/创建文档，触发 Indexing。
  - **请求体**: `dataset_id`, `file`, `metadata`。
- `GET /api/documents`
  - **功能**: 获取所有文档，支持 dataset 过滤。
- `GET /api/documents/{document_id}`
  - **功能**: 查看单个文档详情及索引状态。
- `DELETE /api/documents/{document_id}`
  - **功能**: 删除文档，调用 Storage 删除向量 + Graph 节点。

##### 检索/对话

- `POST /api/search`: 检索接口，可选 `graph_filters` 用于知识图谱检索。
- `POST /api/chat`: 对话接口，内部调用 Orchestration 完整 RAG 流程。

#### 2.4 集成测试用例

- **Case 1: Dataset CRUD**
  - 测试创建 -> 查询 -> 删除全流程。
- **Case 2: Document CRUD**
  - 上传文档、查询状态、删除文档并验证 Storage 清理。
- **Case 3: 端到端对话**
  - 调用 `POST /api/chat`，验证 SSE 流输出。
- **Case 4: 参数校验失败**
  - 调用 `POST /api/search` 缺失 `dataset_id`，期望 HTTP 422。

#### 2.5 技术栈选型

- **FastAPI**: 高性能，原生支持异步，自动生成 Swagger 文档。
- **Pydantic**: 强大的数据验证。
- **Uvicorn**: ASGI 服务器。

#### 2.6 需要的配置定义

- `API_PORT`: 监听端口。
- `API_PREFIX`: 路径前缀（如 `/v1`）。
- `CORS_ORIGINS`: 允许跨域的域名列表。

#### 2.7 项目目录结构

```text
api/
├── __init__.py
├── main.py             # FastAPI App 入口
├── dependencies.py     # 依赖注入（如获取 DB Session）
├── middlewares.py      # 中间件（Auth, Log）
├── routers/
│   ├── __init__.py
│   ├── dataset_router.py
│   ├── document_router.py
│   ├── search_router.py
│   └── chat_router.py
└── schemas/
    ├── __init__.py
    ├── dataset_schema.py
    ├── document_schema.py
    ├── chat_schema.py
    └── common_schema.py
```

#### 2.8 每个目录下 py 文件说明

- **`api/main.py`**
  - `create_app() -> FastAPI`: 初始化应用、注册中间件与路由、配置异常处理器。
- **`api/schemas/dataset_schema.py`**
  - 定义 Dataset CRUD 请求/响应模型（含分页参数）。
- **`api/schemas/document_schema.py`**
  - 定义 Document CRUD 请求/响应模型（含上传字段、graph metadata）。
- **`api/routers/dataset_router.py`**
  - 提供 Dataset CRUD 路由，调用 Storage Service。
- **`api/routers/document_router.py`**
  - 处理文档上传/删除，触发 Indexing 和 Storage 清理。
- **`api/routers/search_router.py`**
  - 支持文本检索 + 图谱过滤参数。
- **`api/routers/chat_router.py`**
  - 处理 `/api/chat`，依赖 Orchestration Service。
