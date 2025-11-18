#!/usr/bin/python
#
# Base abstraction for meter devices
# All device types (Multical, DSMR, Warmtelink, etc.) implement this interface

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any

log = logging.getLogger(__name__)


class BaseDevice(ABC):
    """
    Abstract base class for all meter device types.
    
    A device is a physical meter that can be read to obtain parameter values.
    This abstraction allows multiple device types (Multical, DSMR, Warmtelink, etc.)
    to be managed uniformly by the framework.
    """

    def __init__(self, device_id: str, device_config: Dict[str, Any]):
        """
        Initialize a device.
        
        Args:
            device_id: Unique identifier for this device instance (e.g., "kitchen_heater")
            device_config: Device-specific configuration dict from config.d/<device>.yaml
        """
        self.device_id = device_id
        self.device_config = device_config
        self.is_connected = False

    @abstractmethod
    def connect(self) -> bool:
        """
        Establish connection to the device.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        pass

    @abstractmethod
    def disconnect(self):
        """Cleanly close connection to the device."""
        pass

    @abstractmethod
    def read(self) -> Optional[Dict[str, Any]]:
        """
        Read current values from the device.
        
        Returns:
            dict: Mapping of parameter_name -> value
                  Returns None if read fails
        """
        pass

    @abstractmethod
    def get_available_parameters(self) -> List[str]:
        """
        Get list of available parameter names for this device type.
        
        Returns:
            list: Parameter names (e.g., ["energy", "power", "temp1"])
        """
        pass

    def get_enabled_parameters(self) -> List[str]:
        """
        Get list of parameters enabled in configuration.
        
        Returns:
            list: Enabled parameter names, or all available if not specified
        """
        configured = self.device_config.get("parameters")
        if configured:
            return configured if isinstance(configured, list) else [configured]
        return self.get_available_parameters()

    def get_device_info(self) -> Dict[str, str]:
        """
        Get metadata about this device.
        
        Returns:
            dict: Device information (type, manufacturer, model, version, etc.)
        """
        return {
            "id": self.device_id,
            "type": self.get_device_type(),
            "manufacturer": self.get_manufacturer(),
            "model": self.get_model(),
        }

    @abstractmethod
    def get_device_type(self) -> str:
        """
        Get device type identifier.
        
        Returns:
            str: Device type (e.g., "multical", "dsmr", "warmtelink")
        """
        pass

    def get_manufacturer(self) -> str:
        """Get device manufacturer."""
        return "Unknown"

    def get_model(self) -> str:
        """Get device model."""
        return "Unknown"

    def get_poll_interval(self) -> int:
        """
        Get polling interval in seconds.
        
        Returns:
            int: Poll interval (default: 300 seconds = 5 minutes)
        """
        return self.device_config.get("poll_interval", 300)

    def validate_config(self) -> bool:
        """
        Validate device configuration.
        
        Returns:
            bool: True if config is valid
            
        Raises:
            ValueError: If configuration is invalid
        """
        required_keys = self.get_required_config_keys()
        for key in required_keys:
            if key not in self.device_config:
                raise ValueError(f"Missing required config key: {key}")
        return True

    @abstractmethod
    def get_required_config_keys(self) -> List[str]:
        """
        Get list of required configuration keys for this device type.
        
        Returns:
            list: Required config keys
        """
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.device_id}, type={self.get_device_type()})"
