# Implementation Summary: Multical Device & Home Assistant Metadata

## Overview

This implementation adds support for Kamstrup Multical heat meters to meter2mqtt with comprehensive Home Assistant MQTT Discovery integration.

## Files Created

### 1. Device Implementation
- **`src/meter2mqtt/devices/multical.py`**
  - New `MulticalDevice` class extending `BaseDevice`
  - Supports Multical 402/403/603 versions
  - Serial port and network (socket) connections
  - 30+ available parameters
  - Automatically uses kamstrup2mqtt parser library

### 2. Home Assistant Integration
- **`src/meter2mqtt/devices/ha_metadata.py`**
  - Comprehensive parameter metadata for all devices
  - 30+ Multical parameters with full HA metadata
  - 22+ DSMR parameters with full HA metadata
  - Metadata includes:
    - Human-readable names
    - Units of measurement
    - MDI icons
    - Device classes (energy, power, temperature, etc.)
    - State classes (measurement, total, total_increasing)
  - Functions: `get_parameter_metadata()`, `get_parameter_info()`

### 3. Configuration Examples
- **`config.d/multical.yaml.example`** - Multical device configuration template
- **`config.d/dsmr.yaml.example`** - Updated DSMR configuration template

### 4. Documentation
- **`HA_INTEGRATION.md`** - Home Assistant integration guide
  - Overview of MQTT Discovery
  - Device class and state class reference
  - MQTT message format examples
  - How to add new devices with HA support
- **`MULTICAL_QUICKSTART.md`** - Multical device quick start guide
  - Features and configuration examples
  - Parameter reference
  - MQTT topic structure
  - Troubleshooting guide
  - Performance optimization tips

## Files Modified

### 1. Device Registry
- **`src/meter2mqtt/devices/__init__.py`**
  - Added import: `from .multical import MulticalDevice`
  - Registered: `register_device_type("multical", MulticalDevice)`
  - Updated `__all__` exports

## Multical Parameters (30 Total)

### Energy & Power
- `energy` (kWh) - device_class: energy, state_class: total_increasing
- `power` (W) - device_class: power, state_class: measurement
- `e1highres` (kWh) - device_class: energy, state_class: total_increasing

### Temperature
- `temp1`, `temp2` (°C) - device_class: temperature
- `tempdiff` (°C) - device_class: temperature_delta
- `temp1xm3`, `temp2xm3` (°C per m³) - device_class: temperature

### Volume & Flow
- `volume` (m³) - device_class: water, state_class: total_increasing
- `flow` (m³/h) - device_class: volume_flow_rate

### Monthly Statistics (10 parameters)
- Flow: minflow_m, maxflow_m, minflowDate_m, maxflowDate_m
- Power: minpower_m, maxpower_m, minpowerdate_m, maxpowerdate_m
- Temps: avgtemp1_m, avgtemp2_m

### Yearly Statistics (10 parameters)
- Flow: minflow_y, maxflow_y, minflowdate_y, maxflowdate_y
- Power: minpower_y, maxpower_y, minpowerdate_y, maxpowerdate_y
- Temps: avgtemp1_y, avgtemp2_y

### System
- `infoevent` - Event code
- `hourcounter` (h) - state_class: total_increasing

## DSMR Parameters (22 Total)

### Energy (8 parameters)
- Usage: current_electricity_usage, electricity_used_tariff_1/2
- Delivery: current_electricity_delivery, electricity_delivered_tariff_1/2
- Totals: electricity_active_import_total, electricity_active_export_total

### Gas (1 parameter)
- `gas_provided` (m³) - state_class: total_increasing

### Electrical Network (13 parameters)
- Voltage: voltage_l1, voltage_l2, voltage_l3 - device_class: voltage
- Current: current_l1, current_l2, current_l3 - device_class: current
- Power: power_generated_l1/l2/l3 - device_class: power

## Home Assistant Device Classes Used

| Device Class | Parameters | Benefits |
|---|---|---|
| `energy` | energy, e1highres | Energy dashboard integration, state history |
| `power` | power, *_power, current_electricity_* | Real-time power graphs, automations |
| `temperature` | temp1, temp2, *temp* | Temperature history, climate integration |
| `temperature_delta` | tempdiff | Temperature difference tracking |
| `water` | volume | Water usage tracking |
| `volume_flow_rate` | flow, *flow* | Flow monitoring |
| `voltage` | voltage_l* | Voltage monitoring |
| `current` | current_l* | Current monitoring |

## State Classes Used

| State Class | Parameters | Meaning |
|---|---|---|
| `total_increasing` | energy, volume, hourcounter, gas, tariff_used | Monotonically increasing totals |
| `total` | exported energies | Can be reset |
| `measurement` | power, temps, flow, voltage, current | Single readings |

## Configuration Example

```yaml
# config.d/kitchen_heater.yaml
type: multical
connection: serial_port
port: /dev/ttyUSB0
version: 402

parameters:
  - energy
  - power
  - temp1
  - temp2
  - volume
  - flow

poll_interval: 300
```

## Usage in Code

```python
from meter2mqtt.devices import create_device
from meter2mqtt.devices.ha_metadata import get_parameter_info

# Create a multical device
device = create_device(
    device_id="kitchen_heater",
    device_type="multical",
    device_config={
        "connection": "serial_port",
        "port": "/dev/ttyUSB0",
        "parameters": ["energy", "power", "temp1", "temp2"]
    }
)

# Connect and read
if device.connect():
    values = device.read()
    print(values)  # {"energy": 1234.56, "power": 45.8, ...}

# Get metadata for Home Assistant
metadata = get_parameter_info("multical", "energy")
# Returns: {
#     "name": "Energy",
#     "unit": "kWh",
#     "icon": "mdi:flash",
#     "device_class": "energy",
#     "state_class": "total_increasing"
# }

device.disconnect()
```

## Integration Points

1. **Device Factory**: Multical device is registered and can be created via `create_device()`
2. **Lifecycle Manager**: Automatically watches config.d/ for multical configs
3. **Home Assistant**: All parameters include HA discovery metadata
4. **MQTT**: Values published to `meter2mqtt/{device_id}/{parameter}`

## Dependencies

The MulticalDevice requires:
- `kamstrup2mqtt` library (will log helpful error if missing)
- `pyserial` for serial connections

## Testing

Quick test of the implementation:

```python
from meter2mqtt.devices import create_device

config = {
    "connection": "serial_port",
    "port": "/dev/ttyUSB0",
    "parameters": ["energy", "power", "temp1"]
}

device = create_device("test_heater", "multical", config)
print(f"Device: {device}")
print(f"Type: {device.get_device_type()}")
print(f"Manufacturer: {device.get_manufacturer()}")
print(f"Model: {device.get_model()}")
print(f"Available params: {device.get_available_parameters()[:5]}")
```

## Documentation Files

1. **HA_INTEGRATION.md** - Home Assistant concepts and integration guide
2. **MULTICAL_QUICKSTART.md** - Multical device specific guide
3. **config.d/multical.yaml.example** - Configuration template
4. **config.d/dsmr.yaml.example** - Updated DSMR template (with metadata references)

## Future Enhancements

Potential additions:
1. Add more device types (Warmtelink, Kamstrup ultrasonic, etc.)
2. Dynamic parameter discovery from devices
3. Parameter filtering by device class
4. Automatic MQTT Discovery message publishing
5. Parameter value validation and type coercion
6. Device status and heartbeat tracking
