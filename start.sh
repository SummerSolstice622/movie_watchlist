#!/bin/bash

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Movie Watchlist App Starter ===${NC}\n"

# Check if backend/requirements.txt exists
if [ ! -f "backend/requirements.txt" ]; then
    echo -e "${RED}Error: backend/requirements.txt not found${NC}"
    exit 1
fi

# Setup Python virtual environment if not exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating Python virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install backend dependencies
echo -e "${YELLOW}Installing backend dependencies...${NC}"
pip install -q -r backend/requirements.txt

# Export PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Start backend in background
echo -e "${GREEN}Starting backend (FastAPI)...${NC}"
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo -e "${GREEN}Backend started with PID: $BACKEND_PID${NC}"
echo -e "${YELLOW}Backend is running at: http://localhost:8000${NC}"
echo -e "${YELLOW}API Docs available at: http://localhost:8000/docs${NC}\n"

# Check if frontend has package.json
if [ -f "frontend/package.json" ]; then
    cd frontend
    
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    npm install 2>&1 | grep -v "^npm" | head -20 || true
    
    echo -e "${GREEN}Starting frontend (Vite)...${NC}"
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    
    sleep 2
    echo -e "${GREEN}Frontend started with PID: $FRONTEND_PID${NC}"
    echo -e "${YELLOW}Frontend is running at: http://localhost:5173${NC}\n"
else
    echo -e "${YELLOW}Note: frontend/package.json not found. Frontend setup skipped.${NC}"
    echo -e "${YELLOW}To set up frontend manually:${NC}"
    echo -e "  cd frontend"
    echo -e "  npm install"
    echo -e "  npm run dev\n"
fi

echo -e "${GREEN}Application started!${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}\n"

# Handle Ctrl+C
trap "kill $BACKEND_PID 2>/dev/null; [ ! -z '$FRONTEND_PID' ] && kill $FRONTEND_PID 2>/dev/null; exit" INT TERM

# Wait for background processes
wait
