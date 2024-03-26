from dotenv import load_dotenv

load_dotenv()

import logging
import os
from llama_index.readers.github import GithubRepositoryReader

from llama_index.readers.github.repository.github_client import GithubClient
from app.engine.automerging_retrieval import get_automerging_query_engine, build_automerging_index
from app.engine.sentence_window_retrieval import build_sentence_window_index, get_sentence_window_query_engine
from pydantic import BaseModel, ValidationError, validate_arguments
from datetime import datetime
from typing import List, Union
from github import Github
from llama_index.core import Document
import json


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


# owner = os.getenv("OWNER")
# repo = os.getenv("REPO")
# branch = os.getenv("BRANCH")

owner = "transfer-agent-protocol"
repo = "tap-cap-table"
branch = "main"
since= datetime.strptime("2024-01-01", '%Y-%m-%d')
until= datetime.now()
github_access_token = os.getenv("GITHUB_ACCESS_TOKEN")

print(owner, repo, branch)

@validate_arguments
def fetch_commits(owner: str, repo: str, since: datetime, until: datetime, branch: str = "main") -> List[dict]:
    github = Github(github_access_token)
    repo_name = owner + "/" + repo

    print(repo_name)
    try:
        try:
            repo = github.get_repo(repo_name)
        except GithubException.UnknownObjectException:
            print(f"Repository {repo_name} not found. Please check the name and try again.")
            return f"Repository {repo_name} not found. Please check the name and try again, perhaps you're missing owner"
        print("repo ", repo)
        commits = repo.get_commits(sha=branch, since=since, until=until)
        print("commits ", commits)
        commit_data = []
        for commit in commits:
            commit_detail = {
                "sha": commit.sha,
                "author": commit.author.login if commit.author else "Unknown",
                "date": commit.commit.author.date,
                "message": commit.commit.message,
                "files": _fetch_commit_files(commit)
            }

            print("paginating.. please wait ")
            commit_data.append(commit_detail)

        data_dir = "data"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        with open(os.path.join(data_dir, "commit_data.json"), "w") as file:
            file.write(json.dumps(commit_data, indent=4, default=str))
        logger.info(f"Commit data saved to {data_dir}/commit_data.json")

        return commit_data
        
        # documents = []
        # for commit in commit_data:
        #     documents.append(Document(json=commit))


        # print("number of documents ", len(documents))
        # print("last commit ", commit_data[-1])
        # return documents
        
    except ValidationError as e:
        return "Parameter validation failed. Please ensure 'since' and 'until' are datetime objects or ISO 8601 strings.", e

def _fetch_commit_files(commit) -> List[dict]:
    commit_files = []
    for file in commit.files:
        file_detail = {
            "filename": file.filename,
            "additions": file.additions,
            "deletions": file.deletions,
            "patch": file.patch
        }
        commit_files.append(file_detail)
    return commit_files


# might use for loading entire repo
def load_github_data():
    print("loading documents")

    github_documents = fetch_commits()

    # github_client = GithubClient(github_token=github_access_token, verbose=True)

    # github_documents = GithubRepositoryReader(
    #     github_client= github_client,
    #     owner=owner,
    #     repo=repo,
    #     use_parser=False,
    #     verbose=False,
    # ).load_data(branch=branch)



    return github_documents


def load_sentence_window_retrieval_github(llm):
    print("loading window sentence retrieval")

    data_dir = "data"
    commit_data_file = os.path.join(data_dir, "commit_data.json")

    if os.path.exists(commit_data_file):
        print("Fetching commit data from local file.")
        with open(commit_data_file, 'r') as file:
            github_document = json.load(file)
    else:
        print("Fetching commit data from GitHub.")
        github_document = fetch_commits(owner, repo, since, until)

    doc = Document(text=json.dumps(github_document, indent=4, default=str))

    sentence_engine_index = build_sentence_window_index(
        doc, 
        llm
    )

    query_engine = get_sentence_window_query_engine(sentence_engine_index)

    return query_engine

def load_automerging_retrieval_github(llm):
    print("loading automerging retrieval github")

    data_dir = "data"
    commit_data_file = os.path.join(data_dir, "commit_data.json")

    if os.path.exists(commit_data_file):
        print("Fetching commit data from local file.")
        with open(commit_data_file, 'r') as file:
            github_documents = json.load(file)
    else:
        print("Fetching commit data from GitHub.")
        github_documents = fetch_commits(owner, repo, since, until)

   
    doc = Document(text=json.dumps(github_documents, indent=4, default=str))

    print("documents ", doc)

    automerging_index = build_automerging_index(
        doc,
        llm,
        embed_model="local:BAAI/bge-small-en-v1.5",
        save_dir="./index/github/commits/merging_index"
    )
    automerging_engine = get_automerging_query_engine(automerging_index)
    return automerging_engine