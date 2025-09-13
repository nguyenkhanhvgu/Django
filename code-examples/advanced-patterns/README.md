# Advanced Django Patterns - Code Examples

This directory contains practical code examples demonstrating advanced Django patterns covered in the tutorial.

## Structure

```
advanced-patterns/
├── middleware/              # Custom middleware examples
├── signals/                # Django signals examples
├── orm/                    # Advanced ORM techniques
├── patterns/               # Design pattern implementations
├── requirements.txt        # Project dependencies
└── manage.py              # Django management script
```

## Setup Instructions

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Create a superuser:
```bash
python manage.py createsuperuser
```

5. Run the development server:
```bash
python manage.py runserver
```

## Examples Included

### Middleware Examples
- Request logging middleware
- API authentication middleware
- Rate limiting middleware
- Custom security middleware

### Signals Examples
- Model signal handlers
- Custom signal implementations
- Event-driven architecture patterns
- Signal best practices

### ORM Examples
- Custom managers and querysets
- Advanced query techniques
- Raw SQL integration
- Performance optimization patterns

### Design Patterns
- Repository pattern
- Service layer pattern
- Factory pattern
- Observer pattern with signals
- Strategy pattern
- Decorator pattern
- Command pattern

## Running Examples

Each example includes test cases and usage demonstrations. Run tests with:

```bash
python manage.py test
```

## Learning Path

1. Start with middleware examples to understand request/response processing
2. Explore signals for event-driven architecture
3. Study ORM patterns for database optimization
4. Implement design patterns for better code organization

## Additional Resources

- Django Documentation: https://docs.djangoproject.com/
- Django Best Practices: https://django-best-practices.readthedocs.io/
- Design Patterns in Python: https://python-patterns.guide/