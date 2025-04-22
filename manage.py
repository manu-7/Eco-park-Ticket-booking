#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from django.contrib.auth import get_user_model

def create_superuser():
    """Create a superuser if it doesn't already exist."""
    User = get_user_model()
    USERNAME = os.getenv("DJANGO_SUPERUSER_USERNAME", "admin")
    EMAIL = os.getenv("DJANGO_SUPERUSER_EMAIL", "admin@example.com")
    PASSWORD = os.getenv("DJANGO_SUPERUSER_PASSWORD", "adminpass123")

    if not User.objects.filter(username=USERNAME).exists():
        User.objects.create_superuser(USERNAME, EMAIL, PASSWORD)
        print("✅ Superuser created.")
    else:
        print("ℹ️ Superuser already exists.")

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecopark.settings')

    # Create superuser before running any other Django commands
    create_superuser()

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
