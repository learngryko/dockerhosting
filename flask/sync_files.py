from flask import Flask, request, jsonify
import os
import requests
import logging

# Set the base directory where files will be synced
BASE_DIRECTORY = os.getenv('BASE_DIRECTORY', '/app/repos/')
DJANGO_API_URL = os.getenv('DJANGO_API_URL', 'http://django:8000/projects/')

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
    files = fetch_file_list(project_id)
    if not files:
        logger.warning("No files to sync.")
        return

    for file in files:
        process_and_save_file(file, project_id)


def fetch_file_list(project_id):
    """Fetch the list of files for the given project from the Django API."""
    base_file_url = f"{DJANGO_API_URL}{project_id}/files/"
    logger.debug(f"Fetching file list from: {base_file_url}")

    response = requests.get(base_file_url)
    if response.status_code == 404:
        raise Exception("Project not found on Django side.")
    
    response.raise_for_status()

    try:
        data = response.json()
        return data.get('files', [])
    except ValueError as e:
        logger.error(f"Error parsing JSON: {e}")
        raise Exception("Invalid JSON response from Django API.")


def process_and_save_file(file, project_id):
    """Process each file and save its content to the specified path."""
    file_path = file.get('file_path')
    if not file_path:
        logger.warning("File path is empty, skipping...")
        return

    logger.debug(f"Processing file path: {file_path}")

    content = fetch_file_content(project_id, file_path)
    if content is None:
        return  # Skip if content could not be fetched

    save_file_content(project_id, file_path, content)


def fetch_file_content(project_id, file_path):
    """Fetch the content for a specific file from the Django API."""
    file_content_url = f"{DJANGO_API_URL}{project_id}/files/{file_path}"
    logger.debug(f"Fetching content from: {file_content_url}")

    content_response = requests.get(file_content_url)
    if content_response.status_code != 200:
        logger.warning(f"Failed to fetch content for {file_path}, status code: {content_response.status_code}")
        return None

    try:
        content_data = content_response.json()
        return content_data.get('content', '')
    except ValueError as e:
        logger.error(f"Error parsing JSON content for {file_path}: {e}")
        return None


def save_file_content(project_id, file_path, content):
    """Save the content of a file to the local file system."""
    full_file_path = os.path.join(BASE_DIRECTORY + project_id, file_path)
    os.makedirs(os.path.dirname(full_file_path), exist_ok=True)

    with open(full_file_path, 'w') as f:
        f.write(content)

    logger.info(f"Synced {full_file_path}")

# Run Flask server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
