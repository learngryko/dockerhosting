# Project Overview

---

This project provides a robust setup for developing, deploying, and managing applications in a containerized web environment. Enjoy coding!


---
This project is a containerized development environment that integrates:
- **PostgreSQL** - Database for storage
- **Django** - Backend API
- **Next.js** - Frontend interface
- **Docker-in-Docker (DinD)** - Manages container creation via API
- **Traefik/Nginx** - Reverse proxy for secure routing

## Prerequisites

Before starting, ensure you have the following installed:
- **Docker** (latest version recommended)
- **Docker Compose**

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```bash
POSTGRES_USER=postgres
POSTGRES_PASSWORD=supersecret
POSTGRES_DB=mydb

DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=adminpwd
DJANGO_SECRET=reallysecret

DJANGO_DEBUG=True  # Set to False for production
NEXT_DEBUG=False
HOST_IP=127.0.0.1
NEXT_PUBLIC_BACKEND_URL=https://127.0.0.1/api
```

Update these values based on your configuration.

## Getting Started

### 1. Clone the Repository

```bash
git clone <repository-url>
cd <repository-name>
```

### 2. Build & Run the Containers

```bash
docker-compose up --build
```

### 3. Access the Services

- **Django API**: [http://localhost:8000](http://localhost:8000)
- **Next.js Frontend**: [http://localhost:3000](http://localhost:3000)
- **Traefik/Nginx Reverse Proxy**: [https://localhost](https://localhost)

## Project Structure

```
.
├── backend/            # Django Backend
│   ├── Dockerfile      
│   ├── requirements.txt
│   └── entrypoint.sh   
├── frontend/           # Next.js Frontend
│   ├── Dockerfile
│   ├── entrypoint.sh
│   └── ...
├── dind/               # Docker-in-Docker Configuration
├── docker-compose.yml  # Container Orchestration
├── .env                # Environment Variables
└── ...
```

## API Endpoints

The Django API provides:
- **Authentication**: JWT-based login
- **Project Management**: Clone and manage repositories
- **File Handling**: Retrieve and update file contents
- **Container Management**: Create, start, stop, and delete containers

## Common Commands

- Start containers:
  ```bash
  docker-compose up -d
  ```
- Stop and remove containers:
  ```bash
  docker-compose down
  ```
- View logs:
  ```bash
  docker-compose logs -f
  ```

## Notes

- Use `docker-compose logs -f <service_name>` to monitor specific service logs.
- Ensure SSL certificates are configured correctly in production.
- Secure your `.env` file to protect sensitive information.


