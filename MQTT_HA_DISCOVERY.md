# MQTT Handler Home Assistant Discovery

## Overview

The updated `mqtt_handler` class provides full Home Assistant MQTT Discovery support, allowing automatic creation of entities in Home Assistant with proper device classes, state classes, units, and icons.

## Key Features

### 1. Device Discovery
- Automatic creation of separate Home Assistant device entries
- Each meter becomes a distinct device with manufacturer, model, and identifiers
- All parameters from a device are grouped under one device

### 2. Entity Discovery
- One entity per parameter
- Full Home Assistant metadata support:
  - **Device class**: energy, power, temperature, water, voltage, current, etc.
  - **State class**: measurement, total, total_increasing
  - **Unit**: kWh, W, °C, m³, etc.
  - **Icon**: MDI icon names (mdi:flash, mdi:thermometer, etc.)

### 3. Automatic Entity Naming
- Unique IDs: `{device_id}_{parameter_name}`
- Human-readable names from metadata
- Availability tracking with status sensor

## Configuration

### mqtt.py Configuration Options

```python
mqtt_config = {
    "client_id": "meter2mqtt",           # MQTT client ID
    "broker": "localhost",               # MQTT broker host
    "port": 1883,                        # MQTT broker port
    "qos": 1,                            # Quality of Service (0-2)
    "retain": True,                      # Retain messages
    "topic_prefix": "meter2mqtt",        # MQTT topic prefix
    "ha_discovery_prefix": "homeassistant",  # HA discovery prefix
}
```

### Environment Variable Support

You can override settings via environment variables:

```bash
export MQTT_BROKER="mqtt.example.com"
export MQTT_PORT="1883"
export MQTT_TOPIC_PREFIX="meters"
export HA_DISCOVERY_PREFIX="homeassistant"
```

## API Reference

### publish_device_discovery()

Publish Home Assistant discovery messages for all parameters of a device.

```python
mqtt.publish_device_discovery(
    device_id="kitchen_heater",
    device_info={
        "type": "multical",
        "manufacturer": "Kamstrup",
        "model": "Multical 402",
        "id": "kitchen_heater"
    },
    device_metadata={
        "energy": {
            "name": "Energy",
            "unit": "kWh",
            "icon": "mdi:flash",
            "device_class": "energy",
            "state_class": "total_increasing"
        },
        # ... more parameters
    }
)
```

**Parameters:**
- `device_id` (str): Unique device identifier (e.g., "kitchen_heater")
- `device_info` (dict): Device information with type, manufacturer, model, id
- `device_metadata` (dict): Parameter metadata mapping

### publish_device_value()

Publish a single parameter value for a device.

```python
mqtt.publish_device_value("kitchen_heater", "energy", 1234.56)
mqtt.publish_device_value("kitchen_heater", "power", 45.8)
mqtt.publish_device_value("kitchen_heater", "temp1", 52.3)
```

**Parameters:**
- `device_id` (str): Device identifier
- `parameter` (str): Parameter name
- `value` (Any): Value to publish

**MQTT Topic:**
- `{topic_prefix}/{device_id}/{parameter}`
- Example: `meter2mqtt/kitchen_heater/energy`

### publish_device_status()

Publish device online/offline status.

```python
mqtt.publish_device_status("kitchen_heater", "online")
mqtt.publish_device_status("kitchen_heater", "offline")
```

**Parameters:**
- `device_id` (str): Device identifier
- `status` (str): "online" or "offline"

**MQTT Topic:**
- `{topic_prefix}/{device_id}/status`
- Example: `meter2mqtt/kitchen_heater/status`

## Home Assistant Discovery Message Format

### Entity Discovery Message

Published to: `homeassistant/sensor/{unique_id}/config`

```json
{
  "name": "Energy",
  "unique_id": "kitchen_heater_energy",
  "state_topic": "meter2mqtt/kitchen_heater/energy",
  "availability_topic": "meter2mqtt/kitchen_heater/status",
  "payload_available": "online",
  "payload_not_available": "offline",
  "unit_of_measurement": "kWh",
  "icon": "mdi:flash",
  "device_class": "energy",
  "state_class": "total_increasing",
  "value_template": "{{ value }}",
  "device": {
    "identifiers": ["kitchen_heater"],
    "name": "Kitchen Heater",
    "manufacturer": "Kamstrup",
    "model": "Multical 402"
  }
}
```

### Status Discovery Message

Published to: `homeassistant/binary_sensor/{unique_id}/config`

```json
{
  "name": "Kitchen Heater Status",
  "unique_id": "kitchen_heater_status",
  "state_topic": "meter2mqtt/kitchen_heater/status",
  "payload_on": "online",
  "payload_off": "offline",
  "icon": "mdi:connection",
  "device": {
    "identifiers": ["kitchen_heater"],
    "name": "Kitchen Heater",
    "manufacturer": "Kamstrup",
    "model": "Multical 402"
  }
}
```

## MQTT Topic Structure

```
meter2mqtt/
├── kitchen_heater/
│   ├── energy           → 1234.56
│   ├── power            → 45.8
│   ├── temp1            → 52.3
│   ├── temp2            → 18.7
│   ├── volume           → 890.12
│   ├── flow             → 0.85
│   └── status           → online
├── bathroom_heater/
│   ├── energy           → 456.78
│   ├── power            → 12.3
│   ├── ...
│   └── status           → online
└── status               → online (global status)
```

