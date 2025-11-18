# Multi-stage build for meter2mqtt
# Stage 1: Builder
FROM python:3-alpine AS builder

WORKDIR /build

# Install build dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    linux-headers

# Copy requirements
COPY requirements.txt .

# Build wheels for all dependencies
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /build/wheels -r requirements.txt


# Stage 2: Runtime
FROM python:3-alpine

WORKDIR /app

# Install runtime dependencies only
RUN apk add --no-cache \
    libusb

# Copy wheels from builder
COPY --from=builder /build/wheels /wheels

# Install Python dependencies from wheels
RUN pip install --no-cache /wheels/* \
    && rm -rf /wheels

# Copy application code
COPY src/ /app/src/
COPY requirements.txt /app/

# Create non-root user for security
RUN addgroup -g 1000 meter2mqtt \
    && adduser -D -u 1000 -G meter2mqtt meter2mqtt

USER meter2mqtt

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import socket; socket.create_connection(('localhost', 1883), timeout=5)" || exit 1

# Set Python to unbuffered mode for Docker logs
ENV PYTHONUNBUFFERED=1

# Run the application
ENTRYPOINT ["python", "-m", "meter2mqtt"]
