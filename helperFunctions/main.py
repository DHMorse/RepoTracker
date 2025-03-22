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
    """
    Adds new repos to the database, removes ignored repos, and handles repositories that no longer exist.
    
    This function:
    1. Fetches current GitHub repositories
    2. Gets repositories from the local database
    3. Processes the .repoignore file
    4. Removes ignored repositories
    5. Adds new repositories
    6. Removes repositories that no longer exist on GitHub
    """
    githubRepoNameList: list[str] = getUserReposNames(USERNAME)
    repoIgnoreList: list[str] = []
    reposInTheDatabase: list[str] = []

    # Load ignore list first
    if os.path.exists(".repoignore"):
        with open(".repoignore", "r") as file:
            repoIgnoreList = [name.lower().strip() for name in file.read().splitlines() if name.strip()]
    
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
    
    # First, handle ignored repositories (remove them from database regardless of GitHub status)
    for repoName in reposInTheDatabase:
        if repoName.lower() in repoIgnoreList:
            removeRepo(repoName)
            # Also remove from our tracking list to avoid further processing
            reposInTheDatabase = [r for r in reposInTheDatabase if r != repoName]
    
    # Now handle the remaining repositories
    for githubRepoName in githubRepoNameList:
        # Skip if the repo is in the ignore list
        if githubRepoName.lower() in repoIgnoreList:
            continue
            
        # Add new repositories that aren't ignored
        if githubRepoName not in reposInTheDatabase:
            updateRepo(USERNAME, githubRepoName, 'high', 0, 'N/A', 0, 0)
    
    # Remove repositories that no longer exist on GitHub
    for dbRepoName in reposInTheDatabase:
        if dbRepoName not in githubRepoNameList:
            removeRepo(dbRepoName)
