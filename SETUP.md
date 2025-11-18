# Meter2MQTT Setup Guide

## Installation

### 1. Clone/Download

```bash
cd /home/arnoud
# Already created: /home/arnoud/meter2mqtt
```

### 2. Install Dependencies

```bash
cd /home/arnoud/meter2mqtt
pip install -r requirements.txt
```

### 3. Configure

Copy example configs:

```bash
cp config.yaml.example config.yaml
mkdir -p config.d
cp config.d/dsmr.yaml.example config.d/dsmr.yaml
```

### 4. Edit Configuration

**config.yaml** - MQTT broker settings:

```yaml
mqtt:
  host: "your-mqtt-broker"
  port: 1883
  topic_prefix: "meters"
```

**config.d/dsmr.yaml** - Your DSMR meter:

```yaml
type: "dsmr"
port: "/dev/ttyUSB0"  # Your serial port
version: "50"
parameters:
  - "current_electricity_usage"
  - "gas_provided"
poll_interval: 10
```

### 5. Run Daemon

```bash
python -m meter2mqtt
```

Output:
```
INFO - Meter2MQTT daemon started successfully
INFO - Base configuration loaded
INFO - Started device: dsmr (dsmr)
INFO - MQTT handler initialized
DEBUG - Publishing 'meters/dsmr/dsmr/current_electricity_usage': 2.34
```

## Adding More Devices

Simply create new YAML files in `config.d/`:

```bash
# Add Multical heat meter
cat > config.d/multical_kitchen.yaml <<EOF
type: "multical"
connection: "serial_port"
port: "/dev/ttyUSB1"
version: "402"
parameters:
  - "energy"
  - "power"
poll_interval: 300
EOF
```

Daemon detects and starts it automatically!

## Troubleshooting

### Device not starting

Check logs for errors:

```bash
python -m meter2mqtt 2>&1 | grep ERROR
```

Common issues:

- **"Unknown device type"**: Device type not registered
- **"Missing required config key"**: Check your YAML syntax
- **"Failed to open serial connection"**: Wrong port or permissions

### Serial port permissions

On Linux, add your user to the `dialout` group:

```bash
sudo usermod -a -G dialout $USER
# Logout and login for group to take effect
```

Or run as root (not recommended):

```bash
sudo python -m meter2mqtt
```

### MQTT not connecting

Check broker settings:

```bash
# Test MQTT connection
mosquitto_pub -h localhost -t test -m "hello"
```

## MQTT Topics

Your metrics appear at:

```
meters/dsmr/dsmr/current_electricity_usage
meters/dsmr/dsmr/gas_provided
meters/multical/kitchen/energy
meters/multical/kitchen/power
```

Subscribe to all:

```bash
mosquitto_sub -h localhost -t 'meters/#'
```

## Docker (Future)

A Dockerfile will be provided for containerized deployment.

## Support

See `ARCHITECTURE.md` for technical details.
