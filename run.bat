@echo off
REM filepath: .\run.bat

REM Color codes for Windows console
set RED=^[91m
set GREEN=^[92m
set YELLOW=^[93m
set BLUE=^[94m
set NC=^[0m

REM Print colored messages
call :define_print_functions

REM Make sure we're running from the project root
pushd %~dp0

REM Check if .env file exists, if not create it with default values
if not exist .env (
    call :warning ".env file not found. Creating a default one."
    echo # GitHub username > .env
    echo USERNAME=your_github_username >> .env
    echo # Database path >> .env
    echo DATABASE_PATH=./data/repos.db >> .env
    call :info "Please edit the .env file with your actual GitHub username."
    exit /b 1
)

REM If the data directory doesn't exist, create it
if not exist data mkdir data

REM Main execution
call :info "Starting setup process..."

call :check_python
call :check_node
call :setup_venv
call :setup_node
call :build_typescript

call :success "Setup complete! Starting application now."
call :run_app

exit /b 0

:check_python
call :info "Checking Python version..."
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    call :error "Python not found. Please install Python 3.8+"
    exit /b 1
)

for /f "tokens=2" %%a in ('python --version 2^>^&1') do set PYTHON_VERSION=%%a
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
    set MAJOR=%%a
    set MINOR=%%b
)

if %MAJOR% geq 3 if %MINOR% geq 8 (
    call :success "Python %PYTHON_VERSION% detected"
) else (
    call :error "Python 3.8+ is required (found %PYTHON_VERSION%)"
    exit /b 1
)
goto :eof

:check_node
call :info "Checking Node.js and npm..."
node --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    call :error "Node.js not found. Please install Node.js"
    exit /b 1
)

npm --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    call :error "npm not found. Please install npm"
    exit /b 1
)

for /f "tokens=*" %%a in ('node -v') do set NODE_VERSION=%%a
for /f "tokens=*" %%a in ('npm -v') do set NPM_VERSION=%%a
call :success "Node.js %NODE_VERSION% and npm %NPM_VERSION% detected"
goto :eof

:setup_venv
call :info "Setting up Python virtual environment..."

if not exist .venv (
    python -m venv .venv
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Install Python dependencies
call :info "Installing Python dependencies..."
pip install -q -r requirements.txt

call :success "Python environment set up successfully"
goto :eof

:setup_node
call :info "Setting up Node.js dependencies..."
call npm install
call :success "Node.js dependencies installed"
goto :eof

:build_typescript
call :info "Building TypeScript..."
call npx tsc
call :success "TypeScript build complete"
goto :eof

:run_app
call :info "Starting application..."
python app.py
goto :eof

:define_print_functions
REM Define print functions for colored output
goto :eof

:info
echo [INFO] %~1
goto :eof

:success
echo [SUCCESS] %~1
goto :eof

:warning
echo [WARNING] %~1
goto :eof

:error
echo [ERROR] %~1
goto :eof