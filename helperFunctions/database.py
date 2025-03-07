import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_PATH: str = os.getenv('DATABASE_PATH')


def createUsersTables():
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS users (userId INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)')
        conn.commit()

def createReposTable():
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS repos (
                repoId INTEGER PRIMARY KEY AUTOINCREMENT, 
                userId INTEGER, 
                name TEXT,
                priority TEXT,
                priorityOrder INTEGER,
                nextMilestone TEXT,
                timeToNextMilestone INTEGER,
                progress INTEGER, 
                FOREIGN KEY(userId) REFERENCES users(userId)
            )''')
        conn.commit()

def createDatabase():
    createUsersTables()
    createReposTable()

def insertUser(username: str):
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users WHERE name = ?', (username,))
        user = cursor.fetchone()
        if user:
            return

        cursor.execute('INSERT INTO users (name) VALUES (?)', (username,))
        conn.commit()

def updateRepo(username: str, repoName: str, repoPrioity: str, repoPrioityOrder: int, nextMilestone: str, timeToNextMilestone: int, progress: int):
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users WHERE name = ?', (username,))
        user = cursor.fetchone()
        if not user:
            return
        
        userId: int = user[0]

        cursor.execute('SELECT * FROM repos WHERE userId = ? AND name = ?', (userId, repoName))
        repo = cursor.fetchone()
        
        if repo:
            cursor.execute('''UPDATE repos SET priority = ?,
                            priorityOrder = ?,
                            nextMilestone = ?, 
                            timeToNextMilestone = ?, 
                            progress = ? WHERE repoId = ?''', (
                                repoPrioity, 
                                repoPrioityOrder,
                                nextMilestone, 
                                timeToNextMilestone, 
                                progress, 
                                repo[0]
                            )
                        )
        
        else:
            cursor.execute('''INSERT INTO repos (
                            userId, 
                            name, 
                            priority, 
                            priorityOrder,
                            nextMilestone, 
                            timeToNextMilestone, 
                            progress) VALUES (?, ?, ?, ?, ?, ?, ?)''', (
                                userId, 
                                repoName, 
                                repoPrioity, 
                                repoPrioityOrder,
                                nextMilestone, 
                                timeToNextMilestone, 
                                progress
                            )
                        )

        # Resolve priorityOrder conflicts
        if repo:
            current_repo_id = repo[0]
        else:
            cursor.execute('SELECT last_insert_rowid()')
            current_repo_id = cursor.fetchone()[0]

        # Find all repos with the same or higher priorityOrder (excluding current repo)
        # and shift them up by 1 to make room for the new/updated repo
        cursor.execute(
            'UPDATE repos SET priorityOrder = priorityOrder + 1 WHERE userId = ? AND priorityOrder >= ? AND repoId != ?',
            (userId, repoPrioityOrder, current_repo_id)
        )

        conn.commit()

def removeRepo(repoName: str):
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute('DELETE FROM repos WHERE name = ?', (repoName,))
        conn.commit()

def getReposNameAndProgress(username: str) -> list[tuple[str, int]]:
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users WHERE name = ?', (username,))
        user = cursor.fetchone()
        if not user:
            return []

        userId: int = user[0]

        cursor.execute('SELECT * FROM repos WHERE userId = ?', (userId,))
        repos = cursor.fetchall()

        return [(repo[2], repo[3]) for repo in repos]
    

def sortRepoPriorityOrder(username: str):
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users WHERE name = ?', (username,))
        user = cursor.fetchone()
        if not user:
            return

        userId: int = user[0]

        cursor.execute('SELECT * FROM repos WHERE userId = ? ORDER BY priorityOrder', (userId,))
        repos = cursor.fetchall()

        high_priority_repos = []
        medium_priority_repos = []
        low_priority_repos = []

        for repo in repos:
            match repo[3]:
                case 'high':
                    high_priority_repos.append(repo)
                case 'medium':
                    medium_priority_repos.append(repo)
                case 'low':
                    low_priority_repos.append(repo)

        fuckingNewOrder = 0
        for repo in high_priority_repos:
            cursor.execute('UPDATE repos SET priorityOrder = ? WHERE repoId = ?', (fuckingNewOrder, repo[0]))
            fuckingNewOrder += 1
        
        for repo in medium_priority_repos:
            cursor.execute('UPDATE repos SET priorityOrder = ? WHERE repoId = ?', (fuckingNewOrder, repo[0]))
            fuckingNewOrder += 1

        for repo in low_priority_repos:
            cursor.execute('UPDATE repos SET priorityOrder = ? WHERE repoId = ?', (fuckingNewOrder, repo[0]))
            fuckingNewOrder += 1

        conn.commit()