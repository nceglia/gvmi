#!/bin/bash
# Installation script for gvmi (Gene Vector Mutual Information)

set -e

# Get the absolute path of the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GVMI_PATH="$SCRIPT_DIR/gvmi"

# Check if gvmi exists
if [ ! -f "$GVMI_PATH" ]; then
    echo "Error: gvmi script not found at $GVMI_PATH"
    exit 1
fi

# Make sure gvmi is executable
chmod +x "$GVMI_PATH"

# Determine the user's shell and profile file
if [ -n "$ZSH_VERSION" ]; then
    SHELL_NAME="zsh"
    PROFILE_FILE="$HOME/.zshrc"
elif [ -n "$BASH_VERSION" ]; then
    SHELL_NAME="bash"
    if [ -f "$HOME/.bash_profile" ]; then
        PROFILE_FILE="$HOME/.bash_profile"
    else
        PROFILE_FILE="$HOME/.bashrc"
    fi
else
    SHELL_NAME="unknown"
    PROFILE_FILE="$HOME/.profile"
fi

echo "Detected shell: $SHELL_NAME"
echo "Profile file: $PROFILE_FILE"

# Create local bin directory if it doesn't exist
LOCAL_BIN="$HOME/.local/bin"
mkdir -p "$LOCAL_BIN"

# Create symlink to gvmi in local bin
GVMI_SYMLINK="$LOCAL_BIN/gvmi"
if [ -L "$GVMI_SYMLINK" ]; then
    echo "Removing existing gvmi symlink..."
    rm "$GVMI_SYMLINK"
fi

echo "Creating symlink: $GVMI_SYMLINK -> $GVMI_PATH"
ln -s "$GVMI_PATH" "$GVMI_SYMLINK"

# Check if ~/.local/bin is in PATH
if [[ ":$PATH:" != *":$LOCAL_BIN:"* ]]; then
    echo "Adding $LOCAL_BIN to PATH in $PROFILE_FILE"
    
    # Add to PATH in profile file
    echo "" >> "$PROFILE_FILE"
    echo "# Added by gvmi installer" >> "$PROFILE_FILE"
    echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> "$PROFILE_FILE"
    
    # Also export for current session
    export PATH="$LOCAL_BIN:$PATH"
    
    echo "✅ Added $LOCAL_BIN to PATH"
else
    echo "✅ $LOCAL_BIN already in PATH"
fi

# Test the installation
echo ""
echo "Testing installation..."

if command -v gvmi >/dev/null 2>&1; then
    echo "✅ gvmi is now available in your PATH"
    echo ""
    echo "You can now run: gvmi --help"
    echo ""
    echo "For the changes to take effect in new terminal sessions, either:"
    echo "1. Restart your terminal"
    echo "2. Run: source $PROFILE_FILE"
else
    echo "⚠️  gvmi not found in PATH. You may need to restart your terminal or run:"
    echo "   source $PROFILE_FILE"
fi

echo ""
echo "Installation complete!"
echo ""
echo "Quick start:"
echo "  gvmi input.h5ad -o results.pkl --max-genes 100"
