#!/bin/bash

# ERA Robot Arm Systemd Service Installer
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
SERVICE_TEMPLATE="$SCRIPT_DIR/era-robot-arm.service"
SYSTEMD_DIR="/etc/systemd/system"
SERVICE_NAME="era-robot-arm.service"

# Get current user and group information
CURRENT_USER=$(id -un)
CURRENT_GROUP=$(id -gn)

echo -e "${GREEN}ERA Robot Arm Service Installer${NC}"
echo "================================"

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}Error: This script should not be run as root${NC}"
   echo "Please run without sudo. The script will prompt for sudo when needed."
   exit 1
fi

# Check if service template exists
if [[ ! -f "$SERVICE_TEMPLATE" ]]; then
    echo -e "${RED}Error: Service template not found at $SERVICE_TEMPLATE${NC}"
    exit 1
fi

# Check required files
REQUIRED_FILES=("main.py" "public/index.html" "pyproject.toml")
for file in "${REQUIRED_FILES[@]}"; do
    if [[ ! -f "$PROJECT_DIR/$file" ]]; then
        echo -e "${RED}Error: Required file not found: $PROJECT_DIR/$file${NC}"
        exit 1
    fi
done

echo -e "${BLUE}Project directory: $PROJECT_DIR${NC}"
echo -e "${BLUE}Service will be installed to: $SYSTEMD_DIR/$SERVICE_NAME${NC}"
echo -e "${BLUE}Service will run as user: $CURRENT_USER (group: $CURRENT_GROUP)${NC}"
echo

# Stop service if it's running
if systemctl is-active --quiet "$SERVICE_NAME" 2>/dev/null; then
    echo -e "${YELLOW}Stopping existing service...${NC}"
    sudo systemctl stop "$SERVICE_NAME"
fi

# Disable service if it's enabled
if systemctl is-enabled --quiet "$SERVICE_NAME" 2>/dev/null; then
    echo -e "${YELLOW}Disabling existing service...${NC}"
    sudo systemctl disable "$SERVICE_NAME"
fi

# Set proper ownership and permissions for project directory
echo -e "${YELLOW}Setting file permissions...${NC}"
sudo chown -R "$CURRENT_USER:$CURRENT_GROUP" "$PROJECT_DIR"
sudo chmod +x "$PROJECT_DIR/main.py"

# Install uv if not already installed
UV_PATH="/home/$CURRENT_USER/.local/bin/uv"
if [[ ! -f "$UV_PATH" ]]; then
    echo -e "${YELLOW}Installing uv package manager...${NC}"
    sudo -u "$CURRENT_USER" bash -c "curl -LsSf https://astral.sh/uv/install.sh | sh"
    
    # Verify installation
    if [[ ! -f "$UV_PATH" ]]; then
        echo -e "${RED}Error: Failed to install uv${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ uv installed successfully${NC}"
else
    echo -e "${GREEN}✓ uv already installed${NC}"
fi

# Install Python dependencies using uv
echo -e "${YELLOW}Installing Python dependencies with uv...${NC}"
sudo -u "$CURRENT_USER" bash -c "cd '$PROJECT_DIR' && '$UV_PATH' sync"

# Generate systemd service file from template
echo -e "${YELLOW}Generating systemd service file...${NC}"
TEMP_SERVICE=$(mktemp)
sed -e "s|{{USER}}|$CURRENT_USER|g" -e "s|{{GROUP}}|$CURRENT_GROUP|g" -e "s|{{PROJECT_DIR}}|$PROJECT_DIR|g" "$SERVICE_TEMPLATE" > "$TEMP_SERVICE"

# Install service file
echo -e "${YELLOW}Installing systemd service file...${NC}"
sudo cp "$TEMP_SERVICE" "$SYSTEMD_DIR/$SERVICE_NAME"
rm "$TEMP_SERVICE"

# Set proper permissions on service file
sudo chmod 644 "$SYSTEMD_DIR/$SERVICE_NAME"

# Reload systemd
echo -e "${YELLOW}Reloading systemd daemon...${NC}"
sudo systemctl daemon-reload

# Enable service
echo -e "${YELLOW}Enabling service to start on boot...${NC}"
sudo systemctl enable "$SERVICE_NAME"

# Start service
echo -e "${YELLOW}Starting service...${NC}"
sudo systemctl start "$SERVICE_NAME"

# Check status
sleep 3
if systemctl is-active --quiet "$SERVICE_NAME"; then
    echo -e "${GREEN}✓ ERA Robot Arm service installed and started successfully!${NC}"
    echo
    echo -e "${GREEN}Installation Summary:${NC}"
    echo "  • Using project directory: $PROJECT_DIR"
    echo "  • uv package manager installed and dependencies synced"
    echo "  • Service file installed to: $SYSTEMD_DIR/$SERVICE_NAME"
    echo "  • Service enabled for automatic startup"
    echo "  • Service is currently running"
    echo
    echo "Service status:"
    sudo systemctl status "$SERVICE_NAME" --no-pager -l
    echo
    echo -e "${BLUE}Useful commands:${NC}"
    echo "  Check status:    sudo systemctl status $SERVICE_NAME"
    echo "  View logs:       sudo journalctl -u $SERVICE_NAME -f"
    echo "  Stop service:    sudo systemctl stop $SERVICE_NAME"
    echo "  Start service:   sudo systemctl start $SERVICE_NAME"
    echo "  Restart service: sudo systemctl restart $SERVICE_NAME"
    echo "  Disable service: sudo systemctl disable $SERVICE_NAME"
    echo
    echo -e "${GREEN}The robot arm web interface should now be available at: http://localhost:5000${NC}"
else
    echo -e "${RED}✗ Service failed to start${NC}"
    echo "Check the logs with: sudo journalctl -u $SERVICE_NAME -f"
    echo "Project directory: $PROJECT_DIR"
    exit 1
fi