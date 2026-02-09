#!/bin/bash

# FerPS Anonymous Bot - Docker Manual Build & Run Script
# Use if you prefer manual Docker commands over docker-compose

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMAGE_NAME="ferps-anon-bot"
CONTAINER_NAME="ferps-anon"
DATA_DIR="$SCRIPT_DIR/data"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

usage() {
    echo "FerPS Anonymous Bot - Docker Manager"
    echo ""
    echo "Usage: $0 {build|run|stop|logs|shell|clean}"
    echo ""
    echo "Commands:"
    echo "  build     - Build Docker image"
    echo "  run       - Build and run bot"
    echo "  stop      - Stop running bot"
    echo "  logs      - View bot logs"
    echo "  shell     - Open shell in running container"
    echo "  clean     - Stop and remove container/image"
    exit 1
}

build_image() {
    echo -e "${BLUE}🔨 Building Docker image...${NC}"
    docker build -t "$IMAGE_NAME" "$SCRIPT_DIR"
    echo -e "${GREEN}✅ Image built: $IMAGE_NAME${NC}"
}

run_bot() {
    # Check if image exists
    if ! docker image inspect "$IMAGE_NAME" > /dev/null 2>&1; then
        echo -e "${BLUE}Image not found, building...${NC}"
        build_image
    fi
    
    # Create data directory
    mkdir -p "$DATA_DIR"
    
    # Check if container already running
    if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        echo -e "${RED}Container already exists. Removing...${NC}"
        docker rm -f "$CONTAINER_NAME"
    fi
    
    echo -e "${BLUE}🚀 Running bot...${NC}"
    
    docker run -d \
        --name "$CONTAINER_NAME" \
        --restart unless-stopped \
        -e DO_NOT_EDIT_BELOW=true \
        --env-file "$SCRIPT_DIR/.env" \
        -v "$DATA_DIR:/data" \
        -p 8080:8080 \
        "$IMAGE_NAME"
    
    echo -e "${GREEN}✅ Bot started!${NC}"
    echo ""
    echo "Container ID: $(docker ps -q -f name=$CONTAINER_NAME)"
    echo "View logs: docker logs -f $CONTAINER_NAME"
    echo "Stop: docker stop $CONTAINER_NAME"
}

stop_bot() {
    echo -e "${BLUE}⏹️  Stopping bot...${NC}"
    if docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
        docker stop "$CONTAINER_NAME"
        echo -e "${GREEN}✅ Bot stopped${NC}"
    else
        echo "Bot not running"
    fi
}

view_logs() {
    if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        docker logs -f "$CONTAINER_NAME"
    else
        echo -e "${RED}Container not found: $CONTAINER_NAME${NC}"
        exit 1
    fi
}

open_shell() {
    if docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
        docker exec -it "$CONTAINER_NAME" /bin/bash
    else
        echo -e "${RED}Container not running: $CONTAINER_NAME${NC}"
        exit 1
    fi
}

clean_up() {
    echo -e "${RED}⚠️  Cleaning up...${NC}"
    
    # Stop container
    if docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
        echo "Stopping container..."
        docker stop "$CONTAINER_NAME"
    fi
    
    # Remove container
    if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        echo "Removing container..."
        docker rm "$CONTAINER_NAME"
    fi
    
    # Remove image
    if docker image inspect "$IMAGE_NAME" > /dev/null 2>&1; then
        echo "Removing image..."
        docker rmi "$IMAGE_NAME"
    fi
    
    echo -e "${GREEN}✅ Cleanup complete${NC}"
}

# Main
if [ $# -eq 0 ]; then
    usage
fi

case "$1" in
    build)
        build_image
        ;;
    run)
        run_bot
        ;;
    stop)
        stop_bot
        ;;
    logs)
        view_logs
        ;;
    shell)
        open_shell
        ;;
    clean)
        clean_up
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        usage
        ;;
esac
