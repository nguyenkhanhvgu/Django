#!/bin/bash

# Django Production Deployment Script
# This script automates the deployment process for Django applications

set -e  # Exit on any error

# Configuration
PROJECT_NAME="myproject"
PROJECT_DIR="/var/www/$PROJECT_NAME"
VENV_DIR="$PROJECT_DIR/venv"
REPO_URL="https://github.com/yourusername/yourproject.git"
BRANCH="main"
USER="django"
GROUP="www-data"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    error "This script should not be run as root"
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    if ! command_exists git; then
        error "Git is not installed"
    fi
    
    if ! command_exists python3; then
        error "Python 3 is not installed"
    fi
    
    if ! command_exists pip3; then
        error "pip3 is not installed"
    fi
    
    log "Prerequisites check passed"
}

# Create project directory and set permissions
setup_directory() {
    log "Setting up project directory..."
    
    if [ ! -d "$PROJECT_DIR" ]; then
        sudo mkdir -p "$PROJECT_DIR"
        sudo chown $USER:$GROUP "$PROJECT_DIR"
    fi
    
    cd "$PROJECT_DIR"
}

# Clone or update repository
update_code() {
    log "Updating code from repository..."
    
    if [ -d ".git" ]; then
        log "Repository exists, pulling latest changes..."
        git fetch origin
        git reset --hard origin/$BRANCH
    else
        log "Cloning repository..."
        git clone -b $BRANCH "$REPO_URL" .
    fi
    
    log "Code updated successfully"
}

# Setup virtual environment
setup_virtualenv() {
    log "Setting up virtual environment..."
    
    if [ ! -d "$VENV_DIR" ]; then
        python3 -m venv "$VENV_DIR"
    fi
    
    source "$VENV_DIR/bin/activate"
    pip install --upgrade pip
    
    if [ -f "requirements/production.txt" ]; then
        pip install -r requirements/production.txt
    elif [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    else
        error "No requirements file found"
    fi
    
    log "Virtual environment setup complete"
}

# Run database migrations
run_migrations() {
    log "Running database migrations..."
    
    source "$VENV_DIR/bin/activate"
    python manage.py migrate --noinput
    
    log "Database migrations completed"
}

# Collect static files
collect_static() {
    log "Collecting static files..."
    
    source "$VENV_DIR/bin/activate"
    python manage.py collectstatic --noinput --clear
    
    log "Static files collected"
}

# Create superuser if it doesn't exist
create_superuser() {
    log "Checking for superuser..."
    
    source "$VENV_DIR/bin/activate"
    
    if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
        python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists():
    User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME', '$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')
    print('Superuser created')
else:
    print('Superuser already exists')
EOF
    else
        warning "Superuser environment variables not set, skipping superuser creation"
    fi
}

# Restart services
restart_services() {
    log "Restarting services..."
    
    # Restart Gunicorn
    if sudo systemctl is-active --quiet gunicorn; then
        sudo systemctl restart gunicorn
        log "Gunicorn restarted"
    else
        warning "Gunicorn service not found or not running"
    fi
    
    # Restart Nginx
    if sudo systemctl is-active --quiet nginx; then
        sudo systemctl reload nginx
        log "Nginx reloaded"
    else
        warning "Nginx service not found or not running"
    fi
    
    # Restart Celery (if exists)
    if sudo systemctl is-active --quiet celery; then
        sudo systemctl restart celery
        log "Celery restarted"
    fi
}

# Run health checks
health_check() {
    log "Running health checks..."
    
    source "$VENV_DIR/bin/activate"
    
    # Django system check
    python manage.py check --deploy
    
    # Check if application is responding
    sleep 5
    if curl -f http://localhost:8000/health/ >/dev/null 2>&1; then
        log "Application health check passed"
    else
        warning "Application health check failed"
    fi
}

# Backup database
backup_database() {
    log "Creating database backup..."
    
    source "$VENV_DIR/bin/activate"
    
    BACKUP_DIR="$PROJECT_DIR/backups"
    mkdir -p "$BACKUP_DIR"
    
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.json"
    
    python manage.py dumpdata --exclude contenttypes --exclude auth.permission > "$BACKUP_FILE"
    
    # Keep only last 10 backups
    ls -t "$BACKUP_DIR"/backup_*.json | tail -n +11 | xargs -r rm
    
    log "Database backup created: $BACKUP_FILE"
}

# Main deployment function
deploy() {
    log "Starting deployment of $PROJECT_NAME..."
    
    check_prerequisites
    setup_directory
    backup_database
    update_code
    setup_virtualenv
    run_migrations
    collect_static
    create_superuser
    restart_services
    health_check
    
    log "Deployment completed successfully!"
}

# Parse command line arguments
case "${1:-deploy}" in
    deploy)
        deploy
        ;;
    backup)
        setup_directory
        backup_database
        ;;
    update)
        setup_directory
        update_code
        setup_virtualenv
        collect_static
        restart_services
        ;;
    migrate)
        setup_directory
        run_migrations
        ;;
    static)
        setup_directory
        collect_static
        ;;
    restart)
        restart_services
        ;;
    health)
        health_check
        ;;
    *)
        echo "Usage: $0 {deploy|backup|update|migrate|static|restart|health}"
        echo ""
        echo "Commands:"
        echo "  deploy  - Full deployment (default)"
        echo "  backup  - Create database backup"
        echo "  update  - Update code and restart services"
        echo "  migrate - Run database migrations"
        echo "  static  - Collect static files"
        echo "  restart - Restart services"
        echo "  health  - Run health checks"
        exit 1
        ;;
esac