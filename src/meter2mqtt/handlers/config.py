#!/usr/bin/python
#
# Configuration management for meter2mqtt
# Supports base config + dynamic per-device configs from config.d/

import logging
import yaml
import os
import ssl
from pathlib import Path
from typing import Dict, Any

log = logging.getLogger(__name__)


def load_base_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """
    Load base configuration from YAML file with environment variable overrides.
    
    Base config contains:
    - MQTT settings
    - Logging settings
    - Home Assistant settings
    - Global defaults
    
    Environment variables take precedence over config file values.
    
    Args:
        config_path: Path to base configuration file (default: config.yaml)
    
    Returns:
        dict: Parsed configuration with environment variable overrides applied
    """
    config = {}
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)
            
            if config is None:
                config = {}
            
            log.debug(f"Base configuration loaded from: {config_path}")
        
        except yaml.YAMLError as e:
            log.error(f"Error parsing YAML configuration: {e}")
            raise
        except Exception as e:
            log.error(f"Error loading configuration: {e}")
            raise
    else:
        log.debug(f"Configuration file not found: {config_path}, using environment variables")
    
    # Apply environment variable overrides
    config = _apply_env_overrides(config)
    
    return config


def load_device_configs(config_dir: str = "config.d") -> Dict[str, Dict[str, Any]]:
    """
    Load all device configurations from config.d/ directory.
    
    Each YAML file in config.d/ should define a single device.
    Filename (without .yaml) becomes the device_id.
    
    Args:
        config_dir: Path to devices config directory (default: config.d)
    
    Returns:
        dict: Mapping of device_id -> device_config
    """
    devices = {}
    config_path = Path(config_dir)
    
    if not config_path.exists():
        log.debug(f"Config directory does not exist: {config_dir}")
        return devices
    
    if not config_path.is_dir():
        log.error(f"Config path is not a directory: {config_dir}")
        return devices
    
    # Find all YAML files in config.d/
    yaml_files = sorted(config_path.glob("*.yaml")) + sorted(config_path.glob("*.yml"))
    
    for config_file in yaml_files:
        device_id = config_file.stem  # filename without extension
        
        try:
            with open(config_file, "r") as f:
                device_config = yaml.safe_load(f)
            
            if device_config is None:
                log.warning(f"Device config file is empty: {config_file}")
                continue
            
            if "type" not in device_config:
                log.error(f"Device config missing 'type' field: {config_file}")
                continue
            
            devices[device_id] = device_config
            log.debug(f"Loaded device config: {device_id} (type={device_config.get('type')})")
        
        except yaml.YAMLError as e:
            log.error(f"Error parsing device config {config_file}: {e}")
        except Exception as e:
            log.error(f"Error loading device config {config_file}: {e}")
    
    return devices


