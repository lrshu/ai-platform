from langchain_openai import ChatOpenAI
from src.state import AgentState
import os
from src.tools import get_tools
from langchain.agents import create_agent

def get_vl_llm():
    llm = ChatOpenAI(
        model=os.getenv("MODEL_NAME", "qwen3-vl-plus"),
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL")
    )
    return llm

def get_llm():
    llm = ChatOpenAI(
        model=os.getenv("MODEL_NAME", "qwen3-max"),
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL")
    )
    return llm


async def get_agent_with_tools(llm):
    agent = create_agent(model=llm, tools= await get_tools())
    return agent

    