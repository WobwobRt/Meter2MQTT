# Contributing to meter2mqtt

Welcome! 👋 We're excited to have you contribute to meter2mqtt. This guide will help you get started, whether you're fixing a bug, adding a new device, or improving documentation.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Adding Device Support](#adding-device-support)
- [Development Workflow](#development-workflow)
- [Code Style](#code-style)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

We're committed to providing a welcoming and inclusive environment. Please:
- Be respectful and constructive
- Help others learn and grow
- Report issues privately to maintainers if needed
- Celebrate wins and help each other debug problems

## Getting Started

### Prerequisites

- Python 3.8+
- Git
- MQTT broker (mosquitto, EMQX, etc.)
- Basic knowledge of MQTT and your meter device

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/WobwobRt/meter2mqtt.git
cd meter2mqtt

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install pytest pytest-cov black flake8
```

### Explore the Project Structure

```
meter2mqtt/
├── src/meter2mqtt/
│   ├── devices/              # Device drivers
│   │   ├── base.py           # BaseDevice abstract class
│   │   ├── dsmr.py           # Dutch smart meter (DSMR)
│   │   ├── multical.py       # Kamstrup heat meter
│   │   ├── factory.py        # Device creation
│   │   └── lifecycle.py      # Device lifecycle manager
│   ├── mqtt.py               # MQTT handler
│   ├── config.py             # Configuration loader
│   └── __main__.py           # Entry point
├── config.d/                 # Configuration examples
├── CONTRIBUTING.md           # This file!
├── ARCHITECTURE.md           # System design
└── README.md                 # Project overview
```

## How to Contribute

### Report Bugs

Found a bug? Great! Here's how to report it:

1. **Check existing issues** - Search to see if it's already reported
2. **Create a new issue** with:
   - Clear title describing the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - Device type and meter model
   - Configuration (sanitize any sensitive info)
   - Error logs/stack traces

Example:
```
Title: Multical device fails to connect on startup

Steps to reproduce:
1. Configure multical device with serial port /dev/ttyUSB0
2. Start meter2mqtt
3. Check logs

Expected: Device connects successfully
Actual: Connection timeout error after 30s

Device: Kamstrup Multical 402
Error: [ERROR] Connection failed: timeout on /dev/ttyUSB0
```

### Suggest Features

Have an idea? We'd love to hear it!

1. **Check existing discussions** - Avoid duplicates
2. **Create an issue** describing:
   - What you want to achieve
   - Why it would be useful
   - Possible implementation approach (optional)

Example:
```
Title: Add Kamstrup Multical 603 support

I have a Multical 603 heat meter and would like to add support.
It's similar to the 402 but has additional parameters for
multi-circuit metering.

Reference: https://github.com/wobwobrt/kamstrup2mqtt
```

### Improve Documentation

Documentation improvements are always welcome!

- Fix typos or unclear explanations
- Add examples or clarifications
- Improve formatting or structure
- Translate documentation

Simply edit the relevant `.md` file and submit a pull request.

### Fix Bugs or Implement Features

Ready to code? Jump to [Development Workflow](#development-workflow) below.

## Adding Device Support

Adding a new device is straightforward! Here's the complete process:

### Step 1: Research Your Device

Gather information about your meter:
- **Device name & manufacturer** (e.g., "Kamstrup Multical 402")
- **Connection type** (serial, network, USB, etc.)
- **Protocol** (DLMS, Modbus, DSMR, custom, etc.)
- **Available parameters** (what can we read?)
- **Parameter details**:
  - Human-readable names
  - Units (kWh, W, °C, m³, etc.)
  - Data types (int, float, string)
  - Hex codes or parameter IDs
  - Home Assistant device classes
- **Documentation/GitHub repo** with parser code or examples

### Step 2: Create Device Driver

Create a new file in `src/meter2mqtt/devices/`:

```python
# src/meter2mqtt/devices/your_device.py

from .base import BaseDevice
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class YourDeviceClass(BaseDevice):
    """Driver for Your Device manufacturer."""
    
    def __init__(self, device_id: str, config: Dict[str, Any]):
        """Initialize device.
        
        Args:
            device_id: Unique device identifier
            config: Device configuration dict with:
                - connection: Connection details (serial port, host, etc.)
                - version: Device version (optional)
                - parameters: List of parameters to read (optional)
        """
        super().__init__(device_id, config)
        self.connection = None
        # Add device-specific attributes
        
    def connect(self) -> bool:
        """Connect to the device.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Implement connection logic
            logger.info(f"Connected to {self.device_id}")
            return True
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False
    
    def disconnect(self) -> bool:
        """Disconnect from the device.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Implement disconnection logic
            logger.info(f"Disconnected from {self.device_id}")
            return True
        except Exception as e:
            logger.error(f"Disconnection failed: {e}")
            return False
    
    def read(self) -> Dict[str, Any]:
        """Read all available parameters from device.
        
        Returns:
            Dictionary of parameter names to values:
            {
                "energy": 1234.56,
                "power": 45.8,
                "temperature_1": 52.3,
                ...
            }
        """
        try:
            if not self.is_connected():
                raise RuntimeError("Device not connected")
            
            # Implement reading logic
            values = {}
            
            # Example:
            # values["energy"] = self._read_energy()
            # values["power"] = self._read_power()
            
            return values
        except Exception as e:
            logger.error(f"Read failed: {e}")
            return {}
    
    def get_available_parameters(self) -> list:
        """Get list of available parameters.
        
        Returns:
            List of parameter names available from this device
        """
        return [
            "energy",
            "power",
            "temperature_1",
            "temperature_2",
            "volume",
            "flow",
            # ... add all supported parameters
        ]
    
    def is_connected(self) -> bool:
        """Check if device is connected.
        
        Returns:
            True if connected, False otherwise
        """
        return self.connection is not None
    
    def get_device_info(self) -> Dict[str, str]:
        """Get device information for Home Assistant.
        
        Returns:
            Dictionary with device info:
            {
                "type": "your_device",
                "manufacturer": "Manufacturer Name",
                "model": "Model XYZ",
                "id": self.device_id
            }
        """
        return {
            "type": "your_device",
            "manufacturer": "Manufacturer Name",
            "model": "Model XYZ",
            "id": self.device_id
        }
    
    # Helper methods (private)
    
    def _read_energy(self) -> float:
        """Read energy value from device."""
        # Implementation specific to your device
        pass


# Optional: Add helper functions
def parse_device_response(response: bytes) -> Dict[str, Any]:
    """Parse device response into parameter values."""
    # Implementation specific to your device protocol
    pass
```

### Step 3: Add Home Assistant Metadata

Add your device's parameters to `src/meter2mqtt/devices/ha_metadata.py`:

```python
# In ha_metadata.py, add to appropriate section or create new:

YOUR_DEVICE_PARAMS = {
    "energy": {
        "name": "Energy",
        "unit": "kWh",
        "icon": "mdi:flash",
        "device_class": "energy",
        "state_class": "total_increasing",
    },
    "power": {
        "name": "Current Power",
        "unit": "W",
        "icon": "mdi:lightning-bolt",
        "device_class": "power",
        "state_class": "measurement",
    },
    "temperature_1": {
        "name": "Temperature 1",
        "unit": "°C",
        "icon": "mdi:thermometer",
        "device_class": "temperature",
        "state_class": "measurement",
    },
    # ... add all parameters
}
```

Then update the `get_parameter_metadata()` function to include your device.

### Step 4: Register Your Device

Update `src/meter2mqtt/devices/__init__.py`:

```python
from .your_device import YourDeviceClass

# Register the device type
register_device_type("your_device", YourDeviceClass)
```

### Step 5: Create Configuration Example

Create `config.d/your_device.yaml.example`:

```yaml
# Example configuration for Your Device
device:
  type: your_device
  device_id: my_device
  
  # Connection options
  connection:
    # For serial connection:
    port: /dev/ttyUSB0
    baudrate: 9600
    
    # For network connection:
    # host: 192.168.1.100
    # port: 502
  
  # Optional: Device version/model
  version: "2"
  
  # Optional: Specific parameters to read
  parameters:
    - energy
    - power
    - temperature_1
  
  # Optional: Poll interval
  poll_interval: 30
```

### Step 6: Write Tests

Create `tests/test_your_device.py`:

```python
import pytest
from meter2mqtt.devices.your_device import YourDeviceClass


class TestYourDevice:
    """Tests for YourDeviceClass."""
    
    def test_initialization(self):
        """Test device initialization."""
        config = {
            "connection": {"port": "/dev/ttyUSB0"},
        }
        device = YourDeviceClass("test_device", config)
        assert device.device_id == "test_device"
    
    def test_get_available_parameters(self):
        """Test parameter list."""
        config = {"connection": {}}
        device = YourDeviceClass("test_device", config)
        params = device.get_available_parameters()
        assert "energy" in params
        assert len(params) > 0
    
    def test_get_device_info(self):
        """Test device info format."""
        config = {"connection": {}}
        device = YourDeviceClass("test_device", config)
        info = device.get_device_info()
        assert info["type"] == "your_device"
        assert info["id"] == "test_device"
        assert "manufacturer" in info
```

### Step 7: Update Documentation

Add device documentation to relevant files:

1. **README.md** - Add to supported devices list
2. **SETUP.md** - Add setup instructions for your device
3. **docs/DEVICES.md** (create if needed) - Full device documentation

Example for README.md:
```markdown
## Supported Devices

- **Dutch Smart Meter (DSMR)** - via serial connection
- **Kamstrup Multical** - Heat meter via serial/network
- **Your Device** - Via serial/network (v2.0+)
```

### Step 8: Submit Pull Request

1. Create a feature branch: `git checkout -b add-your-device-support`
2. Commit your changes with clear messages
3. Push to your fork
4. Create a pull request with:
   - Descriptive title: "Add support for Your Device"
   - Description including:
     - Device name and manufacturer
     - Connection type
     - Parameters supported
     - Testing done
     - Any dependencies added

## Development Workflow

### 1. Create a Branch

```bash
# Create feature branch from main
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/bug-description

# Or for documentation
git checkout -b docs/description
```

### 2. Make Changes

```bash
# Install in development mode
pip install -e .

# Make your changes
# Test frequently!

# Run tests
pytest tests/

# Check code style
flake8 src/
black --check src/
```

### 3. Commit Your Changes

```bash
# Stage changes
git add src/meter2mqtt/your_changes.py

# Commit with clear message
git commit -m "Add feature X for device Y

- Implement reading of parameter Z
- Add Home Assistant metadata
- Update configuration example

Closes #123"
```

### 4. Keep Updated

```bash
# Fetch latest changes
git fetch origin

# Rebase on main
git rebase origin/main

# Or merge if you prefer
git merge origin/main
```

### 5. Push and Create PR

```bash
# Push your branch
git push origin feature/your-feature-name

# Create PR on GitHub
# Use template provided
```

## Code Style

### Python Style Guide

We follow PEP 8 with these preferences:

```python
# Use type hints
def read(self) -> Dict[str, Any]:
    """Read device parameters."""
    pass

# Use descriptive names
# Good: energy_total, power_current
# Bad: e, p, val1, val2

# Add docstrings to all public methods
def connect(self) -> bool:
    """Connect to device.
    
    Returns:
        True if connection successful, False otherwise
    """
    pass

# Use logging, not print
import logging
logger = logging.getLogger(__name__)
logger.info("Device connected")

# Use context managers for resources
with serial.Serial(port, baudrate) as conn:
    data = conn.read()
```

### Format Code

```bash
# Auto-format with black
black src/

# Check style with flake8
flake8 src/
```

### Documentation

- Use clear, concise language
- Add examples where helpful
- Keep README.md updated
- Document configuration options
- Include troubleshooting tips

## Testing

### Run Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_devices.py

# Run with coverage
pytest --cov=src/meter2mqtt

# Run specific test
pytest tests/test_devices.py::TestDSMR::test_connect
```

### What to Test

For device drivers:
- ✅ Initialization with valid/invalid config
- ✅ Connection/disconnection
- ✅ Parameter reading (mock if needed)
- ✅ Error handling
- ✅ Device info format

For MQTT handler:
- ✅ Connection to broker
- ✅ Publishing messages
- ✅ Subscriptions
- ✅ Reconnection logic

For configuration:
- ✅ Loading valid configs
- ✅ Validation of required fields
- ✅ Handling missing optional fields

## Pull Request Process

### Before Submitting

- [ ] Code follows style guide (run `black src/`)
- [ ] All tests pass (`pytest`)
- [ ] No linting errors (`flake8 src/`)
- [ ] Added tests for new functionality
- [ ] Updated documentation (README, examples, etc.)
- [ ] Commit messages are clear and descriptive
- [ ] Branch is up to date with main

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Device support
- [ ] Documentation update
- [ ] Performance improvement

## Device Support (if applicable)
- Device: Manufacturer Model
- Type: Heat meter / Smart meter / etc.
- Connection: Serial / Network / USB / etc.
- Parameters: List of parameters

## Testing
- [ ] Tested with actual device
- [ ] Unit tests added
- [ ] Configuration tested
- [ ] Home Assistant integration verified

## Related Issues
Closes #123

## Checklist
- [ ] Code follows style guide
- [ ] Tests pass
- [ ] Documentation updated
- [ ] No breaking changes
```

### Review Process

1. **Maintainer Review** - We'll review your PR within a few days
2. **Feedback** - We may ask for changes or clarifications
3. **Iterate** - Address feedback with new commits
4. **Approval** - Once approved, we'll merge it!
5. **Release** - Your changes will be in the next release

## Questions?

- 📖 Check [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- 📚 See existing devices for examples (DSMR, Multical)
- 💬 Open an issue or discussion for questions
- 🤝 Ask in pull request comments

## Recognition

Contributors will be recognized in:
- Release notes
- CONTRIBUTORS.md file
- GitHub contributors page

Thank you for making meter2mqtt better! 🎉

---

**Happy contributing!** 🚀

Need help? Open an issue or start a discussion. We're here to help!
