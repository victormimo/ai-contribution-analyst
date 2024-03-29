import os 
from langchain.document_loaders import GithubFileLoader
import json

print(os.getenv("GITHUB_REPOSITORY"))

from github import Github

g = Github(os.getenv("GITHUB_APP_PRIVATE_KEY"))

repo = g.get_repo(os.getenv("GITHUB_REPOSITORY"))

loader = GithubFileLoader(
    repo=os.getenv("GITHUB_REPOSITORY"),
    access_token=os.getenv("ACCESS_TOKEN"),  # delete/comment out this argument if you've set the access token as an env var.
    # file_filter=lambda file_path: file_path.endswith(".md")
)

documents = loader.load()

for doc in documents:
    print("Content: ", doc.page_content)
    print("Metadata: ", doc.metadata)


