# Refactored Goggles

A task prioritization and project management tool that integrates with your GitHub repositories, helping you organize and track progress on your coding projects.

## 🚀 Features

- **GitHub Integration**: Automatically imports your repositories
- **Priority Management**: Organize tasks by priority (high, medium, low)
- **Progress Tracking**: Visualize project completion
- **Milestone Planning**: Set and track milestones
- **Drag & Drop Reordering**: Easily reposition tasks

## 📋 Prerequisites

- Python 3.8 or higher
- Node.js and npm
- SQLite3

## 🔧 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/refactored-goggles.git
   cd refactored-goggles
   ```

2. Create a `.env` file in the root directory:
   ```ini
   USERNAME=your_github_username
   DATABASE_PATH=./data/repos.db
   ```

3. Run the setup script:
   ```bash
   chmod +x run.sh
   ./run.sh
   ```

## 🖥️ Usage

1. Start the application:
   ```bash
   ./run.sh
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
refactored-goggles/
├── app.py                 # Main Flask application
├── helperFunctions/       # Helper modules
│   └── database.py        # Database operations
├── static/                # Static assets
│   ├── dist/              # Compiled TypeScript
│   ├── src/               # TypeScript source
│   └── styles.css         # CSS styles
├── templates/             # HTML templates
│   └── index.html         # Main page template
├── run.sh                 # Setup and run script
├── requirements.txt       # Python dependencies
└── package.json           # Node.js dependencies
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

