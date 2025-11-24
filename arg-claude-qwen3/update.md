# 手动修改

1. os.getenv 只应该在 config.py 中使用, 其他地方应该使用 config.py 来获取配置信息
2. EmbeddingGenerator 中使用 OpenAIEmbeddings 来获取向量
