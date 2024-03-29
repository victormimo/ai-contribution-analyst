from github import Github, RateLimitExceededException
import os
import json
from datetime import datetime, timedelta
import time

# Initialize GitHub with your access token
access_token = os.getenv('ACCESS_TOKEN')
g = Github(access_token)

# Specify the repository you want to access
repo_name = "transfer-agent-protocol/tap-cap-table"  # Replace with your repository

# Get the repository object
repo = g.get_repo(repo_name)

from datetime import datetime, timezone
import time

def wait_for_rate_limit_reset(github):
    """
    Checks the current rate limit and waits until the reset time if necessary.
    """
    rate_limit = github.get_rate_limit()
    reset_time = rate_limit.core.reset
    remaining = rate_limit.core.remaining
    print(f"Rate Limit Remaining: {remaining}")
    if remaining < 10:  # Arbitrary low number to avoid hitting the limit
        # Ensure both datetimes are timezone-aware
        now = datetime.now(timezone.utc)
        wait_duration = (reset_time - now).total_seconds() + 10  # Adding a buffer
        print(f"Approaching rate limit. Waiting for {wait_duration} seconds.")
        time.sleep(max(wait_duration, 1))

        
def fetch_commits(repo, since, until, branch="main"):
    """
    Fetches commits from a GitHub repository within a specified date range.
    """
    commit_data = []
    n = 0
    try:
        commits = repo.get_commits(sha=branch, since=since, until=until)
        
        for commit in commits:
            n += 1
            print(f"Processing commit number {n}")
            wait_for_rate_limit_reset(g)  # Check rate limit before each API call
            commit_detail = {
                "sha": commit.sha,
                "author": commit.author.login if commit.author else "Unknown",
                "date": commit.commit.author.date,
                "message": commit.commit.message,
                "files": [{
                    "filename": file.filename,
                    "additions": file.additions,
                    "deletions": file.deletions,
                    "patch": file.patch
                } for file in commit.files]
            }
           
            commit_data.append(commit_detail)
    except RateLimitExceededException:
        print("Rate limit exceeded. Waiting for reset...")
        wait_for_rate_limit_reset(g)
        # Optionally, retry the failed operation here
    return commit_data

# Define the date range for commit retrieval
since = datetime.strptime("2023-01-01", '%Y-%m-%d')
until = datetime.now()

# Fetch commits
commit_data = fetch_commits(repo, since, until)

# Save the commit data to a JSON file
with open('fairmint-studio-commits.json', 'w') as f:
    json.dump(commit_data, f, default=str)

print("Commit data has been saved to fairmint-studio-commits.json")