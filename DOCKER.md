# Docker Deployment Guide

This guide explains how to deploy the Skill Digital Twin application using Docker and Docker Compose.

## Prerequisites

- Docker Engine 20.10+ or Docker Desktop
- Docker Compose V2 (included with Docker Desktop)
- At least 4GB of free RAM
- OpenAI API key (for AI features)
- YouTube API key (for video recommendations)

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd skill-digital-twin
```

### 2. Configure Environment Variables

Copy the example environment file and edit it with your API keys:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
OPENAI_API_KEY=your-actual-openai-api-key
YOUTUBE_API_KEY=your-actual-youtube-api-key
SECRET_KEY=generate-a-random-secret-key
JWT_SECRET_KEY=generate-another-random-secret-key
```

**Security Note**: Generate secure random keys for production:
```bash
# Generate random keys
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Start the Application

**Option A: Using Docker Compose directly**

```bash
docker compose up -d
```

**Option B: Using Makefile (recommended)**

```bash
make up
```

The Makefile provides convenient shortcuts for common Docker operations. Run `make help` to see all available commands.

This command will:
- Pull required Docker images (PostgreSQL, Redis, Node, Python)
- Build custom images for backend and frontend
- Start all services in the background

**First-time build** may take 5-10 minutes depending on your internet connection.

### 4. Access the Application

Once all services are running:

- **Frontend Application**: http://localhost
- **Backend API**: http://localhost:8000
- **API Documentation (Swagger)**: http://localhost:8000/docs
- **Alternative API Docs (ReDoc)**: http://localhost:8000/redoc

### 5. Initialize Database (Optional)

If you want to seed the database with sample data:

```bash
docker compose exec backend python -m app.seed_data
```

## Common Commands

### View Logs

```bash
# View all logs
docker compose logs -f

# View specific service logs
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f postgres
```

### Stop Services

```bash
# Stop all services
docker compose down

# Stop and remove all data (clean slate)
docker compose down -v
```

### Restart Services

```bash
# Restart all services
docker compose restart

# Restart specific service
docker compose restart backend
```

### Rebuild After Code Changes

```bash
# Rebuild and restart specific service
docker compose up -d --build backend

# Rebuild all services
docker compose build
docker compose up -d
```

### Execute Commands in Containers

```bash
# Access backend shell
docker compose exec backend bash

# Access PostgreSQL
docker compose exec postgres psql -U postgres -d skill_digital_twin

# Run Django management commands
docker compose exec backend python -m app.seed_data
```

## Development Mode

For development with hot-reloading:

```bash
docker compose -f docker-compose.dev.yml up
```

This starts:
- Backend with auto-reload on code changes (port 8000)
- Frontend with Vite dev server and HMR (port 3000)
- PostgreSQL and Redis services

Access the development frontend at: http://localhost:3000

### Development Workflow

1. Make changes to your code in `backend/` or `frontend/`
2. Changes are automatically reflected:
   - Frontend: Hot Module Replacement (instant)
   - Backend: Auto-reload (few seconds)
3. No need to rebuild containers during development

## Production Deployment

### Using Docker Compose (Production)

For production deployment:

1. Update `.env` with production values:
   ```env
   DEBUG=False
   SECRET_KEY=<strong-random-key>
   JWT_SECRET_KEY=<strong-random-key>
   VITE_API_URL=https://your-api-domain.com
   ```

2. Start services:
   ```bash
   docker compose up -d
   ```

3. Set up a reverse proxy (nginx/Traefik) for SSL/TLS

### Using Docker Swarm or Kubernetes

For cluster deployments, see:
- Docker Swarm: Convert docker-compose.yml using `docker stack deploy`
- Kubernetes: Use Kompose or create custom manifests

## Troubleshooting

### Container Won't Start

Check logs:
```bash
docker compose logs backend
```

Common issues:
- Missing environment variables
- Port conflicts (8000, 80, 5432, 6379)
- Insufficient memory

### Database Connection Errors

Ensure PostgreSQL is healthy:
```bash
docker compose ps
docker compose logs postgres
```

Reset database:
```bash
docker compose down -v
docker compose up -d
```

### Port Already in Use

Change ports in `docker-compose.yml`:
```yaml
services:
  frontend:
    ports:
      - "8080:80"  # Change 80 to 8080
  backend:
    ports:
      - "8001:8000"  # Change 8000 to 8001
```

### SSL Certificate Issues During Build

If you encounter SSL issues during pip install, the Dockerfile includes a fallback with trusted hosts. If issues persist, you may need to configure your corporate proxy.

### Out of Memory

Increase Docker memory limit in Docker Desktop settings to at least 4GB.

## Architecture

### Services Overview

| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| frontend | Custom (Node + Nginx) | 80 | React application |
| backend | Custom (Python) | 8000 | FastAPI application |
| postgres | postgres:15-alpine | 5432 | Database |
| redis | redis:7-alpine | 6379 | Cache |

### Volumes

- `postgres_data`: Persistent PostgreSQL data
- `redis_data`: Persistent Redis data

### Network

All services communicate via the `skill-dt-network` bridge network.

## Maintenance

### Backup Database

```bash
docker compose exec postgres pg_dump -U postgres skill_digital_twin > backup.sql
```

### Restore Database

```bash
docker compose exec -T postgres psql -U postgres skill_digital_twin < backup.sql
```

### Update Application

```bash
git pull
docker compose build
docker compose up -d
```

### Clean Up

Remove unused Docker resources:
```bash
docker system prune -a
```

## Security Best Practices

1. **Never commit `.env` file** - It's in `.gitignore`
2. **Use strong random keys** for SECRET_KEY and JWT_SECRET_KEY
3. **Set DEBUG=False** in production
4. **Use HTTPS** with a reverse proxy (nginx, Traefik, Caddy)
5. **Keep Docker images updated** - Regularly rebuild
6. **Limit exposed ports** - Only expose what's necessary
7. **Use Docker secrets** for sensitive data in production

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [React Production Build](https://react.dev/learn/start-a-new-react-project#production-grade-react-frameworks)

## Getting Help

If you encounter issues:
1. Check the logs: `docker compose logs -f`
2. Review this guide's troubleshooting section
3. Open an issue on GitHub
