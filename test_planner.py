import sys
import asyncio
from backend.agents.planner_agent import PlannerAgent
import logging

logging.basicConfig(level=logging.INFO)

prompt = """
Project: TITAN GPT – Production-Grade AI Chatbot
# ... (rest of the giant prompt the user pasted, let me just pass a big prompt)
Make 50 tasks for a complex full stack chatbot with FastAPI, LangChain, React, etc.
"""

agent = PlannerAgent()
response = agent.plan(prompt)
print("Response tasks:", len(response["tasks"]))
print("Success!")
