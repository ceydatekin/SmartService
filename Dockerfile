FROM python:3.9-slim

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy proto files first
COPY src/proto /app/src/proto/

# Generate proto files
RUN python -m grpc_tools.protoc \
    --proto_path=/app/src/proto \
    --python_out=/app/src \
    --grpc_python_out=/app/src \
    /app/src/proto/smart_service.proto

# Copy rest of the source code
COPY src/ /app/src/

# Create necessary directories
RUN mkdir -p /app/logs

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Command to run the service
CMD ["python", "-m", "src.main"]