#!/usr/bin/env python3
"""
Django Installation Verification Script

This script checks if Django is properly installed and configured
in your development environment.

Usage:
    python verify_installation.py

Requirements:
    - Python 3.8+
    - Django (any version)
    - Virtual environment (recommended)
"""

import sys
import os
import subprocess
import importlib.util
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(text):
    """Print a formatted header"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*50}")
    print(f"{text}")
    print(f"{'='*50}{Colors.END}")


def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.END}")


def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")


def print_info(text):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")


def check_python_version():
    """Check if Python version is compatible with Django"""
    print_header("Checking Python Version")
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    print(f"Python version: {version_str}")
    
    if version.major == 3 and version.minor >= 8:
        print_success(f"Python {version_str} is compatible with Django")
        return True
    else:
        print_error(f"Python {version_str} is not compatible with Django")
        print_info("Django requires Python 3.8 or higher")
        return False


def check_virtual_environment():
    """Check if running in a virtual environment"""
    print_header("Checking Virtual Environment")
    
    # Check for virtual environment indicators
    venv_indicators = [
        os.environ.get('VIRTUAL_ENV'),
        os.environ.get('CONDA_DEFAULT_ENV'),
        hasattr(sys, 'real_prefix'),
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    ]
    
    if any(venv_indicators):
        venv_path = os.environ.get('VIRTUAL_ENV', 'Unknown')
        print_success(f"Running in virtual environment: {venv_path}")
        return True
    else:
        print_warning("Not running in a virtual environment")
        print_info("It's recommended to use a virtual environment for Django projects")
        return False


def check_django_installation():
    """Check if Django is installed and get version"""
    print_header("Checking Django Installation")
    
    try:
        import django
        version = django.get_version()
        print_success(f"Django {version} is installed")
        
        # Check Django version compatibility
        major_version = int(version.split('.')[0])
        if major_version >= 3:
            print_success("Django version is supported")
        else:
            print_warning(f"Django {version} is quite old, consider upgrading")
        
        return True, version
    except ImportError:
        print_error("Django is not installed")
        print_info("Install Django with: pip install django")
        return False, None


def check_django_admin():
    """Check if django-admin command is available"""
    print_header("Checking Django Admin Command")
    
    try:
        result = subprocess.run(
            ['django-admin', '--version'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            version = result.stdout.strip()
            print_success(f"django-admin command available (version {version})")
            return True
        else:
            print_error("django-admin command failed")
            return False
            
    except (subprocess.TimeoutExpired, FileNotFoundErr