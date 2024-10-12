# Use the official Python image as a base
FROM python:3.9

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Copy requirements.txt to the working directory
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port that the Django app runs on
EXPOSE 8000

# Command to run the Django development server
CMD ["sh", "-c", "if [ ! -f manage.py ]; then django-admin startproject project . && cd project && django-admin startapp app; fi && python manage.py runserver 0.0.0.0:8000"]
