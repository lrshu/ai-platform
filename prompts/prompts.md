# constitution

制定以代码质量、测试标准、用户体验一致性及性能要求为核心的原则

# create feature rag backend specify

构建一个简单的标准化的 RAG 后端系统，核心流水线包括：Indexing、Pre-Retrieval、Retrieval、Post-Retrieval、Generation 、Orchestration。

## 技术栈

如果没有指定使用的技术方向，优先使用 langchain 体系下的方式实现后续功能

- **Runtime**: Python 3.12+ (uv)
- **Framework**: LangChain (Core)
- **Database**: Memgraph with neo4j
- **LLM**: Qwen3-Max
- **Embedding**: Qwen text-embedding-v4
- **Rerank**: DashScopeRerank

# 定义配置 .env

```env
# QWen Configuration
QWEN_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_API_KEY="sk-bac503b5a123456aa106e9574c89b0a0"

# Memgraph
DATABASE_URL="bolt://127.0.0.1:7687"
DATABASE_USER=""
DATABASE_PASSWORD=""
```

# 核心功能如下

## indexing.py

解析(文件地址): 读取解析 pdf 文件，返回 markdown
切分(markdown): 返回切分后内容
获取向量(分块): 返回分块对应的向量
获取知识图谱(分块)：获取的实体关系
存储(name, 向量和图谱)： 按 name 保存向量和知识图谱到 memgraph

## pre_retrieval.py

查询扩展(问题)：返回扩写的问题
执行检索前(问题， 是否扩展查询)：返回处理后的问题内容

## retrieval.py

获取向量(原始问题，检索前处理后的问题)： 返回向量
执行检索(name, 原始问题): 混合检索，执行 Vector + Graph Search，返回合并结果

## post_retrieval.py

重排序(检索结果)：返回排序后结果

## generation.py

执行生成(问题，检索结果)： 组装 Prompt， 调用 LLm，返回生成结果

## orchestration.py

索引(name,文件地址): 完成文档索引, 返回文档 id
检索(name, 问题，选项)：返回重排序后的检索结果
对话(name，问题，选项): 返回执行生成的结果
选项默认设置: top_k, 开启扩展查询，执行重排序，执行向量检索，执行关键词检查，执行图谱检索

## main.py

python main.py indexing --name [name1] --file [file_path]
python main.py search --name [name1] --question [question]
python main.py chat --name [name1]

# create plans for rag backend feature

实现所有需求
生成.env 配置文件
添加集成测试
运行集成测试，根据测试结果修复问题
