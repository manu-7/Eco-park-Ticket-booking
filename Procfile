web: python manage.py migrate && python /opt/render/project/src/create_superuser.py && gunicorn --bind 0.0.0.0:$PORT ecopark.wsgi:application
