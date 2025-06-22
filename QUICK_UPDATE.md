# GVMI Quick Update Reference

## 🚀 Fastest Update Method

```bash
cd /Users/ceglian/Codebase/GitHub/gvmi
./update_gvmi.sh
```

## 📋 Manual Update Steps

```bash
# 1. Navigate to project
cd /Users/ceglian/Codebase/GitHub/gvmi

# 2. Clean build (optional)
cargo clean

# 3. Build and install
/Users/ceglian/miniforge3/envs/ml/bin/python -m maturin develop --release

# 4. Test
gvmi --help
```

## 🔧 Development Build (Faster)

```bash
# Skip --release for faster development builds
/Users/ceglian/miniforge3/envs/ml/bin/python -m maturin develop
```

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| `gvmi: command not found` | `ln -sf /Users/ceglian/Codebase/GitHub/gvmi/gvmi ~/.local/bin/gvmi` |
| `maturin: command not found` | `/Users/ceglian/miniforge3/envs/ml/bin/python -m pip install maturin` |
| `ModuleNotFoundError` | `/Users/ceglian/miniforge3/envs/ml/bin/python -m pip install numpy anndata` |
| Rust errors | `rustup update && cargo clean` |

## 📁 Important Paths

- **Project**: `/Users/ceglian/Codebase/GitHub/gvmi`
- **Python**: `/Users/ceglian/miniforge3/envs/ml/bin/python`
- **gvmi CLI**: `~/.local/bin/gvmi` → `/Users/ceglian/Codebase/GitHub/gvmi/gvmi`

## ✅ Verification Commands

```bash
which gvmi                    # Check PATH
gvmi --help                   # Test CLI
python -c "import gvmi"  # Test module
```
