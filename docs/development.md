# Developer Setup Guide

## Prerequisites
- Python 3.9+
- PostgreSQL 14+
- Redis
- Docker & Kubernetes
- gRPC tools

## Local Development Setup

### 1. Environment Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup
```bash
# Create database
createdb smartdb

# Set environment variables
export DATABASE_URL="postgresql://localhost/smartdb"
export REDIS_URL="redis://localhost:6379"
```

### 3. Running Tests
```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/
```

### 4. Local Development
```bash
# Generate proto files
python -m grpc_tools.protoc -I./proto --python_out=./src --grpc_python_out=./src ./proto/smart_service.proto

# Start service
python src/main.py
```

## Project Structure
```
smart-service/
├── src/
│   ├── domain/      # Domain models and rules
│   ├── services/    # Business logic
│   ├── integrations/# External integrations
│   └── utils/       # Shared utilities
├── tests/          # Test suite
├── kubernetes/     # K8s manifests
└── docs/           # Documentation
```

## Design Decisions

### 1. Architecture Choices
- **gRPC**: Chosen for efficient binary communication and strong typing
- **PostgreSQL**: Robust relational database with JSON support
- **Redis**: Fast in-memory caching for performance
- **Kubernetes**: Scalable container orchestration

### 2. Code Organization
- **Domain-Driven Design**: Clear separation of business logic
- **Service Layer Pattern**: Encapsulated business operations
- **Repository Pattern**: Data access abstraction
- **Factory Pattern**: For integration management

### 3. Testing Strategy
- **Unit Tests**: For business logic and domain rules
- **Integration Tests**: For external service interaction
- **Mock Objects**: For isolation and predictability

## Common Tasks
- Adding a new model type
- Implementing a new integration
- Adding API endpoints
- Deploying to production