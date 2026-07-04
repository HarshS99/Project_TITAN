import asyncio
from backend.mcp_servers.mcp_clients import run_action

print("Testing GitHub Agent...")
response = run_action("What tools do you have available for GitHub?")
print("Response:", response)
