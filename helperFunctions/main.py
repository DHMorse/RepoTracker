import os 
import requests
import sqlite3

from helperFunctions.database import removeRepo, updateRepo, insertUser

USERNAME: str = os.getenv('USERNAME')
DATABASE_PATH: str = os.getenv('DATABASE_PATH')

def getUserReposNames(username: str) -> list[str]:
    """
    Fetches all repository names for a given GitHub username, handling pagination.
    
    Args:
        username: GitHub username to fetch repositories for
        
    Returns:
        A list of repository names
    """
    repoList: list[str] = []
    page: int = 1
    per_page: int = 100  # Maximum allowed by GitHub API
    
    while True:
        url: str = f"https://api.github.com/users/{username}/repos?page={page}&per_page={per_page}"
        response = requests.get(url)
        repos = response.json()
        
        # Check if repos is a list (valid response) before processing
        if isinstance(repos, list):
            if not repos:  # Empty page means we've processed all repos
                break
                
            for repo in repos:
                repoList.append(repo['name'])
                
            page += 1  # Move to next page
        else:
            print(f"Error fetching repositories: {repos}")
            break
    
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
