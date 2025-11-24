# Use Python 3.12 slim image as base
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Copy project files
COPY . .

# Install Python dependencies using pip
RUN pip install --no-cache-dir .

# Create a non-root user
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port (if needed for future web API)
EXPOSE 8000

# Default command
CMD ["python", "main.py", "--help"]