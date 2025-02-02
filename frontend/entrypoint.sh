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

# Install dependencies
npm install
npm update --save

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

# Install Tailwind CSS and required dependencies
echo "Installing Tailwind CSS..."
npm install -D tailwindcss postcss autoprefixer

# Install jwt-decode if not already installed
if ! npm list jwt-decode > /dev/null 2>&1; then
  echo "Installing jwt-decode..."
  npm install jwt-decode
else
  echo "jwt-decode is already installed. Skipping."
fi

# Install @heroicons/react if not already installed
if ! npm list @heroicons/react > /dev/null 2>&1; then
  echo "Installing @heroicons/react..."
  npm install @heroicons/react
else
  echo "@heroicons/react is already installed. Skipping."
fi

# Install @headlessui/react if not already installed
if ! npm list @headlessui/react > /dev/null 2>&1; then
  echo "Installing @headlessui/react..."
  npm install @headlessui/react
else
  echo "@headlessui/react is already installed. Skipping."
fi

# Install @monaco-editor/react if not already installed
if ! npm list @monaco-editor/react > /dev/null 2>&1; then
  echo "Installing @monaco-editor/react..."
  npm install @monaco-editor/react
else
  echo "@monaco-editor/react is already installed. Skipping."
fi

# Start the Next.js app
npm run dev -- -H 0.0.0.0

