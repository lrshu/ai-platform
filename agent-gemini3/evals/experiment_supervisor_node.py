import asyncio
from ragas import Dataset, experiment, RunConfig
from ragas.metrics import AgentGoalAccuracyWithReference
from ragas.llms import LangchainLLMWrapper
from ragas.dataset_schema import MultiTurnSample
from ragas.integrations.langgraph import convert_to_ragas_messages
from src.llm import get_llm
from src.tools import get_json
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from src.agents.supervisor import supervisor_node
from src.state import AgentState
import json
import traceback
from langgraph.graph import StateGraph, END, START
from src.state import AgentState
from pathlib import Path



llm = get_llm()

def load_dataset(name: str):
    dataset = Dataset.load(
        name=name,
        backend="local/csv",
        root_dir="evals")
    return dataset

def deserialize_messages(serialized_messages_str):
    """反序列化消息历史"""
    if not serialized_messages_str:
        return []

    try:
        serialized_messages = json.loads(serialized_messages_str)
        messages = []
        for msg_data in serialized_messages:
            if msg_data["type"] == "human":
                messages.append(HumanMessage(content=msg_data["content"]))
            elif msg_data["type"] == "ai":
                messages.append(AIMessage(content=msg_data["content"]))
            elif msg_data["type"] == "system":
                messages.append(SystemMessage(content=msg_data["content"]))
        return messages
    except Exception as e:
        print(f"Error deserializing messages: {e}")
        return []

def deserialize_checklist(checklist_str):
    """反序列化检查列表"""
    if not checklist_str:
        return {}
    try:
        return json.loads(checklist_str)
    except Exception as e:
        print(f"Error deserializing checklist: {e}")
        return {}


sem = asyncio.Semaphore(10)  # 限制为 4 个并发
    
@experiment()
async def run_experiment(row):
    """运行单个测试用例"""
    async with sem:
        try:
            # 构建测试状态
            messages = deserialize_messages(row.get("messages", "[]"))
            checklist = deserialize_checklist(row.get("checklist", "{}"))

            # 创建AgentState
            state: AgentState = {
                "messages": messages,
                "checklist": checklist,
                "next_step": None,
                "employee_info": {},
                "error_msg": None
            }

            # 运行supervisor节点
            result = await supervisor_node(state)

            # 构建完整的对话历史用于评估
            full_conversation = messages + result.get("messages", [])

            # 转换为Ragas消息格式
            ragas_trace = convert_to_ragas_messages(full_conversation)

            # 创建MultiTurnSample
            sample = MultiTurnSample(
                user_input=ragas_trace,
                reference=f"Supervisor 应该输出消息，引导用户继续完成相应的任务"
            )

            # 计算智能体目标准确率
            scorer = AgentGoalAccuracyWithReference()
            evaluator_llm = LangchainLLMWrapper(llm)
            scorer.llm = evaluator_llm

            # 获取准确率分数
            accuracy_score = await scorer.multi_turn_ascore(sample)

            # 验证结果
            expected_next_steps = [
                "first_chat", "id_verifier", "info_collector",
                "permissions_granted", "final_briefing",
                "query_checklist", "others"
            ]

            next_step_correct = result.get("next_step") in expected_next_steps

            # 返回实验结果
            experiment_result = {
                **row,
                "predicted_next_step": result.get("next_step", ""),
                "guide_message": result.get("messages", [AIMessage(content="")])[0].content if result.get("messages") else "",
                "next_step_correct": 1.0 if next_step_correct else 0.0,
                "goal_accuracy": float(accuracy_score),
                "success": 1.0
            }

            return experiment_result

        except Exception as e:
            print(f"Error in run_single_test: {e}")
            traceback.print_exc()
            # 返回失败的实验结果
            return {
                **row,
                "predicted_next_step": "",
                "guide_message": f"Error: {str(e)}",
                "next_step_correct": 0.0,
                "goal_accuracy": 0.0,
                "success": 0.0
            }
        

async def run():
    """运行supervisor节点评估实验"""
    print("Running supervisor node experiment...")

    # 加载数据集
    dataset = load_dataset("supervisor_node_dataset")
    print(f"Dataset loaded successfully, {len(dataset)} test cases")

    # 运行所有测试用例
    experiment_results = await run_experiment.arun(dataset)

    # 计算统计数据
    total_tests = len(experiment_results)
    successful_tests = sum(1 for r in experiment_results if r["success"] == 1.0)
    correct_next_steps = sum(r["next_step_correct"] for r in experiment_results)
    avg_goal_accuracy = sum(r["goal_accuracy"] for r in experiment_results) / total_tests if total_tests > 0 else 0

    success_rate = successful_tests / total_tests if total_tests > 0 else 0
    accuracy_rate = correct_next_steps / total_tests if total_tests > 0 else 0

    print(f"\nExperiment completed!")
    print(f"Total test cases: {total_tests}")
    print(f"Successful tests: {successful_tests}")
    print(f"Success rate: {success_rate:.2%}")
    print(f"Next step accuracy: {accuracy_rate:.2%}")
    print(f"Average goal accuracy: {avg_goal_accuracy:.2%}")

    experiment_results.save()
    csv_path = Path(".") / "experiments" / f"{experiment_results.name}.csv"
    print(f"\nExperiment results saved to: {csv_path.resolve()}")