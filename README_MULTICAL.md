# Multical Device & Home Assistant Metadata - Complete Implementation

## What Was Implemented

### 1. **Multical Device Class** (`src/meter2mqtt/devices/multical.py`)
A complete device implementation for Kamstrup Multical heat meters with:
- Support for Multical 402, 403, 603 versions
- Serial port and network (socket) connections
- 30+ available parameters
- Full integration with the meter2mqtt framework

### 2. **Home Assistant Metadata System** (`src/meter2mqtt/devices/ha_metadata.py`)
Comprehensive parameter metadata for Home Assistant MQTT Discovery:

**Multical Parameters (30 total):**
- Core: energy, power, temp1, temp2, volume, flow, tempdiff (7 params)
- Temperature ratios: temp1xm3, temp2xm3 (2 params)
- Monthly statistics: flow/power/temp min/max/dates (10 params)
- Yearly statistics: flow/power/temp min/max/dates (10 params)
- Other: infoevent, hourcounter, e1highres (3 params)

**DSMR Parameters (22 total):**
- Electricity usage (8 params)
- Gas (1 param)
- Voltage/Current/Power per phase (13 params)

**Each parameter includes:**
- Human-readable name
- Unit of measurement (kWh, W, °C, m³/h, etc.)
- MDI icon (mdi:flash, mdi:thermometer, etc.)
- Home Assistant device_class (energy, power, temperature, water, voltage, current, etc.)
- Home Assistant state_class (measurement, total, total_increasing)

### 3. **Configuration Examples**
- `config.d/multical.yaml.example` - Multical configuration template (70 lines)
- `config.d/dsmr.yaml.example` - Updated DSMR configuration template (60 lines)

### 4. **Documentation** (4 comprehensive guides)
1. **HA_INTEGRATION.md** (200 lines)
   - Overview of Home Assistant MQTT Discovery
   - Device class and state class reference
   - MQTT message format examples
   - Instructions for adding new devices

2. **MULTICAL_QUICKSTART.md** (250 lines)
   - Features and supported parameters
   - Configuration examples (minimal, network, full)
   - Available parameters by category
   - MQTT topic structure
   - Troubleshooting guide
   - Performance optimization tips

3. **IMPLEMENTATION_SUMMARY.md** (150 lines)
   - Overview of all files created/modified
   - Complete parameter listing with metadata
   - Usage examples and integration points
   - Future enhancement suggestions

4. **ARCHITECTURE_MULTICAL.md** (200 lines)
   - Component overview diagram
   - Data flow from meter to Home Assistant
   - Configuration resolution process
   - Device type extension template

## Home Assistant Device Classes & State Classes

### Device Classes (enable special formatting and features)
- **energy**: Total energy consumed/generated → Energy dashboard
- **power**: Current power draw → Power automations and graphs
- **temperature**: Temperature readings → Climate automations
- **temperature_delta**: Temperature difference → Monitoring
- **water**: Water volume → Water usage tracking
- **volume_flow_rate**: Flow rate → Flow monitoring
- **voltage**: Electrical voltage → Voltage monitoring
- **current**: Electrical current → Current monitoring

### State Classes (define value semantics)
- **measurement**: Single instantaneous reading (temps, power, voltage)
- **total**: Lifetime total that can be reset (exports)
- **total_increasing**: Monotonically increasing total (energy, water, gas)

## Example Configuration

```yaml
# config.d/kitchen_heater.yaml
type: multical
connection: serial_port
port: /dev/ttyUSB0
version: 402

parameters:
  - energy          # kWh - device_class: energy
  - power           # W - device_class: power
  - temp1           # °C - device_class: temperature
  - temp2           # °C - device_class: temperature
  - volume          # m³ - device_class: water
  - flow            # m³/h - device_class: volume_flow_rate

poll_interval: 300  # 5 minutes
```

## Home Assistant Integration

When meter2mqtt publishes data with this configuration:

