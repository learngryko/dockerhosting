# Use a Node.js image as the base
FROM node:18

# Set the working directory in the container
WORKDIR /app

# Copy the entrypoint script and make it executable
COPY entrypoint.sh .

RUN chmod +x /app/entrypoint.sh 

# Expose the port on which the app will run
EXPOSE 3000

# Use the entrypoint script to start the app
CMD ["sh", "./entrypoint.sh", "my-next-app", "--ts --eslint --tailwind --src-dir --app --import-alias @/*"]
