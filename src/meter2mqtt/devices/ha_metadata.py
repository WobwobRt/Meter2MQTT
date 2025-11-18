#!/usr/bin/python
#
# Home Assistant metadata for all device parameters
# Provides device_class, state_class, unit, and icon for Home Assistant MQTT discovery

"""
Home Assistant Parameter Metadata

This module defines Home Assistant MQTT discovery metadata for parameters across all supported devices.
Each parameter includes:
- name: Display name in Home Assistant
- unit: Unit of measurement (Home Assistant will convert between units)
- icon: MDI icon for the UI
- device_class: Home Assistant device class (enables state formatting, history stats, etc.)
- state_class: Measurement type (measurement, total, total_increasing)

Device Classes Reference:
- energy: Total energy consumed/generated (kWh, MWh, etc.)
- power: Current power draw (W, kW, etc.)
- temperature: Temperature readings (°C, °F)
- temperature_delta: Temperature difference (ΔK, ΔC)
- water: Water volume (L, m³, gal, etc.)
- volume_flow_rate: Flow rate (L/min, m³/h, etc.)
- voltage: Electrical voltage (V)
- current: Electrical current (A)
- frequency: Frequency (Hz)

State Classes Reference:
- measurement: Single reading (temperature, voltage, etc.)
- total: Lifetime total (can be reset)
- total_increasing: Monotonically increasing total (never decreases)
"""

