# Django Deployment and Production Exercises

## Overview
These exercises will help you practice deploying Django applications to production environments. You'll work with different deployment platforms, configure security settings, and implement monitoring solutions.

## Prerequisites
- Completed intermediate Django tutorials
- Basic understanding of command line operations
- Access to at least one cloud platform account (Heroku, AWS, or DigitalOcean)
- Docker installed on your local machine

## Exercise 1: Production Settings Configuration

### Objective
Configure a Django application for production deployment with proper security settings.

### Tasks

1. **Create Production Settings Structure**
   - Create a `settings/` directory in your Django project
   - Move your current `settings.py` to `settings/base.py`
   - Create `settings/development.py` and `settings/production.py`
   - Update `manage.py` and `wsgi.py` to use the new settings structure

2. **Configure Environment Variables**
   - Install `python-decouple`
   - Create a `.env.example` file with all required environment variables
   - Update your settings to use environment variables for sensitive data
   - Ensure `DEBUG=False` in production settings

3. **Implement Security Headers**
   - Configure HTTPS settings (`SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, etc.)
   - Set up security headers (`X_FRAME_OPTIONS`, `SECURE_BROWSER_XSS_FILTER`, etc.)
   - Configure HSTS settings
   - Run `python manage.py check --deploy` and fix any issues

### Validation
- [ ] Settings are properly separated by environment
- [ ] All sensitive data uses environment variables
- [ ] Security check passes without warnings
- [ ] Application runs with production settings locally

## Exercise 2: Docker Configuration

### Objective
Create Docker configurations for both development and production environments.

### Tasks

1. **Create Development Docker Setup**
   - Write a `Dockerfile` for development
   - Create `docker-compose.yml` with Django, PostgreSQL, and Redis services
   - Include volume mounts for live code reloading
   - Test the setup with `docker-compose up`

2. **Create Production Docker Setup**
   - Write a production `Dockerfile` with multi-stage build
   - Create `docker-compose.prod.yml` with optimized configurations
   - Include nginx service for serving static files
   - Add health checks for all services

3. **Optimize Docker Images**
   - Use `.dockerignore` to exclude unnecessary files
   - Implement non-root user in containers
   - Minimize image size using alpine base images where appropriate
   - Add security scanning to your Docker build process

### Validation
- [ ] Development environment runs successfully with Docker
- [ ] Production Docker setup serves the application correctly
- [ ] Images are optimized for size and security
- [ ] Health checks work for all services

## Exercise 3: Platform Deployment

### Objective
Deploy your Django application to at least one cloud platform.

### Choose One Platform:

#### Option A: Heroku Deployment

1. **Prepare Application**
   - Create `Procfile` with web and release processes
   - Create `runtime.txt` specifying Python version
   - Configure `requirements.txt` for Heroku
   - Set up Heroku-specific settings

2. **Deploy to Heroku**
   - Create Heroku application
   - Configure environment variables
   - Add PostgreSQL addon
   - Deploy using Git
   - Run migrations and create superuser

#### Option B: AWS Deployment

1. **Elastic Beanstalk Deployment**
   - Configure `.ebextensions/` directory
   - Set up RDS PostgreSQL database
   - Configure S3 for static files
   - Deploy using EB CLI

2. **Alternative: ECS Deployment**
   - Create ECR repository
   - Build and push Docker image
   - Configure ECS task definition
   - Set up load balancer and auto-scaling

#### Option C: DigitalOcean Deployment

1. **App Platform Deployment**
   - Create `app.yaml` configuration
   - Set up managed database
   - Configure environment variables
   - Deploy from GitHub repository

2. **Alternative: Droplet Deployment**
   - Set up Ubuntu droplet
   - Install and configure nginx, gunicorn, PostgreSQL
   - Configure systemd services
   - Set up SSL certificate with Let's Encrypt

### Validation
- [ ] Application is accessible via public URL
- [ ] Database is properly configured and migrations applied
- [ ] Static files are served correctly
- [ ] HTTPS is configured and working
- [ ] Environment variables are properly set

## Exercise 4: Security Implementation

### Objective
Implement comprehensive security measures for your production application.

### Tasks

1. **Security Headers and HTTPS**
   - Configure all security headers in Django settings
   - Set up SSL/TLS certificate (Let's Encrypt or platform-provided)
   - Implement Content Security Policy (CSP)
   - Test security headers using online tools

2. **Database Security**
   - Configure database SSL connections
   - Implement database connection pooling
   - Set up database backups
   - Configure database user permissions properly

3. **Application Security**
   - Implement rate limiting for API endpoints
   - Configure CORS properly for frontend applications
   - Set up proper logging without exposing sensitive data
   - Implement security monitoring and alerting

### Validation
- [ ] All security headers are properly configured
- [ ] SSL/TLS certificate is valid and properly configured
- [ ] Database connections use SSL
- [ ] Rate limiting is working correctly
- [ ] Security monitoring is in place

## Exercise 5: Monitoring and Maintenance

### Objective
Set up monitoring, logging, and maintenance procedures for your production application.

### Tasks

1. **Health Monitoring**
   - Create health check endpoint
   - Implement database and cache connectivity checks
   - Set up uptime monitoring (using external service)
   - Configure alerting for downtime

2. **Logging Configuration**
   - Configure structured logging for production
   - Set up log rotation and retention policies
   - Implement error tracking (Sentry or similar)
   - Create log analysis and monitoring dashboards

3. **Performance Monitoring**
   - Implement application performance monitoring
   - Set up database query monitoring
   - Configure memory and CPU usage alerts
   - Create performance benchmarking tests

4. **Backup and Recovery**
   - Set up automated database backups
   - Implement media files backup strategy
   - Create disaster recovery procedures
   - Test backup restoration process

### Validation
- [ ] Health checks are working and monitored
- [ ] Comprehensive logging is configured
- [ ] Performance monitoring is in place
- [ ] Backup and recovery procedures are tested

## Exercise 6: CI/CD Pipeline

### Objective
Implement continuous integration and deployment pipeline for your Django application.

### Tasks

1. **Set Up CI Pipeline**
   - Configure GitHub Actions, GitLab CI, or similar
   - Run tests automatically on pull requests
   - Implement code quality checks (linting, security scanning)
   - Build and test Docker images

2. **Implement CD Pipeline**
   - Set up automatic deployment to staging environment
   - Implement manual approval for production deployments
   - Configure rollback procedures
   - Set up deployment notifications

3. **Environment Management**
   - Create separate staging and production environments
   - Implement environment-specific configurations
   - Set up database migration strategies
   - Configure feature flags for gradual rollouts

### Validation
- [ ] CI pipeline runs tests and quality checks automatically
- [ ] CD pipeline deploys to staging automatically
- [ ] Production deployments require manual approval
- [ ] Rollback procedures are tested and working

## Troubleshooting Guide

### Common Issues and Solutions

1. **Static Files Not Loading**
   - Check `STATIC_ROOT` and `STATIC_URL` settings
   - Ensure `collectstatic` command runs successfully
   - Verify web server configuration for static file serving

2. **Database Connection Errors**
   - Verify database credentials and connection settings
   - Check network connectivity and firewall rules
   - Ensure database server is running and accessible

3. **SSL/HTTPS Issues**
   - Verify certificate installation and configuration
   - Check for mixed content warnings
   - Ensure all redirects are properly configured

4. **Performance Issues**
   - Check database query optimization
   - Implement caching strategies
   - Monitor memory and CPU usage
   - Optimize static file delivery

### Getting Help

- Review the deployment guide documentation
- Check platform-specific documentation
- Use community forums and Stack Overflow
- Consult with experienced DevOps engineers

## Next Steps

After completing these exercises, you should be able to:
- Deploy Django applications to multiple platforms
- Implement comprehensive security measures
- Set up monitoring and maintenance procedures
- Create CI/CD pipelines for automated deployments

Continue your learning by exploring:
- Advanced container orchestration with Kubernetes
- Infrastructure as Code with Terraform
- Advanced monitoring and observability
- Microservices architecture patterns