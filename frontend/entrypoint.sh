#!/bin/sh

# Set the default app name and options
APP_NAME=${1:-my-next-app}
CREATE_NEXT_OPTIONS=${2:-""}

# Check if the Next.js app exists in the host directory
if [ ! -d "./$APP_NAME" ]; then
  echo "Creating a new Next.js app named '$APP_NAME' with options '$CREATE_NEXT_OPTIONS'..."
  npx create-next-app@latest "$APP_NAME" $CREATE_NEXT_OPTIONS
else
  echo "Next.js app '$APP_NAME' already exists. Skipping creation."
fi

# Change to the app directory
cd "$APP_NAME" || { echo "Failed to enter directory '$APP_NAME'"; exit 1; }

# Check if package.json exists
if [ ! -f "package.json" ]; then
  echo "Error: package.json not found in $APP_NAME directory. Ensure the Next.js app was created successfully."
  exit 1
fi

# Install dependencies (if they exist)
npm install

# Start the Next.js app
npm run dev
