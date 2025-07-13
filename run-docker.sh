#!/bin/bash

# SnapPad Docker Runner Script
# This script sets up X11 forwarding and runs SnapPad in Docker

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

# Function to setup X11 forwarding
setup_x11() {
    OS=$(detect_os)
    
    case $OS in
        "linux")
            print_status "Setting up X11 forwarding for Linux..."
            
            # Allow X11 forwarding
            xhost +local:docker || {
                print_warning "Could not run 'xhost +local:docker'. GUI may not work."
                print_warning "Try running: xhost +local:docker"
            }
            
            # Set DISPLAY if not set
            if [ -z "$DISPLAY" ]; then
                export DISPLAY=:0
                print_status "Set DISPLAY to :0"
            fi
            
            # Create data directory
            mkdir -p data
            ;;
            
        "macos")
            print_status "Setting up X11 forwarding for macOS..."
            
            # Check if XQuartz is installed
            if ! command_exists xquartz; then
                print_error "XQuartz is not installed. Please install it first:"
                print_error "brew install --cask xquartz"
                exit 1
            fi
            
            # Check if XQuartz is running
            if ! pgrep -x "Xquartz" > /dev/null; then
                print_status "Starting XQuartz..."
                open -a XQuartz
                sleep 3
            fi
            
            # Allow connections from localhost
            xhost +localhost || {
                print_warning "Could not run 'xhost +localhost'. GUI may not work."
            }
            
            # Set DISPLAY for macOS
            export DISPLAY=host.docker.internal:0
            print_status "Set DISPLAY to host.docker.internal:0"
            
            # Create data directory
            mkdir -p data
            ;;
            
        "windows")
            print_status "Setting up X11 forwarding for Windows..."
            
            # Check if VcXsrv or similar is running
            print_warning "Make sure you have an X11 server running (VcXsrv, Xming, etc.)"
            print_warning "Configure it to allow connections from localhost"
            
            # Set DISPLAY for Windows
            export DISPLAY=host.docker.internal:0
            print_status "Set DISPLAY to host.docker.internal:0"
            
            # Create data directory
            mkdir -p data
            ;;
            
        *)
            print_error "Unsupported operating system: $OS"
            exit 1
            ;;
    esac
}

# Function to build Docker image
build_image() {
    print_status "Building SnapPad Docker image..."
    
    if docker build -t snappad:latest .; then
        print_success "Docker image built successfully"
    else
        print_error "Failed to build Docker image"
        exit 1
    fi
}

# Function to run Docker container
run_container() {
    print_status "Running SnapPad in Docker container..."
    
    # Stop existing container if running
    if docker ps -q -f name=snappad | grep -q .; then
        print_status "Stopping existing SnapPad container..."
        docker stop snappad
        docker rm snappad
    fi
    
    # Run the container
    if docker-compose up -d; then
        print_success "SnapPad container started successfully"
        print_status "Container name: snappad"
        print_status "To view logs: docker logs snappad"
        print_status "To stop: docker-compose down"
    else
        print_error "Failed to start SnapPad container"
        exit 1
    fi
}

# Function to show logs
show_logs() {
    print_status "Showing SnapPad logs..."
    docker logs -f snappad
}

# Function to stop container
stop_container() {
    print_status "Stopping SnapPad container..."
    docker-compose down
    print_success "SnapPad container stopped"
}

# Function to show help
show_help() {
    echo "SnapPad Docker Runner"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  build     Build the Docker image"
    echo "  run       Run SnapPad in Docker container"
    echo "  start     Build and run SnapPad (default)"
    echo "  logs      Show container logs"
    echo "  stop      Stop the container"
    echo "  help      Show this help message"
    echo ""
    echo "Prerequisites:"
    echo "  - Docker and Docker Compose installed"
    echo "  - X11 server running (Linux: built-in, macOS: XQuartz, Windows: VcXsrv/Xming)"
    echo ""
    echo "Examples:"
    echo "  $0 start    # Build and run SnapPad"
    echo "  $0 logs     # View application logs"
    echo "  $0 stop     # Stop the application"
}

# Main function
main() {
    print_status "SnapPad Docker Runner"
    
    # Check if Docker is installed
    if ! command_exists docker; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command_exists docker-compose; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Parse command line arguments
    case "${1:-start}" in
        "build")
            build_image
            ;;
        "run")
            setup_x11
            run_container
            ;;
        "start")
            setup_x11
            build_image
            run_container
            ;;
        "logs")
            show_logs
            ;;
        "stop")
            stop_container
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@" 