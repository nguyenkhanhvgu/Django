# Django Authentication Project

This is a complete Django authentication system that demonstrates user registration, login, logout, and profile management with security best practices.

## Features

- User registration with email validation
- Secure login/logout functionality
- User profile management with avatar uploads
- Password change functionality
- Security best practices implementation
- Responsive Bootstrap UI
- Rate limiting for login attempts
- Custom user profile model

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone or download this project**
   ```bash
   cd authentication-project
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv auth_env
   
   # On Windows
   auth_env\Scripts\activate
   
   # On macOS/Linux
   source auth_env/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create a superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Create media directory**
   ```bash
   mkdir media
   mkdir media/profile_pics
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Open your browser and go to `http://127.0.0.1:8000/accounts/register/`
   - Register a new account or login with existing credentials

## Project Structure

```
authentication-project/
├── manage.py
├── requirements.txt
├── README.md
├── authentication_project/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   ├── migrations/
│   └── templates/
│       └── accounts/
│           ├── base.html
│           ├── login.html
│           ├── register.html
│           ├── dashboard.html
│           ├── profile.html
│           └── password_change.html
└── media/
    └── profile_pics/
```

## Usage

### Registration
1. Navigate to `/accounts/register/`
2. Fill in the registration form with username, email, first name, last name, and password
3. Submit the form to create your account
4. You'll be automatically logged in and redirected to the dashboard

### Login
1. Navigate to `/accounts/login/`
2. Enter your username and password
3. Click "Login" to access your dashboard

### Profile Management
1. After logging in, click "Profile" in the navigation
2. Update your personal information
3. Upload an avatar image (automatically resized to 300x300 pixels)
4. Save changes to update your profile

### Password Change
1. From the dashboard, click "Change Password"
2. Enter your current password and new password
3. Confirm the new password and submit

## Security Features

- **Password Validation**: Strong password requirements enforced
- **CSRF Protection**: All forms protected against CSRF attacks
- **Secure Sessions**: Session cookies configured for security
- **Input Validation**: All user inputs validated and sanitized
- **Rate Limiting**: Login attempts are rate-limited (can be enabled)
- **Image Processing**: Uploaded avatars are automatically resized

## Customization

### Adding New Fields to User Profile
1. Edit `accounts/models.py` and add fields to `UserProfile` model
2. Update `accounts/forms.py` to include new fields in `ProfileUpdateForm`
3. Update the profile template to display new fields
4. Run migrations: `python manage.py makemigrations && python manage.py migrate`

### Styling
- The project uses Bootstrap 5 for styling
- Custom CSS can be added to the base template
- Templates are located in `accounts/templates/accounts/`

### Email Configuration
For production, update the email settings in `settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'your-smtp-server.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@example.com'
EMAIL_HOST_PASSWORD = 'your-password'
```

## Testing

Run the Django test suite:
```bash
python manage.py test
```

## Troubleshooting

### Common Issues

1. **Migration errors**: Delete `db.sqlite3` and migration files, then run migrations again
2. **Media files not loading**: Ensure `MEDIA_URL` and `MEDIA_ROOT` are configured in settings
3. **Avatar upload errors**: Install Pillow: `pip install Pillow`
4. **Permission errors**: Check file permissions for media directory

### Debug Mode
The project runs in debug mode by default. For production:
1. Set `DEBUG = False` in settings.py
2. Configure `ALLOWED_HOSTS`
3. Use a production database
4. Configure static file serving

## Learning Objectives

This project demonstrates:
- Django's built-in authentication system
- Custom user profile models
- Form handling and validation
- File uploads and image processing
- Template inheritance and Bootstrap integration
- Security best practices
- URL routing and view organization

## Next Steps

- Add email verification for registration
- Implement password reset functionality
- Add social authentication (Google, GitHub)
- Implement two-factor authentication
- Add user roles and permissions
- Create API endpoints with authentication

## Resources

- [Django Authentication Documentation](https://docs.djangoproject.com/en/stable/topics/auth/)
- [Django Forms Documentation](https://docs.djangoproject.com/en/stable/topics/forms/)
- [Bootstrap Documentation](https://getbootstrap.com/docs/5.1/getting-started/introduction/)