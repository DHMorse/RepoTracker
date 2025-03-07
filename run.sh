#!/bin/bash
# filepath: /home/daniel/Documents/myCode/refactored-goggles/run.sh

# Color codes for better output visualization
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored messages
info() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Make sure we're running from the project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || { error "Cannot change to script directory"; exit 1; }

# Check if .env file exists, if not create it with default values
if [ ! -f .env ]; then
    warning ".env file not found. Creating a default one."
    cat > .env << EOF
# GitHub username
USERNAME=your_github_username
# Database path
DATABASE_PATH=./data/repos.db
EOF
    info "Please edit the .env file with your actual GitHub username."
    exit 1
fi

# If the data directory doesn't exist, create it
mkdir -p data

# Function to check python version
check_python() {
    info "Checking Python version..."
    # Check if Python 3.8+ is installed
    if command -v python3 &>/dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d ' ' -f 2)
        MAJOR=$(echo "$PYTHON_VERSION" | cut -d '.' -f 1)
        MINOR=$(echo "$PYTHON_VERSION" | cut -d '.' -f 2)
        
        if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 8 ]; then
            success "Python $PYTHON_VERSION detected"
        else
            error "Python 3.8+ is required (found $PYTHON_VERSION)"
            exit 1
        fi
    else
        error "Python 3 not found. Please install Python 3.8+"
        exit 1
    fi
}

# Function to check for Node.js and npm
check_node() {
    info "Checking Node.js and npm..."
    if ! command -v node &>/dev/null; then
        error "Node.js not found. Please install Node.js"
        exit 1
    fi
    
    if ! command -v npm &>/dev/null; then
        error "npm not found. Please install npm"
        exit 1
    fi
    
    NODE_VERSION=$(node -v)
    NPM_VERSION=$(npm -v)
    success "Node.js $NODE_VERSION and npm $NPM_VERSION detected"
}

# Function to set up Python virtual environment
setup_venv() {
    info "Setting up Python virtual environment..."
    
    # Check if venv exists
    if [ ! -d ".venv" ]; then
        python3 -m venv .venv
    fi
    
    # Activate virtual environment
    source .venv/bin/activate
    
    # Install Python dependencies
    info "Installing Python dependencies..."
    pip install -q -r requirements.txt
    
    success "Python environment set up successfully"
}

# Function to check for Node.js and npm - now optional
check_node() {
    info "Checking if Node.js is available..."
    if ! command -v node &>/dev/null || ! command -v npm &>/dev/null; then
        warning "Node.js or npm not found. Skipping TypeScript build steps."
        # Set a flag to indicate we should skip node-related steps
        SKIP_NODE_STEPS=true
    else
        NODE_VERSION=$(node -v)
        NPM_VERSION=$(npm -v)
        success "Node.js $NODE_VERSION and npm $NPM_VERSION detected"
        SKIP_NODE_STEPS=false
    fi
}

# Function to install Node.js dependencies - now conditional
setup_node() {
    if [ "$SKIP_NODE_STEPS" = true ]; then
        info "Skipping Node.js setup (not installed)"
        # Check if the compiled JavaScript exists
        if [ ! -f "static/dist/index.js" ]; then
            error "Compiled JavaScript not found and Node.js not available to build it"
            error "Please install Node.js or add the compiled JavaScript files"
            exit 1
        fi
        info "Using existing compiled JavaScript"
    else
        info "Setting up Node.js dependencies..."
        npm install
        success "Node.js dependencies installed"
    fi
}

# Function to build TypeScript - now conditional
build_typescript() {
    if [ "$SKIP_NODE_STEPS" = true ]; then
        info "Skipping TypeScript build (Node.js not installed)"
    else
        info "Building TypeScript..."
        npx tsc
        success "TypeScript build complete"
    fi
}

# Function to start the application
run_app() {
    info "Starting application..."
    python app.py
}

# Main execution
main() {
    info "Starting setup process..."
    
    # Initialize the flag
    SKIP_NODE_STEPS=false
    
    check_python
    check_node
    setup_venv
    setup_node
    build_typescript
    
    success "Setup complete! Starting application now."
    run_app
}

# Run the main function
main