#!/bin/sh
echo "Waiting for database to be ready..."
until nc -z -v -w30 db 5432
do
    echo "Waiting for database connection..."
    sleep 1
done

echo "Running migrations..."
python manage.py makemigrations
python manage.py migrate

echo "Creating superuser if not exists..."
echo "from django.contrib.auth.models import User; \
    User.objects.filter(username='${DJANGO_SUPERUSER_USERNAME}').exists() or \
    User.objects.create_superuser('${DJANGO_SUPERUSER_USERNAME}', '${DJANGO_SUPERUSER_EMAIL}', '${DJANGO_SUPERUSER_PASSWORD}')" | python manage.py shell

echo "Starting server..."
exec "$@"