```
MQTT Topics:
  meter2mqtt/kitchen_heater/energy → 1234.56
  meter2mqtt/kitchen_heater/power → 45.8
  meter2mqtt/kitchen_heater/temp1 → 52.3
  meter2mqtt/kitchen_heater/temp2 → 18.7
  meter2mqtt/kitchen_heater/volume → 890.12
  meter2mqtt/kitchen_heater/flow → 0.85
  meter2mqtt/kitchen_heater/status → online

Home Assistant Creates:
  ✓ sensor.kitchen_heater_energy (kWh, device_class: energy)
  ✓ sensor.kitchen_heater_power (W, device_class: power)
  ✓ sensor.kitchen_heater_temperature_1 (°C, device_class: temperature)
  ✓ sensor.kitchen_heater_temperature_2 (°C, device_class: temperature)
  ✓ sensor.kitchen_heater_volume (m³, device_class: water)
  ✓ sensor.kitchen_heater_flow (m³/h, device_class: volume_flow_rate)
  ✓ binary_sensor.kitchen_heater_status (availability)

Features Enabled:
  ✓ Energy dashboard integration (energy entity)
  ✓ History and statistics
  ✓ Automations based on power/temperature
  ✓ Unit conversion by Home Assistant
  ✓ Icons and formatted display
```

## Files Created

```
src/meter2mqtt/devices/multical.py          (195 lines) - Device class
src/meter2mqtt/devices/ha_metadata.py       (454 lines) - HA metadata
config.d/multical.yaml.example              (70 lines)  - Config template
HA_INTEGRATION.md                           (200 lines) - HA guide
MULTICAL_QUICKSTART.md                      (250 lines) - User guide
IMPLEMENTATION_SUMMARY.md                   (150 lines) - Summary
ARCHITECTURE_MULTICAL.md                    (200 lines) - Architecture
```

## Files Modified

```
src/meter2mqtt/devices/__init__.py
  - Added import: from .multical import MulticalDevice
  - Registered: register_device_type("multical", MulticalDevice)
  - Updated __all__ exports

config.d/dsmr.yaml.example
  - Updated with comprehensive parameter list
  - Added Home Assistant metadata references
```

## Key Features

✅ **30+ Multical parameters** with full HA metadata
✅ **22+ DSMR parameters** with full HA metadata
✅ **Serial and network connections** supported
✅ **Automatic entity creation** in Home Assistant
✅ **Device classes** enable automations and statistics
✅ **State classes** enable proper value semantics
✅ **Extensible architecture** for new device types
✅ **Comprehensive documentation** with examples
✅ **Configuration templates** for quick setup
✅ **Zero breaking changes** to existing code

## Usage

### Configuration
```yaml
# config.d/my_multical.yaml
type: multical
connection: serial_port
port: /dev/ttyUSB0

parameters:
  - energy
  - power
  - temp1
  - temp2
  - volume
  - flow

poll_interval: 300
```

### Python Code
```python
from meter2mqtt.devices import create_device
from meter2mqtt.devices.ha_metadata import get_parameter_info

# Create device
device = create_device(
    device_id="kitchen_heater",
    device_type="multical",
    device_config={
        "connection": "serial_port",
        "port": "/dev/ttyUSB0",
        "parameters": ["energy", "power", "temp1"]
    }
)

# Connect and read
if device.connect():
    values = device.read()  # {"energy": 1234.56, "power": 45.8, ...}
    
    # Get metadata for Home Assistant
    for param, value in values.items():
        metadata = get_parameter_info("multical", param)
        print(f"{metadata['name']}: {value} {metadata['unit']}")
        # Energy: 1234.56 kWh
        # Power: 45.8 W
        # Temperature 1: 52.3 °C
```

## Testing

Quick verification:
```python
from meter2mqtt.devices import create_device, get_registered_device_types
from meter2mqtt.devices.ha_metadata import get_parameter_metadata

# Verify device is registered
print(get_registered_device_types())  # ['dsmr', 'multical']

# Verify metadata exists
metadata = get_parameter_metadata("multical")
print(len(metadata))  # 30 parameters

# Check a parameter
energy = metadata["energy"]
print(energy)
# {
#   "name": "Energy",
#   "unit": "kWh",
#   "icon": "mdi:flash",
#   "device_class": "energy",
#   "state_class": "total_increasing"
# }
```

## Next Steps

1. **Test the implementation** with your Multical meter
2. **Update your config.yaml** main configuration if needed
3. **Create config.d/kitchen_heater.yaml** (or your device name)
4. **Restart meter2mqtt** to load the new device
5. **Verify MQTT topics** are published correctly
6. **Check Home Assistant** for automatically created entities

## Documentation Location

- `MULTICAL_QUICKSTART.md` - Start here for quick setup
- `HA_INTEGRATION.md` - For Home Assistant concepts
- `ARCHITECTURE_MULTICAL.md` - For technical architecture
- `IMPLEMENTATION_SUMMARY.md` - Complete technical details
- `config.d/multical.yaml.example` - Configuration reference
