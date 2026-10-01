import sys
from backend.agents.code_agent import CodeAgent

agent = CodeAgent()
try:
    prompt = agent.fix_code("test.py", "def test():\n    return {1, 2, 3}", "TypeError: 'set' object is not callable", "some context")
    print("Success")
except Exception as e:
    print(f"Failed: {e}")
