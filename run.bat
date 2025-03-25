@echo off
setlocal enabledelayedexpansion

:: Color codes for Windows console
set "RED=31"
set "GREEN=32"
set "YELLOW=33"
set "BLUE=34"

:: Print colored messages functions
call :define_print_functions

:: Make sure we're running from the project root
pushd "%~dp0"

:: Check if .env file exists, if not create it with default values
if not exist .env (
    call :warning ".env file not found. Creating a default one."
    (
        echo # GitHub username
        echo USERNAME=your_github_username
        echo # Database path
        echo DATABASE_PATH=./data/repos.db
        echo # Repoignore path
        echo REPOIGNORE_PATH=.repoignore
        echo # Environment path
        echo ENV_PATH=.env
    ) > .env
    call :info "Please edit the .env file with your actual GitHub username."
    exit /b 1
)

:: If the data directory doesn't exist, create it
if not exist data mkdir data

:: Check Python version
call :check_python

:: Check for Node.js and npm
call :check_node

:: Set up Python virtual environment
call :setup_venv

:: Setup Node.js (if available)
call :setup_node

:: Build TypeScript (if Node.js is available)
call :build_typescript

call :success "Setup complete! Starting application now."
call :run_app

goto :eof

::------------------------------------------------------------------------------
:: FUNCTION DEFINITIONS
::------------------------------------------------------------------------------

:define_print_functions
:: Define the color printing functions
for %%G in (info:BLUE success:GREEN warning:YELLOW error:RED) do (
    for /f "tokens=1,2 delims=:" %%a in ("%%G") do (
        setlocal EnableDelayedExpansion
        set "func=%%a"
        set "color=%%b"
        endlocal & (
            echo set "%%a=for %%%%I in (1^) do (echo [!%%color!m[%%a]![NC!m %%%%~1)"
        ) >> "%temp%\colorprint.bat"
    )
)
set "NC=0"
call "%temp%\colorprint.bat"
del "%temp%\colorprint.bat"
goto :eof

:info
echo [%BLUE%m[INFO][0m %~1
goto :eof

:success
echo [%GREEN%m[SUCCESS][0m %~1
goto :eof

:warning
echo [%YELLOW%m[WARNING][0m %~1
goto :eof

:error
echo [%RED%m[ERROR][0m %~1
goto :eof

:check_python
call :info "Checking Python version..."
:: Check if Python 3.10+ is installed
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    python3 --version >nul 2>&1
    if %ERRORLEVEL% neq 0 (
        call :error "Python 3 not found. Please install Python 3.10+"
        exit /b 1
    ) else (
        set PYTHON_CMD=python3
    )
) else (
    set PYTHON_CMD=python
)

for /f "tokens=2" %%V in ('%PYTHON_CMD% --version 2^>^&1') do set PYTHON_VERSION=%%V
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
    set MAJOR=%%a
    set MINOR=%%b
)

if %MAJOR% LSS 3 (
    call :error "Python 3.10+ is required (found %PYTHON_VERSION%)"
    exit /b 1
)
if %MAJOR% EQU 3 (
    if %MINOR% LSS 10 (
        call :error "Python 3.10+ is required (found %PYTHON_VERSION%)"
        exit /b 1
    )
)
call :success "Python %PYTHON_VERSION% detected"
goto :eof

:check_node
call :info "Checking if Node.js is available..."
where node >nul 2>&1
if %ERRORLEVEL% neq 0 (
    call :warning "Node.js not found. Skipping TypeScript build steps."
    set "SKIP_NODE_STEPS=true"
    goto :eof
)

where npm >nul 2>&1
if %ERRORLEVEL% neq 0 (
    call :warning "npm not found. Skipping TypeScript build steps."
    set "SKIP_NODE_STEPS=true"
    goto :eof
)

for /f "tokens=1" %%V in ('node -v') do set NODE_VERSION=%%V
for /f "tokens=1" %%V in ('npm -v') do set NPM_VERSION=%%V
call :success "Node.js %NODE_VERSION% and npm %NPM_VERSION% detected"
set "SKIP_NODE_STEPS=false"
goto :eof

:setup_venv
call :info "Setting up Python virtual environment..."

:: Get Python version from .python-version file if it exists
if exist .python-version (
    set /p PYTHON_VERSION=<.python-version
    set PYTHON_VERSION=%PYTHON_VERSION: =%
) else (
    set PYTHON_VERSION=%PYTHON_VERSION%
)

:: Check if venv exists
if not exist .venv (
    :: Check if uv is installed
    where uv >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        call :info "Using uv to create virtual environment..."
        uv venv -p "python%PYTHON_VERSION%" .venv
    ) else (
        call :info "Using venv module to create virtual environment..."
        %PYTHON_CMD% -m venv .venv
    )
)

:: Activate virtual environment
call .venv\Scripts\activate

:: Check if uv is installed for package installation
where uv >nul 2>&1
if %ERRORLEVEL% equ 0 (
    call :info "Using uv for package installation..."
    :: Use uv to install dependencies from pyproject.toml
    uv pip install -q -r pyproject.toml
) else (
    call :warning "uv not found. Using pip instead. Consider installing uv for faster package installation."
    :: Fallback to pip with requirements.txt if it exists
    if exist requirements.txt (
        pip install -q -r requirements.txt
    ) else (
        :: If no requirements.txt, install from pyproject.toml
        pip install -q -r pyproject.toml
    )
)

call :success "Python environment set up successfully"
goto :eof

:setup_node
if "%SKIP_NODE_STEPS%"=="true" (
    call :info "Skipping Node.js setup (not installed)"
    :: Check if the compiled JavaScript exists
    if not exist "src/static/dist\index.js" (
        call :error "Compiled JavaScript not found and Node.js not available to build it"
        call :error "Please install Node.js or add the compiled JavaScript files"
        exit /b 1
    )
    call :info "Using existing compiled JavaScript"
) else (
    call :info "Setting up Node.js dependencies..."
    npm install
    call :success "Node.js dependencies installed"
)
goto :eof

:build_typescript
if "%SKIP_NODE_STEPS%"=="true" (
    call :info "Skipping TypeScript build (Node.js not installed)"
) else (
    call :info "Building TypeScript..."
    npx tsc
    call :success "TypeScript build complete"
)
goto :eof

:run_app
call :info "Running application..."

:: Make sure we're still in the virtual environment
if exist .venv\Scripts\activate.bat (
    if not defined VIRTUAL_ENV (
        call .venv\Scripts\activate.bat
    )
)

:: Check if app.py exists
if not exist src\app.py (
    call :error "src/app.py not found. Cannot start application."
    exit /b 1
)

:: Run the Python application with proper parameters
call :info "Starting the application server..."
%PYTHON_CMD% src\app.py

:: If Python app exits with error
if %ERRORLEVEL% neq 0 (
    call :error "Application crashed or failed to start (exit code: %ERRORLEVEL%)"
    exit /b %ERRORLEVEL%
)

goto :eof

endlocal