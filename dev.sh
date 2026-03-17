#!/bin/bash

# Development startup script with automatic port selection
# This script finds available ports if the default ports are already in use

set -e

# Default ports
DEFAULT_BACKEND_PORT=8000
DEFAULT_FRONTEND_PORT=3000

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if a port is in use
is_port_in_use() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 || \
       netstat -an 2>/dev/null | grep "\.$port " | grep LISTEN >/dev/null || \
       curl -s http://localhost:$port >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is available
    fi
}

# Function to find an available port starting from a base port
find_available_port() {
    local base_port=$1
    local max_attempts=100
    local attempt=0

    while [ $attempt -lt $max_attempts ]; do
        local test_port=$((base_port + attempt))
        if ! is_port_in_use $test_port; then
            echo $test_port
            return 0
        fi
        attempt=$((attempt + 1))
    done

    echo -e "${RED}Error: Could not find an available port starting from $base_port${NC}"
    exit 1
}

# Function to display banner
show_banner() {
    echo -e "${BLUE}╔══════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║   ContentCued Development Environment    ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════╝${NC}"
    echo ""
}

# Main execution
main() {
    show_banner

    # Check backend port
    echo -e "${YELLOW}Checking backend port (default: $DEFAULT_BACKEND_PORT)...${NC}"
    if is_port_in_use $DEFAULT_BACKEND_PORT; then
        BACKEND_PORT=$(find_available_port $DEFAULT_BACKEND_PORT)
        echo -e "${GREEN}✓ Port $DEFAULT_BACKEND_PORT is in use, using port $BACKEND_PORT instead${NC}"
    else
        BACKEND_PORT=$DEFAULT_BACKEND_PORT
        echo -e "${GREEN}✓ Port $BACKEND_PORT is available${NC}"
    fi

    # Check frontend port
    echo -e "${YELLOW}Checking frontend port (default: $DEFAULT_FRONTEND_PORT)...${NC}"
    if is_port_in_use $DEFAULT_FRONTEND_PORT; then
        FRONTEND_PORT=$(find_available_port $DEFAULT_FRONTEND_PORT)
        echo -e "${GREEN}✓ Port $DEFAULT_FRONTEND_PORT is in use, using port $FRONTEND_PORT instead${NC}"
    else
        FRONTEND_PORT=$DEFAULT_FRONTEND_PORT
        echo -e "${GREEN}✓ Port $FRONTEND_PORT is available${NC}"
    fi

    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════${NC}"
    echo -e "${GREEN}Starting services with the following ports:${NC}"
    echo -e "  • Backend:  ${GREEN}http://localhost:$BACKEND_PORT${NC}"
    echo -e "  • Frontend: ${GREEN}http://localhost:$FRONTEND_PORT${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════${NC}"
    echo ""

    # Export environment variables for docker-compose
    export BACKEND_PORT
    export FRONTEND_PORT

    # Check if docker compose is available
    if command -v docker-compose &> /dev/null; then
        DOCKER_COMPOSE="docker-compose"
    else
        DOCKER_COMPOSE="docker compose"
    fi

    # Stop any existing containers
    echo -e "${YELLOW}Stopping existing containers...${NC}"
    $DOCKER_COMPOSE -f docker-compose.dev.yml --env-file .env down 2>/dev/null || true

    # Build and start containers with port overrides
    echo -e "${YELLOW}Building and starting containers...${NC}"
    BACKEND_PORT=$BACKEND_PORT FRONTEND_PORT=$FRONTEND_PORT \
        $DOCKER_COMPOSE -f docker-compose.dev.yml --env-file .env up --build

    # Cleanup on exit
    trap 'echo -e "${YELLOW}Stopping containers...${NC}"; $DOCKER_COMPOSE -f docker-compose.dev.yml --env-file .env down; exit' INT TERM
}

# Run main function
main "$@"
