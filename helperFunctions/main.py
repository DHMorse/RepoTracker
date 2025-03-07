import os 
import requests

from helperFunctions.database import removeRepo

def getUserReposNames(username: str) -> list[str]:
    ignoreList: list[str] = []
    
    if os.path.exists(".repoignore"):
        with open(".repoignore", "r") as file:
            ignoreList = file.read().lower().strip().splitlines()

    url: str = f"https://api.github.com/users/{username}/repos"
    response: dict = requests.get(url)
    repos: dict = response.json()
    
    repoList: list[str] = []
    
    # Check if repos is a list (valid response) before processing
    if isinstance(repos, list):
        for repo in repos:
            if isinstance(repo, dict) and 'name' in repo:
                if ignoreList and repo['name'].lower().strip() in ignoreList:
                    removeRepo(repo['name'])
                    continue
                repoList.append(repo['name'])
    else:
        print(f"Error fetching repositories: {repos}")
    
    return repoList