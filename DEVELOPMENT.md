# Development Guide - Virtual Environment

This guide explains how to set up and work with QuickSave & Notes using Python virtual environments.

## 🚀 **Quick Start Methods**

### **Method 1: Automated Setup (Recommended)**
**For Command Prompt:**
```bash
# Double-click this file
setup_venv.bat
```

**For PowerShell:**
```powershell
# Right-click and "Run with PowerShell"
setup_venv.ps1
```

### **Method 2: Manual Setup**

#### **Step 1: Create Virtual Environment**
```bash
# Navigate to project directory
cd C:\Users\shake\Desktop\Builds\SnapPad

# Create virtual environment
python -m venv quicksave_env
```

#### **Step 2: Activate Virtual Environment**
**Command Prompt:**
```bash
quicksave_env\Scripts\activate
```

**PowerShell:**
```powershell
quicksave_env\Scripts\Activate.ps1
```

#### **Step 3: Install Dependencies**
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Install project dependencies
pip install -r requirements.txt
```

#### **Step 4: Run the Application**
```bash
python main.py
```

## 🔧 **Development Workflow**

### **Daily Development Routine**
1. **Activate environment**:
   ```bash
   quicksave_env\Scripts\activate
   ```

2. **Work on your code**:
   ```bash
   # Edit files with your preferred editor
   code .  # VS Code
   # or
   notepad main.py  # Notepad
   ```

3. **Test changes**:
   ```bash
   python test_application.py
   python main.py
   ```

4. **Deactivate when done**:
   ```bash
   deactivate
   ```

### **Adding New Dependencies**
```bash
# Activate environment
quicksave_env\Scripts\activate

# Install new package
pip install package_name

# Update requirements.txt
pip freeze > requirements.txt
```

### **Working with Different Python Versions**
```bash
# Create environment with specific Python version
python3.9 -m venv quicksave_env_39
python3.10 -m venv quicksave_env_310

# Activate specific version
quicksave_env_39\Scripts\activate
```

## 🛠️ **IDE Integration**

### **VS Code Setup**
1. Open project folder in VS Code
2. Press `Ctrl+Shift+P`
3. Type "Python: Select Interpreter"
4. Choose `quicksave_env\Scripts\python.exe`

### **PyCharm Setup**
1. Open project in PyCharm
2. Go to File → Settings → Project → Python Interpreter
3. Add new interpreter → Existing Environment
4. Select `quicksave_env\Scripts\python.exe`

## 📝 **Common Commands**

### **Environment Management**
```bash
# Check if environment is active
echo $VIRTUAL_ENV  # Linux/Mac
echo %VIRTUAL_ENV%  # Windows

# List installed packages
pip list

# Check package versions
pip show package_name

# Create requirements.txt
pip freeze > requirements.txt

# Install from requirements.txt
pip install -r requirements.txt
```

### **Running Tests**
```bash
# Run all tests
python test_application.py

# Run specific test function
python -c "from test_application import test_database; test_database()"

# Run with verbose output
python test_application.py -v
```

### **Debugging**
```bash
# Run with debug mode
python -c "import config; config.DEBUG_MODE = True; exec(open('main.py').read())"

# Run with Python debugger
python -m pdb main.py
```

## 🔍 **Troubleshooting**

### **Common Issues**

#### **1. "Virtual environment not found"**
```bash
# Recreate the environment
python -m venv quicksave_env
quicksave_env\Scripts\activate
pip install -r requirements.txt
```

#### **2. "Permission denied (PowerShell)"**
```powershell
# Run this once
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then retry
.\setup_venv.ps1
```

#### **3. "Module not found"**
```bash
# Make sure environment is activated
quicksave_env\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

#### **4. "Python not found"**
```bash
# Check Python installation
python --version

# Or try
py --version
```

### **Environment Info**
```bash
# Check environment status
pip list
python -c "import sys; print(sys.executable)"
python -c "import sys; print(sys.path)"
```

## 📦 **Project Structure in Virtual Environment**

```
SnapPad/
├── quicksave_env/              # Virtual environment (auto-created)
│   ├── Scripts/
│   │   ├── activate.bat       # Activation script
│   │   ├── python.exe         # Python executable
│   │   └── pip.exe            # Package installer
│   └── Lib/                   # Installed packages
├── main.py                    # Application entry point
├── requirements.txt           # Dependencies
├── setup_venv.bat            # Automated setup (Command Prompt)
├── setup_venv.ps1            # Automated setup (PowerShell)
└── ...other files...
```

## 🎯 **Best Practices**

1. **Always activate** the environment before working
2. **Keep requirements.txt updated** when adding packages
3. **Use meaningful environment names** for different projects
4. **Don't commit** the `quicksave_env/` folder to version control
5. **Test in the environment** before deploying
6. **Document environment setup** for team members

## 🚀 **Production Deployment**

```bash
# Create a clean environment for deployment
python -m venv quicksave_env_prod
quicksave_env_prod\Scripts\activate

# Install only production dependencies
pip install -r requirements.txt

# Test the application
python test_application.py
python main.py
```

---

**Happy coding! 🎉**

For any issues, check the main README.md or run the test suite to diagnose problems. 