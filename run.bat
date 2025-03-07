@echo off
SETLOCAL

echo Checking for Python 3.8+...
python --version 2>NUL | findstr /r "3\.[89]\|3\.[1-9][0-9]" >NUL
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python 3.8 or higher is required but not installed.
    echo Please download and install from https://www.python.org/downloads/
    exit /b 1
)

echo Checking for Node.js and npm...
where npm >NUL 2>NUL
if %ERRORLEVEL% NEQ 0 (
    echo Error: Node.js and npm are required but not installed.
    echo Please download and install from https://nodejs.org/
    exit /b 1
)

echo Creating data directory...
if not exist data mkdir data

echo Creating Python virtual environment...
if not exist .venv (
    python -m venv .venv
    if %ERRORLEVEL% NEQ 0 (
        echo Error: Failed to create virtual environment.
        exit /b 1
    )
)

echo Activating virtual environment...
call .venv\Scripts\activate

echo Installing Python dependencies...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to install Python dependencies.
    exit /b 1
)

echo Installing npm packages...
npm install
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to install npm packages.
    exit /b 1
)

echo Compiling TypeScript...
npm run build || npx tsc
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to compile TypeScript.
    exit /b 1
)

echo Running application...
python app.py

ENDLOCAL