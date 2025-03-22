import os 
import requests
import sqlite3

from helperFunctions.database import removeRepo, updateRepo

USERNAME: str = os.getenv('USERNAME')
DATABASE_PATH: str = os.getenv('DATABASE_PATH')

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

def checkRepos() -> None:
    """Adds new repos to the database and removes ignored repos"""

    repoList: list[str] = getUserReposNames(USERNAME)

    ignoreList: list[str] = []

    reposInTheDatabase: list[str] = []

    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM repos WHERE userId = ?', (USERNAME,))
        repos = cursor.fetchall()

        for repo in repos:
            reposInTheDatabase.append(repo[2])

    if os.path.exists(".repoignore"):
        with open(".repoignore", "r") as file:
            ignoreList = file.read().lower().strip().splitlines()
            
    for repo in repoList:
        if repo in ignoreList:
            removeRepo(repo)
        elif repo not in reposInTheDatabase:
            updateRepo(USERNAME, repo, 'high', 0, 'N/A', 0, 0)
