# Django Deployment and Production Guide

## Table of Contents
1. [Production Settings Configuration](#production-settings-configuration)
2. [Environment Variables Management](#environment-variables-management)
3. [Docker Configuration](#docker-configuration)
4. [Platform-Specific Deployment](#platform-specific-deployment)
   - [Heroku Deployment](#heroku-deployment)
   - [AWS Deployment](#aws-deployment)
   - [DigitalOcean Deployment](#digitalocean-deployment)
5. [Production Security Checklist](#production-security-checklist)
6. [Monitoring and Maintenance](#monitoring-and-maintenance)

## Introduction

Deploying Django applications to production requires careful consideration of security, performance, and scalability. This guide covers deployment strategies for popular platforms and essential production configurations.

## Production Settings Configuration

### Creating Production Settings

Create a separate settings file for production:

```python
# settings/production.py
from .base import *
import os

# Security Settings
DEBUG = False
ALLOWED_HOSTS = [
    'yourdomain.com',
    'www.yourdomain.com',
    # Add your production domains
]

# Database Configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Static Files Configuration
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media Files Configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Security Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# HTTPS Settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}
```

### Base Settings Structure

```python
# settings/base.py
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'corsheaders',
]

LOCAL_APPS = [
    'blog',
    'accounts',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'myproject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'myproject.wsgi.application'

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
```

## Environment Variables Management

### Using python-decouple

Install python-decouple for environment variable management:

```bash
pip install python-decouple
```

Create a `.env` file for local development:

```env
# .env (for development only - never commit to version control)
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=myproject_dev
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-email-password
```

Update your settings to use environment variables:

```python
# settings/base.py
from decouple import config, Csv

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

# CORS Settings
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:3000,http://127.0.0.1:3000',
    cast=Csv()
)
```

### Environment Variable Best Practices

1. **Never commit sensitive data** to version control
2. **Use different values** for development, staging, and production
3. **Document required variables** in your README
4. **Provide sensible defaults** where possible
5. **Use type casting** for non-string values

## Docker Configuration

### Dockerfile

Create a production-ready Dockerfile:

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=myproject.settings.production

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements/production.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "myproject.wsgi:application"]
```

### Docker Compose for Development

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    environment:
      - DEBUG=True
      - DB_HOST=db
    depends_on:
      - db
    command: python manage.py runserver 0.0.0.0:8000

  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      - POSTGRES_DB=myproject
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

### Docker Compose for Production

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DJANGO_SETTINGS_MODULE=myproject.settings.production
    env_file:
      - .env.prod
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    env_file:
      - .env.prod.db

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    env_file:
      - .env.prod

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./staticfiles:/app/staticfiles
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web

volumes:
  postgres_data:
```

### Multi-stage Dockerfile for Production

```dockerfile
# Dockerfile.prod
# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements/production.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r production.txt

# Production stage
FROM python:3.11-slim

# Create app user
RUN addgroup --system app && adduser --system --group app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=myproject.settings.production

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY --from=builder /app/wheels /wheels
COPY requirements/production.txt .
RUN pip install --no-cache /wheels/*

# Copy project
WORKDIR /app
COPY . .
RUN chown -R app:app /app

# Switch to app user
USER app

# Collect static files
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "myproject.wsgi:application"]
```

## Platform-Specific Deployment

### Heroku Deployment

#### Prerequisites
- Heroku CLI installed
- Git repository initialized

#### Step 1: Prepare Your Application

Create `requirements/production.txt`:
```txt
Django>=4.2,<5.0
gunicorn>=21.2.0
psycopg2-binary>=2.9.7
whitenoise>=6.5.0
python-decouple>=3.8
dj-database-url>=2.1.0
```

Create `Procfile`:
```
web: gunicorn myproject.wsgi --log-file -
release: python manage.py migrate
```

Create `runtime.txt`:
```
python-3.11.5
```

#### Step 2: Configure Settings for Heroku

```python
# settings/heroku.py
from .production import *
import dj_database_url

# Database configuration
DATABASES['default'] = dj_database_url.config(
    conn_max_age=600,
    conn_health_checks=True,
)

# Static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Allowed hosts
ALLOWED_HOSTS = ['.herokuapp.com']
```

#### Step 3: Deploy to Heroku

```bash
# Login to Heroku
heroku login

# Create Heroku app
heroku create your-app-name

# Set environment variables
heroku config:set SECRET_KEY="your-secret-key"
heroku config:set DEBUG=False
heroku config:set DJANGO_SETTINGS_MODULE=myproject.settings.heroku

# Add PostgreSQL addon
heroku addons:create heroku-postgresql:mini

# Deploy
git add .
git commit -m "Prepare for Heroku deployment"
git push heroku main

# Run migrations
heroku run python manage.py migrate

# Create superuser
heroku run python manage.py createsuperuser
```

### AWS Deployment

#### Using AWS Elastic Beanstalk

Create `.ebextensions/django.config`:
```yaml
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: myproject.wsgi:application
  aws:elasticbeanstalk:environment:proxy:staticfiles:
    /static: staticfiles
```

Create `requirements.txt`:
```txt
Django>=4.2,<5.0
gunicorn>=21.2.0
psycopg2-binary>=2.9.7
boto3>=1.28.0
django-storages>=1.14.0
```

Configure S3 for static files:
```python
# settings/aws.py
from .production import *

# AWS S3 Configuration
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='us-east-1')
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'

# Static files
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'

# Media files
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
```

Deploy commands:
```bash
# Install EB CLI
pip install awsebcli

# Initialize EB application
eb init

# Create environment
eb create production

# Deploy
eb deploy
```

#### Using AWS ECS with Fargate

Create `task-definition.json`:
```json
{
  "family": "django-app",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "django-container",
      "image": "your-account.dkr.ecr.region.amazonaws.com/django-app:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DJANGO_SETTINGS_MODULE",
          "value": "myproject.settings.production"
        }
      ],
      "secrets": [
        {
          "name": "SECRET_KEY",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:django-secrets"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/django-app",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### DigitalOcean Deployment

#### Using DigitalOcean App Platform

Create `app.yaml`:
```yaml
name: django-app
services:
- name: web
  source_dir: /
  github:
    repo: your-username/your-repo
    branch: main
  run_command: gunicorn --worker-tmp-dir /dev/shm myproject.wsgi
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: DEBUG
    value: "False"
  - key: DJANGO_SETTINGS_MODULE
    value: myproject.settings.production
  - key: SECRET_KEY
    value: ${SECRET_KEY}
    type: SECRET

databases:
- name: db
  engine: PG
  version: "15"
  size: basic-xs

static_sites:
- name: static
  source_dir: staticfiles
  routes:
  - path: /static
```

#### Using DigitalOcean Droplets

Create deployment script:
```bash
#!/bin/bash
# deploy.sh

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3-pip python3-venv nginx postgresql postgresql-contrib

# Create application user
sudo adduser --disabled-password --gecos '' django

# Setup application directory
sudo mkdir -p /var/www/django-app
sudo chown django:django /var/www/django-app

# Clone repository
cd /var/www/django-app
sudo -u django git clone https://github.com/your-username/your-repo.git .

# Create virtual environment
sudo -u django python3 -m venv venv
sudo -u django ./venv/bin/pip install -r requirements/production.txt

# Configure environment variables
sudo -u django cp .env.example .env.prod
# Edit .env.prod with production values

# Run migrations and collect static files
sudo -u django ./venv/bin/python manage.py migrate
sudo -u django ./venv/bin/python manage.py collectstatic --noinput

# Configure Gunicorn service
sudo tee /etc/systemd/system/gunicorn.service > /dev/null <<EOF
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=django
Group=www-data
WorkingDirectory=/var/www/django-app
ExecStart=/var/www/django-app/venv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/var/www/django-app/django-app.sock myproject.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

# Start and enable Gunicorn
sudo systemctl start gunicorn
sudo systemctl enable gunicorn

# Configure Nginx
sudo tee /etc/nginx/sites-available/django-app > /dev/null <<EOF
server {
    listen 80;
    server_name your-domain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /var/www/django-app;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/django-app/django-app.sock;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/django-app /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

## Production Security Checklist

### Essential Security Settings

```python
# Security checklist for production settings

# 1. Debug Mode
DEBUG = False  # ✓ Never True in production

# 2. Secret Key
SECRET_KEY = config('SECRET_KEY')  # ✓ Use environment variable

# 3. Allowed Hosts
ALLOWED_HOSTS = [
    'yourdomain.com',
    'www.yourdomain.com',
]  # ✓ Specify exact domains

# 4. HTTPS Settings
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# 5. Security Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# 6. HSTS (HTTP Strict Transport Security)
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# 7. Content Security Policy
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")

# 8. Database Security
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'OPTIONS': {
            'sslmode': 'require',
        },
        # ... other settings
    }
}

# 9. Session Security
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_HTTPONLY = True

# 10. Password Validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 12,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
```

### Security Checklist

- [ ] **Debug Mode**: Ensure `DEBUG = False` in production
- [ ] **Secret Key**: Use a strong, unique secret key stored in environment variables
- [ ] **Allowed Hosts**: Specify exact domain names, never use `['*']`
- [ ] **HTTPS**: Enable SSL/TLS and redirect HTTP to HTTPS
- [ ] **Security Headers**: Implement all security headers (XSS, HSTS, etc.)
- [ ] **Database**: Use SSL connections and strong passwords
- [ ] **Static Files**: Serve static files through a CDN or web server
- [ ] **Media Files**: Validate and sanitize uploaded files
- [ ] **Dependencies**: Keep all packages updated and scan for vulnerabilities
- [ ] **Logging**: Implement comprehensive logging without exposing sensitive data
- [ ] **Backup**: Set up automated database and media backups
- [ ] **Monitoring**: Implement error tracking and performance monitoring
- [ ] **Rate Limiting**: Implement rate limiting for API endpoints
- [ ] **CORS**: Configure CORS properly for API access
- [ ] **Admin Interface**: Secure admin interface with strong authentication

### Security Tools and Commands

```bash
# Check for security issues
python manage.py check --deploy

# Scan for vulnerabilities
pip install safety
safety check

# Update dependencies
pip list --outdated
pip install -U package-name

# Generate strong secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Monitoring and Maintenance

### Health Check Endpoint

```python
# views.py
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
import redis

def health_check(request):
    """Health check endpoint for monitoring"""
    status = {
        'status': 'healthy',
        'database': 'unknown',
        'cache': 'unknown',
    }
    
    # Check database
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        status['database'] = 'healthy'
    except Exception as e:
        status['database'] = 'unhealthy'
        status['status'] = 'unhealthy'
    
    # Check cache
    try:
        cache.set('health_check', 'ok', 30)
        if cache.get('health_check') == 'ok':
            status['cache'] = 'healthy'
        else:
            status['cache'] = 'unhealthy'
    except Exception as e:
        status['cache'] = 'unhealthy'
    
    return JsonResponse(status)
```

### Logging Configuration

```python
# Production logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/django/django.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'mail_admins'],
            'level': 'INFO',
            'propagate': True,
        },
        'myproject': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### Maintenance Commands

Create management commands for common maintenance tasks:

```python
# management/commands/backup_db.py
from django.core.management.base import BaseCommand
from django.core.management import call_command
import os
from datetime import datetime

class Command(BaseCommand):
    help = 'Backup database'

    def handle(self, *args, **options):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'backup_{timestamp}.json'
        
        with open(filename, 'w') as f:
            call_command('dumpdata', stdout=f, exclude=['contenttypes', 'auth.permission'])
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created backup: {filename}')
        )
```

### Performance Monitoring

```python
# middleware/monitoring.py
import time
import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

class PerformanceMonitoringMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.start_time = time.time()

    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            if duration > 1.0:  # Log slow requests
                logger.warning(
                    f'Slow request: {request.method} {request.path} '
                    f'took {duration:.2f}s'
                )
        return response
```

## Conclusion

This guide covers the essential aspects of deploying Django applications to production. Remember to:

1. **Test thoroughly** in a staging environment before production deployment
2. **Monitor your application** continuously after deployment
3. **Keep dependencies updated** and scan for security vulnerabilities
4. **Implement proper backup strategies** for data protection
5. **Use environment-specific configurations** to maintain security

For more advanced topics, consider exploring:
- Container orchestration with Kubernetes
- Advanced caching strategies with Redis
- Database optimization and scaling
- Continuous integration and deployment (CI/CD)
- Infrastructure as Code (IaC) with Terraform

## Next Steps

After completing this tutorial, you should be able to:
- Configure Django applications for production environments
- Deploy to major cloud platforms (Heroku, AWS, DigitalOcean)
- Implement security best practices
- Set up monitoring and maintenance procedures
- Use Docker for containerized deployments

Continue your Django journey by exploring advanced topics like performance optimization, testing strategies, and scalable architecture patterns.