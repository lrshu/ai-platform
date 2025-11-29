### 模块设计文档：Common (通用基础模块)

#### 10.1 模块介绍

Common 模块存放项目中所有非业务强相关的通用代码。它是项目的“润滑剂”，确保各个模块使用统一的日志格式、错误码定义、工具函数以及常量，避免代码重复（DRY 原则）。

#### 10.2 业务流程说明

该模块不包含独立业务流程，而是被其他 9 个模块引用。

- **全局异常捕获**: 定义 `BaseError`，API 层捕获此类型错误并返回标准 JSON。
- **日志记录**: 初始化 Loguru 或 logging，配置日志轮转、颜色、格式。

#### 10.3 对外接口说明

主要是工具函数库：

- `logger.info/error(...)`
- `format_date(datetime) -> str`
- `generate_uuid() -> str`
- `count_tokens(text: str) -> int`

#### 10.4 集成测试用例

- **Case 1: Token 计数**
  - **输入**: "Hello World"
  - **期望**: 返回正确的 token 数估算（如 2）。
- **Case 2: 异常定义**
  - **操作**: 抛出 `ResourceNotFoundError(msg="doc not found")`。
  - **期望**: 该异常包含 `code=404` 属性，能被 API 层识别。

#### 10.5 技术栈选型

- **Loguru**: 现代化的 Python 日志库，比标准 `logging` 更好用。
- **Tiktoken**: OpenAI 官方的分词库，用于精准计算 Token 数。
- **Python-dotenv**: 加载 `.env` 环境变量。

#### 10.6 需要的配置定义

- `LOG_LEVEL`: 日志级别 (INFO / DEBUG)。
- `TIME_ZONE`: 系统时区。

#### 10.7 项目目录结构

```text
common/
├── __init__.py
├── constants.py        # 全局常量 (如默认 prompt)
├── exceptions.py       # 自定义异常类
├── logger.py           # 日志配置
└── utils/
    ├── __init__.py
    ├── security.py     # Hash, 加密工具
    └── tokenizer.py    # Token 计算工具
```

#### 10.8 每个目录下 py 文件说明

- **`common/exceptions.py`**:
  - `class RAGBaseException(Exception)`: 基类。
  - `class NotFoundError(RAGBaseException)`: 资源未找到。
  - `class ProviderError(RAGBaseException)`: 模型调用失败。
- **`common/logger.py`**:
  - `setup_logger()`: 配置 Loguru 的 Sink（控制台输出 + 文件轮转保存）。
- **`common/utils/tokenizer.py`**:
  - `get_token_count(text, model)`: 使用 `tiktoken` 计算字符串长度。
