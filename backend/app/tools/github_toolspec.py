from typing import List, Optional
from github import Github
from datetime import datetime
from llama_index.core.tools.tool_spec.base import BaseToolSpec
import os
from pydantic import BaseModel, ValidationError, validate_arguments
from datetime import datetime
from typing import List, Union


github_access_token = os.getenv("GITHUB_ACCESS_TOKEN")

class GithubToolSpec(BaseToolSpec):
    """Interact with Github API"""

    spec_functions = ["fetch_commits"]

    def __init__(self):
        self.access_token = github_access_token
        self.github = Github(github_access_token)

    @validate_arguments
    def fetch_commits(self, repo_name: str, since: datetime, until: datetime, branch: str = "main") -> List[dict]:
        """
            Fetch all commits for a repo between two dates. This only works for public repos. Ensure the repo name contains owner and repo name
            Ensure that since and until parameters are datetime objects.

            Example inputs:
                I want to fetch all commits since march 2020

        """

        try:
            try:
                repo = self.github.get_repo(repo_name)
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
                    "files": self._fetch_commit_files(commit)
                }
                commit_data.append(commit_detail)
            return commit_data
        except ValidationError as e:
            return "Parameter validation failed. Please ensure 'since' and 'until' are datetime objects or ISO 8601 strings.", e
      

    def _fetch_commit_files(self, commit) -> List[dict]:
        commit_files = []
        for file in commit.files:
            file_detail = {
                "filename": file.filename,
                "additions": file.additions,
                "deletions": file.deletions
            }
            commit_files.append(file_detail)
        return commit_files


