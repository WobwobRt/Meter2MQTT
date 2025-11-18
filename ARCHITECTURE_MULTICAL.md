# Architecture & Integration Diagram

## Component Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         meter2mqtt Framework                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                   MQTT Broker (Home Assistant)               │   │
│  │  (Receives values from devices, publishes Home Assistant    │   │
│  │   discovery messages)                                        │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                           ▲                                           │
│                           │ MQTT Values & Discovery                  │
│                           │                                           │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │              Device Lifecycle Manager                        │   │
│  │  (Watches config.d/, spawns/reloads/stops devices)          │   │
│  └──────────────────────────────────────────────────────────────┘   │
│       ▲                                                               │
│       │ Watches                                                       │
│       │                                                               │
│  ┌────┴──────────────────────────────────────────────────────────┐  │
│  │         config.d/ (Configuration Directory)                  │  │
│  ├────────────────────────────────────────────────────────────────┤ │
│  │ multical.yaml ──────┐                                         │ │
│  │ dsmr.yaml ────────┐ │                                         │ │
│  │ warmtelink.yaml   │ │ (future)                                │ │
│  └────┬──────────────┼─┼─────────────────────────────────────────┘ │
│       │              │ │                                             │
│       │              │ │                                             │
│  ┌────▼──────────────┼─┼──────────────────────────────────────────┐ │
│  │    Device Factory                                             │ │
│  │  (Creates device instances based on type)                   │ │
│  │                                                               │ │
│  │  create_device("kitchen_heater", "multical", config) ──────┐ │ │
│  └─────────────────────────────────────────────────────────────┼─┘ │
│                                                                  │   │
│        ┌─────────────────────────────────────────────────────────┘   │
│        │                                                             │
│        ▼                                                             │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │            Device Base Class                                 │   │
│  │  (Abstract interface for all device types)                  │   │
│  │                                                               │   │
│  │  • connect()         - Establish connection                 │   │
│  │  • disconnect()      - Close connection                     │   │
│  │  • read()            - Read values from device              │   │
│  │  • get_device_info() - Device metadata                      │   │
│  └────────┬──────────────────────────────────┬───────────────────┘   │
│           │                                  │                       │
│  ┌────────▼────────────┐        ┌────────────▼──────────────┐       │
│  │  MulticalDevice     │        │    DSMRDevice            │       │
│  │  (Kamstrup Multical)│        │ (Dutch Smart Meter)      │       │
│  │                     │        │                          │       │
│  │ • 30+ parameters    │        │ • 22+ parameters         │       │
│  │ • Serial/Network    │        │ • Serial/Network         │       │
│  │ • v402/403/603      │        │ • v40/42/50/53           │       │
│  └────────┬────────────┘        └────────────┬──────────────┘       │
│           │                                  │                       │
│           ▼                                  ▼                       │
│  ┌─────────────────────────────────────────────────────┐            │
│  │     Home Assistant Metadata                        │            │
│  │  (ha_metadata.py)                                  │            │
│  │                                                     │            │
│  │  MULTICAL_PARAMS = {                               │            │
│  │    "energy": {                                      │            │
│  │      "name": "Energy",                              │            │
│  │      "unit": "kWh",                                 │            │
│  │      "icon": "mdi:flash",                           │            │
│  │      "device_class": "energy",                      │            │
│  │      "state_class": "total_increasing"             │            │
│  │    },                                               │            │
│  │    ...                                              │            │
│  │  }                                                  │            │
│  │                                                     │            │
│  │  DSMR_PARAMS = { ... }                             │            │
│  └─────────────────────────────────────────────────────┘            │
│           ▲ Used by device-specific code                            │
│           │                                                          │
│  ┌────────┴──────────────────────────────────────────────────────┐  │
│  │  Physical Meters                                              │  │
│  │                                                               │  │
│  │  ┌──────────────────┐      ┌──────────────────┐             │  │
│  │  │ Kamstrup Multical│      │ Dutch Smart Meter│             │  │
│  │  │ Heat Meter (402) │      │  DSMR v50        │             │  │
│  │  │                  │      │                  │             │  │
│  │  │ /dev/ttyUSB0     │      │ /dev/ttyUSB1     │             │  │
│  │  │  (Serial)        │      │  (Serial)        │             │  │
│  │  └──────────────────┘      └──────────────────┘             │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Reading a Value

