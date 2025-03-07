@echo off
setlocal EnableDelayedExpansion

:: Color codes for better output visualization (not natively supported in cmd, using echo instead)
set "BLUE=[INFO]"
set "GREEN=[SUCCESS]"
set "YELLOW=[WARNING]"
set "RED=[ERROR]"

:: Function to print messages
echo %BLUE% Starting setup process...

:: Change directory to script location
cd /d "%~dp0" || (
    echo %RED% Cannot change to script directory
    exit /b 1
)

:: Check if .env file exists, if not create it
if not exist .env (
    echo %YELLOW% .env file not found. Creating a default one.
    echo # GitHub username > .env
    echo USERNAME=your_github_username >> .env
    echo # Database path >> .env
    echo DATABASE_PATH=./data/repos.db >> .env
    echo %BLUE% Please edit the .env file with your actual GitHub username.
    exit /b 1
)

:: Create data directory if it doesn't exist
if not exist data mkdir data

:: Check Python version
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo %RED% Python 3 not found. Please install Python 3.8+
    exit /b 1
)

for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set PYTHON_VERSION=%%v
for /f "tokens=1,2 delims=." %%a in ("!PYTHON_VERSION!") do (
    set MAJOR=%%a
    set MINOR=%%b
)

if !MAJOR! LSS 3 ( 
    echo %RED% Python 3.8+ is required (found !PYTHON_VERSION!)
    exit /b 1
)
if !MAJOR! EQU 3 if !MINOR! LSS 8 (
    echo %RED% Python 3.8+ is required (found !PYTHON_VERSION!)
    exit /b 1
)

echo %GREEN% Python !PYTHON_VERSION! detected

:: Check Node.js and npm
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo %RED% Node.js not found. Please install Node.js
    exit /b 1
)

where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo %RED% npm not found. Please install npm
    exit /b 1
)

echo %GREEN% Node.js and npm detected

:: Set up Python virtual environment
if not exist .venv (
    python -m venv .venv
)

call .venv\Scripts\activate

echo %BLUE% Installing Python dependencies...
pip install -q -r requirements.txt

echo %GREEN% Python environment set up successfully

:: Install Node.js dependencies
echo %BLUE% Setting up Node.js dependencies...
npm install

echo %GREEN% Node.js dependencies installed

:: Build TypeScript
echo %BLUE% Building TypeScript...
npx tsc

echo %GREEN% TypeScript build complete

:: Start the application
echo %GREEN% Setup complete! Starting application now.
python app.py

endlocal
