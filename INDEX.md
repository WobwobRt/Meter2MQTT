# Meter2MQTT Documentation Index

## Quick Reference

### Getting Started

1. **[SETUP.md](SETUP.md)** - Installation and quick start
2. **[README.md](README.md)** - Project overview and features
3. **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Complete project overview

### Technical Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design and components

### Configuration Examples

- **config.yaml.example** - Base configuration template
- **config.d/dsmr.yaml.example** - Example device configuration

### Source Code

```
src/meter2mqtt/
├── __main__.py          # Daemon entry point
├── config.py            # Configuration loader
├── mqtt.py              # MQTT handler
├── devices/
│   ├── base.py          # BaseDevice abstraction
│   ├── factory.py       # Device factory
│   ├── dsmr.py          # DSMR implementation
│   └── lifecycle.py     # Device lifecycle manager
└── extensions/          # Optional integrations
```

## Quick Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Setup configs
cp config.yaml.example config.yaml
mkdir -p config.d
cp config.d/dsmr.yaml.example config.d/dsmr.yaml

# Run daemon
python -m meter2mqtt

# Watch logs
tail -f /var/log/meter2mqtt.log

# Subscribe to metrics
mosquitto_sub -t 'meters/#'
```

## Key Concepts

### Device Types

Each device type inherits from `BaseDevice` and implements:
- `connect()` / `disconnect()` - Connection management
- `read()` - Read current values
- `get_available_parameters()` - List readable params
- `get_device_type()` - Return type identifier

### Configuration Files

- **Base config** (`config.yaml`): MQTT, logging, global settings
- **Device configs** (`config.d/*.yaml`): One file per device
- **Hot-reload**: File changes detected automatically

### MQTT Publishing

All metrics published to:
```
meters/<device_type>/<device_id>/<parameter>
```

### Device Lifecycle

```
config.d/meter.yaml created
    ↓
File watcher detects (debounced)
    ↓
Device instantiated
    ↓
connect() called
    ↓
Added to active devices
    ↓
read() called per poll_interval
    ↓
Metrics published to MQTT
```

## Extending Meter2MQTT

### Add New Device Type

1. Create `src/meter2mqtt/devices/mydevice.py`
2. Implement `BaseDevice`
3. Register: `register_device_type("mydevice", MyDeviceClass)`
4. Create `config.d/mydevice.yaml`

### Add Extensions

Create `src/meter2mqtt/extensions/my_extension.py` for:
- Home Assistant MQTT Discovery
- InfluxDB publishing
- Prometheus exporting
- Custom integrations

## Status

- ✅ Architecture implemented
- ✅ DSMR support ready
- ⏳ Multical adapter (wrapper to kamstrup2mqtt)
- ⏳ Home Assistant extension
- ⏳ Additional device types

## Support

- Check logs for errors: `grep ERROR /var/log/meter2mqtt.log`
- See ARCHITECTURE.md for technical details
- See SETUP.md for troubleshooting
