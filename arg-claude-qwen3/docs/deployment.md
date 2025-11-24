# RAG Backend System Deployment Guide

This guide provides instructions for deploying the RAG Backend System in various environments, from local development to production.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Local Development Deployment](#local-development-deployment)
- [Docker Deployment](#docker-deployment)
- [Production Deployment](#production-deployment)
- [Environment Configuration](#environment-configuration)
- [Database Setup](#database-setup)
- [Monitoring and Logging](#monitoring-and-logging)
- [Security Considerations](#security-considerations)
- [Scaling and Performance](#scaling-and-performance)
- [Backup and Recovery](#backup-and-recovery)

## Prerequisites

Before deploying the RAG Backend System, ensure you have:

1. **Python 3.12+** installed
2. **Docker** (for containerized deployment)
3. **Memgraph database** instance
4. **DashScope API key** for Qwen models
5. **uv package manager** (recommended for dependency management)

## Local Development Deployment

### 1. Clone the Repository

```bash
git clone <repository-url>
cd rag-backend
```

### 2. Install Dependencies

Using uv (recommended):

```bash
uv sync
```

Or using pip:

```bash
pip install -e .
```

### 3. Configure Environment Variables

Copy the example environment file and customize it:

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 4. Start Memgraph Database

For local development, you can run Memgraph using Docker:

```bash
docker run -d -p 7687:7687 -p 7444:7444 --name memgraph memgraph/memgraph
```

### 5. Test the Installation

Run the unit tests to verify the installation:

```bash
pytest tests/unit
```

## Docker Deployment

### 1. Build the Docker Image

```bash
docker build -t rag-backend .
```

### 2. Using Docker Compose (Recommended)

The project includes a `docker-compose.yml` file that sets up both the RAG backend and Memgraph database:

```bash
docker-compose up -d
```

This will start:
- `rag-backend`: The RAG application service
- `memgraph`: The Memgraph database service

### 3. Customizing Docker Deployment

You can customize the deployment by modifying the `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  rag-backend:
    build: .
    container_name: rag-backend
    environment:
      - QWEN_API_KEY=${QWEN_API_KEY}
      - DATABASE_URL=${DATABASE_URL:-bolt://memgraph:7687}
      - DATABASE_USER=${DATABASE_USER}
      - DATABASE_PASSWORD=${DATABASE_PASSWORD}
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
    volumes:
      - ./data:/app/data
      - ./.env:/app/.env
    depends_on:
      - memgraph
    command: python main.py --help

  memgraph:
    image: memgraph/memgraph:latest
    container_name: rag-memgraph
    ports:
      - "7687:7687"
      - "7444:7444"
    volumes:
      - memgraph_data:/var/lib/memgraph
      - ./memgraph.conf:/etc/memgraph/memgraph.conf

volumes:
  memgraph_data:
```

### 4. Running Commands in Docker

To run commands in the Docker container:

```bash
# Index a document
docker exec -it rag-backend python main.py indexing --name my_collection --file /app/data/document.pdf

# Search documents
docker exec -it rag-backend python main.py search --name my_collection --question "What is this about?"

# Chat with documents
docker exec -it rag-backend python main.py chat --name my_collection --question "Can you explain this?"
```

## Production Deployment

### 1. Infrastructure Requirements

For production deployment, you'll need:

- **Application Server**: Linux server with Python 3.12+
- **Database Server**: Memgraph database (can be hosted or self-managed)
- **Load Balancer**: For handling multiple instances (optional)
- **Monitoring**: For system health and performance metrics

### 2. Environment Setup

#### Install System Dependencies

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y python3.12 python3.12-venv build-essential

# Install uv package manager
pip install uv
```

#### Create Virtual Environment

```bash
python3.12 -m venv venv
source venv/bin/activate
```

#### Install Application Dependencies

```bash
uv sync
```

### 3. Configuration Management

In production, manage configuration through:

1. **Environment Variables**: Set through your deployment platform
2. **Secrets Management**: Use your platform's secrets management (AWS Secrets Manager, Azure Key Vault, etc.)
3. **Configuration Files**: Mount configuration files as volumes

### 4. Process Management

Use a process manager like systemd or supervisor to manage the application:

#### systemd Service File

Create `/etc/systemd/system/rag-backend.service`:

```ini
[Unit]
Description=RAG Backend Service
After=network.target

[Service]
Type=simple
User=rag
WorkingDirectory=/opt/rag-backend
Environment=QWEN_API_KEY=your-api-key
Environment=DATABASE_URL=bolt://localhost:7687
ExecStart=/opt/rag-backend/venv/bin/python main.py --help
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl enable rag-backend
sudo systemctl start rag-backend
```

## Environment Configuration

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `QWEN_API_KEY` | DashScope API key for Qwen models | `sk-xxxxxxxx` |
| `DATABASE_URL` | Memgraph database connection URL | `bolt://localhost:7687` |
| `DATABASE_USER` | Database username (if required) | `memgraph` |
| `DATABASE_PASSWORD` | Database password (if required) | `password` |

### Optional Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LOG_LEVEL` | Logging level | `INFO` |
| `LOG_FILE` | Log file path | None (console only) |
| `MAX_CHUNK_SIZE` | Maximum document chunk size | `1000` |
| `MAX_CONCURRENT_REQUESTS` | Maximum concurrent API requests | `10` |
| `DEBUG` | Enable debug mode | `false` |

### Example .env File

```env
# Qwen Configuration
QWEN_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_API_KEY=your-api-key-here

# Memgraph Database
DATABASE_URL=bolt://127.0.0.1:7687
DATABASE_USER=
DATABASE_PASSWORD=

# Optional Configuration
LOG_LEVEL=INFO
LOG_FILE=/var/log/rag-backend.log
DEBUG=false
MAX_CHUNK_SIZE=1000
MAX_CONCURRENT_REQUESTS=10
```

## Database Setup

### Local Development Database

For local development, run Memgraph in Docker:

```bash
docker run -d -p 7687:7687 -p 7444:7444 --name memgraph memgraph/memgraph
```

### Production Database

For production, you can:

1. **Self-host Memgraph**: Install Memgraph on a dedicated server
2. **Use Managed Service**: If available from your cloud provider

#### Installing Memgraph on Ubuntu

```bash
wget https://download.memgraph.com/memgraph/v2.10.0/ubuntu-20.04/memgraph_2.10.0-1_amd64.deb
sudo dpkg -i memgraph_2.10.0-1_amd64.deb
sudo systemctl start memgraph
sudo systemctl enable memgraph
```

### Database Configuration

Memgraph configuration can be customized using a configuration file. Create `memgraph.conf`:

```conf
# Memgraph configuration
--bolt-port=7687
--http-port=7444
--log-level=INFO
--memory-limit=2048
```

Mount this configuration file when running Memgraph:

```bash
docker run -d -p 7687:7687 -p 7444:7444 \
  -v ./memgraph.conf:/etc/memgraph/memgraph.conf \
  --name memgraph memgraph/memgraph
```

## Monitoring and Logging

### Application Logging

The application uses structured logging with the following levels:

- **DEBUG**: Detailed information for diagnosing problems
- **INFO**: General information about application operation
- **WARNING**: Warning messages about potential issues
- **ERROR**: Error messages about serious problems
- **CRITICAL**: Critical errors that may require immediate attention

### Log Output

Logs can be directed to:

1. **Console**: Default output
2. **File**: Configure `LOG_FILE` environment variable
3. **External Systems**: Use log aggregation tools like Fluentd, Logstash, etc.

### Performance Monitoring

The application includes built-in monitoring capabilities:

- **Function Timing**: Tracks execution time of key functions
- **System Metrics**: Monitors CPU, memory, and thread usage
- **Rate Limiting**: Tracks API request rates
- **Error Tracking**: Counts and categorizes errors

### External Monitoring

For production deployments, integrate with monitoring systems:

- **Prometheus**: Export metrics for collection
- **Grafana**: Visualize metrics and create dashboards
- **ELK Stack**: Centralized log management
- **Datadog/New Relic**: Comprehensive application monitoring

## Security Considerations

### API Security

1. **Rate Limiting**: Built-in rate limiting prevents abuse
2. **Input Validation**: All inputs are validated and sanitized
3. **Authentication**: API key authentication for external services

### Data Security

1. **Encryption**: Sensitive data is encrypted at rest and in transit
2. **Access Control**: Database access is controlled through authentication
3. **Audit Logging**: Security-relevant events are logged

### Network Security

1. **Firewall Rules**: Restrict access to necessary ports only
2. **TLS/SSL**: Use encrypted connections for all external communication
3. **Private Networks**: Deploy services on private networks when possible

### Secrets Management

Never hardcode secrets in the application. Use:

1. **Environment Variables**: For simple deployments
2. **Secrets Management Services**: For production deployments
3. **Vault Solutions**: HashiCorp Vault, AWS Secrets Manager, etc.

## Scaling and Performance

### Horizontal Scaling

The application can be scaled horizontally by:

1. **Multiple Instances**: Run multiple application instances
2. **Load Balancer**: Distribute requests across instances
3. **Shared Database**: All instances connect to the same database

### Performance Optimization

1. **Caching**: Implement caching for frequently accessed data
2. **Database Indexing**: Ensure proper database indexing
3. **Connection Pooling**: Use database connection pooling
4. **Asynchronous Processing**: For long-running operations

### Resource Requirements

#### Minimum Requirements

- **CPU**: 2 cores
- **Memory**: 4 GB RAM
- **Storage**: 10 GB disk space

#### Recommended Requirements

- **CPU**: 4 cores
- **Memory**: 8 GB RAM
- **Storage**: 50 GB disk space (SSD recommended)

## Backup and Recovery

### Data Backup

1. **Database Backup**: Regular Memgraph database backups
2. **Configuration Backup**: Backup environment files and configuration
3. **Document Storage**: Backup indexed documents if stored locally

### Database Backup Procedure

```bash
# Create a backup of the Memgraph database
docker exec memgraph mg_dump > backup_$(date +%Y%m%d_%H%M%S).cypher

# Restore from backup
docker exec -i memgraph mg_import_csv < backup_file.cypher
```

### Disaster Recovery

1. **Automated Backups**: Schedule regular automated backups
2. **Off-site Storage**: Store backups in multiple locations
3. **Recovery Testing**: Regularly test backup restoration
4. **Documentation**: Maintain detailed recovery procedures

## Troubleshooting

### Common Issues

1. **Database Connection Failed**: Check database URL and credentials
2. **API Key Invalid**: Verify Qwen API key is correct and active
3. **Insufficient Memory**: Increase system memory or reduce chunk size
4. **Rate Limit Exceeded**: Reduce request frequency or increase limits

### Debugging

1. **Enable Debug Logging**: Set `LOG_LEVEL=DEBUG`
2. **Check Application Logs**: Review log output for error messages
3. **Verify Configuration**: Ensure all required environment variables are set
4. **Test Components**: Test individual components in isolation

### Support

For issues and feature requests, please [open an issue](../../issues) on GitHub.