def _apply_env_overrides(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply environment variable overrides to configuration.
    
    Args:
        config: Base configuration dict from YAML
    
    Returns:
        dict: Configuration with environment variable overrides applied
    """
    # Ensure nested dicts exist
    if "mqtt" not in config:
        config["mqtt"] = {}
    if "logging" not in config:
        config["logging"] = {}
    
    # MQTT configuration overrides
    if "MQTT_HOST" in os.environ:
        config["mqtt"]["host"] = os.getenv("MQTT_HOST")
    if "MQTT_PORT" in os.environ:
        config["mqtt"]["port"] = int(os.getenv("MQTT_PORT"))
    if "MQTT_CLIENT" in os.environ:
        config["mqtt"]["client"] = os.getenv("MQTT_CLIENT")
    if "MQTT_QOS" in os.environ:
        config["mqtt"]["qos"] = int(os.getenv("MQTT_QOS"))
    if "MQTT_RETAIN" in os.environ:
        config["mqtt"]["retain"] = os.getenv("MQTT_RETAIN").lower() in ("true", "1", "yes")
    if "MQTT_AUTHENTICATION" in os.environ:
        config["mqtt"]["authentication"] = os.getenv("MQTT_AUTHENTICATION").lower() in ("true", "1", "yes")
    if "MQTT_USERNAME" in os.environ:
        config["mqtt"]["username"] = os.getenv("MQTT_USERNAME")
    if "MQTT_PASSWORD" in os.environ:
        config["mqtt"]["password"] = os.getenv("MQTT_PASSWORD")
    if "MQTT_TLS_ENABLED" in os.environ:
        config["mqtt"]["tls_enabled"] = os.getenv("MQTT_TLS_ENABLED").lower() in ("true", "1", "yes")
    if "MQTT_TLS_CA_CERT" in os.environ:
        config["mqtt"]["tls_ca_cert"] = os.getenv("MQTT_TLS_CA_CERT")
    if "MQTT_TLS_CERT" in os.environ:
        config["mqtt"]["tls_cert"] = os.getenv("MQTT_TLS_CERT")
    if "MQTT_TLS_KEY" in os.environ:
        config["mqtt"]["tls_key"] = os.getenv("MQTT_TLS_KEY")
    if "MQTT_TLS_KEY_PASSWORD" in os.environ:
        config["mqtt"]["tls_key_password"] = os.getenv("MQTT_TLS_KEY_PASSWORD")
    if "MQTT_TLS_INSECURE" in os.environ:
        config["mqtt"]["tls_insecure"] = os.getenv("MQTT_TLS_INSECURE").lower() in ("true", "1", "yes")
    if "MQTT_TLS_VERSION" in os.environ:
        config["mqtt"]["tls_version"] = os.getenv("MQTT_TLS_VERSION")
    if "MQTT_TOPIC_PREFIX" in os.environ:
        config["mqtt"]["topic_prefix"] = os.getenv("MQTT_TOPIC_PREFIX")
    
    # Logging level override
    if "LOG_LEVEL" in os.environ:
        config["logging"]["level"] = os.getenv("LOG_LEVEL")
    
    return config


def get_mqtt_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract and transform MQTT configuration for paho-mqtt client.
    
    Args:
        config: Full configuration dict from load_base_config()
    
    Returns:
        dict: Paho-mqtt compatible configuration parameters
    """
    mqtt_config = config.get("mqtt", {})
    
    paho_config = {
        "broker": mqtt_config.get("host", "localhost"),
        "port": mqtt_config.get("port", 1883),
        "client_id": mqtt_config.get("client", "meter2mqtt"),
        "keepalive": 60,
    }
    
    # Authentication
    if mqtt_config.get("authentication"):
        paho_config["username"] = mqtt_config.get("username")
        paho_config["password"] = mqtt_config.get("password")
    
    # TLS configuration
    if mqtt_config.get("tls_enabled"):
        tls_params = {
            "ca_certs": mqtt_config.get("tls_ca_cert"),
            "certfile": mqtt_config.get("tls_cert"),
            "keyfile": mqtt_config.get("tls_key"),
            "cert_reqs": ssl.CERT_REQUIRED,
            "tls_version": _parse_tls_version(mqtt_config.get("tls_version")),
            "ciphers": None,
        }
        paho_config["tls_params"] = tls_params
        paho_config["tls_insecure"] = mqtt_config.get("tls_insecure", False)
    
    # Publish/subscribe settings
    paho_config["qos"] = mqtt_config.get("qos", 1)
    paho_config["retain"] = mqtt_config.get("retain", True)
    paho_config["topic_prefix"] = mqtt_config.get("topic_prefix", "meters")
    
    return paho_config


def _parse_tls_version(tls_version_str: str) -> any:
    """
    Parse TLS version string to ssl module constant.
    
    Args:
        tls_version_str: String like 'PROTOCOL_TLSv1_2' or None
    
    Returns:
        SSL protocol constant, defaults to PROTOCOL_TLS
    """
    if not tls_version_str:
        return ssl.PROTOCOL_TLS
    
    try:
        return getattr(ssl, tls_version_str)
    except AttributeError:
        log.warning(f"Unknown TLS version: {tls_version_str}, using default")
        return ssl.PROTOCOL_TLS


def get_logging_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Extract logging configuration from config dict."""
    return config.get("logging", {})


def get_homeassistant_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Extract Home Assistant configuration from config dict."""
    return config.get("homeassistant", {})
