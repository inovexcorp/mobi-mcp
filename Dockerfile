# Use Python 3.12 slim image as base
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Create a non-root user (use numeric UID to avoid name conflicts)
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Change ownership of the app directory
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Set environment variables with defaults
ENV MOBI_BASE_URL="https://127.0.0.1:8443"
ENV MOBI_USERNAME="admin"
ENV MOBI_PASSWORD="admin"
ENV MOBI_IGNORE_CERT="true"

# Set Python path
ENV PYTHONPATH=/app/src

# Expose port for SSE
EXPOSE 8000

# Run the MCP server with SSE transport
CMD ["python", "src/mobi-mcp.py", "--sse"]