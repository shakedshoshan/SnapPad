# SnapPad Docker Setup 🐳

This guide explains how to run SnapPad in a Docker container with full GUI support, making it easy to run and share across different platforms.

## 📋 Prerequisites

### Required Software
- **Docker Desktop** - [Download here](https://www.docker.com/products/docker-desktop)
- **Docker Compose** - Usually included with Docker Desktop
- **X11 Server** - For GUI support (platform-specific)

### Platform-Specific Requirements

#### 🐧 Linux
- X11 server (usually pre-installed)
- No additional software needed

#### 🍎 macOS
- **XQuartz** - X11 server for macOS
  ```bash
  brew install --cask xquartz
  ```
  Or download from: https://www.xquartz.org/

#### 🪟 Windows
- **VcXsrv** (recommended) - Download from: https://sourceforge.net/projects/vcxsrv/
- **Xming** (alternative) - Download from: https://sourceforge.net/projects/xming/

## 🚀 Quick Start

### Method 1: Using Runner Scripts (Recommended)

#### Linux/macOS
```bash
# Make script executable (Linux/macOS only)
chmod +x run-docker.sh

# Build and run SnapPad
./run-docker.sh start

# View logs
./run-docker.sh logs

# Stop container
./run-docker.sh stop
```

#### Windows
```cmd
# Build and run SnapPad
run-docker.bat start

# View logs
run-docker.bat logs

# Stop container
run-docker.bat stop
```

### Method 2: Manual Docker Commands

```bash
# Build the image
docker build -t snappad:latest .

# Run with Docker Compose
docker-compose up -d

# View logs
docker logs snappad

# Stop container
docker-compose down
```

## 🖥️ X11 Server Setup

### Linux Setup
X11 is usually pre-installed. Just allow Docker to connect:
```bash
xhost +local:docker
```

### macOS Setup
1. Install XQuartz:
   ```bash
   brew install --cask xquartz
   ```
2. Start XQuartz:
   ```bash
   open -a XQuartz
   ```
3. Allow connections:
   ```bash
   xhost +localhost
   ```

### Windows Setup
1. **Download and install VcXsrv**:
   - Download from: https://sourceforge.net/projects/vcxsrv/
   - Run the installer with default settings

2. **Configure VcXsrv**:
   - Start XLaunch from the Start menu
   - Choose "Multiple windows"
   - Display number: 0
   - **Important**: Check "Disable access control"
   - **Important**: Check "Public networks"

3. **Start VcXsrv**:
   - The X server should now be running in your system tray

## 🐳 Docker Configuration

### Dockerfile Features
- **Base Image**: Python 3.11 slim
- **GUI Support**: Full Qt6 and X11 libraries
- **Cross-Platform**: Uses Docker-specific requirements (no Windows dependencies)
- **Security**: Non-root user execution
- **Health Checks**: Automatic application monitoring
- **Persistent Data**: Volume mounting for data persistence

### Docker Compose Features
- **X11 Forwarding**: Automatic display forwarding
- **Volume Mounts**: Persistent data storage
- **Network Access**: Host network mode for full functionality
- **Device Access**: Input device access for hotkeys
- **Auto-restart**: Container restarts on failure

## 📁 Data Persistence

Your SnapPad data is stored in:
- **Host Directory**: `./data/` (created automatically)
- **Container Path**: `/app/data/`
- **Database**: `./data/snappad.db`

This ensures your notes and settings persist between container restarts.

## 📦 Dependencies

SnapPad uses different requirement files for different platforms:

- **`requirements.txt`**: Native Windows installation (includes pywin32)
- **`requirements-docker.txt`**: Docker/Linux installation (excludes Windows-specific packages)

The Docker build automatically uses `requirements-docker.txt` to avoid platform-specific dependency issues.

## 🎮 Usage

### Available Commands

#### Runner Script Commands
```bash
# Build and run (default)
./run-docker.sh start

# Build only
./run-docker.sh build

# Run only (assumes image exists)
./run-docker.sh run

# Show logs
./run-docker.sh logs

# Stop container
./run-docker.sh stop

# Show help
./run-docker.sh help
```

#### Manual Docker Commands
```bash
# Build image
docker build -t snappad:latest .

# Run container
docker-compose up -d

# Stop container
docker-compose down

# View logs
docker logs snappad

# Access container shell
docker exec -it snappad bash

# Remove container and image
docker-compose down --rmi all
```

### Application Features in Docker
- ✅ **Full GUI**: Complete PyQt6 interface
- ✅ **Clipboard Access**: Cross-platform clipboard integration
- ✅ **Global Hotkeys**: System-wide keyboard shortcuts
- ✅ **System Tray**: Minimizes to system tray
- ✅ **Persistent Data**: Notes saved between sessions
- ✅ **Auto-restart**: Container restarts on failure

## 🛠️ Troubleshooting

### Common Issues

#### GUI Not Showing
1. **Check X11 Server**: Ensure X11 server is running
2. **Check DISPLAY**: Verify DISPLAY variable is set correctly
3. **Check Permissions**: Run `xhost +local:docker` (Linux) or `xhost +localhost` (macOS)

#### Container Won't Start
1. **Check Docker**: Ensure Docker Desktop is running
2. **Check Ports**: Ensure no conflicting applications
3. **Check Logs**: Run `docker logs snappad` for error details

#### Hotkeys Not Working
1. **Check Privileges**: Container needs access to input devices
2. **Check Host System**: Verify hotkeys work on host system
3. **Check Permissions**: Ensure container has proper device access

### Platform-Specific Issues

#### Linux
- **Permission Denied**: Run `xhost +local:docker`
- **Display Not Found**: Set `export DISPLAY=:0`

#### macOS
- **XQuartz Not Found**: Install with `brew install --cask xquartz`
- **Connection Refused**: Allow connections with `xhost +localhost`

#### Windows
- **VcXsrv Not Working**: 
  - Ensure "Disable access control" is checked
  - Ensure "Public networks" is allowed
  - Restart VcXsrv if needed
- **pywin32 Error**: Docker uses `requirements-docker.txt` which excludes Windows-specific packages

### Debug Mode
To run in debug mode with verbose output:
```bash
# Set debug environment
export SNAPPAD_DEBUG=1

# Run with debug logging
docker-compose up
```

## 🔧 Advanced Configuration

### Custom Environment Variables
```yaml
# In docker-compose.yml
environment:
  - DISPLAY=${DISPLAY}
  - SNAPPAD_DEBUG=1
  - SNAPPAD_CONFIG_PATH=/app/data/config.py
```

### Custom Volume Mounts
```yaml
# In docker-compose.yml
volumes:
  - ./data:/app/data
  - ./custom-config:/app/config
```

### Network Configuration
```yaml
# Use bridge network instead of host
networks:
  - snappad-network
```

## 📦 Building and Sharing

### Building for Distribution
```bash
# Build optimized image
docker build -t snappad:latest --no-cache .

# Tag for registry
docker tag snappad:latest your-registry/snappad:latest

# Push to registry
docker push your-registry/snappad:latest
```

### Sharing with Others
1. **Share the entire project folder**
2. **Recipient runs**: `./run-docker.sh start`
3. **Everything is automatically set up**

## 🚀 Docker Hub Distribution

### Pulling from Docker Hub
```bash
# Pull pre-built image
docker pull snappad/snappad:latest

# Run directly
docker run -it --rm \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v $(pwd)/data:/app/data \
  snappad/snappad:latest
```

### Building Multi-Architecture Images
```bash
# Build for multiple platforms
docker buildx build --platform linux/amd64,linux/arm64 -t snappad:latest .
```

## 📄 License

This Docker setup is part of the SnapPad project and follows the same MIT License.

## 🤝 Contributing

Contributions to improve the Docker setup are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Test your changes across platforms
4. Submit a pull request

## 📞 Support

If you encounter issues with the Docker setup:
1. Check this documentation
2. Review the troubleshooting section
3. Check existing GitHub issues
4. Create a new issue with:
   - Your operating system
   - Docker version
   - Error messages
   - Steps to reproduce 