```
┌─────────────────────────────────────────────────────────────────────┐
│ 1. Lifecycle Manager triggers device.read()                        │
└─────────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 2. MulticalDevice.read() calls parser.run()                        │
│    (Uses kamstrup2mqtt library)                                    │
└─────────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 3. Serial/Network connection to meter                              │
│    Reads each parameter (energy, power, temp1, ...)                │
└─────────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 4. Returns dict: {"energy": 1234.56, "power": 45.8, ...}          │
└─────────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 5. Framework gets metadata from ha_metadata.py                     │
│    - energy → {"device_class": "energy", ...}                      │
│    - power → {"device_class": "power", ...}                        │
└─────────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 6. Publishes to MQTT:                                              │
│    • Values: meter2mqtt/kitchen_heater/energy → 1234.56            │
│    • Discovery: homeassistant/sensor/.../config → {...}           │
│    • Status: meter2mqtt/kitchen_heater/status → online             │
└─────────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 7. Home Assistant receives:                                        │
│    • Creates entity: sensor.kitchen_heater_energy                 │
│    • Sets device_class: energy                                    │
│    • Sets state_class: total_increasing                           │
│    • Displays with energy icon in UI                              │
│    • Enables Energy dashboard integration                         │
└─────────────────────────────────────────────────────────────────────┘
```

## Configuration Resolution

```
config.d/kitchen_heater.yaml
    │
    ├─ type: multical              → device_type = "multical"
    │
    ├─ connection: serial_port     → connection_type = "serial_port"
    │
    ├─ port: /dev/ttyUSB0          → port = "/dev/ttyUSB0"
    │
    ├─ parameters: [...]           → parameters list
    │                                 ├─ energy → energy metadata
    │                                 ├─ power → power metadata
    │                                 └─ temp1 → temp1 metadata
    │
    ├─ version: 402                → Multical version (402/403/603)
    │
    └─ poll_interval: 300          → 300 seconds between reads
                    │
                    ▼
Device Factory creates MulticalDevice(
    device_id="kitchen_heater",
    device_config={...}
)
                    │
                    ▼
Device connects to /dev/ttyUSB0
                    │
                    ▼
On each poll interval:
    └─ read() → returns values dict
                    │
                    ▼
For each value:
    ├─ Get metadata from ha_metadata.py
    ├─ Publish to MQTT
    └─ Home Assistant receives discovery message
```

## Home Assistant Entity Creation

```
Parameter: energy
    │
    ├─ name: "Energy"
    ├─ unit_of_measurement: "kWh"
    ├─ icon: "mdi:flash"
    ├─ device_class: "energy"           ← Enables energy formatting
    ├─ state_class: "total_increasing"  ← Enables Energy dashboard
    │
    ▼
Home Assistant creates:
    │
    ├─ Entity ID: sensor.kitchen_heater_energy
    ├─ Display: "1234.56 kWh" with energy icon
    ├─ History: Tracked for energy statistics
    ├─ Dashboard: Appears in Energy dashboard
    │
    ▼
User benefits:
    ├─ Energy consumption tracking
    ├─ Daily/monthly/yearly statistics
    ├─ Integration with Home Assistant automations
    ├─ History graphs
    └─ Cost calculation (if configured)
```

## Device Type Extension

To add a new device type (e.g., Warmtelink):

```
1. Create src/meter2mqtt/devices/warmtelink.py
   └─ class WarmtelinkDevice(BaseDevice)
      ├─ connect()
      ├─ disconnect()
      ├─ read()
      ├─ get_available_parameters()
      └─ ...

2. Add metadata to src/meter2mqtt/devices/ha_metadata.py
   └─ WARMTELINK_PARAMS = {
        "param1": {"name": "...", "unit": "...", ...},
        ...
      }
   └─ PARAMETER_METADATA["warmtelink"] = WARMTELINK_PARAMS

3. Register in src/meter2mqtt/devices/__init__.py
   ├─ from .warmtelink import WarmtelinkDevice
   └─ register_device_type("warmtelink", WarmtelinkDevice)

4. Create config.d/warmtelink.yaml.example
   └─ Configuration template for users

5. Done! Device can be used via:
   ├─ config.d/my_device.yaml (type: warmtelink)
   └─ Automatic Home Assistant integration
```

## File Organization

```
meter2mqtt/
├── src/meter2mqtt/
│   └── devices/
│       ├── __init__.py              ← Device registry
│       ├── base.py                  ← BaseDevice abstract class
│       ├── factory.py               ← Device factory
│       ├── lifecycle.py             ← Device lifecycle manager
│       ├── dsmr.py                  ← DSMR device ✓
│       ├── multical.py              ← Multical device ✓ NEW
│       └── ha_metadata.py           ← HA metadata for all devices ✓ NEW
│
├── config.d/
│   ├── dsmr.yaml.example            ← DSMR config template (updated)
│   └── multical.yaml.example        ← Multical config template ✓ NEW
│
└── Documentation/
    ├── IMPLEMENTATION_SUMMARY.md    ← This implementation ✓ NEW
    ├── HA_INTEGRATION.md            ← HA concepts & integration ✓ NEW
    ├── MULTICAL_QUICKSTART.md       ← Multical usage guide ✓ NEW
    └── ARCHITECTURE.md              ← Overall architecture (existing)
```

## Summary

- **MulticalDevice**: Reads 30+ parameters from Kamstrup heat meters
- **ha_metadata.py**: Comprehensive Home Assistant metadata for all devices
- **Home Assistant**: Automatic entity creation with device classes
- **Extensible**: Easy to add more device types following the same pattern
