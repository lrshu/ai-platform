#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

from app.common.config_loader import config_loader

print("Configuration contents:")
print(config_loader.config)

print("\nDatabase config:")
db_config = config_loader.get('database', {})
print(db_config)

print("\nDatabase URI:", db_config.get('uri', 'Not found'))
print("Database user:", db_config.get('user', 'Not found'))
print("Database password:", db_config.get('password', 'Not found'))

print("\nPipeline capabilities:")
pipeline_caps = config_loader.get('pipeline_capabilities', {})
print(pipeline_caps)

print("\nProvider map:")
provider_map = config_loader.get('provider_map', {})
print(provider_map)

print("\nDashScope API key:")
api_key = config_loader.get('dashscope_api_key', 'Not found')
print(api_key)