# Use the official Python image as a base
FROM python:3.9

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1





ARG DJANGO_SUPERUSER_USERNAME
ARG DJANGO_SUPERUSER_EMAIL
ARG DJANGO_SUPERUSER_PASSWORD
ARG DJANGO_SECRET
ARG DEBUG
ARG DATABASE_URL
ARG POSTGRES_DB
ARG POSTGRES_USER
ARG POSTGRES_PASSWORD
ARG HOST_IP
ARG DOCKER_HOSTdind:2375

# Set environment variables for Django superuser (runtime)
ENV DJANGO_SUPERUSER_USERNAME=${DJANGO_SUPERUSER_USERNAME}
ENV DJANGO_SUPERUSER_EMAIL=${DJANGO_SUPERUSER_EMAIL}
ENV DJANGO_SUPERUSER_PASSWORD=${DJANGO_SUPERUSER_PASSWORD}
ENV DJANGO_SECRET=${DJANGO_SECRET}
ENV DEBUG: ${DJANGO_DEBUG}
ENV DATABASE_URL: postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
ENV POSTGRES_DB: ${POSTGRES_DB}
ENV POSTGRES_USER: ${POSTGRES_USER}
ENV POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
ENV HOST_IP: ${HOST_IP}
ENV DOCKER_HOST: "tcp://dind:2375"

# Set the working directory in the container
WORKDIR /app

# Copy requirements.txt to the working directory
COPY requirements.txt /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port that the Django app runs on
EXPOSE 8000

# Check if manage.py exists; if not, initialize Django project
RUN sh -c 'if [ ! -f manage.py ]; then django-admin startproject project .; fi'

# Check if app exists; if not, create Django app
RUN sh -c 'if [ ! -d project/app ]; then cd project && django-admin startapp app; fi'

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
