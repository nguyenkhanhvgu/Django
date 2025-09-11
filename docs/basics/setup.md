# Django Development Environment Setup

This guide will walk you through setting up a complete Django development environment on Windows, macOS, and Linux.

## Step 1: Install Python

Django requires Python 3.8 or higher. Let's check if Python is already installed and install it if needed.

### Check Current Python Installation

Open your terminal/command prompt and run:

```bash
python --version
# or try
python3 --version
```

If you see `Python 3.8.x` or higher, you're good to go. If not, follow the installation steps below.

### Windows Installation

1. **Download Python**:
   - Visit [python.org/downloads](https://www.python.org/downloads/)
   - Download the latest Python 3.x version
   - **Important**: Check "Add Python to PATH" during installation

2. **Verify Installation**:
   ```cmd
   python --version
   pip --version
   ```

### macOS Installation

**Option 1: Using Homebrew (Recommended)**
```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python
```

**Option 2: Official Installer**
- Download from [python.org/downloads](https://www.python.org/downloads/)
- Run the installer package

### Linux Installation

**Ubuntu/Debian**:
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

**CentOS/RHEL/Fedora**:
```bash
# CentOS/RHEL
sudo yum install python3 python3-pip

# Fedora
sudo dnf install python3 python3-pip
```

## Step 2: Set Up Virtual Environment

Virtual environments isolate your project dependencies, preventing conflicts between different projects.

### Create a Project Directory

```bash
# Create and navigate to your project directory
mkdir django-tutorial
cd django-tutorial
```

### Create Virtual Environment

**Windows**:
```cmd
# Create virtual environment
python -m venv django_env

# Activate virtual environment
django_env\Scripts\activate
```

**macOS/Linux**:
```bash
# Create virtual environment
python3 -m venv django_env

# Activate virtual environment
source django_env/bin/activate
```

### Verify Virtual Environment

When activated, your terminal prompt should show `(django_env)` at the beginning:
```bash
(django_env) $ 
```

To deactivate the virtual environment later, simply run:
```bash
deactivate
```

## Step 3: Install Django

With your virtual environment activated, install Django:

```bash
# Install the latest Django version
pip install django

# Verify installation
django-admin --version
```

You should see output like `4.2.7` (version numbers may vary).

### Install Additional Useful Packages

```bash
# Install commonly used packages
pip install pillow          # For image handling
pip install python-decouple # For environment variables
pip install django-debug-toolbar  # For debugging
```

## Step 4: Create Your First Django Project

Let's create a test project to verify everything works:

```bash
# Create a new Django project
django-admin startproject mysite

# Navigate to the project directory
cd mysite

# Run the development server
python manage.py runserver
```

If successful, you'll see output like:
```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).

You have 18 unapplied migration(s). Your project may not work properly until you apply the migrations for app(s): admin, auth, contenttypes, sessions.
Run 'python manage.py migrate' to apply them.

December 10, 2024 - 15:30:45
Django version 4.2.7, using settings 'mysite.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

Open your browser and visit `http://127.0.0.1:8000/`. You should see the Django welcome page!

## Step 5: Configure Your Development Environment

### Code Editor Setup

**Visual Studio Code (Recommended)**:
1. Install VS Code from [code.visualstudio.com](https://code.visualstudio.com/)
2. Install the Python extension
3. Install the Django extension
4. Configure Python interpreter to use your virtual environment

**PyCharm**:
1. Install PyCharm Community or Professional
2. Configure Python interpreter to use your virtual environment
3. Enable Django support in settings

### Git Setup (Optional but Recommended)

```bash
# Initialize git repository
git init

# Create .gitignore file
echo "*.pyc
__pycache__/
db.sqlite3
django_env/
.env" > .gitignore

# Make initial commit
git add .
git commit -m "Initial Django project setup"
```

## Development Workflow

Here's your typical Django development workflow:

1. **Activate Virtual Environment**:
   ```bash
   source django_env/bin/activate  # macOS/Linux
   django_env\Scripts\activate     # Windows
   ```

2. **Start Development Server**:
   ```bash
   python manage.py runserver
   ```

3. **Make Changes**: Edit your code in your preferred editor

4. **Apply Database Changes**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Test Your Application**: Visit `http://127.0.0.1:8000/` in your browser

## Next Steps

Now that your environment is set up, you're ready to:
- Learn about Django's architecture and core concepts
- Build your first Django application
- Explore Django's powerful features

Continue to the next section to dive into Django's architecture and start building!