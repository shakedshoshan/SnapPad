# SnapPad Docker Image
# This Dockerfile creates a containerized version of SnapPad with GUI support

FROM python:3.11-slim

# Set environment variables for GUI applications
ENV DISPLAY=:0
ENV QT_X11_NO_MITSHM=1
ENV XDG_RUNTIME_DIR=/tmp/runtime-root

# Install system dependencies for GUI applications
RUN apt-get update && apt-get install -y \
    # Qt6 and GUI dependencies
    libqt6core6 \
    libqt6gui6 \
    libqt6widgets6 \
    qt6-qpa-plugins \
    libxkbcommon-x11-0 \
    libxkbcommon0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-xinerama0 \
    libxcb-xfixes0 \
    libxcb-shape0 \
    libxcb-cursor0 \
    # X11 and display dependencies
    libx11-6 \
    libxext6 \
    libxrender1 \
    libxi6 \
    libxtst6 \
    # Additional system tools
    xvfb \
    x11-utils \
    dbus-x11 \
    # Clipboard and system integration
    xclip \
    xsel \
    # Fonts for better GUI rendering
    fonts-dejavu-core \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Create application directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements-docker.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-docker.txt

# Copy application files
COPY . .

# Create runtime directory
RUN mkdir -p /tmp/runtime-root && chmod 700 /tmp/runtime-root

# Create a non-root user for security
RUN groupadd -r snappad && useradd -r -g snappad snappad

# Set up volume for persistent data
VOLUME ["/app/data"]

# Create data directory and set permissions
RUN mkdir -p /app/data && chown -R snappad:snappad /app/data

# Switch to non-root user
USER snappad

# Expose display (not really needed for X11 forwarding but good practice)
EXPOSE 6000

# Health check to verify the application can start
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import main; print('SnapPad ready')" || exit 1

# Default command
CMD ["python", "main.py"] 