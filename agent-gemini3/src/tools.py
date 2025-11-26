from langchain_core.tools import tool
import aiohttp
from langchain_mcp_adapters.client import MultiServerMCPClient
import json
import os


# 模拟 MCP 客户端调用
async def get_tools():
    mcp_url = os.getenv("MCP_SERVER")
    # 在真实场景中，这里会发送 POST 请求到 MCP Server
    mcp_client = MultiServerMCPClient(
        {
            "account_apply": {
                "url": mcp_url,
                "headers": {
                    "Authorization":"Bearer secret-token"
                },
                "transport": "streamable_http",
            }
        }
    )
    return await mcp_client.get_tools()



def get_json(s: str) -> dict:
    if s == "" or s is None or s == "{}":
        return {}
    try:
        start = s.find("{")
        s = s[start:]
        end = s.rfind("}") + 1
        if end == 0:
            r = s + "}"
        else:
            r = s[0:end]
        # remove \ and \n from string
        r = r.replace('\\', '').replace('\n', '')
        return json.loads(r)
    except Exception as e:
        print('get_json error:', s, e)
        return {}
    

def get_checklist(state) -> dict:
    return state.get("checklist", {"first_chat": False,
        "id_verified": False, "info_collected": False,
        "permissions_granted": False, "final_briefing": False
    })