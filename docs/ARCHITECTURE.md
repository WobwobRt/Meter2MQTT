# Meter2MQTT Architecture

Complete pluggable, multi-device meter aggregation gateway architecture.

## Overview

Meter2MQTT is designed to read multiple meters simultaneously and publish all readings to MQTT. It supports:

- **Multical** heat meters (via wrapper to kamstrup2mqtt)
- **DSMR** electricity meters (Dutch Smart Meter Requirements)
- **Custom device types** (extensible via BaseDevice interface)

## Core Components

### 1. Device Abstraction (`devices/base.py`)

All device types inherit from `BaseDevice`:

- `connect()` - Establish device connection
- `disconnect()` - Close connection
- `read()` - Read parameter values
- `get_available_parameters()` - List readable parameters
- `get_device_type()` - Return device type ID
- `get_poll_interval()` - Return read frequency
- `validate_config()` - Validate configuration

### 2. Device Factory (`devices/factory.py`)

Provides:

- Device registration: `register_device_type(type, class)`
- Device creation: `create_device(id, type, config)`
- Type discovery: `get_registered_device_types()`

### 3. Device Implementations

- `devices/dsmr.py` - Dutch Smart Meter
- `devices/multical.py` (planned) - Kamstrup heat meters
- Add custom types easily

### 4. Device Lifecycle Manager (`devices/lifecycle.py`)

Manages device lifecycle with **dynamic configuration**:

- **File watching**: Monitors `config.d/` directory
- **Hot-reload**: Automatic reload on config changes
- **Graceful reconciliation**: Start/reload/stop devices
- **Debouncing**: Groups rapid file changes

How it works:

1. Each YAML file in `config.d/` = one device
2. Filename (without .yaml) = device ID
3. File changes trigger automatic reload
4. Checksums detect real changes vs. file touches

### 5. MQTT Handler (`mqtt.py`)

Handles MQTT connection and publishing:

- Connection management
- QoS and retain settings
- Last Will Testament
- Authentication and TLS support

### 6. Daemon (`__main__.py`)

Central orchestrator:

- Loads base + device configs
- Manages MQTT connection
- Coordinates device polling
- Publishes metrics

## Configuration

### Base Config (`config.yaml`)

Global settings:

```yaml
mqtt:
  host: "localhost"
  port: 1883
  topic_prefix: "meters"

logging:
  level: "INFO"

homeassistant:
  enabled: false
```

### Device Configs (`config.d/*.yaml`)

One file per device. Example:

```yaml
type: "dsmr"
connection: "serial_port"
port: "/dev/ttyUSB0"
version: "50"
parameters:
  - "current_electricity_usage"
  - "gas_provided"
poll_interval: 10
```

## MQTT Topic Structure

```
meters/<device_type>/<device_id>/<parameter>
```

Examples:
```
meters/dsmr/dsmr_main/current_electricity_usage
meters/dsmr/dsmr_main/gas_provided
meters/multical/kitchen/energy
meters/multical/kitchen/power
```

## Adding a Device Type

### 1. Create implementation

```python
# devices/mydevice.py
from .base import BaseDevice

class MyDevice(BaseDevice):
    def get_device_type(self) -> str:
        return "mydevice"
    
    def connect(self) -> bool:
        # Connection logic
        pass
    
    # Implement other abstract methods...
```

### 2. Register

```python
# devices/__init__.py
register_device_type("mydevice", MyDevice)
```

### 3. Create config

```yaml
# config.d/my_device.yaml
type: "mydevice"
port: "/dev/ttyUSB1"
parameters: [...]
poll_interval: 60
```

### 4. Done!

Daemon auto-loads it on startup or when file is created.

## Dynamic Configuration

### Hot-reload

Just edit/create/delete config files in `config.d/`:

```bash
# Create new device
echo "type: dsmr
port: /dev/ttyUSB1
poll_interval: 10" > config.d/dsmr_bathroom.yaml

# Daemon detects and starts device automatically
```

### File watching

- Watches `config.d/` directory
- Debounces rapid changes (1 second default)
- Restarts device cleanly on config change
- No daemon restart needed

## Extensions

Optional integrations in `extensions/`:

- `ha_metadata.py` - Home Assistant MQTT Discovery (future)
- `influxdb.py` - InfluxDB publisher (future)
- `prometheus.py` - Prometheus exporter (future)

Extensions are only imported when needed.

## Running

```bash
# Install dependencies
pip install -r requirements.txt

# Copy example configs
cp config.yaml.example config.yaml
mkdir -p config.d
cp config.d/dsmr.yaml.example config.d/dsmr.yaml

# Run daemon
python -m meter2mqtt

# Or with custom paths
METER2MQTT_CONFIG=my_config.yaml METER2MQTT_CONFIG_DIR=/etc/meter2mqtt python -m meter2mqtt
```

## Logging

Logs show device lifecycle and metric publishing:

```
INFO - Meter2MQTT daemon started successfully
INFO - Base configuration loaded
INFO - Started watching config directory: config.d
DEBUG - Loaded device config: dsmr (type=dsmr)
INFO - Started device: dsmr (dsmr)
DEBUG - Publishing 'meters/dsmr/dsmr/current_electricity_usage': 2.34
```

Config changes are detected automatically:

```
DEBUG - Config file created: config.d/new_device.yaml
INFO - Started device: new_device (dsmr)
DEBUG - Config file modified: config.d/dsmr.yaml
INFO - Reloading device dsmr (config changed)
```

## Future Enhancements

- Per-device child processes (better isolation)
- Device status reporting to MQTT
- Batch metrics publishing
- Caching with timestamps
- Web API for device status
- Home Assistant MQTT Discovery
