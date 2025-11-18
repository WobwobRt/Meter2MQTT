# Meter2MQTT

A pluggable, multi-device meter aggregation gateway that publishes readings to MQTT. Read multiple meters (Multical, DSMR, Warmtelink, etc.) from your meter cupboard and publish all readings via MQTT.

## Features

- **Multi-device support**: Simultaneously read from multiple meter types
- **Hot-reload configuration**: Add/remove/modify devices without restarting
- **Pluggable architecture**: Easy to add new device types
- **MQTT-first design**: All metrics published to MQTT
- **Home Assistant ready**: Optional MQTT Discovery support
- **File-watching dynamic config**: Traefik-style configuration
- **Per-device polling**: Each device has independent polling interval

## Supported Devices

- **Multical** - Kamstrup heat meters (402, 403, 603)
- **DSMR** - Dutch Smart Meter Requirements (electricity/gas)
- **Warmtelink** - Heat allocation meters (planned)
- Custom device types (extensible)

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone repository
git clone https://github.com/WobwobRt/meter2mqtt.git
cd meter2mqtt

# Copy example configs
cp config.yaml.example config.yaml
mkdir -p config.d
cp config.d/multical.yaml.example config.d/multical.yaml

# Edit config.yaml and config.d/*.yaml for your setup

# Start services (includes MQTT broker and optional Home Assistant)
docker-compose up -d

# View logs
docker-compose logs -f meter2mqtt
```

See [DOCKER_GUIDE.md](docs/DOCKER_GUIDE.md) for detailed Docker documentation.

### Option 2: Native Python

```bash
# Install dependencies
pip install -r requirements.txt

# Configure
cp config.yaml.example config.yaml
mkdir -p config.d
cp config.d/multical.yaml.example config.d/multical.yaml

# Run application
python -m meter2mqtt
```

## Configuration

### Base Config (`config.yaml`)

Global MQTT, logging, and Home Assistant settings.

### Device Configs (`config.d/*.yaml`)

One YAML file per device. Filename (without extension) becomes device ID.

Example: `config.d/kitchen_heater.yaml` → device ID is `kitchen_heater`

### Dynamic Reload

Just drop a new config file in `config.d/` and it will be loaded automatically. No daemon restart needed!

## MQTT Topic Structure

```
meters/<device_type>/<device_id>/<parameter>
```

Examples:
```
meters/multical/kitchen_heater/energy
meters/multical/kitchen_heater/power
meters/dsmr/electricity/current_usage
meters/dsmr/electricity/gas_provided
```

## Documentation

Comprehensive documentation is available in the [`docs/`](docs/) directory:

### Getting Started
- **[SETUP.md](docs/SETUP.md)** - Installation and configuration guide
- **[QUICK_START.md](docs/QUICK_START.md)** - Get up and running in 5 minutes

### Device Guides
- **[MULTICAL_GUIDE.md](docs/MULTICAL_GUIDE.md)** - Kamstrup Multical heat meter setup
- **[DSMR_GUIDE.md](docs/DSMR_GUIDE.md)** - Dutch Smart Meter setup

### Home Assistant Integration
- **[HA_INTEGRATION.md](docs/HA_INTEGRATION.md)** - Full Home Assistant setup guide
- **[HA_DISCOVERY_QUICKREF.md](docs/HA_DISCOVERY_QUICKREF.md)** - Quick reference for MQTT Discovery
- **[MQTT_HA_DISCOVERY.md](docs/MQTT_HA_DISCOVERY.md)** - Complete MQTT Discovery API reference

### Architecture & Development
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System design and architecture
- **[CONTRIBUTING.md](docs/CONTRIBUTING.md)** - Contributing guide and device support walkthrough
- **[PROJECT_SUMMARY.md](docs/PROJECT_SUMMARY.md)** - Project overview and status

### Examples
- **[examples/ha_discovery_example.py](examples/ha_discovery_example.py)** - Working Home Assistant MQTT Discovery example

## License

[Your License]

## Contributing

Contributions welcome! See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines on reporting bugs, suggesting features, and adding device support.
