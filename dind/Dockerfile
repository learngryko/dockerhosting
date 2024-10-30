FROM docker:24.0.1-dind 

WORKDIR /app

# Install Python and Flask for the HTTP listener
RUN apk add --no-cache python3 py3-pip && pip install requests Flask

# Copy the sync script
COPY sync_files.py /app/sync_files.py 

# Run the sync script and Flask server
CMD ["python3", "/app/sync_files.py"]
