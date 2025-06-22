#!/bin/bash
# Wrapper script for computing mutual information from h5ad files

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Run the gvmi script
"$SCRIPT_DIR/gvmi" "$@"
