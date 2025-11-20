#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/zhengliu/Desktop/workspace/work/study/ai-platform')

print("Testing imports...")

try:
    print("Importing ConfigLoader...")
    from app.common.config_loader import ConfigLoader
    print("✅ ConfigLoader imported successfully")
except Exception as e:
    print(f"❌ Error importing ConfigLoader: {e}")
    import traceback
    traceback.print_exc()

try:
    print("Importing ProviderFactory...")
    from app.common.factory import ProviderFactory
    print("✅ ProviderFactory imported successfully")
except Exception as e:
    print(f"❌ Error importing ProviderFactory: {e}")
    import traceback
    traceback.print_exc()

try:
    print("Importing MemgraphDB...")
    from app.database.memgraph_db import MemgraphDB
    print("✅ MemgraphDB imported successfully")
except Exception as e:
    print(f"❌ Error importing MemgraphDB: {e}")
    import traceback
    traceback.print_exc()

try:
    print("Importing QwenProvider...")
    from app.providers.qwen_provider import QwenProvider
    print("✅ QwenProvider imported successfully")
except Exception as e:
    print(f"❌ Error importing QwenProvider: {e}")
    import traceback
    traceback.print_exc()