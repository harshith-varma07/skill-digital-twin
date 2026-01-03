#!/bin/bash

# Health check script for Skill Digital Twin Docker services
# This script checks if all services are healthy and responding

set -e

echo "🏥 Skill Digital Twin Health Check"
echo "===================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if a service is running
check_service() {
    local service=$1
    local status=$(docker compose ps --format json | jq -r ".[] | select(.Service==\"$service\") | .State")
    
    if [ "$status" = "running" ]; then
        echo -e "${GREEN}✓${NC} $service is running"
        return 0
    else
        echo -e "${RED}✗${NC} $service is not running (status: $status)"
        return 1
    fi
}

# Function to check HTTP endpoint
check_endpoint() {
    local name=$1
    local url=$2
    local timeout=${3:-5}
    
    if curl -sf --max-time "$timeout" "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $name is responding at $url"
        return 0
    else
        echo -e "${RED}✗${NC} $name is not responding at $url"
        return 1
    fi
}

# Check if docker compose is available
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗${NC} Docker is not installed or not in PATH"
    exit 1
fi

# Check Docker services
echo "Checking Docker Services:"
echo "-------------------------"
check_service "postgres" || true
check_service "redis" || true
check_service "backend" || true
check_service "frontend" || true
echo ""

# Check endpoints
echo "Checking Endpoints:"
echo "-------------------"
check_endpoint "Backend API" "http://localhost:8000/" 10 || true
check_endpoint "Backend Docs" "http://localhost:8000/docs" 10 || true
check_endpoint "Frontend" "http://localhost:80/" 10 || true
echo ""

# Check database connectivity
echo "Checking Database:"
echo "------------------"
if docker compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} PostgreSQL is ready"
else
    echo -e "${RED}✗${NC} PostgreSQL is not ready"
fi
echo ""

# Check Redis connectivity
echo "Checking Cache:"
echo "---------------"
if docker compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Redis is responding"
else
    echo -e "${RED}✗${NC} Redis is not responding"
fi
echo ""

echo "===================================="
echo "Health check complete!"
