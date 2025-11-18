#!/usr/bin/python
#
# Example: Integrating MulticalDevice with Home Assistant MQTT Discovery
# 
# This example shows how to use the updated mqtt_handler with device metadata
# to automatically create Home Assistant entities with proper device classes.

import logging
import time
from meter2mqtt.devices import create_device
from meter2mqtt.devices.ha_metadata import get_parameter_metadata
from meter2mqtt.mqtt import mqtt_handler

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def main():
    """Example: Read from device and publish to Home Assistant via MQTT."""
    
    # 1. Create MQTT handler with Home Assistant discovery
    mqtt_config = {
        "client_id": "meter2mqtt",
        "broker": "localhost",
        "port": 1883,
        "qos": 1,
        "retain": True,
        "topic_prefix": "meter2mqtt",
        "ha_discovery_prefix": "homeassistant",
    }
    
    mqtt = mqtt_handler(mqtt_config)
    mqtt.connect()
    
    # Wait for connection
    for _ in range(10):
        if mqtt.is_connected:
            break
        time.sleep(0.5)
    
    if not mqtt.is_connected:
        log.error("Failed to connect to MQTT")
        return
    
    # 2. Create device
    device_config = {
        "connection": "serial_port",
        "port": "/dev/ttyUSB0",
        "parameters": ["energy", "power", "temp1", "temp2", "volume", "flow"],
    }
    
    device = create_device("kitchen_heater", "multical", device_config)
    
    if not device.connect():
        log.error("Failed to connect to device")
        return
    
    # 3. Get device metadata
    device_info = device.get_device_info()
    device_metadata = get_parameter_metadata("multical")
    
    # 4. Publish Home Assistant discovery
    mqtt.publish_device_discovery(
        device_id="kitchen_heater",
        device_info=device_info,
        device_metadata=device_metadata
    )
    
    # 5. Publish device status
    mqtt.publish_device_status("kitchen_heater", "online")
    
    # 6. Read values and publish
    try:
        values = device.read()
        if values:
            for param_name, value in values.items():
                mqtt.publish_device_value("kitchen_heater", param_name, value)
                log.info(f"Published {param_name}: {value}")
    except Exception as e:
        log.error(f"Failed to read device: {e}")
    
    # 7. Cleanup
    device.disconnect()
    mqtt.publish_device_status("kitchen_heater", "offline")
    mqtt.disconnect()
    mqtt.loop_stop()


if __name__ == "__main__":
    main()
