from openai import OpenAI
import os
from ragas.llms import llm_factory
from ragas import Dataset
from ragas.testset import TestsetGenerator
from src.llm import get_llm
from src.tools import get_json
from langchain_core.messages import HumanMessage
from tqdm import tqdm

llm = get_llm()

def generate():
    dataset = Dataset(
        name="mcp_tool_eval_dataset",
        backend="local/csv",
        root_dir="evals",
    )
    prompt = f"""请随机生成{10}个不同到的真实的姓名和身份证号，姓名不能包含特殊字符，身份证号必须是18位数字，结果以JSON格式返回，示例如下：
        {{
            users: [{{
                "name": "张三",
                "id_number": "44030419900101001X"
            }}]
        }}
"""
    res = llm.invoke([HumanMessage(content=prompt)])
    print(res.content)
    info = get_json(res.content)
    for info in tqdm(info.get("users", [])):
        # 随机生成姓名和身份证号
        if not info or "name" not in info or "id_number" not in info:
            continue
        dataset.append({
            **info,
            "position": "行政",
        })
        dataset.append({
            **info,
            "position": "IT",
        })
    dataset.save()

