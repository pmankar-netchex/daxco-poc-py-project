# Daxco POC Docker Setup

This repository contains a Docker-based setup for the Daxco POC application, which consists of a React frontend and a Python FastAPI backend.

## Prerequisites

- Docker and Docker Compose installed on your system
- Git for cloning the repository

## Quick Start

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Daxco\ POC
   ```

2. Configure the environment:
   - Make sure the `.env` file in the `backend` directory is properly configured with your database credentials

3. Build and start the containers:
   ```bash
   docker-compose up -d
   ```

4. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5001

## Docker Components

### Frontend (React + Material UI)

- Built with React and Material UI
- Served via Nginx
- Automatically proxies API requests to the backend

### Backend (FastAPI)

- Built with Python 3.10 and FastAPI
- Connects to SQL Server database
- Provides REST API endpoints for CSV processing

## Configuration

### Environment Variables

The backend service uses environment variables for configuration:

- `DB_SERVER`: SQL Server hostname or IP
- `DB_NAME`: Database name
- `DB_USERNAME`: Database username
- `DB_PASSWORD`: Database password
- `DB_DRIVER`: ODBC Driver name

### Docker Compose Configuration

The `docker-compose.yml` file defines two services:

1. `frontend`: The React web application served by Nginx
2. `backend`: The FastAPI application

## Development Workflow

### Making Changes

1. Make changes to the source code
2. Rebuild the containers:
   ```bash
   docker-compose build
   docker-compose up -d
   ```

### Viewing Logs

```bash
# View logs from all services
docker-compose logs

# View logs from a specific service
docker-compose logs frontend
docker-compose logs backend

# Follow logs
docker-compose logs -f
```

## Troubleshooting

### Container Won't Start

Check the logs:
```bash
docker-compose logs
```

### Database Connection Issues

Verify your database credentials in the `.env` file and ensure the database server is accessible from the Docker container.

## License

[Your License Here]
