import pytest
from dotenv import load_dotenv
load_dotenv()

from src.graph import build_graph
from langchain_core.messages import HumanMessage

@pytest.mark.asyncio
async def test_onboarding_flow():
    graph = build_graph() # 现在这里面包含了 MemorySaver
    
    # 必须指定 thread_id 以隔离测试状态
    config = {"configurable": {"thread_id": "integration_test_unique_id"}}
    
    # 初始化状态
    initial_state = {
        "checklist": {
            "id_verified": False, "info_collected": False, 
            "role_briefed": False, "permissions_granted": False, "final_briefing": False
        },
        "employee_info": {}
    }
    
    print("\n--- Testing ID Verification ---")
    # 1. 触发流程 (首轮，传入 initial_state)
    inputs = {**initial_state, "messages": [HumanMessage(content="你好，我要入职")]}
    
    # 使用 ainvoke 获取最终状态，而不是流式
    final_state = await graph.ainvoke(inputs, config=config)
    
    # 检查是否正确引导到了 id_verifier 并且输出了提示
    assert "身份证" in final_state["messages"][-1].content
    
    # ... 后续测试步骤保持不变，但 inputs 只需传 messages ...
    # 2. 模拟上传图片
    inputs = {"messages": [HumanMessage(content="[图片] 这是我的身份证")]}
    final_state = await graph.ainvoke(inputs, config=config)
    assert final_state["checklist"]["id_verified"] == True
    
    # ... (其余测试逻辑同理)