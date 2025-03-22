from flask import Flask, jsonify, request, redirect, render_template, send_file
from dotenv import load_dotenv
import os
import sqlite3

from helperFunctions.database import createDatabase, insertUser, updateRepo, sortReposByPriorityOrder, removeRepo
from helperFunctions.main import getUserReposNames, checkRepos

# Init app
app: Flask = Flask(__name__)

load_dotenv()

# Environment variables
DATABASE_PATH: str = os.getenv('DATABASE_PATH')
REPOIGNORE_PATH: str = os.getenv('REPOIGNORE_PATH')
USERNAME: str = os.getenv('USERNAME')

@app.route('/<path:path>')
def catch_all(path):
    return redirect('/')

@app.route('/')
def index():
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor: sqlite3.Cursor = conn.cursor()
        cursor.execute('SELECT * FROM repos')
        repos: list[tuple] = cursor.fetchall()

    highPriorityRepos: list[tuple]
    mediumPriorityRepos: list[tuple]
    lowPriorityRepos: list[tuple]

    # Sort the repos by priority order
    highPriorityRepos, mediumPriorityRepos, lowPriorityRepos = sortReposByPriorityOrder(repos)

    return render_template('index.html', 
                                highPriorityRepos=highPriorityRepos,
                                mediumPriorityRepos=mediumPriorityRepos,
                                lowPriorityRepos=lowPriorityRepos
                            )

@app.route('/api/repos/reorder', methods=['POST'])
def reorder_repo():
    repo: dict = request.json
    
    # Validate request data
    if not repo or 'repoId' not in repo or 'priorityOrder' not in repo:
        return jsonify({'error': 'Missing required fields: name and priorityOrder'}), 400

    # Check that priorityOrder is a valid integer
    try:
        repo['priorityOrder'] = int(repo['priorityOrder'])
    except (ValueError, TypeError):
        return jsonify({'error': 'priorityOrder must be a valid integer'}), 400

    # Check if the repo exists
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor: sqlite3.Cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM repos WHERE repoId = ?', (repo['repoId'],))
        
        if cursor.fetchone()[0] == 0:
            return jsonify({'error': 'Repo not found'}), 404
    
    # Update the repos's priorityOrder
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE repos SET priorityOrder = ? WHERE repoId = ?', (repo['priorityOrder'], repo['repoId']))
        conn.commit()

        # Check if another repo has the same priorityOrder
        cursor.execute('SELECT COUNT(*) FROM repos WHERE priorityOrder = ? AND repoId != ?', (repo['priorityOrder'], repo['repoId']))
        if cursor.fetchone()[0] > 0:
            # If there are other repos with the same priority order, 
            # we need to update them to prevent collisions
            cursor.execute(
                'SELECT repoId FROM repos WHERE priorityOrder = ? AND repoId != ?', 
                (repo['priorityOrder'], repo['repoId'])
            )
            conflictingRepos = cursor.fetchall()

            for conflictingRepo in conflictingRepos:
                # Increment the conflicting repo's priority order
                cursor.execute(
                    'UPDATE repos SET priorityOrder = priorityOrder + 1 WHERE repoId = ?',
                    (conflictingRepo[0],)
                )
            conn.commit()
    
    return jsonify({'message': 'Repo reordered successfully'}), 200

@app.route('/api/repos/update', methods=['POST'])
def update_repo():
    repoData = request.json
    
    # Validate request data
    if not repoData or 'repoId' not in repoData:
        return jsonify({'error': 'Missing required field: repoId'}), 400

    # Extract repo data
    repoId: int = repoData.get('repoId')
    priority: int = repoData.get('priority')
    progress: int = repoData.get('progress')
    milestone: str = repoData.get('milestone')
    timeRequired: str = repoData.get('timeRequired')
    
    # Check if the repo exists
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor: sqlite3.Cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM repos WHERE repoId = ?', (repoId,))
        
        if cursor.fetchone()[0] == 0:
            return jsonify({'error': 'Repo not found'}), 404
    
    # Update the repo in the database
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor: sqlite3.Cursor = conn.cursor()
            
            # Build the update query dynamically based on provided fields
            updateFields: list[str] = []
            updateValues: list[any] = []
            
            if priority is not None:
                updateFields.append('priority = ?')
                updateValues.append(priority)
                
            if progress is not None:
                updateFields.append('progress = ?')
                updateValues.append(progress)
                
            if milestone is not None:
                updateFields.append('nextMilestone = ?')  # Updated column name
                updateValues.append(milestone)
                
            if timeRequired is not None:
                updateFields.append('timeToNextMilestone = ?')  # Updated column name
                updateValues.append(timeRequired)
            
            if not updateFields:
                return jsonify({'error': 'No fields to update'}), 400
            
            # Construct and execute the update query
            updateQuery: str = f'UPDATE repos SET {", ".join(updateFields)} WHERE repoId = ?'
            updateValues.append(repoId)
            
            cursor.execute(updateQuery, tuple(updateValues))
            conn.commit()
    
    except Exception as e:
        return jsonify({'error': f'Failed to update repo: {str(e)}'}), 500
    
    return jsonify({'message': 'Repo updated successfully'}), 200

@app.route('/api/repoignore', methods=['GET'])
def get_repoignore():
    try:
        with open(REPOIGNORE_PATH, 'r') as file:
            content: str = file.read()
        return content
    
    except Exception as e:
        return jsonify({'error': f'Failed to read .repoignore: {str(e)}'}), 500

@app.route('/api/repoignore', methods=['POST'])
def update_repoignore():
    try:
        content: str = request.get_data(as_text=True)
        with open(REPOIGNORE_PATH, 'w') as file:
            file.write(content)

        checkRepos()
        return jsonify({'message': '.repoignore updated successfully'}), 200

    except Exception as e:
        return jsonify({'error': f'Failed to update .repoignore: {str(e)}'}), 500

@app.route('/api/repos/refresh', methods=['POST'])
def refresh_repos():
    checkRepos()
    return jsonify({'message': 'Repos refreshed successfully'}), 200

if __name__ == '__main__':
    createDatabase()

    checkRepos()
    
    app.run(host='0.0.0.0', port=5000, debug=True)