# Multical device parameters
MULTICAL_PARAMS = {
    # Core energy and power parameters
    "energy": {
        "name": "Energy",
        "unit": "kWh",
        "icon": "mdi:flash",
        "device_class": "energy",
        "state_class": "total_increasing",
    },
    "power": {
        "name": "Current Power",
        "unit": "W",
        "icon": "mdi:lightning-bolt",
        "device_class": "power",
        "state_class": "measurement",
    },
    
    # Temperature parameters
    "temp1": {
        "name": "Temperature 1",
        "unit": "°C",
        "icon": "mdi:thermometer",
        "device_class": "temperature",
        "state_class": "measurement",
    },
    "temp2": {
        "name": "Temperature 2",
        "unit": "°C",
        "icon": "mdi:thermometer",
        "device_class": "temperature",
        "state_class": "measurement",
    },
    "tempdiff": {
        "name": "Temperature Difference",
        "unit": "°C",
        "icon": "mdi:thermometer-minus",
        "device_class": "temperature_delta",
        "state_class": "measurement",
    },
    "temp1xm3": {
        "name": "Temperature 1 per m³",
        "unit": "°C",
        "icon": "mdi:thermometer",
        "device_class": "temperature",
        "state_class": "measurement",
    },
    "temp2xm3": {
        "name": "Temperature 2 per m³",
        "unit": "°C",
        "icon": "mdi:thermometer",
        "device_class": "temperature",
        "state_class": "measurement",
    },
    
    # Volume and flow parameters
    "volume": {
        "name": "Volume",
        "unit": "m³",
        "icon": "mdi:water",
        "device_class": "water",
        "state_class": "total_increasing",
    },
    "flow": {
        "name": "Flow Rate",
        "unit": "m³/h",
        "icon": "mdi:water-percent",
        "device_class": "volume_flow_rate",
        "state_class": "measurement",
    },
    
    # Monthly statistics - flow
    "minflow_m": {
        "name": "Min Flow (Month)",
        "unit": "m³/h",
        "icon": "mdi:water-percent",
        "device_class": "volume_flow_rate",
        "state_class": "measurement",
    },
    "maxflow_m": {
        "name": "Max Flow (Month)",
        "unit": "m³/h",
        "icon": "mdi:water-percent",
        "device_class": "volume_flow_rate",
        "state_class": "measurement",
    },
    "minflowDate_m": {
        "name": "Min Flow Date (Month)",
        "unit": None,
        "icon": "mdi:calendar",
        "device_class": None,
        "state_class": None,
    },
    "maxflowDate_m": {
        "name": "Max Flow Date (Month)",
        "unit": None,
        "icon": "mdi:calendar",
        "device_class": None,
        "state_class": None,
    },
    
    # Monthly statistics - power
    "minpower_m": {
        "name": "Min Power (Month)",
        "unit": "W",
        "icon": "mdi:lightning-bolt",
        "device_class": "power",
        "state_class": "measurement",
    },
    "maxpower_m": {
        "name": "Max Power (Month)",
        "unit": "W",
        "icon": "mdi:lightning-bolt",
        "device_class": "power",
        "state_class": "measurement",
    },
    "minpowerdate_m": {
        "name": "Min Power Date (Month)",
        "unit": None,
        "icon": "mdi:calendar",
        "device_class": None,
        "state_class": None,
    },
    "maxpowerdate_m": {
        "name": "Max Power Date (Month)",
        "unit": None,
        "icon": "mdi:calendar",
        "device_class": None,
        "state_class": None,
    },
    
    # Monthly statistics - temperatures
    "avgtemp1_m": {
        "name": "Average Temperature 1 (Month)",
        "unit": "°C",
        "icon": "mdi:thermometer",
        "device_class": "temperature",
        "state_class": "measurement",
    },
    "avgtemp2_m": {
        "name": "Average Temperature 2 (Month)",
        "unit": "°C",
        "icon": "mdi:thermometer",
        "device_class": "temperature",
        "state_class": "measurement",
    },
    
    # Yearly statistics - flow
    "minflow_y": {
        "name": "Min Flow (Year)",
        "unit": "m³/h",
        "icon": "mdi:water-percent",
        "device_class": "volume_flow_rate",
        "state_class": "measurement",
    },
    "maxflow_y": {
        "name": "Max Flow (Year)",
        "unit": "m³/h",
        "icon": "mdi:water-percent",
        "device_class": "volume_flow_rate",
        "state_class": "measurement",
    },
    "minflowdate_y": {
        "name": "Min Flow Date (Year)",
        "unit": None,
        "icon": "mdi:calendar",
        "device_class": None,
        "state_class": None,
    },
    "maxflowdate_y": {
        "name": "Max Flow Date (Year)",
        "unit": None,
        "icon": "mdi:calendar",
        "device_class": None,
        "state_class": None,
    },
    
    # Yearly statistics - power
    "minpower_y": {
        "name": "Min Power (Year)",
        "unit": "W",
        "icon": "mdi:lightning-bolt",
        "device_class": "power",
        "state_class": "measurement",
    },
    "maxpower_y": {
        "name": "Max Power (Year)",
        "unit": "W",
        "icon": "mdi:lightning-bolt",
        "device_class": "power",
        "state_class": "measurement",
    },
    "minpowerdate_y": {
        "name": "Min Power Date (Year)",
        "unit": None,
        "icon": "mdi:calendar",
        "device_class": None,
        "state_class": None,
    },
    "maxpowerdate_y": {
        "name": "Max Power Date (Year)",
        "unit": None,
        "icon": "mdi:calendar",
        "device_class": None,
        "state_class": None,
    },
    
    # Yearly statistics - temperatures
    "avgtemp1_y": {
        "name": "Average Temperature 1 (Year)",
        "unit": "°C",
        "icon": "mdi:thermometer",
        "device_class": "temperature",
        "state_class": "measurement",
    },
    "avgtemp2_y": {
        "name": "Average Temperature 2 (Year)",
        "unit": "°C",
        "icon": "mdi:thermometer",
        "device_class": "temperature",
        "state_class": "measurement",
    },
    
    # Other parameters
    "infoevent": {
        "name": "Info Event",
        "unit": None,
        "icon": "mdi:information",
        "device_class": None,
        "state_class": None,
    },
    "hourcounter": {
        "name": "Hour Counter",
        "unit": "h",
        "icon": "mdi:clock",
        "device_class": None,
        "state_class": "total_increasing",
    },
    "e1highres": {
        "name": "Energy 1 (High Resolution)",
        "unit": "kWh",
        "icon": "mdi:flash",
        "device_class": "energy",
        "state_class": "total_increasing",
    },
}

