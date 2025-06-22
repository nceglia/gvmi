#!/bin/bash
# Automated GVMI build and installation script

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project paths
PROJECT_DIR="/Users/ceglian/Codebase/GitHub/gvmi"
PYTHON_PATH="/Users/ceglian/miniforge3/envs/ml/bin/python"
GVMI_SYMLINK="$HOME/.local/bin/gvmi"

echo -e "${BLUE}🔧 Building GVMI (GeneVector Mutual Information)...${NC}"

# Change to project directory
cd "$PROJECT_DIR" || {
    echo -e "${RED}❌ Error: Could not change to project directory: $PROJECT_DIR${NC}"
    exit 1
}

echo -e "${YELLOW}📁 Working directory: $(pwd)${NC}"

# Clean previous build
echo -e "${YELLOW}🧹 Cleaning previous build...${NC}"
if command -v cargo >/dev/null 2>&1; then
    cargo clean
    echo "   ✓ Cargo clean completed"
else
    echo -e "${RED}   ⚠️  Warning: cargo not found, skipping clean${NC}"
fi

# Check Python environment
echo -e "${YELLOW}🐍 Checking Python environment...${NC}"
if [ ! -f "$PYTHON_PATH" ]; then
    echo -e "${RED}❌ Error: Python not found at $PYTHON_PATH${NC}"
    exit 1
fi

echo "   ✓ Python found: $PYTHON_PATH"

# Check maturin availability
echo -e "${YELLOW}📦 Checking maturin...${NC}"
if ! "$PYTHON_PATH" -m maturin --version >/dev/null 2>&1; then
    echo "   Installing maturin..."
    "$PYTHON_PATH" -m pip install maturin
fi
echo "   ✓ Maturin available"

# Build the Rust extension
echo -e "${YELLOW}🦀 Building Rust extension...${NC}"
"$PYTHON_PATH" -m maturin develop --release

if [ $? -eq 0 ]; then
    echo "   ✓ Rust extension built successfully"
else
    echo -e "${RED}❌ Error: Failed to build Rust extension${NC}"
    exit 1
fi

# Update symlink
echo -e "${YELLOW}🔗 Updating symlink...${NC}"
ln -sf "$PROJECT_DIR/gvmi" "$GVMI_SYMLINK"

if [ -L "$GVMI_SYMLINK" ]; then
    echo "   ✓ Symlink updated: $GVMI_SYMLINK -> $PROJECT_DIR/gvmi"
else
    echo -e "${RED}❌ Error: Failed to create symlink${NC}"
    exit 1
fi

# Make gvmi executable
chmod +x "$PROJECT_DIR/gvmi"

# Test installation
echo -e "${YELLOW}✅ Testing installation...${NC}"

# Test 1: Check if gvmi is in PATH
if command -v gvmi >/dev/null 2>&1; then
    echo "   ✓ gvmi is available in PATH"
else
    echo -e "${RED}   ❌ gvmi not found in PATH${NC}"
    exit 1
fi

# Test 2: Run help command
if gvmi --help >/dev/null 2>&1; then
    echo "   ✓ gvmi help command works"
else
    echo -e "${RED}   ❌ gvmi help command failed${NC}"
    exit 1
fi

# Test 3: Check Python module import
if "$PYTHON_PATH" -c "import gvmi; print('✓ gvmi module imported successfully')" 2>/dev/null; then
    echo "   ✓ Python module imports correctly"
else
    echo -e "${RED}   ❌ Python module import failed${NC}"
    exit 1
fi

# Success message
echo ""
echo -e "${GREEN}🎉 GVMI updated successfully!${NC}"
echo ""
echo "You can now use:"
echo "  gvmi --help                    # Show help"
echo "  gvmi input.h5ad -o output.pkl # Process h5ad files"
echo ""

# Show version info if available
echo "Installation details:"
echo "  Script location: $PROJECT_DIR/gvmi"
echo "  Symlink location: $GVMI_SYMLINK"
echo "  Python environment: $PYTHON_PATH"

# Optional: Show gvmi location
GVMI_LOCATION=$(which gvmi 2>/dev/null)
if [ -n "$GVMI_LOCATION" ]; then
    echo "  Command resolves to: $GVMI_LOCATION"
fi
