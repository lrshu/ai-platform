from src.llm import get_vl_llm
from langchain_core.messages import HumanMessage, AIMessage
from src.state import AgentState
from langgraph.types import interrupt
from src.tools import get_json
import base64
import mimetypes
import os


# LLM 初始化代码
llm = get_vl_llm()

def image_to_base64_url(file_path):
    # 1. Check if file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
        
    # 2. Determine the MIME type (e.g., 'image/png', 'image/jpeg')
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type is None:
        mime_type = 'image/jpeg' # Default fallback if unknown

    # 3. Read the binary file and encode it
    with open(file_path, "rb") as image_file:
        # b64encode returns bytes, so we .decode('utf-8') to get a string
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

    # 4. Construct the Data URL
    return f"data:{mime_type};base64,{encoded_string}"

async def id_verifier_node(state: AgentState):
    # interrupt 要求用户输入身份证照片
    base64_image = None
    prompt = "请上传您的身份证照片以便核验身份"
    while True:
        image_file_path = interrupt(prompt)
        # image_file_path = input_json["file"]
        base64_image = image_to_base64_url(image_file_path)
        break

    extracted_info = await llm.ainvoke(
            [HumanMessage(content=[f"""请验证以下照片是否为正确的身份证照片，并提取姓名、身份证号.
提取后返回 JSON 格式，返回示例如下：
{{
    "photo_verified": true,
    "name": "张三",
    "id_number": "44030519900101001X"
}}
""", {
      "type": "image_url",
      "image_url": {
        "url": base64_image, 
        "detail": "auto"
      }
    }])]
    )
    extracted_info = get_json(extracted_info.content)
    if not extracted_info["photo_verified"]:
        return {
            "messages": [AIMessage(content="照片验证失败，请重新上传。")],
            "checklist": {**state["checklist"], "id_verified": False},
            "next_step": "id_verifier"
        }
    else:
        return {
            "messages": [AIMessage(content=f"身份核验成功。姓名：{extracted_info['name']}, 身份证号：{extracted_info['id_number']}。")],
            "employee_info": {**state.get("employee_info", {}), **extracted_info, "photo_verified": True},
            "checklist": {**state["checklist"], "id_verified": True},
            "next_step": "info_collector"
        }