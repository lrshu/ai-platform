from ragas import MultiTurnSample
from openai import OpenAI
import os
from ragas.llms import llm_factory
from ragas.testset import TestsetGenerator
from src.llm import get_llm, get_agent_with_tools
from src.tools import get_json
from langchain_core.messages import HumanMessage
from src.tools import get_tools
from tqdm import tqdm
import sys
from pathlib import Path
from ragas.metrics import ToolCallAccuracy
from ragas.dataset_schema import MultiTurnSample
from ragas.integrations.langgraph import convert_to_ragas_messages
import ragas.messages as r
from ragas import Dataset, experiment
import traceback

llm = get_llm()

def load_dataset(name: str):
    dataset = Dataset.load( 
        name=name,
        backend="local/csv",
        root_dir="evals")
    return dataset

tools = {
    "IT": {
        "prompt": f"您是 IT 岗位的员工，将申请git账号权限, 调用git账号申请工具，姓名：{{name}}， 身份证号：{{id_number}}",
        "name": "provision_git"
    },
    "行政": {
        "prompt": f"您是行政岗位的员工，将申请邮箱账号权限, 调用邮件账号申请工具，姓名：{{name}}， 身份证号：{{id_number}}",
        "name": "provision_email"
    }
}

def is_tool_call_pass(row, tool, tool_call_message):
    if len(tool_call_message.tool_calls) == 1:
        tool_call = tool_call_message.tool_calls[0]
        if tool_call.get("name") == tool.get("name"):
            args = tool_call.get('args')
            for arg in tool_call.get('args').keys():
                if args[arg] != row.get(arg):
                    return False
            return True
        else:
            return False
    else:
        return False

@experiment()
async def run_experiment(row):
    try:
        agent = await get_agent_with_tools(llm)
        tool = tools.get(row.get('position'))

        result = await agent.ainvoke({"messages": [HumanMessage(content=tool.get("prompt").format(name=row.get('name'), id_number=row.get('id_number')))]})
        tool_call_message = result["messages"][1]
        tool_accuracy = 1.0 if is_tool_call_pass(row, tool, tool_call_message) else 0.0
        
        last_message = result["messages"][-1]
        experiment_view = {
            **row,
            "response": last_message.content,
            "log_file": result.get("logs", " "),
            "accuracy": tool_accuracy,
        }
        return experiment_view
    except Exception as e:
        print("Error in run_experiment:", e)
        traceback.print_exc()
        raise e


async def run():
    dataset = load_dataset("mcp_tools_dataset")
    print("dataset loaded successfully", dataset)
    experiment_results = await run_experiment.arun(dataset)
    print("Experiment completed successfully!")
    print("Experiment results:", experiment_results)
    # experiment_results is list

    avg_accuracy = sum([item["accuracy"] for item in experiment_results]) / len(experiment_results)
    print("Average accuracy:", avg_accuracy)
    # Save experiment results to CSV
    experiment_results.save()
    csv_path = Path(".") / "experiments" / f"{experiment_results.name}.csv"
    print(f"\nExperiment results saved to: {csv_path.resolve()}")


