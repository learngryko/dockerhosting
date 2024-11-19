#!/bin/sh

APP_NAME=${1:-my-react-app}
CREATE_REACT_OPTIONS=${2:-""}

# Check if the React app exists
if [ ! -d "./$APP_NAME" ]; then
  echo "Creating a new React app '$APP_NAME'..."
  npx create-react-app "$APP_NAME" $CREATE_REACT_OPTIONS
else
  echo "React app '$APP_NAME' already exists. Skipping creation."
fi

# Navigate to app directory
cd "$APP_NAME" || { echo "Failed to enter directory '$APP_NAME'"; exit 1; }

# Check if package.json exists
if [ ! -f "package.json" ]; then
  echo "Error: package.json not found in $APP_NAME directory."
  exit 1
fi

# Install axios if not already installed
if ! npm list axios > /dev/null 2>&1; then
  echo "Installing axios..."
  npm install axios
else
  echo "Axios is already installed. Skipping."
fi

# Install dotenv if not already installed
if ! npm list dotenv > /dev/null 2>&1; then
  echo "Installing dotenv..."
  npm install dotenv
else
  echo "dotenv is already installed. Skipping."
fi

# Install dotenv if not already installed
if ! npm list react-router-dom > /dev/null 2>&1; then
  echo "Installing dotenv..."
  npm install react-router-dom
else
  echo "react-router-dom is already installed. Skipping."
fi
# Install dependencies
npm install

# Start the React app
npm run start
