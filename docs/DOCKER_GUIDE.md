# Docker Deployment Guide

Complete guide for running meter2mqtt in Docker with optional Home Assistant integration.

## Table of Contents

- [Quick Start](#quick-start)
- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [Running](#running)
- [Configuration](#configuration)
- [Serial Devices](#serial-devices)
- [Home Assistant Integration](#home-assistant-integration)
- [Troubleshooting](#troubleshooting)
- [Production Deployment](#production-deployment)

## Quick Start

```bash
# Clone and navigate
git clone https://github.com/WobwobRt/meter2mqtt.git
cd meter2mqtt

# Copy example configs
cp config.yaml.example config.yaml
mkdir -p config.d
cp config.d/multical.yaml.example config.d/multical.yaml

# Start containers
docker-compose up -d

# View logs
docker-compose logs -f meter2mqtt
```

## Prerequisites

- Docker Engine 20.10+ or Docker Desktop
- Docker Compose 1.29+
- Serial meter device (e.g., Multical, DSMR meter)
- MQTT broker (included in docker-compose or external)

### Install Docker

**Ubuntu/Debian:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

**macOS:**
```bash
brew install docker docker-compose
```

**Windows:**
Download [Docker Desktop](https://www.docker.com/products/docker-desktop)

## Setup

### 1. Clone Repository

```bash
git clone https://github.com/WobwobRt/meter2mqtt.git
cd meter2mqtt
```

### 2. Create Configuration Files

```bash
# Copy main config
cp config.yaml.example config.yaml

# Create device configs directory
mkdir -p config.d

# Copy device examples
cp config.d/multical.yaml.example config.d/multical.yaml
cp config.d/dsmr.yaml.example config.d/dsmr.yaml
```

### 3. Edit Configuration Files

Edit `config.yaml` for MQTT broker settings:

```yaml
mqtt:
  host: mosquitto          # Use 'mosquitto' for docker-compose
  port: 1883
  client_id: meter2mqtt
  topic_prefix: meters
  ha_discovery_prefix: homeassistant

logging:
  level: INFO
  file: /app/logs/meter2mqtt.log
```

Edit `config.d/multical.yaml` for your meter:

```yaml
device:
  type: multical
  device_id: kitchen_heater
  
  connection:
    port: /dev/ttyUSB0
    baudrate: 9600
  
  poll_interval: 30
```

## Running

### Start All Services

```bash
# Start in background
docker-compose up -d

# View logs
docker-compose logs -f
```

### Start Only meter2mqtt (with existing MQTT)

```bash
docker-compose up -d meter2mqtt
```

### Start Only MQTT Broker

```bash
docker-compose up -d mosquitto
```

### Stop Services

```bash
# Stop all
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Stop and remove everything (including images)
docker-compose down -v --rmi all
```

### View Logs

```bash
# All services
docker-compose logs

# Specific service
docker-compose logs meter2mqtt
docker-compose logs mosquitto

# Follow logs in real-time
docker-compose logs -f meter2mqtt

# Last N lines
docker-compose logs --tail=50 meter2mqtt
```

## Configuration

### MQTT Connection

Edit `config.yaml` to connect to different MQTT broker:

**Using external MQTT broker:**
```yaml
mqtt:
  host: 192.168.1.100      # External IP
  port: 1883
  username: mqtt_user       # Optional
  password: mqtt_pass       # Optional
```

**Using docker-compose MQTT:**
```yaml
mqtt:
  host: mosquitto          # Service name in docker-compose
  port: 1883
```

### Device Configuration

Create separate YAML file for each device in `config.d/`:

**For Multical heat meter:**
```yaml
# config.d/kitchen_heater.yaml
device:
  type: multical
  device_id: kitchen_heater
  
  connection:
    port: /dev/ttyUSB0
    baudrate: 9600
  
  parameters:
    - energy
    - power
    - temperature_1
    - temperature_2
    - volume
    - flow
  
  poll_interval: 30
```

**For DSMR electricity meter:**
```yaml
# config.d/electricity.yaml
device:
  type: dsmr
  device_id: electricity
  
  connection:
    port: /dev/ttyUSB0
    baudrate: 115200
  
  poll_interval: 10
```

### Resource Limits

Adjust in `docker-compose.yaml`:

```yaml
meter2mqtt:
  deploy:
    resources:
      limits:
        cpus: '0.5'        # Max 50% CPU
        memory: 256M       # Max 256MB RAM
      reservations:
        cpus: '0.25'
        memory: 128M
```

## Serial Devices

### Identify Serial Ports

**Linux:**
```bash
# List serial devices
ls -la /dev/ttyUSB*
ls -la /dev/ttyACM*

# Find device info
dmesg | grep tty
```

**macOS:**
```bash
ls -la /dev/tty.*
ls -la /dev/cu.*
```

### Mount in Docker

In `docker-compose.yaml`:

```yaml
meter2mqtt:
  volumes:
    - /dev/ttyUSB0:/dev/ttyUSB0
    - /dev/ttyACM0:/dev/ttyACM0
```

### Permissions Issues

If you get permission denied errors:

**Linux (add user to dialout group):**
```bash
sudo usermod -aG dialout $USER
newgrp dialout
```

**Docker compose workaround:**
```yaml
meter2mqtt:
  user: "0"  # Run as root (less secure)
```

### Testing Connection

```bash
# Install minicom or picocom
sudo apt install minicom

# Test serial port
minicom -D /dev/ttyUSB0 -b 9600
```

## Home Assistant Integration

### Enable Home Assistant Service

Uncomment in `docker-compose.yaml`:

```yaml
homeassistant:
  image: homeassistant/home-assistant:latest
  container_name: homeassistant
  depends_on:
    - mosquitto
  ports:
    - "8123:8123"
  # ... rest of config
```

### Start Services

```bash
docker-compose up -d
```

### Initial Setup

1. Open http://localhost:8123
2. Follow Home Assistant setup wizard
3. Configure MQTT integration:
   - Host: `mosquitto`
   - Port: `1883`
   - Username/Password: (if configured)

### Verify MQTT Discovery

In Home Assistant:
1. Go to Settings → Devices & Services
2. Look for discovered devices from meter2mqtt
3. Each meter should appear as a separate device
4. Entities should be grouped under the device

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs meter2mqtt

# Validate config
docker-compose config

# Rebuild image
docker-compose build --no-cache
```

### Serial Port Issues

```bash
# Check port permissions
ls -la /dev/ttyUSB0

# Check if port is in use
lsof /dev/ttyUSB0

# Try different port
docker exec meter2mqtt dmesg | grep tty
```

### MQTT Connection Failed

```bash
# Check MQTT container
docker-compose logs mosquitto

# Test connection
docker exec mosquitto mosquitto_sub -h localhost -t test

# Check network
docker-compose exec meter2mqtt ping mosquitto
```

### High CPU/Memory Usage

```bash
# Check resource usage
docker stats

# Reduce poll interval in config
poll_interval: 60  # Increase from 30
```

### Missing Data in MQTT

```bash
# Subscribe to MQTT topic
docker exec mosquitto mosquitto_sub -h localhost -t 'meters/#' -v

# Check application logs
docker-compose logs -f meter2mqtt

# Enable debug logging (in config.yaml)
logging:
  level: DEBUG
```

## Production Deployment

### Security Hardening

1. **Enable MQTT Authentication**

```bash
# Generate password hash
docker exec mosquitto mosquitto_passwd -c /mosquitto/data/passwd meter2mqtt
```

Update `mosquitto.conf`:
```
password_file /mosquitto/data/passwd
allow_anonymous false
```

2. **Use Environment Variables for Secrets**

```bash
# Create .env file
cat > .env << EOF
MQTT_HOST=mosquitto
MQTT_USERNAME=meter2mqtt
MQTT_PASSWORD=your_secure_password
HA_TOKEN=your_long_lived_token
EOF

# In docker-compose.yaml
meter2mqtt:
  environment:
    - MQTT_PASSWORD=${MQTT_PASSWORD}
```

3. **Enable TLS/SSL**

Mount certificates in docker-compose:
```yaml
mosquitto:
  volumes:
    - /path/to/cert.pem:/mosquitto/config/certs/cert.pem:ro
    - /path/to/key.pem:/mosquitto/config/certs/key.pem:ro
```

### Backup Strategy

```bash
# Backup volumes
docker run --rm -v meter2mqtt_mosquitto_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/mosquitto-backup.tar.gz -C /data .

# Backup configuration
tar czf config-backup.tar.gz config.yaml config.d/

# Restore
tar xzf config-backup.tar.gz
```

### Monitoring

Add health checks to `docker-compose.yaml`:

```yaml
meter2mqtt:
  healthcheck:
    test: ["CMD", "ps", "aux"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 10s
```

Monitor with:
```bash
docker ps --all  # Show health status
docker stats     # Monitor resource usage
```

### Logging

Enable centralized logging:

```yaml
meter2mqtt:
  logging:
    driver: "json-file"
    options:
      max-size: "10m"
      max-file: "3"
```

View logs:
```bash
docker logs meter2mqtt --tail 100 -f
journalctl -u docker -f  # System logs
```

### Restart Policy

```yaml
meter2mqtt:
  restart: unless-stopped  # Restart on failure
```

Options:
- `no` - Don't restart
- `always` - Always restart
- `unless-stopped` - Restart unless explicitly stopped
- `on-failure` - Restart on failure

## Advanced Usage

### Build Custom Image

```bash
# Build with custom Python version
docker build --build-arg PYTHON_VERSION=3.11 -t meter2mqtt:latest .
```

### Run Single Container (no compose)

```bash
# Build image
docker build -t meter2mqtt:latest .

# Run container
docker run -d \
  --name meter2mqtt \
  --device /dev/ttyUSB0 \
  -v $(pwd)/config.yaml:/app/config.yaml:ro \
  -v $(pwd)/config.d:/app/config.d:ro \
  -e MQTT_HOST=192.168.1.100 \
  meter2mqtt:latest
```

### Development Mode

Mount source code for live development:

```yaml
meter2mqtt:
  build: .
  volumes:
    - ./src:/app/src          # Live code editing
    - ./config.yaml:/app/config.yaml:ro
    - ./config.d:/app/config.d:ro
```

Rebuild on changes:
```bash
docker-compose build meter2mqtt
docker-compose up -d meter2mqtt
```

## Support

For issues:
1. Check logs: `docker-compose logs meter2mqtt`
2. Review docs: [../docs/](../docs/)
3. Open issue on GitHub
4. Check CONTRIBUTING.md for guidelines
