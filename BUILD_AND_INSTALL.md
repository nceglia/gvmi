# GVMI Build and Installation Guide

This document provides step-by-step instructions for building and installing gvmi updates.

## Prerequisites

Before building, ensure you have:

1. **Rust toolchain** (cargo, rustc)
2. **Python environment** with required packages
3. **Maturin** for building Python extensions

## Quick Update Steps

For routine updates when you've made changes to the code:

```bash
# Navigate to the project directory
cd /Users/ceglian/Codebase/GitHub/gvmi

# 1. Clean previous build (optional but recommended)
cargo clean

# 2. Build and install the updated Rust library
/Users/ceglian/miniforge3/envs/ml/bin/python -m maturin develop --release

# 3. Test the installation
gvmi --help
```

## Detailed Build Process

### Step 1: Environment Setup

```bash
# Ensure you're in the project directory
cd /Users/ceglian/Codebase/GitHub/gvmi

# Activate the correct Python environment (if needed)
# Note: gvmi uses the hardcoded path in the shebang
source /Users/ceglian/miniforge3/envs/ml/bin/activate  # if using conda
```

### Step 2: Clean Previous Build (Recommended)

```bash
# Remove all build artifacts
cargo clean

# This removes:
# - target/ directory
# - Compiled Rust objects
# - Previous Python wheels
```

### Step 3: Build the Rust Library

```bash
# Build and install the Python extension
/Users/ceglian/miniforge3/envs/ml/bin/python -m maturin develop --release

# What this does:
# - Compiles the Rust code with optimizations (--release)
# - Creates Python bindings via PyO3
# - Installs the gene_mutual_info module
# - Makes it available to the gvmi script
```

### Step 4: Verify CLI Installation

```bash
# Check that gvmi is accessible
which gvmi
# Should show: /Users/ceglian/.local/bin/gvmi

# Test the command
gvmi --help

# Quick functionality test
gvmi /Users/ceglian/Data/h5ads/mye_with_palantir.h5ad -o test.pkl --max-genes 10
rm test.pkl  # cleanup
```

## Troubleshooting

### Common Issues and Solutions

#### 1. `gvmi: command not found`

**Problem**: The gvmi symlink is broken or PATH is not set correctly.

**Solution**:
```bash
# Check if symlink exists
ls -la ~/.local/bin/gvmi

# If missing, recreate the symlink
ln -sf /Users/ceglian/Codebase/GitHub/gvmi/gvmi ~/.local/bin/gvmi

# Ensure ~/.local/bin is in PATH
echo $PATH | grep ".local/bin"

# If not in PATH, add it:
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bash_profile
source ~/.bash_profile
```

#### 2. `ModuleNotFoundError: No module named 'numpy'`

**Problem**: Wrong Python environment or missing dependencies.

**Solution**:
```bash
# Install missing dependencies in the correct environment
/Users/ceglian/miniforge3/envs/ml/bin/python -m pip install numpy anndata

# Or reinstall all dependencies
/Users/ceglian/miniforge3/envs/ml/bin/python -m pip install -r requirements.txt
```

#### 3. `maturin: command not found`

**Problem**: Maturin is not installed in the current environment.

**Solution**:
```bash
# Install maturin
/Users/ceglian/miniforge3/envs/ml/bin/python -m pip install maturin

# Verify installation
/Users/ceglian/miniforge3/envs/ml/bin/python -m maturin --version
```

#### 4. Rust compilation errors

**Problem**: Rust compiler issues or dependency conflicts.

**Solution**:
```bash
# Update Rust toolchain
rustup update

# Clean and rebuild
cargo clean
/Users/ceglian/miniforge3/envs/ml/bin/python -m maturin develop --release
```

#### 5. Permission errors

**Problem**: Insufficient permissions for installation.

**Solution**:
```bash
# Ensure ~/.local/bin directory exists and is writable
mkdir -p ~/.local/bin
chmod 755 ~/.local/bin

# Make gvmi executable
chmod +x /Users/ceglian/Codebase/GitHub/gvmi/gvmi
```

## Advanced Build Options

### Development Build (Faster, Less Optimized)

For development/testing, you can use a debug build:

```bash
# Faster compilation, larger binaries, includes debug symbols
/Users/ceglian/miniforge3/envs/ml/bin/python -m maturin develop
```

### Production Build with Specific Features

```bash
# Build with specific Cargo features
/Users/ceglian/miniforge3/envs/ml/bin/python -m maturin develop --release --features "pyo3/extension-module"
```

### Cross-Platform Build (if needed)

```bash
# For building wheels for distribution
/Users/ceglian/miniforge3/envs/ml/bin/python -m maturin build --release

# Built wheels will be in target/wheels/
ls target/wheels/
```

## Automated Build Script

You can create a simple build script for convenience:

```bash
# Create update_gvmi.sh
cat > update_gvmi.sh << 'EOF'
#!/bin/bash
set -e

echo "🔧 Building GVMI..."
cd /Users/ceglian/Codebase/GitHub/gvmi

echo "🧹 Cleaning previous build..."
cargo clean

echo "🦀 Building Rust extension..."
/Users/ceglian/miniforge3/envs/ml/bin/python -m maturin develop --release

echo "🔗 Updating symlink..."
ln -sf /Users/ceglian/Codebase/GitHub/gvmi/gvmi ~/.local/bin/gvmi

echo "✅ Testing installation..."
gvmi --help > /dev/null && echo "✅ GVMI updated successfully!" || echo "❌ GVMI update failed!"
EOF

chmod +x update_gvmi.sh
```

Then run:
```bash
./update_gvmi.sh
```

## Build Dependencies

### Required System Packages

- **Rust**: Latest stable (via rustup)
- **Python 3.8+**: With development headers
- **C compiler**: For compiling native extensions

### Required Python Packages

```bash
# Core build dependencies
pip install maturin

# Runtime dependencies
pip install numpy>=1.20.0 anndata>=0.8.0

# Development dependencies (optional)
pip install pytest black mypy
```

## Version Management

### Updating Version Numbers

When releasing a new version:

1. **Update Cargo.toml**:
   ```toml
   [package]
   name = "gvmi"
   version = "0.2.0"  # Update this
   ```

2. **Update pyproject.toml** (if using dynamic versioning):
   ```toml
   dynamic = ["version"]
   ```

3. **Rebuild**:
   ```bash
   cargo clean
   /Users/ceglian/miniforge3/envs/ml/bin/python -m maturin develop --release
   ```

## Performance Notes

### Build Time Optimization

- **Use `--release` for production**: Much faster execution, longer build time
- **Use debug builds for development**: Faster builds, slower execution
- **Clean builds when changing dependencies**: Ensures consistency

### Runtime Optimization

- The `--release` flag enables important optimizations:
  - Loop unrolling
  - Dead code elimination
  - Aggressive inlining
  - SIMD vectorization

## Summary

**Quick update workflow**:
1. `cd /Users/ceglian/Codebase/GitHub/gvmi`
2. `cargo clean` (optional)
3. `/Users/ceglian/miniforge3/envs/ml/bin/python -m maturin develop --release`
4. `gvmi --help` (verify)

This process rebuilds the Rust extension and makes it available to the gvmi CLI without requiring system-wide installation or root privileges.
