#!/usr/bin/python
#
# MQTT handler for publishing meter readings with Home Assistant MQTT Discovery

import logging
import json
import paho.mqtt.client as paho
from typing import Dict, Any, Optional

log = logging.getLogger(__name__)


class mqtt_handler:
    """MQTT handler for publishing meter metrics."""
    
    def __init__(self, paho_config):
        """
        Initialize MQTT handler.
        
        Args:
            paho_config: Dictionary from config.get_mqtt_config()
        """
        self.paho_config = paho_config.copy()
        self.mqtt_client = None
        self.is_connected = False
        self.qos = self.paho_config.pop("qos", 1)
        self.retain = self.paho_config.pop("retain", True)
        self.topic_prefix = self.paho_config.pop("topic_prefix", "meters")
        self.ha_discovery_prefix = self.paho_config.pop("ha_discovery_prefix", "homeassistant")
        self.published_entities = {}  # Track which entities have been discovered
    
    def connect(self):
        """Connect to MQTT broker."""
        try:
            # Create client with client_id
            client_id = self.paho_config.pop("client_id")
            self.mqtt_client = paho.Client(paho.CallbackAPIVersion.VERSION1, client_id, True)
            
            # Register callbacks
            self.mqtt_client.on_connect = self._on_connect
            self.mqtt_client.on_disconnect = self._on_disconnect
            
            # Set Last Will Testament
            will_topic = f"{self.topic_prefix}/status"
            self.mqtt_client.will_set(will_topic, payload="offline", qos=1, retain=True)
            
            # Set authentication if provided
            if "username" in self.paho_config and "password" in self.paho_config:
                username = self.paho_config.pop("username")
                password = self.paho_config.pop("password")
                self.mqtt_client.username_pw_set(username, password)
                log.info(f"MQTT authentication enabled for user: {username}")
            
            # Set TLS if provided
            if "tls_params" in self.paho_config:
                tls_params = self.paho_config.pop("tls_params")
                tls_insecure = self.paho_config.pop("tls_insecure", False)
                self.mqtt_client.tls_set(**tls_params)
                self.mqtt_client.tls_insecure_set(tls_insecure)
                log.info("MQTT TLS enabled")
            
            # Connect
            broker = self.paho_config.pop("broker")
            port = self.paho_config.pop("port")
            keepalive = self.paho_config.pop("keepalive", 60)
            
            self.mqtt_client.connect(broker, port, keepalive)
            self.mqtt_client.loop_start()
            
            log.info(f"Connecting to MQTT at: {broker}:{port}")
            
        except Exception as e:
            log.error(f"Failed to connect to MQTT: {e}")
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback for when client connects."""
        if rc == 0:
            self.is_connected = True
            log.info("MQTT client connected successfully")
            try:
                client.publish(f"{self.topic_prefix}/status", "online", qos=1, retain=True)
            except Exception as e:
                log.error(f"Failed to publish online status: {e}")
        else:
            self.is_connected = False
            log.error(f"MQTT connection failed with code {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback for when client disconnects."""
        self.is_connected = False
        if rc != 0:
            log.warning(f"Unexpected disconnection from MQTT (code {rc})")
    
    def disconnect(self):
        """Disconnect from MQTT broker."""
        try:
            if self.mqtt_client:
                self.mqtt_client.disconnect()
        except Exception as e:
            log.error(f"Failed to disconnect from MQTT: {e}")

    def publish(self, topic: str, message: str):
        """
        Publish message to MQTT topic.
        
        Args:
            topic: Full topic path
            message: Message to publish
        """
        if not self.mqtt_client or not self.mqtt_client.is_connected():
            broker = self.paho_config.get("broker", "unknown")
            port = self.paho_config.get("port", "unknown")
            log.warning(f"Cannot publish to MQTT: not connected to {broker}:{port}")
            return
        
        try:
            log.debug(f"Publishing '{topic}': {message}")
            mqtt_info = self.mqtt_client.publish(topic, message, self.qos, self.retain)
            mqtt_info.wait_for_publish()
        except Exception as e:
            log.error(f"Failed to publish to {topic}: {e}")

    def loop_stop(self):
        """Stop MQTT client loop."""
        if self.mqtt_client:
            self.mqtt_client.loop_stop()

    def publish_device_discovery(self, device_id: str, device_info: Dict[str, Any], 
                                  device_metadata: Dict[str, Dict[str, Any]]):
        """
        Publish Home Assistant MQTT Discovery messages for a device.
        
        Creates separate discovery messages for each parameter, allowing Home Assistant
        to automatically create entities with proper device classes and state classes.
        
        Args:
            device_id: Unique device identifier (e.g., "kitchen_heater")
            device_info: Device information dict with keys:
                - type: Device type (e.g., "multical", "dsmr")
                - manufacturer: Manufacturer name
                - model: Device model
                - id: Device identifier (same as device_id)
            device_metadata: Parameter metadata dict mapping parameter_name -> metadata
                - name: Display name
                - unit: Unit of measurement
                - icon: MDI icon name
                - device_class: Home Assistant device class (or None)
                - state_class: Home Assistant state class (or None)
        """
        if not self.is_connected or not device_metadata:
            log.warning(f"Cannot publish discovery for {device_id}: not connected or no metadata")
            return
        
        try:
            device_type = device_info.get("type", "unknown")
            log.info(f"Publishing Home Assistant discovery for {device_id} ({device_type})")
            
            # Get device info for HA
            ha_device = {
                "identifiers": [device_id],
                "name": device_id.replace("_", " ").title(),
                "manufacturer": device_info.get("manufacturer", "Unknown"),
                "model": device_info.get("model", "Unknown"),
            }
            
            # Publish discovery for each parameter
            published_count = 0
            for param_name, metadata in device_metadata.items():
                if self._publish_entity_discovery(device_id, param_name, metadata, ha_device):
                    published_count += 1
            
            # Publish availability/status sensor
            self._publish_status_discovery(device_id, ha_device)
            
            log.info(f"Published discovery for {published_count} entities for device {device_id}")
            self.published_entities[device_id] = list(device_metadata.keys())
        
        except Exception as e:
            log.error(f"Failed to publish discovery for {device_id}: {e}")
    
    def _publish_entity_discovery(self, device_id: str, param_name: str, 
                                   metadata: Dict[str, Any], ha_device: Dict[str, Any]) -> bool:
        """
        Publish a single Home Assistant entity discovery message.
        
        Args:
            device_id: Device identifier
            param_name: Parameter name
            metadata: Parameter metadata
            ha_device: Home Assistant device info
        
        Returns:
            bool: True if published successfully
        """
        try:
            # Create unique ID and entity ID
            unique_id = f"{device_id}_{param_name}"
            
            # Build discovery payload
            discovery_payload = {
                "name": metadata.get("name", param_name),
                "unique_id": unique_id,
                "state_topic": f"{self.topic_prefix}/{device_id}/{param_name}",
                "availability_topic": f"{self.topic_prefix}/{device_id}/status",
                "payload_available": "online",
                "payload_not_available": "offline",
                "device": ha_device,
            }
            
            # Add unit if present
            if metadata.get("unit"):
                discovery_payload["unit_of_measurement"] = metadata["unit"]
            
            # Add icon if present
            if metadata.get("icon"):
                discovery_payload["icon"] = metadata["icon"]
            
            # Add device_class if present (enables special formatting and features)
            if metadata.get("device_class"):
                discovery_payload["device_class"] = metadata["device_class"]
            
            # Add state_class if present (defines value semantics)
            if metadata.get("state_class"):
                discovery_payload["state_class"] = metadata["state_class"]
            
            # For numeric values, add value template
            discovery_payload["value_template"] = "{{ value }}"
            
            # Publish discovery message to Home Assistant
            discovery_topic = f"{self.ha_discovery_prefix}/sensor/{unique_id}/config"
            payload_json = json.dumps(discovery_payload)
            
            log.debug(f"Publishing discovery to {discovery_topic}")
            self.publish(discovery_topic, payload_json)
            return True
        
        except Exception as e:
            log.error(f"Failed to publish entity discovery for {device_id}/{param_name}: {e}")
            return False
    
    def _publish_status_discovery(self, device_id: str, ha_device: Dict[str, Any]):
        """
        Publish availability/status entity discovery.
        
        Args:
            device_id: Device identifier
            ha_device: Home Assistant device info
        """
        try:
            unique_id = f"{device_id}_status"
            status_payload = {
                "name": f"{device_id} Status",
                "unique_id": unique_id,
                "state_topic": f"{self.topic_prefix}/{device_id}/status",
                "payload_on": "online",
                "payload_off": "offline",
                "device": ha_device,
                "icon": "mdi:connection",
            }
            
            discovery_topic = f"{self.ha_discovery_prefix}/binary_sensor/{unique_id}/config"
            payload_json = json.dumps(status_payload)
            
            self.publish(discovery_topic, payload_json)
        except Exception as e:
            log.error(f"Failed to publish status discovery for {device_id}: {e}")
    
    def publish_device_value(self, device_id: str, parameter: str, value: Any):
        """
        Publish a single parameter value for a device.
        
        Args:
            device_id: Device identifier
            parameter: Parameter name
            value: Parameter value
        """
        topic = f"{self.topic_prefix}/{device_id}/{parameter}"
        self.publish(topic, str(value))
    
    def publish_device_status(self, device_id: str, status: str):
        """
        Publish device status (online/offline).
        
        Args:
            device_id: Device identifier
            status: Status string ("online" or "offline")
        """
        topic = f"{self.topic_prefix}/{device_id}/status"
        self.publish(topic, status)
