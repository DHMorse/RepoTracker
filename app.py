from flask import Flask, render_template
import requests
import os
from dotenv import load_dotenv
import sqlite3
import requests
from flask import request, jsonify


from helperFunctions.database import createDatabase, insertUser, updateRepo, removeRepo, sortRepoPriorityOrder
from flask import redirect

# Init app
app = Flask(__name__)
load_dotenv()
DATABASE_PATH: str = os.getenv('DATABASE_PATH')

def getUserReposNames(username: str) -> list[str]:
    ignoreList: list[str] = []
    if os.path.exists(".repoignore"):
        with open(".repoignore", "r") as file:
            ignoreList = file.read().lower().strip().splitlines()

    url = f"https://api.github.com/users/{username}/repos"
    response = requests.get(url)
    repos = response.json()
    
    repoList = []
    
    for repo in repos:
        if ignoreList and repo['name'].lower().strip() in ignoreList:
            removeRepo(repo['name'])
            continue
        repoList.append(repo['name'])

    return repoList

@app.route('/<path:path>')
def catch_all(path):
    return redirect('/')

@app.route('/')
def index():
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM repos')
        repos = cursor.fetchall()
    
    tasks = []
    for repo in repos:
        tasks.append({
            "repoId": repo[0],
            "userId": repo[1],
            "name": repo[2],
            "priority": repo[3],
            "priorityOrder": repo[4],
            "milestone": repo[5],
            "time": repo[6],
            "progress": repo[7]
        })
    
    highPriorityTasks = []
    mediumPriorityTasks = []
    lowPriorityTasks = []
    
    # Sort tasks by priority
    for task in tasks:
        match task["priority"]:
            case "high":
                highPriorityTasks.append(task)
            case "medium":
                mediumPriorityTasks.append(task)
            case "low":
                lowPriorityTasks.append(task)
    
    highPriorityTasks.sort(key=lambda x: x["priorityOrder"])
    mediumPriorityTasks.sort(key=lambda x: x["priorityOrder"])
    lowPriorityTasks.sort(key=lambda x: x["priorityOrder"])

    return render_template('index.html', 
                            high_priority_tasks=highPriorityTasks,
                            medium_priority_tasks=mediumPriorityTasks,
                            low_priority_tasks=lowPriorityTasks)

@app.route('/api/tasks/reorder', methods=['POST'])
def reorder_task():
    task: dict = request.json
    
    # Validate request data
    if not task or 'repoId' not in task or 'priorityOrder' not in task:
        return jsonify({'error': 'Missing required fields: name and priorityOrder'}), 400

    # Check that priorityOrder is a valid integer
    try:
        task['priorityOrder'] = int(task['priorityOrder'])
    except (ValueError, TypeError):
        return jsonify({'error': 'priorityOrder must be a valid integer'}), 400

    # Check if the task exists
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM repos WHERE repoId = ?', (task['repoId'],))
        
        if cursor.fetchone()[0] == 0:
            return jsonify({'error': 'Task not found'}), 404
    
    # Update the task's priorityOrder
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE repos SET priorityOrder = ? WHERE repoId = ?', (task['priorityOrder'], task['repoId']))
        conn.commit()

        # Check if another task has the same priorityOrder
        cursor.execute('SELECT COUNT(*) FROM repos WHERE priorityOrder = ? AND repoId != ?', (task['priorityOrder'], task['repoId']))
        if cursor.fetchone()[0] > 0:
            # If there are other tasks with the same priority order, 
            # we need to update them to prevent collisions
            cursor.execute(
                'SELECT repoId FROM repos WHERE priorityOrder = ? AND repoId != ?', 
                (task['priorityOrder'], task['repoId'])
            )
            conflicting_tasks = cursor.fetchall()

            for conflicting_task in conflicting_tasks:
                # Increment the conflicting task's priority order
                cursor.execute(
                    'UPDATE repos SET priorityOrder = priorityOrder + 1 WHERE repoId = ?',
                    (conflicting_task[0],)
                )
            conn.commit()
    
    return jsonify({'message': 'Task reordered successfully'}), 200

if __name__ == '__main__':

    USERNAME = os.getenv('USERNAME')
    
    createDatabase()
    
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE name = ?', (USERNAME,))
        user = cursor.fetchone()
        
        cursor.execute('SELECT * FROM repos WHERE userId = ?', (user[0],))
        repos = cursor.fetchall()

    repoList: list[str] = getUserReposNames(USERNAME)

    if not user:
        insertUser(USERNAME)
    
    if not repos:
        for repo in repoList:
            updateRepo(USERNAME, repo, 'high', 0, 'N/A', 0, 0)
        
        sortRepoPriorityOrder(USERNAME)

    app.run(host='0.0.0.0', port=5000, debug=True)