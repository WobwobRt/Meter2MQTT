#!/usr/bin/python
#
# Device implementations for various meter types

from .base import BaseDevice
from .factory import register_device_type, create_device, get_registered_device_types
from .dsmr import DSMRDevice
from .multical import MulticalDevice

# Register built-in device types
register_device_type("dsmr", DSMRDevice)
register_device_type("multical", MulticalDevice)

__all__ = ["BaseDevice", "create_device", "get_registered_device_types", "DSMRDevice", "MulticalDevice"]
