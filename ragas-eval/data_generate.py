

def generate_data(markdown_file_path, count=2):
    """
    读取 markdown_file_path 文件中的内容，根据内容， 使用qwen3-max 模型生成 QA文档对 , 生成问答对数量为 count
    将生成结果保存到 data/ 文件夹下
    """

