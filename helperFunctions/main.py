import os 
import requests

from helperFunctions.database import removeRepo, updateRepo

USERNAME: str = os.getenv('USERNAME')

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

def checkRepos(repoList: list[str], repos: list[tuple]) -> list[str]:
    for repo in repoList:
        with open(".repoignore", "r") as file:
            ignoreList = file.read().lower().strip().splitlines()
        if not repo in ignoreList and not repo in [r[2] for r in repos]:
            updateRepo(USERNAME, repo, 'high', 0, 'N/A', 0, 0)
        if repo in ignoreList:
            removeRepo(repo)
