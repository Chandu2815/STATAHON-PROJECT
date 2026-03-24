#!/bin/bash

# STATAHON PROJECT - Start Script
# This script starts the entire STATAHON application

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       🚀 STATAHON PROJECT - STARTING APPLICATION       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"

# Check if Python 3.13 is available
if ! command -v python3.13 &> /dev/null; then
    echo -e "${YELLOW}⚠️  python3.13 not found. Trying python3...${NC}"
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python3.13"
fi

# Check if the application is already running on port 8000
if lsof -i :8000 > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Port 8000 is already in use.${NC}"
    echo "Kill existing process? (y/n)"
    read -r answer
    if [[ $answer == "y" ]]; then
        echo -e "${YELLOW}Killing existing process...${NC}"
        kill -9 $(lsof -ti :8000) 2>/dev/null || true
        sleep 2
    else
        echo -e "${YELLOW}Please free up port 8000 and try again.${NC}"
        exit 1
    fi
fi

# Navigate to project directory
cd "$SCRIPT_DIR"

echo -e "${GREEN}✓${NC} Project directory: $SCRIPT_DIR"

# Check if virtual environment exists
if [ -d ".venv" ]; then
    echo -e "${GREEN}✓${NC} Virtual environment found"
    source .venv/bin/activate
    echo -e "${GREEN}✓${NC} Virtual environment activated"
else
    echo -e "${YELLOW}⚠️  No virtual environment found. Creating one...${NC}"
    $PYTHON_CMD -m venv .venv
    source .venv/bin/activate
    echo -e "${GREEN}✓${NC} Virtual environment created and activated"
fi

# Check if requirements are installed
if [ ! -f "requirements.txt" ]; then
    echo -e "${YELLOW}⚠️  requirements.txt not found${NC}"
else
    echo -e "${BLUE}Checking dependencies...${NC}"
    pip install -q -r requirements.txt 2>/dev/null || true
    echo -e "${GREEN}✓${NC} Dependencies checked"
fi

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Starting STATAHON Application...${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}Server will be available at:${NC}"
echo -e "  🏠 Landing Page:    ${BLUE}http://127.0.0.1:8000/${NC}"
echo -e "  📝 Register:        ${BLUE}http://127.0.0.1:8000/register${NC}"
echo -e "  🔐 Login:           ${BLUE}http://127.0.0.1:8000/login${NC}"
echo -e "  📊 Dashboard:       ${BLUE}http://127.0.0.1:8000/dashboard${NC}"
echo -e "  👨‍💼 Admin:           ${BLUE}http://127.0.0.1:8000/admin${NC}"
echo -e "  📚 API Docs:        ${BLUE}http://127.0.0.1:8000/docs${NC}"
echo ""
echo -e "${YELLOW}Press CTRL+C to stop the server${NC}"
echo ""

# Start the FastAPI application
$PYTHON_CMD -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
