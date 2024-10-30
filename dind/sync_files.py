from flask import Flask, request, jsonify
import os
import requests
import logging

# Set the base directory where files will be synced
BASE_DIRECTORY = os.getenv('BASE_DIRECTORY', '/app/repos/')
DJANGO_API_URL = os.getenv('DJANGO_API_URL', 'http://django-app-url/projects/')

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set the logging level to DEBUG to capture all messages
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Log format
    handlers=[
        logging.StreamHandler()  # Output logs to the console
    ]
)

logger = logging.getLogger(__name__)  # Create a logger for this module

@app.route('/sync-files', methods=['POST'])
def sync_files_endpoint():
    data = request.json
    project_id = data.get("project_id")
    if not project_id:
        logger.error("Project ID is required")
        return jsonify({"error": "Project ID is required"}), 400

    try:
        fetch_and_save_files(project_id)
        logger.info(f"Successfully synced files for project {project_id}")
        return jsonify({"status": "success", "message": f"Synced files for project {project_id}"}), 200
    except Exception as e:
        logger.exception(f"Failed to sync files for project {project_id}: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

def fetch_and_save_files(project_id):
    url = f"{DJANGO_API_URL}{project_id}/files/"
    logger.debug(f"Fetching files from: {url}")

    response = requests.get(url)

    if response.status_code == 404:
        raise Exception("Project not found on Django side.")

    response.raise_for_status()  # Raise an exception for other error statuses

    # Log the response content for debugging
    logger.debug(f"Response from Django: {response.text}")  # Log the response for inspection

    try:
        data = response.json()  # Get the full response JSON
        files = data.get('files', [])  # Access the list of files
    except ValueError as e:
        logger.error(f"Error parsing JSON: {e}")
        raise Exception("Invalid JSON response from Django API.")

    # Check if 'files' is empty
    if not files:
        logger.warning("No files to sync.")
        return  # Exit early if there are no files to sync

    # Process each file in the list
    for file in files:
        file_path = file.get('file_path')  # Access the file path using get to avoid KeyError
        # Log file path to ensure it’s not empty
        logger.debug(f"Processing file path: {file_path}")

        # Check if the file_path is valid
        if not file_path:
            logger.warning("File path is empty, skipping...")
            continue

        # Construct the full file path based on the base directory
        full_file_path = os.path.join(BASE_DIRECTORY+project_id, file_path)

        # Create directories if they don't exist
        os.makedirs(os.path.dirname(full_file_path), exist_ok=True)

        # Write the file content
        content = f"Content for {file_path}"  # Placeholder content; adjust as necessary
        with open(full_file_path, 'w') as f:
            f.write(content)
        
        logger.info(f"Synced {full_file_path}")  # Log successful sync

# Run Flask server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
