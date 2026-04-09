# Docker Setup Guide

## Overview

This project uses Docker Compose v3.9 with modern best practices for containerizing a full-stack Japanese Character Identifier application.

## Prerequisites

- Docker Desktop 4.20+ or Docker Engine 24.0+
- Docker Compose 2.20+
- 4GB+ RAM available for containers
- Windows: WSL2 backend for Docker Desktop

## Quick Start

### 1. Environment Setup

```bash
# Copy the development environment file
cp .env .env.local

# Or for production, use:
cp .env.docker .env.prod
```

### 2. Build and Start Services

```bash
# Development mode (with hot reload)
docker compose up -d

# Production mode
docker compose --env-file .env.prod up -d

# Build fresh images
docker compose build --no-cache
docker compose up -d
```

### 3. Verify Services

```bash
# Check service status
docker compose ps

# View logs
docker compose logs -f

# View specific service logs
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f db
```

## Services

### Database (PostgreSQL 17)
- **Port**: 5432 (localhost only)
- **Health Check**: Active with 5s intervals
- **Volume**: Persistent `postgres_data`
- **Features**: Alpine slim, optimized for container

### Backend (FastAPI)
- **Port**: 8000 (localhost only)
- **Health Check**: HTTP endpoint `/health`
- **Features**: Hot reload in dev, volume mounted code
- **Environment**: Python 3.12, non-root user
- **Dependencies**: FastAPI 0.115.0, SQLAlchemy 2.1.1, PyTorch 2.5.1

### Frontend (Next.js)
- **Port**: 3000 (localhost only)
- **Health Check**: HTTP GET request
- **Features**: Standalone build, optimized multi-stage
- **Environment**: Node.js 20 Alpine, non-root user
- **Build**: SWC minification enabled

## Network

Services communicate via `app-network` bridge:
- Backend connects to `db:5432`
- Frontend connects to `backend:8000`
- All services isolated from host network

## Development Workflow

### Adding Dependencies

**Backend (Python)**:
```bash
# Add new package
docker compose exec backend pip install package_name

# Update requirements
docker compose exec backend pip freeze > requirements.txt

# Restart service
docker compose restart backend
```

**Frontend (Node.js)**:
```bash
# Add new package
docker compose exec frontend npm install package_name

# Restart service
docker compose restart frontend
```

### Database Management

```bash
# Connect to PostgreSQL
docker compose exec db psql -U user -d japanese_identifier

# Run migrations
docker compose exec backend alembic upgrade head

# Create dump
docker compose exec db pg_dump -U user -d japanese_identifier > backup.sql

# Restore dump
docker compose exec -T db psql -U user -d japanese_identifier < backup.sql
```

### Testing

```bash
# Run backend tests
docker compose exec backend pytest

# Run with coverage
docker compose exec backend pytest --cov=app tests/

# Run specific test
docker compose exec backend pytest tests/test_auth.py -v
```

## Troubleshooting

### Port Already in Use
```bash
# Find container using port
docker ps --all
docker port <container_id>

# Kill container
docker kill <container_id>
```

### Database Connection Issues
```bash
# Check database health
docker compose exec db pg_isready -U user -d japanese_identifier

# View DB logs
docker compose logs db

# Reset database (WARNING: deletes data)
docker volume rm japanese-identifier_postgres_data
docker compose restart db
```

### Out of Memory
```bash
# Increase Docker memory limit in Docker Desktop settings
# Windows: Docker Desktop > Settings > Resources > Memory: 4GB+
```

### Build Failures
```bash
# Clean rebuild
docker compose down -v
docker compose build --no-cache
docker compose up -d

# Check build logs
docker compose build --no-cache --progress=plain
```

## Production Deployment

### Environment Variables
Update `.env.docker` with production values:
- `SECRET_KEY`: Strong random string (32+ chars)
- `DATABASE_URL`: Production PostgreSQL server
- `POSTGRES_PASSWORD`: Strong password
- `NEXT_PUBLIC_API_URL`: Production backend URL

### Security
- Bind services to localhost only (default)
- Use reverse proxy (nginx/Traefik) for public access
- Enable HTTPS at proxy level
- Rotate `SECRET_KEY` regularly
- Use separate `.env.prod` file

### Resources
```dockerfile
# Add to docker-compose.yml service:
resources:
  limits:
    cpus: '1'
    memory: 1G
  reservations:
    cpus: '0.5'
    memory: 512M
```

## Monitoring

### Health Checks
All services have health checks enabled:
- **db**: PostgreSQL ready check (5s intervals)
- **backend**: HTTP /health endpoint (10s intervals)
- **frontend**: HTTP GET localhost:3000 (10s intervals)

### Logs
```bash
# Real-time logs
docker compose logs -f

# Last 100 lines
docker compose logs --tail=100

# Since specific time
docker compose logs --since 2024-01-20 backend
```

## Cleanup

```bash
# Stop all services
docker compose down

# Stop and remove volumes (careful!)
docker compose down -v

# Remove dangling images
docker image prune

# Full cleanup
docker system prune -a --volumes
```

## Version Information

- Docker Compose: 3.9 (modern features, no legacy syntax)
- Python: 3.12.x Alpine (slim, security updates regular)
- Node.js: 20.x Alpine (LTS, maintained until April 2026)
- FastAPI: 0.115.0 (latest stable)
- SQLAlchemy: 2.1.1 (async support)
- Next.js: 14.2.0 (latest features)
- PostgreSQL: 17.x Alpine (latest stable)

## References

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Multi-stage Docker Builds](https://docs.docker.com/build/building/multi-stage/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
