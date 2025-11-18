#!/usr/bin/python
#
# DSMR device implementation
# Adapter for Dutch Smart Meter using dsmr-parser library

import logging
from typing import Dict, List, Optional, Any
from .base import BaseDevice

log = logging.getLogger(__name__)


class DSMRDevice(BaseDevice):
    """Device implementation for DSMR (Dutch Smart Meter) electricity meters."""

    def __init__(self, device_id: str, device_config: Dict[str, Any]):
        """
        Initialize DSMR device.
        
        Args:
            device_id: Unique identifier for this device
            device_config: Configuration dict with keys:
                - connection: "serial_port" or "network_url" (required)
                - port or url: Serial port or network URL
                - version: DSMR version (40, 42, 50, 53, etc.)
                - parameters: List of parameters to read (optional)
                - poll_interval: Seconds between reads (default: 10)
                - serial_options: Dict of serial settings
        """
        super().__init__(device_id, device_config)
        self.parser = None
        self.reader = None
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
        Establish connection to DSMR meter.
        
        Returns:
            bool: True if connection successful
        """
        try:
            from dsmr_parser.clients import SerialReader, SocketReader
            
            version = self.device_config.get("version", "50")
            serial_options = self.device_config.get("serial_options", {})
            
            # Set default DSMR serial settings if not overridden
            default_settings = {
                "baudrate": 115200,
                "bytesize": 8,
                "parity": "N",
                "stopbits": 1,
                "timeout": 20,
            }
            settings = {**default_settings, **serial_options}
            
            try:
                connection_type = self.device_config.get("connection", "serial_port")
                
                if connection_type == "serial_port":
                    self.reader = SerialReader(
                        port=self.port,
                        baudrate=settings.get("baudrate"),
                        bytesize=settings.get("bytesize"),
                        parity=settings.get("parity"),
                        stopbits=settings.get("stopbits"),
                        timeout=settings.get("timeout"),
                    )
                elif connection_type == "network_url":
                    self.reader = SocketReader(
                        host=self.port.split(":")[0] if ":" in self.port else self.port,
                        port=int(self.port.split(":")[1]) if ":" in self.port else 23,
                        timeout=settings.get("timeout", 20),
                    )
                
                self.is_connected = True
                log.info(f"Connected to DSMR meter: {self.device_id} (version={version}, type={connection_type})")
                return True
            
            except Exception as e:
                log.error(f"Failed to open connection for {self.device_id}: {e}")
                return False
        
        except ImportError:
            log.error(f"DSMR device requires 'dsmr-parser' library. Install with: pip install dsmr-parser")
            return False
        except Exception as e:
            log.error(f"Connection failed for {self.device_id}: {e}")
            return False

    def disconnect(self):
        """Close connection to meter."""
        try:
            if self.reader:
                self.reader.close()
            self.is_connected = False
            log.debug(f"Disconnected from {self.device_id}")
        except Exception as e:
            log.error(f"Error disconnecting {self.device_id}: {e}")

    def read(self) -> Optional[Dict[str, Any]]:
        """
        Read current values from DSMR meter.
        
        Returns:
            dict: Parameter name -> value mapping
            None if read fails
        """
        if not self.is_connected or not self.reader:
            log.warning(f"Cannot read {self.device_id}: not connected")
            return None
        
        try:
            from dsmr_parser import telegram_to_object
            
            # Read one telegram from DSMR stream
            telegram = self.reader.read_telegram()
            if not telegram:
                return None
            
            # Parse the telegram
            result = telegram_to_object(telegram)
            
            # Extract enabled parameters
            values = {}
            enabled = self.get_enabled_parameters()
            
            for param in enabled:
                if hasattr(result, param):
                    value = getattr(result, param)
                    # Handle objects with 'value' attribute
                    if hasattr(value, 'value'):
                        values[param] = value.value
                    else:
                        values[param] = value
            
            return values if values else None
        
        except Exception as e:
            log.error(f"Failed to read from {self.device_id}: {e}")
            return None

    def get_available_parameters(self) -> List[str]:
        """
        Get all available parameters for DSMR.
        
        Common parameters vary by version, but include:
        - current_electricity_usage
        - current_electricity_delivery
        - electricity_used_tariff_1/2
        - electricity_delivered_tariff_1/2
        - gas_provided
        - voltage_l1/l2/l3
        - current_l1/l2/l3
        
        Returns:
            list: Parameter names
        """
        # Return common DSMR parameters
        return [
            "current_electricity_usage",
            "current_electricity_delivery",
            "electricity_used_tariff_1",
            "electricity_used_tariff_2",
            "electricity_delivered_tariff_1",
            "electricity_delivered_tariff_2",
            "electricity_active_import_total",
            "electricity_active_export_total",
            "gas_provided",
            "voltage_l1",
            "voltage_l2",
            "voltage_l3",
            "current_l1",
            "current_l2",
            "current_l3",
            "power_generated_l1",
            "power_generated_l2",
            "power_generated_l3",
        ]

    def get_device_type(self) -> str:
        """Get device type identifier."""
        return "dsmr"

    def get_manufacturer(self) -> str:
        """Get device manufacturer."""
        return "Various (DSMR standard)"

    def get_model(self) -> str:
        """Get device model."""
        version = self.device_config.get("version", "50")
        return f"DSMR {version}"

    def get_required_config_keys(self) -> List[str]:
        """Get required configuration keys."""
        connection_type = self.device_config.get("connection", "serial_port")
        required = ["connection"]
        if connection_type == "serial_port":
            required.append("port")
        elif connection_type == "network_url":
            required.append("url")
        return required
