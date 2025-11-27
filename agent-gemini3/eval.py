from dotenv import load_dotenv
load_dotenv()
import sys
import asyncio

from evals.dataset_mcp_tools import generate as generate_mcp_tools_dataset
from evals.experiment_mcp_tools import run as run_mcp_tools_experiment
from evals.dataset_supervisor_node import generate as generate_supervisor_node_dataset
from evals.experiment_supervisor_node import run as run_supervisor_node_experiment



if __name__ == "__main__":
    # python eval.py generate_mcp_tool_eval_dataset
    if "generate_mcp_tools_dataset" in sys.argv:
        generate_mcp_tools_dataset()

    # python eval.py run_mcp_tools_experiment
    if "run_mcp_tools_experiment" in sys.argv:
        asyncio.run(run_mcp_tools_experiment())

    # python eval.py generate_supervisor_node_dataset
    if "generate_supervisor_node_dataset" in sys.argv:
        generate_supervisor_node_dataset()

    # python eval.py run_supervisor_node_experiment
    if "run_supervisor_node_experiment" in sys.argv:
        asyncio.run(run_supervisor_node_experiment())
    