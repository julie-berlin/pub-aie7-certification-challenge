# Backend Dockerfile for IntegriBot API
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONPATH=/app:/app/api
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy pyproject.toml, uv.lock, and README.md for dependency installation
COPY pyproject.toml uv.lock* README.md ./

# Install uv for fast package management
RUN pip install uv

# Install Python dependencies
RUN uv sync --frozen

# Copy application code
COPY . .

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/ping || exit 1

# Start the application
CMD ["python", "-m", "uvicorn", "api.app.main:app", "--host", "0.0.0.0", "--port", "8000"]