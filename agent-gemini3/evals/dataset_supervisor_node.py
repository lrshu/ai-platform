from src.llm import get_llm
from src.tools import get_json
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
import json
from ragas import Dataset

llm = get_llm()

def generate():
    dataset = Dataset(
        name="supervisor_node_dataset",
        backend="local/csv",
        root_dir="evals",
    )

    # 定义不同的检查列表状态组合
    checklist_states = [
        # 初始状态
        {
            "first_chat": False,
            "id_verified": False,
            "info_collected": False,
            "permissions_granted": False,
            "final_briefing": False
        },
        # 已完成首次聊天
        {
            "first_chat": True,
            "id_verified": False,
            "info_collected": False,
            "permissions_granted": False,
            "final_briefing": False
        },
        # 已验证身份
        {
            "first_chat": True,
            "id_verified": True,
            "info_collected": False,
            "permissions_granted": False,
            "final_briefing": False
        },
        # 已收集信息
        {
            "first_chat": True,
            "id_verified": True,
            "info_collected": True,
            "permissions_granted": False,
            "final_briefing": False
        },
        # 已授予权限
        {
            "first_chat": True,
            "id_verified": True,
            "info_collected": True,
            "permissions_granted": True,
            "final_briefing": False
        },
        # 完成所有步骤
        {
            "first_chat": True,
            "id_verified": True,
            "info_collected": True,
            "permissions_granted": True,
            "final_briefing": True
        }
    ]

    # 定义不同的消息历史组合
    message_histories = [
        # 空消息历史
        [],
        # 用户初次问候
        [HumanMessage(content="你好，我是新入职的员工")],
        # 用户询问流程
        [HumanMessage(content="我想了解一下入职流程")],
        # 用户已完成身份验证
        [
            HumanMessage(content="你好，我是新入职的员工"),
            AIMessage(content="请上传您的身份证照片以便核验身份。"),
            HumanMessage(content="[上传了身份证照片]"),
            AIMessage(content="身份核验成功。姓名：张三，身份证号：44030519900101001X。"),
        ],
        # 用户已完成信息收集
        [
            HumanMessage(content="你好，我是新入职的员工"),
            AIMessage(content="请上传您的身份证照片以便核验身份。"),
            HumanMessage(content="[上传了身份证照片]"),
            AIMessage(content="身份核验成功。姓名：张三，身份证号：44030519900101001X。"),
            AIMessage(content="请填写您的毕业院校："),
            HumanMessage(content="清华大学"),
            AIMessage(content="请填写您的岗位（行政/ IT）："),
            HumanMessage(content="IT"),
        ]
    ]

    # 为每种组合生成测试用例
    for i, checklist in enumerate(checklist_states):
        for j, messages in enumerate(message_histories):
            # 序列化消息历史以便存储
            serialized_messages = []
            for msg in messages:
                if isinstance(msg, HumanMessage):
                    serialized_messages.append({"type": "human", "content": msg.content})
                elif isinstance(msg, AIMessage):
                    serialized_messages.append({"type": "ai", "content": msg.content})
                elif isinstance(msg, SystemMessage):
                    serialized_messages.append({"type": "system", "content": msg.content})

            # 创建测试用例
            test_case = {
                "test_id": f"case_{i}_{j}",
                "checklist": json.dumps(checklist),
                "messages": json.dumps(serialized_messages),
                "messages_count": len(messages),
                "scenario": f"checklist_state_{i}_messages_{j}"
            }

            # 添加到数据集中
            dataset.append(test_case)

    # 保存数据集
    dataset.save()
    print(f"Generated {len(dataset)} test cases for supervisor node evaluation")