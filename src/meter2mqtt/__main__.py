#!/usr/bin/python
#
# Multi-device daemon for meter2mqtt

import sys
import signal
import logging
import time
from typing import Optional

from meter2mqtt.handlers.config import load_base_config, load_device_configs, get_mqtt_config, get_logging_config
from meter2mqtt.devices.lifecycle import DeviceLifecycleManager
from meter2mqtt.handlers.mqtt import mqtt_handler

log = logging.getLogger(__name__)


class Meter2MQTTDaemon:
    """Main daemon for multi-device meter reading and MQTT publishing."""

    def __init__(self, config_path: str = "config.yaml", config_dir: str = "config.d"):
        """
        Initialize the daemon.
        
        Args:
            config_path: Path to base configuration file
            config_dir: Path to device configs directory
        """
        self.running = True
        self.mqtt_handler_instance: Optional[mqtt_handler] = None
        self.lifecycle_manager: Optional[DeviceLifecycleManager] = None
        
        try:
            # Load base configuration
            self.base_config = load_base_config(config_path)
            log.info("Base configuration loaded")
            
            # Initialize MQTT
            self._initialize_mqtt()
            
            # Initialize device lifecycle manager
            self.lifecycle_manager = DeviceLifecycleManager(config_dir=config_dir)
            self.lifecycle_manager.start_watching()
            
            # Load initial device configurations
            device_configs = load_device_configs(config_dir)
            self.lifecycle_manager.load_and_reconcile_devices(device_configs)
            
            # Register signal handlers
            signal.signal(signal.SIGINT, self.signal_handler)
            signal.signal(signal.SIGTERM, self.signal_handler)
            
        except Exception as e:
            log.error(f"Failed to initialize daemon: {e}")
            raise

    def _initialize_mqtt(self):
        """Initialize MQTT handler."""
        try:
            mqtt_cfg = get_mqtt_config(self.base_config)
            self.mqtt_handler_instance = mqtt_handler(mqtt_cfg)
            self.mqtt_handler_instance.connect()
            log.info("MQTT handler initialized")
        except Exception as e:
            log.error(f"Failed to initialize MQTT handler: {e}")
            raise

    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        log.info(f"Received signal {signum}, shutting down daemon")
        self.running = False
        self.cleanup()
        sys.exit(0)

    def cleanup(self):
        """Clean up resources."""
        try:
            if self.lifecycle_manager:
                self.lifecycle_manager.shutdown()
        except Exception as e:
            log.error(f"Error shutting down device lifecycle manager: {e}")
        
        try:
            if self.mqtt_handler_instance:
                self.mqtt_handler_instance.loop_stop()
                self.mqtt_handler_instance.disconnect()
        except Exception as e:
            log.error(f"Error closing MQTT handler: {e}")

    def run(self):
        """Main daemon loop."""
        log.info("Meter2MQTT daemon started successfully")
        
        try:
            while self.running:
                try:
                    # Read from all active devices
                    self._read_all_devices()
                    
                    # Small delay to prevent busy-waiting
                    time.sleep(1)
                
                except Exception as e:
                    log.error(f"Error in daemon loop: {e}")

        except KeyboardInterrupt:
            log.info("Daemon interrupted")
        finally:
            self.cleanup()

    def _read_all_devices(self):
        """Read from all active devices and publish to MQTT."""
        devices = self.lifecycle_manager.get_all_devices()
        
        for device_id, device in devices.items():
            try:
                poll_interval = device.get_poll_interval()
                
                # Simple polling: read every poll_interval seconds
                current_time = time.time()
                device_attr = f"_last_read_{device_id}"
                last_read = getattr(self, device_attr, 0)
                
                if current_time - last_read >= poll_interval:
                    values = device.read()
                    if values:
                        self._publish_device_metrics(device_id, device, values)
                    setattr(self, device_attr, current_time)
            
            except Exception as e:
                log.error(f"Error reading device {device_id}: {e}")

    def _publish_device_metrics(self, device_id: str, device, values: dict):
        """
        Publish device metrics to MQTT.
        
        Args:
            device_id: Device identifier
            device: Device instance
            values: Dict of parameter_name -> value
        """
        if not self.mqtt_handler_instance:
            return
        
        mqtt_cfg = get_mqtt_config(self.base_config)
        topic_prefix = mqtt_cfg.get("topic_prefix", "meters")
        
        for param_name, param_value in values.items():
            try:
                # Topic structure: meters/<device_type>/<device_id>/<param>
                topic = f"{topic_prefix}/{device.get_device_type()}/{device_id}/{param_name}"
                message = str(param_value)
                self.mqtt_handler_instance.publish(topic, message)
            except Exception as e:
                log.error(f"Failed to publish metric {param_name} for {device_id}: {e}")


def main():
    """Entry point for the daemon."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        daemon = Meter2MQTTDaemon(
            config_path="config.yaml",
            config_dir="config.d"
        )
        daemon.run()
    except Exception as e:
        log.error(f"Daemon failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
