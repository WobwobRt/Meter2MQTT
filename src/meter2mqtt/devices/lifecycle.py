#!/usr/bin/python
#
# Device lifecycle manager with dynamic config file watching
# Handles spawning, reloading, and terminating device processes

import logging
import time
import threading
from pathlib import Path
from typing import Dict, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from .base import BaseDevice
from .factory import create_device

log = logging.getLogger(__name__)


class DeviceConfigWatcher(FileSystemEventHandler):
    """Watches config.d/ directory for device configuration changes."""

    def __init__(self, lifecycle_manager):
        """
        Initialize watcher.
        
        Args:
            lifecycle_manager: Reference to DeviceLifecycleManager
        """
        self.lifecycle_manager = lifecycle_manager

    def on_created(self, event):
        """Handle new config file created."""
        if event.is_directory:
            return
        if self._is_yaml_file(event.src_path):
            log.debug(f"Config file created: {event.src_path}")
            self.lifecycle_manager._on_config_change()

    def on_modified(self, event):
        """Handle config file modified."""
        if event.is_directory:
            return
        if self._is_yaml_file(event.src_path):
            log.debug(f"Config file modified: {event.src_path}")
            self.lifecycle_manager._on_config_change()

    def on_deleted(self, event):
        """Handle config file deleted."""
        if event.is_directory:
            return
        if self._is_yaml_file(event.src_path):
            log.debug(f"Config file deleted: {event.src_path}")
            self.lifecycle_manager._on_config_change()

    def on_moved(self, event):
        """Handle config file moved/renamed."""
        if event.is_directory:
            return
        if self._is_yaml_file(event.dest_path):
            log.debug(f"Config file moved: {event.src_path} -> {event.dest_path}")
            self.lifecycle_manager._on_config_change()

    @staticmethod
    def _is_yaml_file(path: str) -> bool:
        """Check if file is a YAML config file."""
        return path.endswith((".yaml", ".yml"))


class DeviceLifecycleManager:
    """Manages device lifecycle: spawn, reload, terminate."""

    def __init__(self, config_dir: str = "config.d", reload_delay: float = 1.0):
        """
        Initialize lifecycle manager.
        
        Args:
            config_dir: Path to device configs directory
            reload_delay: Delay in seconds before applying config changes (debounce)
        """
        self.config_dir = Path(config_dir)
        self.reload_delay = reload_delay
        self.devices: Dict[str, BaseDevice] = {}
        self.config_checksums: Dict[str, str] = {}
        
        self.observer: Optional[Observer] = None
        self.reload_timer: Optional[threading.Timer] = None
        self._lock = threading.Lock()

    def start_watching(self):
        """Start watching config directory for changes."""
        if not self.config_dir.exists():
            log.warning(f"Config directory does not exist: {self.config_dir}")
            self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.observer = Observer()
        self.observer.schedule(DeviceConfigWatcher(self), str(self.config_dir))
        self.observer.start()
        log.info(f"Started watching config directory: {self.config_dir}")

    def stop_watching(self):
        """Stop watching config directory."""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            log.info("Stopped watching config directory")

    def load_and_reconcile_devices(self, device_configs: Dict[str, dict]):
        """
        Load devices from config and reconcile with running instances.
        
        - Start new devices from configs
        - Reload devices with changed configs
        - Stop devices with removed configs
        
        Args:
            device_configs: Dict of device_id -> device_config from load_device_configs()
        """
        with self._lock:
            log.debug(f"Reconciling devices: found {len(device_configs)} in config")
            
            # Get current config file checksums to detect real changes
            current_checksums = self._compute_config_checksums(device_configs)
            
            # Find devices to add/reload/remove
            config_ids = set(device_configs.keys())
            running_ids = set(self.devices.keys())
            
            # Remove devices with deleted configs
            for device_id in running_ids - config_ids:
                self._stop_device(device_id)
            
            # Add/reload devices
            for device_id, device_config in device_configs.items():
                checksum = current_checksums.get(device_id)
                old_checksum = self.config_checksums.get(device_id)
                
                if device_id not in self.devices:
                    # New device
                    self._start_device(device_id, device_config)
                    self.config_checksums[device_id] = checksum
                elif checksum != old_checksum:
                    # Config changed, reload device
                    log.info(f"Reloading device {device_id} (config changed)")
                    self._stop_device(device_id)
                    self._start_device(device_id, device_config)
                    self.config_checksums[device_id] = checksum

    def _start_device(self, device_id: str, device_config: dict):
        """
        Start a device.
        
        Args:
            device_id: Device identifier
            device_config: Device configuration dict
        """
        try:
            device_type = device_config.get("type")
            device = create_device(device_id, device_type, device_config)
            
            if device is None:
                log.error(f"Failed to create device: {device_id}")
                return
            
            if not device.connect():
                log.error(f"Failed to connect device: {device_id}")
                return
            
            self.devices[device_id] = device
            log.info(f"Started device: {device_id} ({device.get_device_type()})")
        
        except Exception as e:
            log.error(f"Error starting device {device_id}: {e}")

    def _stop_device(self, device_id: str):
        """
        Stop a device.
        
        Args:
            device_id: Device identifier
        """
        try:
            if device_id in self.devices:
                device = self.devices[device_id]
                device.disconnect()
                del self.devices[device_id]
                log.info(f"Stopped device: {device_id}")
            
            if device_id in self.config_checksums:
                del self.config_checksums[device_id]
        
        except Exception as e:
            log.error(f"Error stopping device {device_id}: {e}")

    def get_device(self, device_id: str) -> Optional[BaseDevice]:
        """Get a device by ID."""
        return self.devices.get(device_id)

    def get_all_devices(self) -> Dict[str, BaseDevice]:
        """Get all active devices."""
        return self.devices.copy()

    def _on_config_change(self):
        """Handle config file change (debounced)."""
        with self._lock:
            # Cancel pending reload if any
            if self.reload_timer:
                self.reload_timer.cancel()
            
            # Schedule new reload with debounce delay
            self.reload_timer = threading.Timer(self.reload_delay, self._reload_all)
            self.reload_timer.start()

    def _reload_all(self):
        """Reload all device configurations (called after debounce)."""
        try:
            from ..config import load_device_configs
            device_configs = load_device_configs(str(self.config_dir))
            self.load_and_reconcile_devices(device_configs)
        except Exception as e:
            log.error(f"Error reloading device configs: {e}")

    def _compute_config_checksums(self, device_configs: Dict[str, dict]) -> Dict[str, str]:
        """Compute checksums for device configs to detect real changes."""
        import hashlib
        import json
        checksums = {}
        for device_id, config in device_configs.items():
            # Create checksum from config (excluding comments)
            config_str = json.dumps(config, sort_keys=True)
            checksum = hashlib.md5(config_str.encode()).hexdigest()
            checksums[device_id] = checksum
        return checksums

    def shutdown(self):
        """Shut down all devices and stop watching."""
        self.stop_watching()
        
        with self._lock:
            device_ids = list(self.devices.keys())
            for device_id in device_ids:
                self._stop_device(device_id)
        
        log.info("Device lifecycle manager shut down")
