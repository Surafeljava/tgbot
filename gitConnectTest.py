from dotenv import load_dotenv
import os
from github import Github

load_dotenv()

API_KEY = os.getenv('API_KEY')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
REPO_NAME = os.getenv('REPO_NAME')


print(GITHUB_TOKEN)
# github = Github(GITHUB_TOKEN)
github = Github(GITHUB_TOKEN)

# print(github)
repository = github.get_user().get_repo(REPO_NAME)

print(repository.owner)
