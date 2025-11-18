#!/usr/bin/python
#
# Device factory for instantiating device implementations by type

import logging
from typing import Dict, Any, Optional
from .base import BaseDevice

log = logging.getLogger(__name__)

# Registry of device type -> class mapping
_DEVICE_REGISTRY: Dict[str, type] = {}


def register_device_type(device_type: str, device_class: type):
    """
    Register a device type implementation.
    
    Args:
        device_type: Device type identifier (e.g., "multical", "dsmr")
        device_class: Class that implements BaseDevice
    """
    if not issubclass(device_class, BaseDevice):
        raise TypeError(f"{device_class} must be a subclass of BaseDevice")
    _DEVICE_REGISTRY[device_type.lower()] = device_class
    log.debug(f"Registered device type: {device_type} -> {device_class.__name__}")


def create_device(device_id: str, device_type: str, device_config: Dict[str, Any]) -> Optional[BaseDevice]:
    """
    Create a device instance of the specified type.
    
    Args:
        device_id: Unique identifier for this device instance
        device_type: Device type (e.g., "multical", "dsmr")
        device_config: Device-specific configuration dict
    
    Returns:
        BaseDevice instance or None if device type not registered
    
    Raises:
        ValueError: If device config is invalid
    """
    device_type_lower = device_type.lower()
    
    if device_type_lower not in _DEVICE_REGISTRY:
        log.error(f"Unknown device type: {device_type}. Registered types: {list(_DEVICE_REGISTRY.keys())}")
        return None
    
    try:
        device_class = _DEVICE_REGISTRY[device_type_lower]
        device = device_class(device_id, device_config)
        device.validate_config()
        return device
    except ValueError as e:
        log.error(f"Invalid config for device {device_id}: {e}")
        return None
    except Exception as e:
        log.error(f"Failed to create device {device_id}: {e}")
        return None


def get_registered_device_types() -> list:
    """Get list of all registered device types."""
    return list(_DEVICE_REGISTRY.keys())
