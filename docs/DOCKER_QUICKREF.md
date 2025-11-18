# Docker Quick Reference

Quick commands for managing meter2mqtt in Docker.

## Basic Operations

### Start Services

```bash
# Start all services (MQTT + meter2mqtt + Home Assistant)
docker-compose up -d

# Start specific service
docker-compose up -d meter2mqtt
docker-compose up -d mosquitto

# Build and start
docker-compose up -d --build

# Start in foreground (show logs)
docker-compose up
```

### Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Stop specific service
docker-compose stop meter2mqtt
docker-compose kill meter2mqtt
```

### View Logs

```bash
# All services
docker-compose logs

# Specific service
docker-compose logs meter2mqtt
docker-compose logs mosquitto

# Follow logs (tail -f)
docker-compose logs -f meter2mqtt

# Last 50 lines
docker-compose logs --tail=50 meter2mqtt

# Logs from last 10 minutes
docker-compose logs --since 10m meter2mqtt
```

### Status & Inspection

```bash
# Show running containers
docker-compose ps

# Show all containers (including stopped)
docker-compose ps -a

# Resource usage
docker stats

# Container details
docker-compose exec meter2mqtt ps aux
docker inspect meter2mqtt
```

## Configuration

### Edit Configs (host)

```bash
# Edit main config
nano config.yaml

# Edit device config
nano config.d/kitchen_heater.yaml

# Changes take effect after:
docker-compose restart meter2mqtt
```

### Check Config Inside Container

```bash
# View config inside container
docker-compose exec meter2mqtt cat /app/config.yaml

# List device configs
docker-compose exec meter2mqtt ls -la /app/config.d/
```

## Serial Ports

### Find Serial Ports

```bash
# Linux
ls -la /dev/ttyUSB*
ls -la /dev/ttyACM*

# macOS
ls -la /dev/tty.*

# Show which device is which
dmesg | grep tty
lsof | grep tty
```

### Mount Serial Port

In `docker-compose.yaml`, add to `volumes`:

```yaml
meter2mqtt:
  volumes:
    - /dev/ttyUSB0:/dev/ttyUSB0
    - /dev/ttyACM0:/dev/ttyACM0
```

### Test Serial Port

```bash
# Install tools
sudo apt install minicom

# Test connection
minicom -D /dev/ttyUSB0 -b 9600

# Alternative: picocom
picocom -b 9600 /dev/ttyUSB0
```

## MQTT Operations

### Subscribe to Topics

```bash
# All topics
docker exec mosquitto mosquitto_sub -h mosquitto -t '#' -v

# Specific meter
docker exec mosquitto mosquitto_sub -h mosquitto -t 'meters/multical/#' -v

# Specific parameter
docker exec mosquitto mosquitto_sub -h mosquitto -t 'meters/multical/kitchen_heater/energy' -v
```

### Publish Test Message

```bash
docker exec mosquitto mosquitto_pub -h mosquitto -t test/topic -m "Hello"
```

### Check MQTT Logs

```bash
docker-compose logs mosquitto
docker exec mosquitto tail -f /mosquitto/log/mosquitto.log
```

## Troubleshooting

### Check if Container Started

```bash
docker-compose ps meter2mqtt

# Check exit code
docker-compose ps | grep meter2mqtt
# 0 = running, other = error
```

### View Startup Errors

```bash
# If container exited
docker-compose logs meter2mqtt

# Re-run with debug
docker-compose up --no-detach meter2mqtt
```

### Verify Network Connection

```bash
# Test DNS
docker-compose exec meter2mqtt ping mosquitto

# Test MQTT connection
docker-compose exec meter2mqtt nc -zv mosquitto 1883

# List network
docker network ls
docker network inspect meter2mqtt_meter2mqtt_network
```

### Fix Serial Port Permissions

```bash
# Add user to dialout group (Linux)
sudo usermod -aG dialout $USER
newgrp dialout

# Or run as root in docker-compose.yaml
meter2mqtt:
  user: "0"
```

### Rebuild Container

```bash
# Rebuild image (fresh)
docker-compose build --no-cache meter2mqtt

# Rebuild and restart
docker-compose up -d --build meter2mqtt

# Remove old images
docker system prune
```

### Resource Issues

```bash
# Check container stats
docker stats meter2mqtt

# Restart if using too much memory
docker-compose restart meter2mqtt

# Check swap usage
free -h
```

## Advanced Operations

### Execute Command in Container

```bash
# Interactive shell
docker-compose exec meter2mqtt /bin/sh

# Run command
docker-compose exec meter2mqtt python -c "import sys; print(sys.version)"

# List environment
docker-compose exec meter2mqtt env
```

### View Container Filesystem

```bash
# List directory
docker-compose exec meter2mqtt ls -la /app

# View file
docker-compose exec meter2mqtt cat /app/config.yaml
```

### Backup & Restore

```bash
# Backup configuration
tar czf config-backup.tar.gz config.yaml config.d/

# Backup MQTT data
docker run --rm -v meter2mqtt_mosquitto_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/mosquitto-backup.tar.gz -C /data .

# Restore
tar xzf config-backup.tar.gz
```

### Update Image

```bash
# Pull latest images
docker-compose pull

# Restart with latest
docker-compose up -d
```

## Docker-Compose File Operations

### Validate Configuration

```bash
docker-compose config

# Show merged configuration
docker-compose config --resolve-image-digests
```

### Show Services

```bash
docker-compose config --services
```

### View Environment

```bash
docker-compose exec meter2mqtt env | sort
```

## Cleanup

### Remove Everything

```bash
# Stop and remove containers, networks
docker-compose down

# Remove volumes too
docker-compose down -v

# Remove images too
docker-compose down -v --rmi all

# System-wide cleanup
docker system prune -a
```

### Remove Specific Container

```bash
docker-compose rm meter2mqtt
docker rm meter2mqtt
```

### Remove Volumes

```bash
# List volumes
docker volume ls | grep meter2mqtt

# Remove specific volume
docker volume rm meter2mqtt_mosquitto_data
```

## Environment Variables

### Set in Docker Compose

```yaml
meter2mqtt:
  environment:
    - TZ=Europe/Amsterdam
    - LOG_LEVEL=DEBUG
```

### From .env File

Create `.env`:
```
TZ=Europe/Amsterdam
MQTT_HOST=mosquitto
```

### View Set Variables

```bash
docker-compose exec meter2mqtt env | grep LOG
```

## Performance Tuning

### Limit Resources

```yaml
meter2mqtt:
  deploy:
    resources:
      limits:
        cpus: '0.5'
        memory: 256M
```

### Monitor Performance

```bash
# Real-time stats
docker stats --no-stream

# Historical stats
docker stats meter2mqtt --no-stream >> stats.log
```

## Common Commands Summary

| Task | Command |
|------|---------|
| Start all | `docker-compose up -d` |
| Stop all | `docker-compose down` |
| View logs | `docker-compose logs -f meter2mqtt` |
| Restart | `docker-compose restart meter2mqtt` |
| Rebuild | `docker-compose build --no-cache` |
| Shell | `docker-compose exec meter2mqtt /bin/sh` |
| Status | `docker-compose ps` |
| MQTT test | `docker exec mosquitto mosquitto_sub -h mosquitto -t '#'` |
| Cleanup | `docker-compose down -v` |
| Config check | `docker-compose config` |

## Need More Help?

- See [DOCKER_GUIDE.md](DOCKER_GUIDE.md) for detailed documentation
- Check logs: `docker-compose logs meter2mqtt`
- Review config: `docker-compose config`
- Inspect container: `docker inspect meter2mqtt`
