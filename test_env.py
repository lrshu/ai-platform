#!/usr/bin/env python3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check if the API key is available
print("DASHSCOPE_API_KEY in environment:", "DASHSCOPE_API_KEY" in os.environ)
print("QWEN_API_KEY in environment:", "QWEN_API_KEY" in os.environ)

if "DASHSCOPE_API_KEY" in os.environ:
    print("DASHSCOPE_API_KEY value:", os.environ["DASHSCOPE_API_KEY"][:10] + "...")
else:
    print("DASHSCOPE_API_KEY not found")

if "QWEN_API_KEY" in os.environ:
    print("QWEN_API_KEY value:", os.environ["QWEN_API_KEY"][:10] + "...")
else:
    print("QWEN_API_KEY not found")