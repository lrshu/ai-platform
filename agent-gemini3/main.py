from dotenv import load_dotenv
load_dotenv()
import asyncio
import uuid
from langchain_core.messages import HumanMessage
from src.graph import build_graph

async def main():
    print("--- 新员工入职引导系统 (DeepAgents/LangGraph) ---")
    print("输入 'quit' 退出")
    
    # 构建带 Memory 的图
    graph = build_graph()
    
    # 显式定义初始状态
    initial_state = {
        "checklist": {
            "id_verified": False, 
            "info_collected": False, 
            "role_briefed": False, 
            "permissions_granted": False, 
            "final_briefing": False
        },
        "employee_info": {},
        # messages 不需要在此处初始化，会在下面动态添加
    }
    
    # 这里的 thread_id 用于区分不同的用户会话
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    print("欢迎新员工！请按照提示进行操作，输入 'quit' 退出。")
    user_input = "我是新员工，需要入职。"
    while True:
        try:
            if user_input.lower() in ["quit"]:
                break
            
            inputs = {"messages": [HumanMessage(content=user_input)]}
            # 运行图
            # 这里的 config 确保了状态会被保存到 MemorySaver 中
            async for msg, metadata in graph.astream(inputs, config=config, stream_mode=["messages"]):
                # 场景 A: 如果是最终生成的回复，使用流式打印
                if msg.content and metadata["langgraph_node"] == "agent":
                    print(msg.content, end="", flush=True)
                
                # 场景 B: 如果是工具调用的中间状态，使用 rich 打印提示
                elif msg.tool_calls:
                    from rich import print as rprint
                    for tool in msg.tool_calls:
                        rprint(f"\n[bold yellow]🛠️  正在调用工具: {tool['name']}[/bold yellow]")
                        rprint(f"[dim]参数: {tool['args']}[/dim]")

            user_input = input("\nUser: ")
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())