# DSMR device parameters
DSMR_PARAMS = {
    # Electricity usage
    "current_electricity_usage": {
        "name": "Current Electricity Usage",
        "unit": "kW",
        "icon": "mdi:lightning-bolt",
        "device_class": "power",
        "state_class": "measurement",
    },
    "current_electricity_delivery": {
        "name": "Current Electricity Delivery",
        "unit": "kW",
        "icon": "mdi:lightning-bolt",
        "device_class": "power",
        "state_class": "measurement",
    },
    "electricity_used_tariff_1": {
        "name": "Electricity Used (Tariff 1)",
        "unit": "kWh",
        "icon": "mdi:flash",
        "device_class": "energy",
        "state_class": "total_increasing",
    },
    "electricity_used_tariff_2": {
        "name": "Electricity Used (Tariff 2)",
        "unit": "kWh",
        "icon": "mdi:flash",
        "device_class": "energy",
        "state_class": "total_increasing",
    },
    "electricity_delivered_tariff_1": {
        "name": "Electricity Delivered (Tariff 1)",
        "unit": "kWh",
        "icon": "mdi:flash",
        "device_class": "energy",
        "state_class": "total_increasing",
    },
    "electricity_delivered_tariff_2": {
        "name": "Electricity Delivered (Tariff 2)",
        "unit": "kWh",
        "icon": "mdi:flash",
        "device_class": "energy",
        "state_class": "total_increasing",
    },
    "electricity_active_import_total": {
        "name": "Electricity Active Import Total",
        "unit": "kWh",
        "icon": "mdi:flash",
        "device_class": "energy",
        "state_class": "total_increasing",
    },
    "electricity_active_export_total": {
        "name": "Electricity Active Export Total",
        "unit": "kWh",
        "icon": "mdi:flash",
        "device_class": "energy",
        "state_class": "total_increasing",
    },
    
    # Gas
    "gas_provided": {
        "name": "Gas Provided",
        "unit": "m³",
        "icon": "mdi:gas-cylinder",
        "device_class": None,
        "state_class": "total_increasing",
    },
    
    # Voltage
    "voltage_l1": {
        "name": "Voltage L1",
        "unit": "V",
        "icon": "mdi:flash",
        "device_class": "voltage",
        "state_class": "measurement",
    },
    "voltage_l2": {
        "name": "Voltage L2",
        "unit": "V",
        "icon": "mdi:flash",
        "device_class": "voltage",
        "state_class": "measurement",
    },
    "voltage_l3": {
        "name": "Voltage L3",
        "unit": "V",
        "icon": "mdi:flash",
        "device_class": "voltage",
        "state_class": "measurement",
    },
    
    # Current
    "current_l1": {
        "name": "Current L1",
        "unit": "A",
        "icon": "mdi:flash",
        "device_class": "current",
        "state_class": "measurement",
    },
    "current_l2": {
        "name": "Current L2",
        "unit": "A",
        "icon": "mdi:flash",
        "device_class": "current",
        "state_class": "measurement",
    },
    "current_l3": {
        "name": "Current L3",
        "unit": "A",
        "icon": "mdi:flash",
        "device_class": "current",
        "state_class": "measurement",
    },
    
    # Power (per phase)
    "power_generated_l1": {
        "name": "Power Generated L1",
        "unit": "W",
        "icon": "mdi:lightning-bolt",
        "device_class": "power",
        "state_class": "measurement",
    },
    "power_generated_l2": {
        "name": "Power Generated L2",
        "unit": "W",
        "icon": "mdi:lightning-bolt",
        "device_class": "power",
        "state_class": "measurement",
    },
    "power_generated_l3": {
        "name": "Power Generated L3",
        "unit": "W",
        "icon": "mdi:lightning-bolt",
        "device_class": "power",
        "state_class": "measurement",
    },
}

# Parameter metadata by device type
PARAMETER_METADATA = {
    "multical": MULTICAL_PARAMS,
    "dsmr": DSMR_PARAMS,
}


def get_parameter_metadata(device_type: str) -> dict:
    """
    Get parameter metadata for a device type.
    
    Args:
        device_type: Device type identifier (e.g., "multical", "dsmr")
    
    Returns:
        dict: Parameter metadata mapping (param_name -> metadata)
    """
    return PARAMETER_METADATA.get(device_type.lower(), {})


def get_parameter_info(device_type: str, parameter_name: str) -> dict:
    """
    Get metadata for a specific parameter.
    
    Args:
        device_type: Device type identifier
        parameter_name: Parameter name
    
    Returns:
        dict: Parameter metadata (name, unit, icon, device_class, state_class)
              Returns empty dict if parameter not found
    """
    metadata = get_parameter_metadata(device_type)
    return metadata.get(parameter_name, {})
