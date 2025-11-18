# Home Assistant Integration

This document describes the Home Assistant MQTT Discovery integration for meter2mqtt.

## Overview

Home Assistant MQTT Discovery allows devices to automatically register themselves with Home Assistant through MQTT messages. The meter2mqtt framework supports this through comprehensive parameter metadata that includes:

- **name**: Display name in Home Assistant UI
- **unit**: Unit of measurement (Home Assistant will normalize these)
- **icon**: MDI icon for the UI
- **device_class**: Enables state formatting, history statistics, automations, etc.
- **state_class**: Specifies measurement type (measurement, total, total_increasing)

## Metadata Module

The `devices/ha_metadata.py` module defines all parameter metadata for supported devices:

### Multical Device Parameters

The Multical 402/403/603 heat meters provide 30+ parameters organized into categories:

#### Core Parameters
- **energy** (kWh) - `device_class: energy`, `state_class: total_increasing`
- **power** (W) - `device_class: power`, `state_class: measurement`
- **temp1, temp2** (°C) - `device_class: temperature`, `state_class: measurement`
- **tempdiff** (°C) - `device_class: temperature_delta`, `state_class: measurement`
- **volume** (m³) - `device_class: water`, `state_class: total_increasing`
- **flow** (m³/h) - `device_class: volume_flow_rate`, `state_class: measurement`

#### Temperature Ratios
- **temp1xm3, temp2xm3** - Temperature per m³ measurements

#### Monthly & Yearly Statistics
- Min/max flow, power, and average temperatures for month and year
- Date fields for when min/max values occurred

#### Other Parameters
- **hourcounter** (h) - `state_class: total_increasing`
- **e1highres** - Energy with high resolution
- **infoevent** - System event codes

### DSMR Device Parameters

The Dutch Smart Meter provides 22+ parameters:

#### Electricity Measurements
- **current_electricity_usage, delivery** (kW) - `device_class: power`, `state_class: measurement`
- **electricity_used/delivered_tariff_1/2** (kWh) - `device_class: energy`, `state_class: total_increasing`
- **electricity_active_import/export_total** (kWh) - `device_class: energy`, `state_class: total_increasing`

#### Gas
- **gas_provided** (m³) - `state_class: total_increasing`

#### Electrical Network
- **voltage_l1/l2/l3** (V) - `device_class: voltage`, `state_class: measurement`
- **current_l1/l2/l3** (A) - `device_class: current`, `state_class: measurement`
- **power_generated_l1/l2/l3** (W) - `device_class: power`, `state_class: measurement`

## Device Classes

Home Assistant uses device classes to:
1. Format values appropriately (e.g., "12.5 kWh" with energy icon)
2. Enable automations and history statistics
3. Provide icons and state displays
4. Allow unit conversions

### Supported Device Classes

| Device Class | Use Cases | State Class |
|---|---|---|
| `energy` | Electricity, gas, heat energy totals | `total_increasing` or `total` |
| `power` | Power consumption/generation | `measurement` |
| `temperature` | Temperature readings | `measurement` |
| `temperature_delta` | Temperature differences | `measurement` |
| `voltage` | Electrical voltage | `measurement` |
| `current` | Electrical current | `measurement` |
| `water` | Water volume totals | `total_increasing` |
| `volume_flow_rate` | Flow rate measurements | `measurement` |

## State Classes

State classes define how Home Assistant treats a numeric value:

| State Class | Meaning | Use Cases |
|---|---|---|
| `measurement` | Single instantaneous reading | Temperatures, power, voltage, flow |
| `total` | Total that can be reset | Energy meters with reset capability |
| `total_increasing` | Monotonically increasing total | Energy, water, gas (never decreases) |

## MQTT Discovery Message Format

For each parameter, meter2mqtt will publish a Home Assistant MQTT Discovery message:

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
  "value_template": "{{ value_json.energy }}",
  "device": {
    "identifiers": ["kitchen_heater"],
    "name": "Kitchen Heat Meter",
    "manufacturer": "Kamstrup",
    "model": "Multical 402"
  }
}
```

## Getting Parameter Metadata

### In Python Code

```python
from meter2mqtt.devices.ha_metadata import get_parameter_metadata, get_parameter_info

# Get all metadata for a device type
multical_metadata = get_parameter_metadata("multical")

# Get metadata for a specific parameter
energy_info = get_parameter_info("multical", "energy")
# Returns: {
#     "name": "Energy",
#     "unit": "kWh",
#     "icon": "mdi:flash",
#     "device_class": "energy",
#     "state_class": "total_increasing"
# }
```

### In Device Configuration

Devices automatically use the metadata when configured:

```yaml
# config.d/kitchen_heater.yaml
type: multical
connection: serial_port
port: /dev/ttyUSB0

# These parameters will use metadata from ha_metadata.py
parameters:
  - energy
  - power
  - temp1
  - temp2
  - volume
```

## Adding New Devices with Home Assistant Support

To add a new device type with Home Assistant metadata:

1. **Create device class** (e.g., `devices/mydevice.py`)
   - Extend `BaseDevice`
   - Implement required methods

2. **Add parameter metadata** in `devices/ha_metadata.py`
   ```python
   MYDEVICE_PARAMS = {
       "param1": {
           "name": "Parameter 1",
           "unit": "unit",
           "icon": "mdi:icon-name",
           "device_class": "device_class",
           "state_class": "measurement",
       },
       # ... more parameters
   }
   
   PARAMETER_METADATA["mydevice"] = MYDEVICE_PARAMS
   ```

3. **Register device** in `devices/__init__.py`
   ```python
   from .mydevice import MyDevice
   register_device_type("mydevice", MyDevice)
   ```

4. **Create example config** in `config.d/mydevice.yaml.example`

## Home Assistant Automations and History

With proper device_class and state_class configuration:

### Energy Statistics
For parameters with `device_class: energy` and `state_class: total_increasing`, Home Assistant provides:
- Daily/weekly/monthly energy consumption graphs
- Automated statistics in history
- Integration with Home Assistant Energy dashboard

### Power Measurements
For parameters with `device_class: power` and `state_class: measurement`:
- Real-time power graphs
- Peak power detection
- Power automations

### Temperature Tracking
For parameters with `device_class: temperature` and `state_class: measurement`:
- Temperature history and graphs
- Climate automation triggers
- Heating/cooling statistics

## Reference

### MDI Icons

Common icons used in meter2mqtt:
- `mdi:flash` - Energy/power
- `mdi:lightning-bolt` - Electricity
- `mdi:thermometer` - Temperature
- `mdi:thermometer-minus` - Temperature difference
- `mdi:water` - Water/volume
- `mdi:water-percent` - Flow rate
- `mdi:calendar` - Date values
- `mdi:clock` - Time counters
- `mdi:information` - Event codes
- `mdi:gas-cylinder` - Gas

### Home Assistant Links

- [MQTT Discovery Documentation](https://www.home-assistant.io/integrations/mqtt/#mqtt-discovery)
- [Home Assistant Device Classes](https://developers.home-assistant.io/docs/core/entity/sensor#available-device-classes)
- [State Classes Documentation](https://developers.home-assistant.io/docs/core/entity/sensor#state-class)
- [MDI Icon Reference](https://pictogrammers.com/library/mdi/)
