# Email Template & Triggered Sending Web Application

A comprehensive Django-based web application for managing email templates, configuring event-triggered emails, and tracking email delivery with built-in retry mechanisms.

## Features

### 1. Email Template Management (FR-1 to FR-5)
- ✅ Create, edit, and delete email templates
- ✅ Support for `{{PlaceholderName}}` format
- ✅ Subject, HTML body, and plain text body support
- ✅ Template preview with test data
- ✅ Version control for templates

### 2. Placeholder Management (FR-6 to FR-8)
- ✅ Store predefined placeholders per event type
- ✅ Add custom placeholders
- ✅ Automatic placeholder detection and validation

### 3. Event & Trigger Management (FR-9 to FR-11)
- ✅ Configure events that trigger emails
- ✅ Link events to email templates
- ✅ Multiple trigger methods: API, manual, scheduled, internal

### 4. Email Sending (FR-12 to FR-15)
- ✅ Automatic email sending on event triggers
- ✅ SMTP support (configurable)
- ✅ Email sending logs with status tracking
- ✅ Configurable retry policies for failed emails

### 5. Audit & Reporting (FR-16 to FR-18)
- ✅ Comprehensive email logs with event tracking
- ✅ Search and filter options
- ✅ Export logs to CSV

### 6. Non-Functional Requirements (NFR-1 to NFR-5)
- ✅ Responsive web UI using Bootstrap 5
- ✅ Role-based access control (Django Admin)
- ✅ API for event triggering
- ✅ Scalable architecture

## Installation

### Prerequisites
- Python 3.8+
- Django 5.2.7
- pip

### Setup

1. **Navigate to the project directory**
   ```bash
   cd email_template_system
   ```

2. **Install dependencies** (optional, only Django is required)
   ```bash
   pip install django
   ```

3. **Run migrations**
   ```bash
   python manage.py migrate
   ```

4. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

5. **Run the development server**
   ```bash
   python manage.py runserver
   ```

6. **Access the application**
   - Main app: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

## Project Structure

```
email_template_system/
├── templates_manager/      # Email template management app
│   ├── models.py           # EmailTemplate, Placeholder, TemplateAttachment
│   ├── views.py            # Template CRUD, preview
│   ├── forms.py            # Template and placeholder forms
│   └── admin.py            # Admin interface
├── events/                 # Event and trigger management app
│   ├── models.py           # EventType, EventTrigger, EventPlaceholder
│   ├── views.py            # Event CRUD, API endpoint
│   ├── forms.py            # Event forms
│   └── admin.py            # Admin interface
├── email_service/          # Email sending and logging app
│   ├── models.py           # EmailLog, SMTPConfiguration, EmailRetryPolicy
│   ├── views.py            # Email logs, dashboard, export
│   ├── services.py         # Email sending service
│   └── admin.py            # Admin interface
├── templates/              # HTML templates
│   ├── base.html           # Base template with navigation
│   ├── templates_manager/  # Template management templates
│   ├── events/             # Event management templates
│   └── email_service/      # Email log templates
└── manage.py
```

## Usage Guide

### 1. Creating an Email Template

1. Navigate to **Templates** in the sidebar
2. Click **Create Template**
3. Fill in:
   - Template Name (e.g., "Welcome Email")
   - Subject: `Welcome {{CustomerName}}!`
   - HTML Body: `<h1>Hello {{CustomerName}}</h1><p>Thank you for joining us!</p>`
   - Plain Text Body (optional)
4. Click **Save Template**

### 2. Creating Placeholders

1. Navigate to **Placeholders**
2. Click **Create Placeholder**
3. Define placeholder:
   - Name: `CustomerName`
   - Description: "Customer's full name"
   - Data Type: String
   - Example Value: "John Doe"
4. Click **Save**

### 3. Creating an Event Type

1. Navigate to **Events**
2. Click **Create Event Type**
3. Configure:
   - Name: "User Registration"
   - Slug: `user-registration`
   - Template: Select "Welcome Email"
   - Trigger Method: API Call
4. Click **Save**

### 4. Triggering an Event via API

Send a POST request to `/events/api/trigger/`:

