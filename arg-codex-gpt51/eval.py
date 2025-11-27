from evals.dataset_chat import generate_chat_dataset
from evals.experiment_chat import run as run_chat_experiment
from dotenv import load_dotenv
load_dotenv()
import sys
import asyncio



if __name__ == "__main__":
    # python eval.py generate_mcp_tool_eval_dataset
    if "generate_chat_dataset" in sys.argv:
        generate_chat_dataset()
    
    # python eval.py run_chat_eval_experiment
    if "run_chat_experiment" in sys.argv:
        asyncio.run(run_chat_experiment())


    