#!/bin/bash
# Installation script for Vehicle Tracking System
# Handles externally managed Python environments by creating a virtual environment

echo "========================================================================"
echo "Vehicle Tracking System - Installation Script"
echo "========================================================================"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3.7 or higher first"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "Found Python version: $PYTHON_VERSION"

# Check if we're in an externally managed environment
if python3 -c "import sys; import os; sys.exit(0 if os.path.exists(f'{sys.base_prefix}/lib/python{sys.version_info.major}.{sys.version_info.minor}/EXTERNALLY-MANAGED') else 1)" 2>/dev/null; then
    echo "Detected externally managed Python environment"
    USE_VENV=true
else
    USE_VENV=false
fi

# Check if virtual environment already exists
if [ -d "venv" ]; then
    echo ""
    echo "Virtual environment already exists at ./venv"
    read -p "Do you want to recreate it? (y/N): " RECREATE
    if [[ $RECREATE =~ ^[Yy]$ ]]; then
        echo "Removing existing virtual environment..."
        rm -rf venv
    else
        echo "Using existing virtual environment..."
        USE_VENV=true
    fi
fi

# Create virtual environment if needed or requested
if [ "$USE_VENV" = true ] && [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    
    if [ ! -d "venv" ]; then
        echo "Error: Failed to create virtual environment"
        echo "Make sure python3-venv is installed:"
        echo "  sudo apt install python3-venv"
        exit 1
    fi
    
    echo "✓ Virtual environment created"
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo ""
    echo "Activating virtual environment..."
    source venv/bin/activate
    PYTHON_CMD="venv/bin/python3"
    PIP_CMD="venv/bin/pip3"
    echo "✓ Virtual environment activated"
else
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
fi

# Upgrade pip
echo ""
echo "Upgrading pip..."
if ! $PIP_CMD install --upgrade pip --default-timeout=100; then
    echo "Warning: Failed to upgrade pip, continuing with current version..."
fi

# Install requirements
echo ""
echo "Installing dependencies from requirements.txt..."
echo "This may take a few minutes..."
if ! $PIP_CMD install -r requirements.txt --default-timeout=100; then
    echo ""
    echo "========================================================================"
    echo "ERROR: Failed to install dependencies"
    echo "========================================================================"
    echo ""
    echo "This could be due to:"
    echo "  1. Network connectivity issues - check your internet connection"
    echo "  2. PyPI server timeout - try again later"
    echo "  3. Missing system dependencies - see error messages above"
    echo ""
    echo "To retry installation:"
    if [ -d "venv" ]; then
        echo "  source venv/bin/activate"
        echo "  pip3 install -r requirements.txt"
    else
        echo "  pip3 install -r requirements.txt"
    fi
    echo ""
    echo "For individual package installation, see README.md"
    exit 1
fi

# Verify installation
echo ""
echo "Verifying installation..."
if ! $PYTHON_CMD check_dependencies.py; then
    echo ""
    echo "Warning: Some dependencies may not have installed correctly."
    echo "Please review the error messages above and try installing"
    echo "missing packages individually."
    echo ""
fi

# Create activation script
if [ -d "venv" ]; then
    echo ""
    echo "========================================================================"
    echo "Installation complete!"
    echo "========================================================================"
    echo ""
    echo "A virtual environment has been created at ./venv"
    echo ""
    echo "To use the system, you have two options:"
    echo ""
    echo "Option 1: Activate the virtual environment (recommended):"
    echo "  source venv/bin/activate"
    echo "  python3 main.py"
    echo ""
    echo "Option 2: Use the virtual environment Python directly:"
    echo "  venv/bin/python3 main.py"
    echo ""
    echo "To deactivate the virtual environment later:"
    echo "  deactivate"
    echo ""
else
    echo ""
    echo "========================================================================"
    echo "Installation complete!"
    echo "========================================================================"
    echo ""
    echo "You can now run the system with:"
    echo "  python3 main.py"
    echo ""
fi

# Create a run script for convenience
if [ -d "venv" ]; then
    cat > run.sh << 'EOF'
#!/bin/bash
# Convenience script to run with virtual environment
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"
source venv/bin/activate
python3 "$@"
EOF
    chmod +x run.sh
    echo "Created convenience script: ./run.sh"
    echo "Example usage: ./run.sh main.py start"
    echo ""
fi