```bash
curl -X POST http://127.0.0.1:8000/events/api/trigger/ \
  -H "Content-Type: application/json" \
  -d '{
    "event_slug": "user-registration",
    "data": {
      "recipient_email": "user@example.com",
      "CustomerName": "John Doe"
    }
  }'
```

Response:
```json
{
  "success": true,
  "trigger_id": 1,
  "email_log_id": 1,
  "status": "completed"
}
```

### 5. Viewing Email Logs

1. Navigate to **Email Logs**
2. View delivery status, recipient, subject
3. Filter by status or date
4. Click **View** to see full email content
5. Export logs to CSV for reporting

## Example Flow

### Complete Transaction Notification Example

1. **Create Template**
   - Name: "Transaction Success"
   - Subject: `Hello {{CustomerName}}, your transaction is successful!`
   - Body HTML:
     ```html
     <h2>Transaction Complete</h2>
     <p>Dear {{CustomerName}},</p>
     <p>Your transaction with ID <strong>{{TransactionID}}</strong> 
        of amount <strong>{{Amount}}</strong> on {{Date}} is complete.</p>
     <p>Thank you for your business!</p>
     ```

2. **Create Placeholders**
   - `CustomerName` (string)
   - `TransactionID` (string)
   - `Amount` (string)
   - `Date` (date)

3. **Create Event Type**
   - Name: "Transaction Completed"
   - Slug: `transaction-completed`
   - Template: "Transaction Success"

4. **Trigger the Event**
   ```json
   {
     "event_slug": "transaction-completed",
     "data": {
       "recipient_email": "john.doe@example.com",
       "CustomerName": "John Doe",
       "TransactionID": "TX12345",
       "Amount": "100 USD",
       "Date": "2025-10-02"
     }
   }
   ```

5. **Email is Sent**
   - Subject: `Hello John Doe, your transaction is successful!`
   - Body renders with all placeholder values
   - Status logged in Email Logs

## API Documentation

### Trigger Event Endpoint

**Endpoint:** `POST /events/api/trigger/`

**Request Body:**
```json
{
  "event_slug": "event-slug-here",
  "data": {
    "recipient_email": "required@email.com",
    "PlaceholderName": "value",
    "AnotherPlaceholder": "another value"
  }
}
```

**Response (Success):**
```json
{
  "success": true,
  "trigger_id": 123,
  "email_log_id": 456,
  "status": "completed"
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "Error message here"
}
```

## Configuration

### Email Settings

Edit `email_template_system/settings.py`:

```python
# Development: Console backend (prints to console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Production: SMTP backend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'noreply@example.com'
```

### SMTP Configuration (via Admin)

1. Go to Admin → SMTP Configurations
2. Add new configuration:
   - Name, Host, Port
   - TLS/SSL settings
   - Credentials
   - Set as default

## Admin Interface

Access the Django admin panel at `/admin/` to:
- Manage all templates, placeholders, and events
- View detailed logs and statistics
- Configure SMTP settings
- Set up retry policies
- View triggered events

## Testing

### Manual Testing

1. Create a test template with placeholders
2. Use the **Preview** feature to test rendering
3. Create an event and trigger it via API
4. Check Email Logs to verify delivery

### Console Email Backend

In development, emails are printed to the console instead of being sent. Check your terminal output to see the email content.

## Security Notes

- Use environment variables for production secrets
- Enable HTTPS in production
- Encrypt SMTP passwords in database
- Implement rate limiting for API endpoints
- Use Django's CSRF protection (enabled by default)

## Scalability Considerations

- Use Celery for asynchronous email sending (not included, but recommended)
- Implement database indexing for large email logs
- Use Redis for caching frequently accessed templates
- Consider message queue (RabbitMQ/Redis) for high-volume events

## Troubleshooting

### Emails not sending
- Check SMTP configuration
- Verify EMAIL_BACKEND setting
- Check error logs in Email Logs
- Ensure template has valid placeholders

### Template not rendering
- Verify all placeholders have values in event data
- Check template syntax (use `{{PlaceholderName}}`)
- Use Preview feature to test

### API errors
- Ensure event_slug is correct
- Include recipient_email in data
- Check event is active
- Verify template is linked to event

## License

This project is part of the Django Tutorial repository and is available for educational purposes.

## Support

For issues or questions:
- Check the troubleshooting section
- Review Django documentation
- Check application logs in the admin panel
