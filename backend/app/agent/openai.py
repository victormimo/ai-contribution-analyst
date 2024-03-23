import os
from llama_index.agent.openai import OpenAIAgent
from llama_index.llms.openai import OpenAI as OpenAILLM
from llama_index.core.settings import Settings
from app.agent.system_prompt import system_prompt
from app.tools.github_toolspec import GithubToolSpec

import logging 

logger = logging.getLogger("uvicorn")

github_spec_tool_list = GithubToolSpec()

agent = OpenAIAgent.from_tools(github_spec_tool_list.to_tool_list() ,llm=Settings.llm, verbose=True, system_prompt=system_prompt)

def get_agent():
    return agent

