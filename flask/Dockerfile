FROM python:3.9-slim

WORKDIR /app

# Install Flask
RUN pip install Flask requests

# Copy your Flask app code
COPY sync_files.py /app/sync_files.py

# Expose the Flask port
EXPOSE 5000

# Start the Flask app
CMD ["python", "sync_files.py"]
