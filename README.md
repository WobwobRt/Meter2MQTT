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

```bash
# Install
pip install -r requirements.txt

# Configure
cp config.yaml.example config.yaml
mkdir -p config.d
cp config.d/multical.yaml.example config.d/multical.yaml

# Run
python -m meter2mqtt.daemon
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

## Architecture

See `ARCHITECTURE.md` for detailed design documentation.

## License

[Your License]

## Contributing

Contributions welcome! See CONTRIBUTING.md
