#!/bin/bash

# EquityScope v2-Optimized Development Stop Script

echo "🛑 Stopping EquityScope v2-Optimized Development Environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to kill process by PID file
kill_by_pid_file() {
    local pid_file=$1
    local service_name=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 $pid 2>/dev/null; then
            kill $pid
            echo -e "${GREEN}✅ $service_name stopped (PID: $pid)${NC}"
        else
            echo -e "${YELLOW}⚠️  $service_name was not running${NC}"
        fi
        rm "$pid_file"
    else
        echo -e "${YELLOW}⚠️  No $service_name PID file found${NC}"
    fi
}

# Stop services by PID files
kill_by_pid_file "backend_pid.txt" "Backend server"
kill_by_pid_file "frontend_pid.txt" "Frontend server"

# Kill any remaining processes on our ports
echo -e "${YELLOW}🔍 Checking for remaining processes...${NC}"

# Kill processes on port 8000 (backend)
if lsof -ti:8000 >/dev/null 2>&1; then
    echo -e "${YELLOW}🔧 Killing remaining processes on port 8000...${NC}"
    lsof -ti:8000 | xargs kill -9 2>/dev/null
fi

# Kill processes on port 3000 (frontend) 
if lsof -ti:3000 >/dev/null 2>&1; then
    echo -e "${YELLOW}🔧 Killing remaining processes on port 3000...${NC}"
    lsof -ti:3000 | xargs kill -9 2>/dev/null
fi

# Kill any Python processes that might be our backend
pkill -f "start_server.py" 2>/dev/null

# Kill any npm processes that might be our frontend
pkill -f "react-scripts start" 2>/dev/null

echo -e "${GREEN}✅ All EquityScope development servers stopped${NC}"
echo -e "${YELLOW}💡 To restart, run: ./start_development.sh${NC}"