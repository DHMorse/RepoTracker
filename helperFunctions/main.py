import os 
import requests
import sqlite3

from helperFunctions.database import removeRepo, updateRepo, insertUser

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

    githubRepoNameList: list[str] = getUserReposNames(USERNAME)

    repoIgnoreList: list[str] = []

    reposInTheDatabase: list[str] = []

    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users WHERE name = ?', (USERNAME,))
        user: tuple | None = cursor.fetchone()

        if not user:
            insertUser(USERNAME)

        cursor.execute('SELECT * FROM users WHERE name = ?', (USERNAME,))
        user: tuple | None = cursor.fetchone()

        cursor.execute('SELECT * FROM repos WHERE userId = ?', (user[0],))
        repos = cursor.fetchall()

        for repo in repos:
            reposInTheDatabase.append(repo[2])

    if os.path.exists(".repoignore"):
        with open(".repoignore", "r") as file:
            repoIgnoreList = file.read().lower().strip().splitlines()
            
    for githubRepoName in githubRepoNameList + reposInTheDatabase:
        if githubRepoName in repoIgnoreList:
            removeRepo(githubRepoName)
        elif githubRepoName not in reposInTheDatabase and githubRepoName in githubRepoNameList:
            updateRepo(USERNAME, githubRepoName, 'high', 0, 'N/A', 0, 0)
        elif githubRepoName in reposInTheDatabase and githubRepoName not in githubRepoNameList:
            removeRepo(githubRepoName)
