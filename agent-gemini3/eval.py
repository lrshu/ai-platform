from dotenv import load_dotenv
load_dotenv()
import sys
import asyncio

from evals.dataset_generator import generate_mcp_tool_eval_dataset
from evals.experiment_runner import run_mcp_tools_experiment



if __name__ == "__main__":
    # python eval.py generate_mcp_tool_eval_dataset
    if "generate_mcp_tool_eval_dataset" in sys.argv:
        generate_mcp_tool_eval_dataset()
    
    # python eval.py run_mcp_tools_experiment
    if "run_mcp_tools_experiment" in sys.argv:
        asyncio.run(run_mcp_tools_experiment())
    