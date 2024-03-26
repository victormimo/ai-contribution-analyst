from llama_index.agent.openai import OpenAIAgent
from llama_index.llms.openai import OpenAI as OpenAILLM
from llama_index.core.settings import Settings
from app.agent.system_prompt import system_prompt
from app.tools.github_toolspec import GithubToolSpec
from llama_index.core.tools.tool_spec.load_and_search.base import LoadAndSearchToolSpec
from app.engine.github import load_automerging_retrieval_github, load_sentence_window_retrieval_github
from llama_index.core.tools import QueryEngineTool, ToolMetadata
import os

import logging 

logger = logging.getLogger("uvicorn")

# github_spec = GithubToolSpec()


print(os.getenv("MODEL"))

llm = OpenAILLM(model=os.getenv("MODEL"), temperature=0.1, system_prompt=system_prompt)

# github_query_engine = load_automerging_retrieval_github(llm)
github_query_engine = load_sentence_window_retrieval_github(llm)

owner = "transfer-agent-protocol"
repo = "tap-cap-table"
branch = "main"

# Load the tools
query_tools = [
    QueryEngineTool(
        query_engine=github_query_engine,
        metadata = ToolMetadata(
            name="github_sentence_retrieval",
            description= f"Github Sentence Window Query Engine for repo {owner}/{repo} in branch {branch}",
        )
    ),
]

agent = OpenAIAgent.from_tools(tools=query_tools, llm=llm, verbose=True, system_prompt=system_prompt)

def get_agent():
    return agent

