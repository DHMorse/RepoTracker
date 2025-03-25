# RepoTracker

[![Python](https://img.shields.io/badge/Python_3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![uv](https://img.shields.io/badge/uv-FFE873?style=flat&logo=python&logoColor=black)](https://github.com/astral-sh/uv)
[![Flask](https://img.shields.io/badge/Flask-3daabf?style=flat&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Node.js](https://img.shields.io/badge/Node.js_DevDep-339933?style=flat&logo=node.js&logoColor=white)](https://nodejs.org/)
[![npm](https://img.shields.io/badge/npm_DevDep-CB3837?style=flat&logo=npm&logoColor=white)](https://www.npmjs.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript_DevDep-3178C6?style=flat&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)

A task prioritization and project management tool that integrates with your GitHub repositories, helping you organize and track progress on your coding projects.

## 🚀 Features

- **GitHub Integration**: Automatically imports your repositories
- **Priority Management**: Organize tasks by priority (high, medium, low)
- **Progress Tracking**: Visualize project completion
- **Milestone Planning**: Set and track milestones
- **Drag & Drop Reordering**: Easily reposition tasks

## 📋 Prerequisites

- Python 3.10 or higher
- Node.js and npm
- SQLite3
- uv (recommended for faster dependency management)

## 🔧 Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/DHMorse/RepoTracker.git
    cd RepoTracker
    ```

2. Edit the `.env` file in the root directory:
    ```ini
    USERNAME=YOUR_GITHUB_USERNAME
    DATABASE_PATH=./data/database.db
    REPOIGNORE_PATH=./.repoignore
    ENV_PATH=./.venv
    ```

## 🖥️ Usage

1. Start the application:
    ```bash
    ./run.sh
    ```
    or
    ```cmd
    .\run.bat
    ```

2. Open your browser and go to:
    ```
    http://localhost:5000
    ```

3. Use the interface to:
   - View repositories by priority
   - Track project progress
   - Reorder tasks using drag & drop

## 📁 Project Structure

```
repoTracker/
├── src/                   # Source code directory
│   ├── app.py            # Main Flask application
│   ├── helperFunctions/  # Helper modules
│   │   ├── database.py   # Database operations
│   │   └── main.py       # Main helper functions
│   ├── static/           # Static assets
│   │   ├── dist/        # Compiled TypeScript
│   │   ├── src/         # TypeScript source
│   │   └── styles.css   # CSS styles
│   └── templates/        # HTML templates
│       └── index.html    # Main page template
├── .python-version       # Python version specification
├── pyproject.toml        # Project dependencies and metadata
├── uv.lock              # uv dependency lock file
├── run.sh               # Setup and run script
├── run.bat              # Windows setup and run script
└── package.json         # Node.js dependencies
```

## ⚙️ Configuration

### Repository Ignore List
Create a `.repoignore` file to specify repositories to exclude:

```
# Completed projects
project1
project2

# Not started
project3

# Other exclusions
project4
```

## 📄 License

Licensed under the [GNU General Public License v3.0](LICENSE).

## 🤝 Contributing

Contributions are welcome! Follow these steps:

1. Fork the repository
2. Create a feature branch:
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. Commit your changes:
   ```bash
   git commit -m 'Add some amazing feature'
   ```
4. Push to the branch:
   ```bash
   git push origin feature/amazing-feature
   ```
5. Open a Pull Request

---

Happy coding! 🚀

