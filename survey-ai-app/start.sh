#!/bin/bash

# Survey AI Startup Script
git # This script starts both the frontend and backend servers.
# It uses port 8002 for the backend to avoid conflicts.

# --- CONFIGURATION ---
BACKEND_PORT=8002
FRONTEND_PORT=5173
HOST=0.0.0.0

# --- COLORS ---
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to kill process by port
kill_process_on_port() {
    PORT=$1
    echo -e "${YELLOW}Checking for process on port $PORT...${NC}"
    PID=$(lsof -t -i:$PORT)
    if [ -n "$PID" ]; then
        echo -e "${RED}Killing process $PID on port $PORT...${NC}"
        kill -9 $PID
    else
        echo -e "${GREEN}No process found on port $PORT.${NC}"
    fi
}

# Kill existing processes on the ports we need
kill_process_on_port $BACKEND_PORT
kill_process_on_port $FRONTEND_PORT

# --- Start Backend ---
echo -e "\n${GREEN}--- Starting Survey AI Backend ---${NC}"
cd backend

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating Python virtual environment..."
    source venv/bin/activate
fi

echo "Installing backend dependencies from requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

echo -e "${YELLOW}Starting Uvicorn server on http://$HOST:$BACKEND_PORT...${NC}"
python -m uvicorn main:app --host $HOST --port $BACKEND_PORT --reload &
BACKEND_PID=$!
cd ..

# --- Start Frontend ---
echo -e "\n${GREEN}--- Starting Survey AI Frontend ---${NC}"
cd frontend

echo "Installing frontend dependencies..."
npm install

echo -e "${YELLOW}Starting Vite dev server on http://localhost:$FRONTEND_PORT...${NC}"
npm run dev &
FRONTEND_PID=$!
cd ..

# --- Wait for processes to exit ---
wait $BACKEND_PID
wait $FRONTEND_PID

echo -e "\n${RED}Both servers have been stopped.${NC}"

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  🚀 Survey AI - Startup Script${NC}"
echo -e "${BLUE}========================================${NC}"

# Function to check if port is in use
check_port() {
  if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1; then
    return 0
  else
    return 1
  fi
}

# Kill existing processes on ports if needed
kill_port() {
  if check_port $1; then
    echo -e "${YELLOW}⚠️  Port $1 is in use. Attempting to free it...${NC}"
    lsof -ti :$1 | xargs kill -9 2>/dev/null || true
    sleep 1
  fi
}

# Start Backend
echo -e "\n${BLUE}[1/3]${NC} Starting Backend Server..."
kill_port 8002

cd "$BACKEND_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
  echo -e "${YELLOW}Creating virtual environment...${NC}"
  python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null

# Install/upgrade dependencies
echo -e "${YELLOW}Checking dependencies...${NC}"
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Check .env file
if [ ! -f ".env" ]; then
  echo -e "${YELLOW}⚠️  .env file not found. Creating template...${NC}"
  cat > .env << 'EOF'
# Database Configuration
DB_USER=postgres
DB_PASSWORD=1234
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=survey_db
EOF
  echo -e "${YELLOW}   Edit .env with your database credentials${NC}"
fi

# Start backend in background
echo -e "${GREEN}✓ Backend Server Starting on http://localhost:8002${NC}"
python main.py > backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID" > backend.pid

# Wait for backend to start
sleep 3
if ! kill -0 $BACKEND_PID 2>/dev/null; then
  echo -e "${RED}✗ Backend failed to start. Check backend.log${NC}"
  cat backend.log
  exit 1
fi

# Start Frontend
echo -e "\n${BLUE}[2/3]${NC} Starting Frontend Server..."
kill_port 5173

cd "$FRONTEND_DIR"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
  echo -e "${YELLOW}Installing npm dependencies (this may take a minute)...${NC}"
  npm install --silent
fi

# Start frontend in background
echo -e "${GREEN}✓ Frontend Server Starting on http://localhost:5173${NC}"
npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID" > frontend.pid

# Wait for frontend to start
sleep 5

# Check if both servers are running
echo -e "\n${BLUE}[3/3]${NC} Verifying Services..."
if kill -0 $BACKEND_PID 2>/dev/null && kill -0 $FRONTEND_PID 2>/dev/null; then
  echo -e "${GREEN}✓ Both servers started successfully!${NC}"
else
  echo -e "${RED}✗ One or both servers failed to start${NC}"
  exit 1
fi

# Display summary
echo -e "\n${BLUE}========================================${NC}"
echo -e "${GREEN}✓ Survey AI is Running!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${BLUE}📊 Frontend:${NC} ${GREEN}http://localhost:5173${NC}"
echo -e "${BLUE}💾 Backend:${NC}  ${GREEN}http://localhost:8002${NC}"
echo -e "${BLUE}📚 API Docs:${NC} ${GREEN}http://localhost:8002/docs${NC}"
echo ""
echo -e "${YELLOW}To stop servers:${NC}"
echo "  • Press Ctrl+C to stop all services"
echo "  • Or run: ./stop.sh"
echo ""
echo -e "${YELLOW}Demo Credentials:${NC}"
echo "  Email: ${GREEN}demo@survey-ai.com${NC}"
echo "  Password: (any password)"
echo ""
echo -e "${BLUE}========================================${NC}"

# Trap to ensure both processes are killed on script exit
trap "kill_servers" EXIT INT

kill_servers() {
  echo -e "\n${YELLOW}Shutting down servers...${NC}"
  kill $BACKEND_PID 2>/dev/null || true
  kill $FRONTEND_PID 2>/dev/null || true
  echo -e "${GREEN}✓ Servers stopped${NC}"
}

# Keep the script running
wait
