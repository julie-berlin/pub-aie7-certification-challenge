# IntegriBot Docker Deployment

This guide explains how to run IntegriBot using Docker Compose with all services containerized.

## Prerequisites

- Docker and Docker Compose installed
- API keys configured in `.env.local`

## Quick Start

1. **Ensure API keys are configured:**
   ```bash
   # Make sure .env.local exists with:
   # OPENAI_API_KEY=your_key_here
   # TAVILY_API_KEY=your_key_here  
   # LANGCHAIN_API_KEY=your_key_here
   ```

2. **Build and start all services:**
   ```bash
   docker-compose up --build -d
   ```

3. **Access the application:**
   - **IntegriBot Frontend**: http://localhost:3000
   - **Backend API**: http://localhost:8000
   - **Qdrant Dashboard**: http://localhost:6333/dashboard
   - **API Documentation**: http://localhost:8000/docs

## ✅ Verified Working Status

All services are successfully running:
- ✅ **Qdrant**: Vector database ready on ports 6333/6334
- ✅ **Backend**: FastAPI server with agentic workflow on port 8000  
- ✅ **Frontend**: Next.js IntegriBot interface on port 3000

## Services

### Qdrant Vector Database
- **Container**: `integribot-qdrant`
- **Ports**: 6333 (HTTP), 6334 (gRPC)
- **Storage**: Persistent volume for vector data

### FastAPI Backend
- **Container**: `integribot-backend`
- **Port**: 8000
- **Features**: Streamlined agentic workflow, parallel web search
- **Dependencies**: Qdrant database

### Next.js Frontend
- **Container**: `integribot-frontend`  
- **Port**: 3000
- **Features**: Professional chat interface, user context collection
- **Dependencies**: Backend API

## Commands

```bash
# Start services in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up --build --force-recreate

# Clean up (removes volumes)
docker-compose down -v
```

## Health Checks

All services include health checks:
- **Qdrant**: Ready when `/health` endpoint responds
- **Backend**: Ready when `/api/ping` endpoint responds  
- **Frontend**: Ready when port 3000 responds

## Troubleshooting

1. **Backend fails to start**: Check API keys in `.env.local`
2. **Qdrant connection issues**: Ensure Qdrant container is healthy
3. **Frontend can't reach backend**: Check network configuration
4. **Port conflicts**: Stop services using ports 3000, 6333, 8000

## Development

For development with hot reloading:
```bash
# Run only infrastructure
docker-compose up qdrant

# Run backend locally
cd api && python run_server.py

# Run frontend locally  
cd frontend && npm run dev
```