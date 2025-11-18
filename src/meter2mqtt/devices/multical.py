#!/usr/bin/python
#
# Multical device implementation
# Adapter for Kamstrup Multical heat meters

import logging
from typing import Dict, List, Optional, Any
from .base import BaseDevice

log = logging.getLogger(__name__)


class MulticalDevice(BaseDevice):
    """Device implementation for Kamstrup Multical heat meters."""

    def __init__(self, device_id: str, device_config: Dict[str, Any]):
        """
        Initialize Multical device.
        
        Args:
            device_id: Unique identifier for this device
            device_config: Configuration dict with keys:
                - connection: "serial_port" or "network_url" (required)
                - port or url: Serial port or network URL
                - version: Multical version (402, 403, 603, etc.)
                - parameters: List of parameters to read (optional)
                - poll_interval: Seconds between reads (default: 300)
                - serial_options: Dict of serial settings
        """
        super().__init__(device_id, device_config)
        self.parser = None
        self._validate_and_initialize()

    def _validate_and_initialize(self):
        """Validate config and prepare for connection."""
        connection_type = self.device_config.get("connection", "serial_port")
        
        if connection_type == "serial_port":
            self.port = self.device_config.get("port")
            if not self.port:
                raise ValueError(f"Missing 'port' in config for serial connection")
        elif connection_type == "network_url":
            self.port = self.device_config.get("url")
            if not self.port:
                raise ValueError(f"Missing 'url' in config for network connection")
        else:
            raise ValueError(f"Unknown connection type: {connection_type}")

    def connect(self) -> bool:
        """
        Establish connection to Multical meter.
        
        Returns:
            bool: True if connection successful
        """
        try:
            # Import inside method to handle optional dependency
            try:
                from kamstrup2mqtt.parser import kamstrup_parser
            except ImportError:
                log.error(f"Multical device requires 'kamstrup2mqtt' library. Install with: pip install kamstrup2mqtt")
                return False
            
            version = self.device_config.get("version", "402")
            params = self.device_config.get("parameters", [])
            serial_options = self.device_config.get("serial_options", {})
            
            try:
                self.parser = kamstrup_parser(
                    port=self.port,
                    parameters=params if params else None,
                    version=version,
                    serial_options=serial_options if serial_options else None
                )
                
                self.is_connected = True
                log.info(f"Connected to Multical meter: {self.device_id} (version={version}, port={self.port})")
                return True
            
            except Exception as e:
                log.error(f"Failed to initialize Multical parser for {self.device_id}: {e}")
                return False
        
        except Exception as e:
            log.error(f"Connection failed for {self.device_id}: {e}")
            return False

    def disconnect(self):
        """Close connection to meter."""
        try:
            if self.parser:
                self.parser.close()
            self.is_connected = False
            log.debug(f"Disconnected from {self.device_id}")
        except Exception as e:
            log.error(f"Error disconnecting {self.device_id}: {e}")

    def read(self) -> Optional[Dict[str, Any]]:
        """
        Read current values from Multical meter.
        
        Returns:
            dict: Parameter name -> value mapping
            None if read fails
        """
        if not self.is_connected or not self.parser:
            log.warning(f"Cannot read {self.device_id}: not connected")
            return None
        
        try:
            values = self.parser.run()
            return values if values else None
        
        except Exception as e:
            log.error(f"Failed to read from {self.device_id}: {e}")
            return None

    def get_available_parameters(self) -> List[str]:
        """
        Get all available parameters for Multical.
        
        Includes:
        - Core: energy, power, temp1, temp2, volume, flow, tempdiff
        - Monthly stats: min/max flow, power, average temps
        - Yearly stats: min/max flow, power, average temps
        - Other: temp1xm3, temp2xm3, infoevent, hourcounter
        
        Returns:
            list: Parameter names
        """
        return [
            # Core parameters
            "energy",
            "power",
            "temp1",
            "temp2",
            "volume",
            "flow",
            "tempdiff",
            "temp1xm3",
            "temp2xm3",
            
            # Monthly statistics
            "minflow_m",
            "maxflow_m",
            "minflowDate_m",
            "maxflowDate_m",
            "minpower_m",
            "maxpower_m",
            "minpowerdate_m",
            "maxpowerdate_m",
            "avgtemp1_m",
            "avgtemp2_m",
            
            # Yearly statistics
            "minflow_y",
            "maxflow_y",
            "minflowdate_y",
            "maxflowdate_y",
            "minpower_y",
            "maxpower_y",
            "minpowerdate_y",
            "maxpowerdate_y",
            "avgtemp1_y",
            "avgtemp2_y",
            
            # Other parameters
            "infoevent",
            "hourcounter",
            "e1highres",
        ]

    def get_device_type(self) -> str:
        """Get device type identifier."""
        return "multical"

    def get_manufacturer(self) -> str:
        """Get device manufacturer."""
        return "Kamstrup"

    def get_model(self) -> str:
        """Get device model."""
        version = self.device_config.get("version", "402")
        return f"Multical {version}"

    def get_required_config_keys(self) -> List[str]:
        """Get required configuration keys."""
        connection_type = self.device_config.get("connection", "serial_port")
        required = ["connection"]
        if connection_type == "serial_port":
            required.append("port")
        elif connection_type == "network_url":
            required.append("url")
        return required
