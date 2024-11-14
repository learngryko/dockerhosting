# Use a Node.js image as the base
FROM node:18

# Set the working directory
WORKDIR /app

# Copy entrypoint script
COPY entrypoint.sh .

RUN chmod +x /app/entrypoint.sh

# Expose the port React will run on
EXPOSE 3000

# Run entrypoint script
CMD ["sh", "./entrypoint.sh", "my-react-app", "--template typescript"]
