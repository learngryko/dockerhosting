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

# Install dependencies
npm install

# Start the React app
npm run start
