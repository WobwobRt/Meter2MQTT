# Home Assistant MQTT Discovery - Quick Reference

## What Changed

The `mqtt_handler` class now includes three new methods for Home Assistant MQTT Discovery:

### New Methods

1. **`publish_device_discovery(device_id, device_info, device_metadata)`**
   - Publishes Home Assistant entity discovery messages
   - Creates one entity per parameter
   - Automatically applies device classes and state classes

2. **`publish_device_value(device_id, parameter, value)`**
   - Publishes a single parameter value
   - Topic: `{topic_prefix}/{device_id}/{parameter}`

3. **`publish_device_status(device_id, status)`**
   - Publishes device status ("online" or "offline")
   - Topic: `{topic_prefix}/{device_id}/status`

## Basic Usage Pattern

```python
from meter2mqtt.devices import create_device
from meter2mqtt.devices.ha_metadata import get_parameter_metadata
from meter2mqtt.mqtt import mqtt_handler

# 1. Connect MQTT
mqtt = mqtt_handler(mqtt_config)
mqtt.connect()

# 2. Create device
device = create_device(device_id, device_type, device_config)
device.connect()

# 3. Publish discovery (once per device)
mqtt.publish_device_discovery(
    device_id=device_id,
    device_info=device.get_device_info(),
    device_metadata=get_parameter_metadata(device_type)
)

# 4. Publish values (per read cycle)
values = device.read()
for param, value in values.items():
    mqtt.publish_device_value(device_id, param, value)

mqtt.publish_device_status(device_id, "online")
```

## What Gets Created in Home Assistant

### Entities
For each parameter, Home Assistant creates an entity with:
- Device class (energy, power, temperature, etc.)
- State class (measurement, total, total_increasing)
- Unit of measurement
- Icon
- Availability tracking

### Device
All parameters are grouped under one device:
- Device name: `{device_id}` (formatted nicely)
- Manufacturer: From device info
- Model: From device info
- Identifiers: `[device_id]`

### Example for Multical
```
Device: Kitchen Heater (Kamstrup Multical 402)
├── Entity: Energy (kWh, device_class: energy)
├── Entity: Current Power (W, device_class: power)
├── Entity: Temperature 1 (°C, device_class: temperature)
├── Entity: Temperature 2 (°C, device_class: temperature)
├── Entity: Volume (m³, device_class: water)
├── Entity: Flow Rate (m³/h, device_class: volume_flow_rate)
└── Entity: Status (online/offline, device_class: connectivity)
```

## Configuration

### In config.yaml
```yaml
mqtt:
  host: localhost
  port: 1883
  topic_prefix: meter2mqtt
  ha_discovery_prefix: homeassistant
```

### In Python
```python
mqtt_config = {
    "broker": "localhost",
    "port": 1883,
    "topic_prefix": "meter2mqtt",
    "ha_discovery_prefix": "homeassistant",
}
```

## MQTT Topics

### Discovery Topics
```
homeassistant/sensor/{device_id}_{param}/config
homeassistant/binary_sensor/{device_id}_status/config
```

### Value Topics
```
meter2mqtt/{device_id}/{param}
meter2mqtt/{device_id}/status
```

## Common Integration Patterns

### Single Device
```python
mqtt.publish_device_discovery("kitchen_heater", device_info, metadata)
mqtt.publish_device_value("kitchen_heater", "energy", 1234.56)
mqtt.publish_device_status("kitchen_heater", "online")
```

### Multiple Devices
```python
for device_id in device_ids:
    mqtt.publish_device_discovery(device_id, get_info(device_id), get_metadata(device_id))
```

### Error Handling
```python
try:
    values = device.read()
    for param, value in values.items():
        mqtt.publish_device_value(device_id, param, value)
    mqtt.publish_device_status(device_id, "online")
except Exception as e:
    mqtt.publish_device_status(device_id, "offline")
```

## Home Assistant Features Enabled

### Energy Dashboard
- Energy entities automatically appear
- Daily/monthly/yearly statistics
- Cost calculations

### Automations
- Power threshold triggers
- Temperature alerts
- Device availability

### History
- All sensors tracked
- Statistics calculated
- Graphs generated

### Integrations
- Energy management
- Climate control
- Water usage

## Troubleshooting

### Entities not appearing?
1. Check MQTT connection: `mosquitto_sub -t "homeassistant/#"`
2. Verify discovery prefix matches HA settings
3. Check unique_ids are formatted correctly

### Values not updating?
1. Check MQTT topic: `mosquitto_sub -t "meter2mqtt/#"`
2. Verify parameters match device configuration
3. Check device read returns values

### Device not grouping?
1. Verify `device.identifiers` in all discovery messages
2. Check device_id is consistent
3. Ensure device info is populated

## Next Steps

1. **Setup MQTT broker** (if not already done)
2. **Configure meter2mqtt** with MQTT settings
3. **Create device config** in config.d/
4. **Restart meter2mqtt**
5. **Check Home Assistant** for new devices
6. **Verify MQTT topics** with mosquitto_sub

## See Also

- `MQTT_HA_DISCOVERY.md` - Full documentation
- `mqtt.py` - Source code
- `examples/ha_discovery_example.py` - Complete example
