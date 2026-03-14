#!/bin/bash

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Movie Watchlist Frontend Starter ===${NC}\n"

# Check if frontend directory exists
if [ ! -d "frontend" ]; then
    echo -e "${RED}Error: frontend directory not found${NC}"
    exit 1
fi

cd frontend

# Check if package.json exists
if [ ! -f "package.json" ]; then
    echo -e "${RED}Error: frontend/package.json not found${NC}"
    echo -e "${YELLOW}Please initialize the frontend project first${NC}"
    exit 1
fi

# Install dependencies
echo -e "${YELLOW}Installing frontend dependencies...${NC}"
npm install

# Start frontend
echo -e "${GREEN}Starting frontend with Vite...${NC}\n"
npm run dev