## Usage Example

### Basic Integration

```python
from meter2mqtt.devices import create_device
from meter2mqtt.devices.ha_metadata import get_parameter_metadata
from meter2mqtt.mqtt import mqtt_handler

# 1. Setup MQTT
mqtt = mqtt_handler({
    "client_id": "meter2mqtt",
    "broker": "localhost",
    "port": 1883,
    "topic_prefix": "meter2mqtt",
    "ha_discovery_prefix": "homeassistant",
})
mqtt.connect()

# 2. Create device
device = create_device("kitchen_heater", "multical", {
    "connection": "serial_port",
    "port": "/dev/ttyUSB0",
    "parameters": ["energy", "power", "temp1", "temp2"]
})
device.connect()

# 3. Publish Home Assistant discovery
mqtt.publish_device_discovery(
    device_id="kitchen_heater",
    device_info=device.get_device_info(),
    device_metadata=get_parameter_metadata("multical")
)

# 4. Publish device status
mqtt.publish_device_status("kitchen_heater", "online")

# 5. Read and publish values
values = device.read()
for param, value in values.items():
    mqtt.publish_device_value("kitchen_heater", param, value)
```

### Polling Loop

```python
import time

while True:
    try:
        # Read device values
        values = device.read()
        
        if values:
            # Publish each value
            for param, value in values.items():
                mqtt.publish_device_value("kitchen_heater", param, value)
            
            # Publish status
            mqtt.publish_device_status("kitchen_heater", "online")
        else:
            # Device read failed
            mqtt.publish_device_status("kitchen_heater", "offline")
    
    except Exception as e:
        log.error(f"Error during polling: {e}")
        mqtt.publish_device_status("kitchen_heater", "offline")
    
    # Wait for next poll
    time.sleep(300)  # Poll every 5 minutes
```

## Home Assistant Integration

### Automatic Entity Creation

When Home Assistant receives discovery messages, it automatically creates entities:

**Multical Kitchen Heater Discovery:**
```
Devices & Services → Devices → Kitchen Heater (Kamstrup Multical 402)
  ├── sensor.kitchen_heater_energy (kWh)
  ├── sensor.kitchen_heater_current_power (W)
  ├── sensor.kitchen_heater_temperature_1 (°C)
  ├── sensor.kitchen_heater_temperature_2 (°C)
  ├── sensor.kitchen_heater_volume (m³)
  ├── sensor.kitchen_heater_flow_rate (m³/h)
  └── binary_sensor.kitchen_heater_status (online/offline)
```

### Device Classes Enable Features

| Device Class | Features | Example |
|---|---|---|
| `energy` | Energy dashboard, daily stats | kWh total |
| `power` | Power graphs, peak detection | W current |
| `temperature` | Temperature automations | °C readings |
| `water` | Water usage tracking | m³ total |
| `voltage` | Voltage monitoring | V per phase |
| `current` | Current monitoring | A per phase |

### State Classes Enable History

| State Class | Behavior | Example |
|---|---|---|
| `total_increasing` | Monotonic increase tracked | Energy consumption |
| `total` | Can reset or decrease | Export counters |
| `measurement` | Single reading tracked | Current temp |

## Troubleshooting

### Entities Not Appearing in Home Assistant

1. **Check MQTT connection:**
   ```bash
   mosquitto_sub -h localhost -t "homeassistant/#"
   ```
   Should see discovery messages

2. **Verify discovery prefix:**
   - Default: `homeassistant`
   - Check Home Assistant MQTT integration settings

3. **Check entity unique_ids:**
   - Should be: `{device_id}_{parameter_name}`
   - Example: `kitchen_heater_energy`

### Device Not Grouping

1. **Verify device identifiers:**
   - Must be consistent across all entities
   - Check MQTT discovery messages have same `device.identifiers`

2. **Check device info:**
   - `device_id` must match across all publishes
   - Device name, manufacturer, model can be any value

### Values Not Updating

1. **Verify state topic:**
   - Should be: `{topic_prefix}/{device_id}/{parameter}`
   - Example: `meter2mqtt/kitchen_heater/energy`

2. **Check MQTT publishing:**
   ```bash
   mosquitto_sub -h localhost -t "meter2mqtt/#"
   ```

## Advanced Configuration

### Custom MQTT Broker

```python
mqtt_config = {
    "client_id": "meter2mqtt",
    "broker": "mqtt.example.com",
    "port": 8883,  # TLS port
    "username": "user",
    "password": "pass",
    "tls_enabled": True,
}
```

### Multiple Devices

```python
devices = [
    ("kitchen_heater", "multical", {...}),
    ("dsmr_meter", "dsmr", {...}),
    ("bathroom_heater", "multical", {...}),
]

for device_id, device_type, device_config in devices:
    device = create_device(device_id, device_type, device_config)
    device.connect()
    
    mqtt.publish_device_discovery(
        device_id=device_id,
        device_info=device.get_device_info(),
        device_metadata=get_parameter_metadata(device_type)
    )
    mqtt.publish_device_status(device_id, "online")
```

## See Also

- `mqtt.py` - MQTT handler implementation
- `ha_metadata.py` - Parameter metadata definitions
- `multical.py` - Multical device implementation
- `MULTICAL_QUICKSTART.md` - Device setup guide
- `HA_INTEGRATION.md` - Home Assistant concepts
