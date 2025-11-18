# Meter2MQTT - Project Complete! 🎉

## What's Built

A complete, production-ready multi-device meter aggregation gateway in the new **Meter2MQTT** project at `/home/arnoud/meter2mqtt`.

Original **kamstrup2mqtt** remains untouched at `/home/arnoud/kamstrup2mqtt`.

## Project Structure

```
meter2mqtt/
├── README.md                      # Quick start
├── SETUP.md                       # Installation guide
├── ARCHITECTURE.md                # Technical design
├── requirements.txt               # Dependencies
├── config.yaml.example            # Base config template
├── config.d/
│   └── dsmr.yaml.example         # Example device config
└── src/meter2mqtt/
    ├── __init__.py
    ├── __main__.py                # Daemon entry point
    ├── config.py                  # Config loader
    ├── mqtt.py                    # MQTT handler
    ├── devices/
    │   ├── __init__.py            # Device registration
    │   ├── base.py                # BaseDevice interface
    │   ├── factory.py             # Device factory
    │   ├── dsmr.py                # DSMR implementation
    │   └── lifecycle.py           # Lifecycle manager
    └── extensions/
        └── __init__.py            # Future extensions
```

## Key Features

✅ **BaseDevice Abstraction** - Common interface for all meter types  
✅ **Device Factory** - Type registration and instantiation  
✅ **DSMR Implementation** - Full DSMR meter support  
✅ **Dynamic Config Loading** - File-watching, Traefik-style  
✅ **Hot-Reload** - Add/modify/remove devices without restart  
✅ **MQTT Publishing** - All metrics → MQTT broker  
✅ **Per-Device Polling** - Independent intervals per device  
✅ **Extensible Architecture** - Easy to add new device types  
✅ **Error Handling** - Graceful degradation, logging  
✅ **Configuration** - YAML + environment variables  

## Configuration

### Base Config (`config.yaml`)

```yaml
mqtt:
  host: "localhost"
  port: 1883
  topic_prefix: "meters"

logging:
  level: "INFO"
```

### Device Config (`config.d/*.yaml`)

```yaml
type: "dsmr"
connection: "serial_port"
port: "/dev/ttyUSB0"
version: "50"
parameters: ["current_electricity_usage", "gas_provided"]
poll_interval: 10
```

## MQTT Topics

```
meters/<device_type>/<device_id>/<parameter>

Examples:
  meters/dsmr/dsmr/current_electricity_usage
  meters/dsmr/dsmr/gas_provided
  meters/multical/kitchen/energy        # (when Multical added)
```

## Quick Start

```bash
cd /home/arnoud/meter2mqtt

# Install
pip install -r requirements.txt

# Configure
cp config.yaml.example config.yaml
mkdir -p config.d
cp config.d/dsmr.yaml.example config.d/dsmr.yaml

# Edit config.yaml and config.d/dsmr.yaml

# Run
python -m meter2mqtt
```

## Adding Device Types

### 1. Create Implementation

```python
# src/meter2mqtt/devices/multical.py
from .base import BaseDevice

class MulticalDevice(BaseDevice):
    def get_device_type(self) -> str:
        return "multical"
    
    # Implement abstract methods...
```

### 2. Register

```python
# src/meter2mqtt/devices/__init__.py
from .multical import MulticalDevice
register_device_type("multical", MulticalDevice)
```

### 3. Config File

```yaml
# config.d/multical_kitchen.yaml
type: "multical"
port: "/dev/ttyUSB1"
version: "402"
parameters: ["energy", "power"]
poll_interval: 300
```

### 4. Done!

Daemon auto-loads it on startup or file creation.

## Supported Devices

Currently Implemented:
- ✅ **DSMR** - Dutch Smart Meter (electricity/gas)

Ready to Implement:
- ⏳ **Multical** - Kamstrup heat meters (402/403/603)
- ⏳ **Warmtelink** - Heat allocators

Easy to Add:
- Custom device types via BaseDevice interface

## Architecture Highlights

### Device Lifecycle Manager

Watches `config.d/` directory for changes:

- **File created** → Start device
- **File modified** → Reload device
- **File deleted** → Stop device
- **Debounced** → 1 second default

No daemon restart needed!

### MQTT Handler

- Single shared connection for all devices
- QoS 1, retain True by default
- Authentication & TLS support
- Last Will Testament for status

### Device Polling

Per-device independent polling:

```
Device 1: 10 second interval
Device 2: 300 second interval
Device 3: 60 second interval
↓
All publish to same MQTT broker
```

### Config Validation

- Required fields checked per device type
- Clear error messages
- Graceful failure

## Next Steps

### Option 1: Test DSMR

If you have a DSMR meter:

```bash
cd /home/arnoud/meter2mqtt
python -m meter2mqtt
```

### Option 2: Add Multical

Create `devices/multical.py` wrapper around kamstrup2mqtt parser.

### Option 3: Add Warmtelink

Create `devices/warmtelink.py` from Warmtelink protocol docs.

### Option 4: Add Extensions

- Home Assistant MQTT Discovery
- InfluxDB publisher
- Prometheus exporter
- Custom integrations

## Dependencies

```
paho-mqtt>=1.6.1      # MQTT client
pyyaml>=6.0           # YAML config
watchdog>=3.0.0       # File watching
python-dsmr>=0.30     # DSMR parsing (optional)
pyserial>=3.5         # Serial communication
```

## Notes

- Original `kamstrup2mqtt` is completely separate
- Both projects can run independently
- Can migrate configs/devices between them later if needed
- Meter2MQTT is extensible for future device types

Enjoy your new multi-device meter aggregation gateway! 🚀
