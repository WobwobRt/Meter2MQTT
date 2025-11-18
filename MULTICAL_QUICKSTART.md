# Multical Device Quick Start

## Overview

The Multical device class enables meter2mqtt to read data from Kamstrup Multical 402/403/603 heat meters via serial port or network connection.

## Features

- ✅ Multical 402, 403, 603 support
- ✅ Serial port and network (socket) connections
- ✅ 30+ parameters available
- ✅ Configurable polling interval
- ✅ Home Assistant MQTT Discovery ready
- ✅ Automatic device grouping in Home Assistant

## Configuration

### 1. Minimal Configuration (Serial Port)

Create `config.d/my_heater.yaml`:

```yaml
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
```

### 2. Network Connection

```yaml
type: multical
connection: network_url
url: socket://192.168.1.50:2003

parameters:
  - energy
  - power
  - temp1
  - temp2
```

### 3. Full Configuration with All Options

```yaml
type: multical
device_id: kitchen_heater

# Connection (required)
connection: serial_port
port: /dev/ttyUSB0

# Multical version (optional, default: 402)
version: 402

# Parameters to read (optional, default: all available)
parameters:
  - energy
  - power
  - temp1
  - temp2
  - volume
  - flow
  - tempdiff

# Polling interval in seconds (optional, default: 300 = 5 min)
poll_interval: 300

# Serial settings (optional)
serial_options:
  baudrate: 1200
  parity: none
  stopbits: 2
  bytesize: 8
  timeout: 2.0
```

## Available Parameters

### Core Parameters (Most Common)
```yaml
- energy          # Total energy (kWh)
- power           # Current power (W)
- temp1           # Temperature 1 (°C)
- temp2           # Temperature 2 (°C)
- volume          # Total volume (m³)
- flow            # Current flow (m³/h)
- tempdiff        # Temperature difference (°C)
```

### Temperature Ratios
```yaml
- temp1xm3        # Temperature 1 per m³
- temp2xm3        # Temperature 2 per m³
```

### Monthly Statistics
```yaml
- minflow_m, maxflow_m          # Min/max flow this month
- minflowDate_m, maxflowDate_m  # Dates of min/max
- minpower_m, maxpower_m        # Min/max power this month
- minpowerdate_m, maxpowerdate_m  # Dates of min/max
- avgtemp1_m, avgtemp2_m        # Average temperatures
```

### Yearly Statistics
```yaml
- minflow_y, maxflow_y          # Min/max flow this year
- minflowdate_y, maxflowdate_y  # Dates of min/max
- minpower_y, maxpower_y        # Min/max power this year
- minpowerdate_y, maxpowerdate_y  # Dates of min/max
- avgtemp1_y, avgtemp2_y        # Average temperatures
```

### Other Parameters
```yaml
- infoevent       # System event code
- hourcounter     # Operating hours (h)
- e1highres       # Energy 1 high resolution (kWh)
```

## MQTT Topics

Values are published to:
```
meter2mqtt/{device_id}/{parameter}
meter2mqtt/{device_id}/status        # online/offline
```

Example for device `kitchen_heater`:
```
meter2mqtt/kitchen_heater/energy      → 1234.56
meter2mqtt/kitchen_heater/power       → 45.8
meter2mqtt/kitchen_heater/temp1       → 52.3
meter2mqtt/kitchen_heater/temp2       → 18.7
meter2mqtt/kitchen_heater/status      → online
```

## Home Assistant Integration

### Automatic Discovery

meter2mqtt will automatically publish Home Assistant MQTT Discovery messages for each parameter. Home Assistant will create entities like:

- `sensor.kitchen_heater_energy` (kWh, energy device class)
- `sensor.kitchen_heater_power` (W, power device class)
- `sensor.kitchen_heater_temperature_1` (°C, temperature device class)
- `sensor.kitchen_heater_volume` (m³, water device class)

### Energy Dashboard Integration

Parameters with `device_class: energy` and `state_class: total_increasing` (like `energy`) automatically integrate with Home Assistant's Energy dashboard.

### Temperature Tracking

Parameters with `device_class: temperature` support history graphs and can be used in automations.

## Troubleshooting

### Connection Issues

**Serial port not found:**
```bash
# List available serial ports
ls /dev/ttyUSB*
ls /dev/ttyACM*
```

**Permission denied:**
```bash
# Add user to dialout group
sudo usermod -a -G dialout $USER
# Restart meter2mqtt after adding user
```

**Connection times out:**
- Check baud rate matches meter (default: 1200)
- Check cables and connections
- Try with longer timeout: `timeout: 5.0`

### Network Connection Issues

**Socket connection fails:**
- Verify IP address and port are correct
- Check firewall allows connection
- Ensure network device has proper serial-to-IP adapter

### No Data Read

**Check parameter names:**
```bash
# Device logs should show available parameters
# Verify parameter names match exactly (case-sensitive)
```

**Meter not responding:**
- Check meter is powered on
- Try reading just core parameters first
- Increase poll interval to reduce read frequency

## Performance Tips

1. **Minimize parameters:** Read only parameters you need
   - Reading all 30+ parameters takes longer
   - Core 7 parameters typically read in ~30 seconds

2. **Optimize poll interval:** 
   - For real-time monitoring: 60-300 seconds
   - For history/logging: 300-900 seconds (5-15 minutes)
   - Excessive polling may overload the meter

3. **Use appropriate network:**
   - Serial direct connection: Most reliable
   - Network socket: Better for remote locations

## Examples

### Simple Kitchen Heater

```yaml
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

### Remote Location with Statistics

```yaml
type: multical
device_id: barn_heater
connection: network_url
url: socket://192.168.1.50:2003

version: 402

parameters:
  - energy
  - power
  - temp1
  - temp2
  - volume
  - flow
  - tempdiff
  - avgtemp1_m
  - avgtemp2_m
  - minpower_m
  - maxpower_m

poll_interval: 600  # 10 minutes
```

### Full Data Collection

```yaml
type: multical
connection: serial_port
port: /dev/ttyUSB0

# Read all available parameters
# (Device will use all from get_available_parameters())
poll_interval: 900  # 15 minutes for full dataset
```

## See Also

- `config.d/multical.yaml.example` - Full example configuration
- `HA_INTEGRATION.md` - Home Assistant integration details
- `devices/ha_metadata.py` - Complete parameter metadata
- `PROJECT_SUMMARY.md` - Overall architecture
