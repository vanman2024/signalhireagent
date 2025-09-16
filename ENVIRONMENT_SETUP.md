# Environment Setup Guide

## 🐍 **Python Virtual Environment Standard**

This project uses **`.venv`** as the standard virtual environment name.

### **Why `.venv`?**
- **Python community standard** (PEP 582 recommendation)
- **Hidden directory** (cleaner file listing)
- **IDE recognition** (VS Code, PyCharm auto-detect `.venv`)
- **Consistent across projects**

### **Setup Methods**

#### **Automatic (Recommended)**
```bash
./scripts/ops setup
# Creates .venv automatically if missing
```

#### **Manual Setup**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## 🪟 **WSL Environment**

### **Common Issues & Solutions**

#### **Windows Paths in WSL**
```bash
# Problem: Windows Python in WSL PATH
./scripts/ops env doctor  # Diagnoses the issue

# Solution: Use WSL-native Python
sudo apt install python3-venv python3-pip
```

#### **Environment Variable Loading**
```bash
# Problem: .env not loading in WSL
./scripts/ops env doctor  # Checks .env accessibility

# Solution: Ensure python-dotenv is installed
pip install python-dotenv
```

## 🔄 **Migration from `venv` to `.venv`**

If you have an old `venv` directory:

```bash
# 1. Save current packages (if venv works)
source venv/bin/activate
pip freeze > old_requirements.txt
deactivate

# 2. Remove old venv
rm -rf venv

# 3. Create new .venv
./scripts/ops setup

# 4. Restore packages if needed
source .venv/bin/activate
pip install -r old_requirements.txt
```

## ✅ **Verification**

Check your setup:
```bash
./scripts/ops env doctor  # Full environment diagnostics
./scripts/ops status      # Show current environment status
```

Should show:
- `✅ .venv virtual environment`
- `✅ .env file loadable`
- `✅ All dependencies available`