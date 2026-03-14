#!/bin/bash

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Movie Watchlist Backend Starter ===${NC}\n"

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

# Start backend
echo -e "${GREEN}Starting backend (FastAPI)...${NC}\n"
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
