# Django Setup Troubleshooting Guide

This guide covers common issues you might encounter when setting up Django and their solutions.

## Python Installation Issues

### Issue: "python is not recognized as an internal or external command" (Windows)

**Symptoms**: Command prompt doesn't recognize `python` command

**Solutions**:
1. **Add Python to PATH manually**:
   - Open System Properties → Advanced → Environment Variables
   - Add Python installation directory to PATH (e.g., `C:\Python39\`)
   - Add Scripts directory to PATH (e.g., `C:\Python39\Scripts\`)
   - Restart command prompt

2. **Reinstall Python with PATH option**:
   - Uninstall current Python
   - Download installer from python.org
   - **Check "Add Python to PATH"** during installation

3. **Use Python Launcher**:
   ```cmd
   py --version
   py -m pip install django
   ```

### Issue: Multiple Python Versions Conflict

**Symptoms**: Wrong Python version being used, package installation issues

**Solutions**:
1. **Use specific Python version**:
   ```bash
   # Linux/macOS
   python3.9 -m venv django_env
   
   # Windows
   py -3.9 -m venv django_env
   ```

2. **Check which Python is being used**:
   ```bash
   which python    # Linux/macOS
   where python    # Windows
   ```

3. **Use virtual environments** (always recommended)

## Virtual Environment Issues

### Issue: Virtual Environment Not Activating

**Symptoms**: Prompt doesn't show `(env_name)`, packages install globally

**Solutions**:
1. **Check activation command**:
   ```bash
   # Windows
   django_env\Scripts\activate.bat
   # or
   django_env\Scripts\Activate.ps1  # PowerShell
   
   # Linux/macOS
   source django_env/bin/activate
   ```

2. **PowerShell Execution Policy (Windows)**:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

3. **Recreate virtual environment**:
   ```bash
   rm -rf django_env  # Linux/macOS
   rmdir /s django_env  # Windows
   python -m venv django_env
   ```

### Issue: "No module named 'venv'"

**Symptoms**: `python -m venv` command fails

**Solutions**:
1. **Install venv package**:
   ```bash
   # Ubuntu/Debian
   sudo apt install python3-venv
   
   # CentOS/RHEL
   sudo yum install python3-venv
   ```

2. **Use virtualenv instead**:
   ```bash
   pip install virtualenv
   virtualenv django_env
   ```

## Django Installation Issues

### Issue: "No module named 'django'"

**Symptoms**: Django commands fail, import errors

**Solutions**:
1. **Ensure virtual environment is activated**:
   - Look for `(env_name)` in terminal prompt
   - Reactivate if necessary

2. **Install Django in correct environment**:
   ```bash
   # With virtual environment activated
   pip install django
   
   # Verify installation
   python -c "import django; print(django.get_version())"
   ```

3. **Check pip is using correct environment**:
   ```bash
   which pip    # Should point to virtual environment
   pip list     # Should show Django in the list
   ```

### Issue: Permission Denied During Installation

**Symptoms**: "Permission denied" or "Access denied" errors

**Solutions**:
1. **Use virtual environment** (recommended):
   ```bash
   python -m venv django_env
   source django_env/bin/activate  # Linux/macOS
   pip install django
   ```

2. **User installation** (not recommended):
   ```bash
   pip install --user django
   ```

3. **Fix permissions** (Linux/macOS):
   ```bash
   sudo chown -R $USER:$USER ~/.local/
   ```

## Django Project Issues

### Issue: "django-admin: command not found"

**Symptoms**: Cannot create Django projects

**Solutions**:
1. **Use python -m django**:
   ```bash
   python -m django startproject mysite
   ```

2. **Check PATH includes Scripts directory**:
   ```bash
   # Add to PATH (adjust path as needed)
   export PATH=$PATH:~/.local/bin  # Linux/macOS
   ```

3. **Reinstall Django**:
   ```bash
   pip uninstall django
   pip install django
   ```

### Issue: Development Server Won't Start

**Symptoms**: `python manage.py runserver` fails

**Solutions**:
1. **Check you're in the correct directory**:
   ```bash
   ls -la  # Should see manage.py file
   ```

2. **Apply initial migrations**:
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

3. **Check for port conflicts**:
   ```bash
   # Use different port
   python manage.py runserver 8080
   ```

4. **Check firewall settings**:
   - Ensure port 8000 is not blocked
   - Try accessing via `127.0.0.1:8000` instead of `localhost:8000`

## Database Issues

### Issue: "no such table" Errors

**Symptoms**: Database-related errors when running Django

**Solutions**:
1. **Run migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

2. **Check database file permissions**:
   ```bash
   ls -la db.sqlite3  # Should be writable
   ```

3. **Delete and recreate database**:
   ```bash
   rm db.sqlite3
   python manage.py migrate
   ```

## IDE and Editor Issues

### Issue: VS Code Not Recognizing Django

**Symptoms**: No syntax highlighting, import errors in editor

**Solutions**:
1. **Select correct Python interpreter**:
   - Press `Ctrl+Shift+P` (Cmd+Shift+P on Mac)
   - Type "Python: Select Interpreter"
   - Choose the interpreter from your virtual environment

2. **Install Python extension**:
   - Go to Extensions tab
   - Install "Python" by Microsoft
   - Install "Django" extension

3. **Configure workspace settings**:
   ```json
   // .vscode/settings.json
   {
       "python.defaultInterpreterPath": "./django_env/bin/python",
       "python.terminal.activateEnvironment": true
   }
   ```

## Network and Firewall Issues

### Issue: Cannot Access Development Server

**Symptoms**: Browser shows "This site can't be reached"

**Solutions**:
1. **Check server is running**:
   - Look for "Starting development server" message
   - Ensure no error messages in terminal

2. **Try different URLs**:
   ```
   http://127.0.0.1:8000/
   http://localhost:8000/
   ```

3. **Check firewall settings**:
   - Windows: Allow Python through Windows Firewall
   - macOS: Check System Preferences → Security & Privacy
   - Linux: Check iptables/ufw settings

4. **Run on all interfaces** (for network access):
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

## Getting Help

If you're still experiencing issues:

1. **Check Django Documentation**: [docs.djangoproject.com](https://docs.djangoproject.com/)
2. **Search Stack Overflow**: Include error messages in your search
3. **Django Community Forum**: [forum.djangoproject.com](https://forum.djangoproject.com/)
4. **Django Discord**: Join the Django community Discord server
5. **GitHub Issues**: Check Django's GitHub repository for known issues

## Prevention Tips

1. **Always use virtual environments**
2. **Keep Python and Django updated**
3. **Read error messages carefully**
4. **Check Django compatibility with your Python version**
5. **Use version control (Git) to track changes**
6. **Document your setup process for future reference**

Remember: Most Django setup issues are environment-related. When in doubt, try creating a fresh virtual environment and reinstalling Django.