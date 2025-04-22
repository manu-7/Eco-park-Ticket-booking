# ecopark/create_superuser.py

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ecopark.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

USERNAME = os.getenv("DJANGO_SUPERUSER_USERNAME", "manu")
EMAIL = os.getenv("DJANGO_SUPERUSER_EMAIL", "admin@example.com")
PASSWORD = os.getenv("DJANGO_SUPERUSER_PASSWORD", "adminpass123")

if not User.objects.filter(username=USERNAME).exists():
    User.objects.create_superuser(USERNAME, EMAIL, PASSWORD)
    print("✅ Superuser created.")
else:
    print("ℹ️ Superuser already exists.")
