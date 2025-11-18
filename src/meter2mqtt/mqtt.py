#!/usr/bin/python
#
# MQTT handler for publishing meter readings

import logging
import json
import paho.mqtt.client as paho

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
