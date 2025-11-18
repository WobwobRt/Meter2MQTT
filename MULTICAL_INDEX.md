# Multical Implementation - Documentation Index

## 📖 Start Here

**New to meter2mqtt with Multical?** Start with these files in order:

1. **[README_MULTICAL.md](README_MULTICAL.md)** (5 min read)
   - Complete implementation overview
   - Features and benefits
   - Quick configuration example
   - Next steps

2. **[MULTICAL_QUICKSTART.md](MULTICAL_QUICKSTART.md)** (10 min read)
   - Feature overview
   - Configuration examples (3 scenarios)
   - All 32 parameters documented
   - Troubleshooting guide
   - Performance tips

3. **[config.d/multical.yaml.example](config.d/multical.yaml.example)** (2 min read)
   - Configuration template
   - All parameters listed with descriptions
   - Ready to copy and customize

## 🎯 By Use Case

### "I want to set up a multical meter"
1. Start: [MULTICAL_QUICKSTART.md](MULTICAL_QUICKSTART.md) → Configuration section
2. Copy: [config.d/multical.yaml.example](config.d/multical.yaml.example)
3. Modify: Update port and parameters
4. Done: Restart meter2mqtt

### "I want to understand Home Assistant integration"
1. Read: [HA_INTEGRATION.md](HA_INTEGRATION.md)
2. Reference: Device class descriptions
3. Check: Example discovery message format
4. Explore: Parameter metadata in `devices/ha_metadata.py`

### "I want to understand the architecture"
1. Read: [ARCHITECTURE_MULTICAL.md](ARCHITECTURE_MULTICAL.md)
2. Study: Component overview diagram
3. Understand: Data flow from meter to Home Assistant
4. Learn: How configuration is resolved

### "I'm a developer"
1. Start: [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
2. Review: [src/meter2mqtt/devices/multical.py](src/meter2mqtt/devices/multical.py)
3. Check: [src/meter2mqtt/devices/ha_metadata.py](src/meter2mqtt/devices/ha_metadata.py)
4. Reference: [ARCHITECTURE_MULTICAL.md](ARCHITECTURE_MULTICAL.md) → "Adding New Devices"

### "I need to troubleshoot"
1. Check: [MULTICAL_QUICKSTART.md](MULTICAL_QUICKSTART.md) → Troubleshooting
2. Verify: Connection type and port
3. Test: Serial port availability
4. Review: Meter parameters documentation

## 📚 Complete Documentation Set

### User Guides
| Document | Purpose | Length |
|----------|---------|--------|
| [README_MULTICAL.md](README_MULTICAL.md) | Complete overview for setup | 200 lines |
| [MULTICAL_QUICKSTART.md](MULTICAL_QUICKSTART.md) | Step-by-step guide with examples | 250 lines |
| [MULTICAL_QUICKSTART.md#configuration](MULTICAL_QUICKSTART.md) | Configuration section only | 50 lines |
| [MULTICAL_QUICKSTART.md#troubleshooting](MULTICAL_QUICKSTART.md) | Troubleshooting guide only | 40 lines |

### Technical Documentation
| Document | Purpose | Length |
|----------|---------|--------|
| [HA_INTEGRATION.md](HA_INTEGRATION.md) | Home Assistant concepts and integration | 200 lines |
| [ARCHITECTURE_MULTICAL.md](ARCHITECTURE_MULTICAL.md) | Architecture, diagrams, and data flow | 200 lines |
| [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) | Technical implementation details | 150 lines |
| [IMPLEMENTATION_CHECKLIST.md](IMPLEMENTATION_CHECKLIST.md) | Verification and testing checklist | 150 lines |

### Configuration Templates
| File | Purpose | Status |
|------|---------|--------|
| [config.d/multical.yaml.example](config.d/multical.yaml.example) | Multical configuration template | ✅ Created |
| [config.d/dsmr.yaml.example](config.d/dsmr.yaml.example) | DSMR configuration template | ✅ Updated |

### Implementation Tracking
| Document | Purpose |
|----------|---------|
| [IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md) | Executive summary + quick reference |
| [IMPLEMENTATION_CHECKLIST.md](IMPLEMENTATION_CHECKLIST.md) | Complete checklist of what was done |

## 📊 Parameter Reference

### Quick Parameter List

**Core Parameters (7)**
```
energy, power, temp1, temp2, volume, flow, tempdiff
```

**Statistical Parameters (20)**
```
Monthly: minflow_m, maxflow_m, minflowDate_m, maxflowDate_m,
         minpower_m, maxpower_m, minpowerdate_m, maxpowerdate_m,
         avgtemp1_m, avgtemp2_m

Yearly: minflow_y, maxflow_y, minflowdate_y, maxflowdate_y,
        minpower_y, maxpower_y, minpowerdate_y, maxpowerdate_y,
        avgtemp1_y, avgtemp2_y
```

**Specialty Parameters (5)**
```
temp1xm3, temp2xm3, infoevent, hourcounter, e1highres
```

See [MULTICAL_QUICKSTART.md](MULTICAL_QUICKSTART.md) for full parameter descriptions.

## 🏠 Home Assistant Device Classes

| Device Class | Parameters | Benefits |
|---|---|---|
| `energy` | energy, e1highres | Energy dashboard integration |
| `power` | power, *_power | Real-time power graphs |
| `temperature` | temp*, avgtemp* | Temperature history |
| `temperature_delta` | tempdiff | Temperature difference tracking |
| `water` | volume | Water usage tracking |
| `volume_flow_rate` | flow, *flow* | Flow monitoring |

Learn more in [HA_INTEGRATION.md](HA_INTEGRATION.md).

## 🔧 Files Structure

```
meter2mqtt/
├── src/meter2mqtt/devices/
│   ├── multical.py           ← MulticalDevice implementation (195 lines)
│   └── ha_metadata.py        ← HA metadata for all devices (454 lines)
│
├── config.d/
│   ├── multical.yaml.example ← Configuration template
│   └── dsmr.yaml.example     ← Updated template
│
├── Documentation/
│   ├── HA_INTEGRATION.md              ← HA concepts
│   ├── MULTICAL_QUICKSTART.md         ← User guide
│   ├── ARCHITECTURE_MULTICAL.md       ← Architecture
│   ├── IMPLEMENTATION_SUMMARY.md      ← Tech details
│   ├── README_MULTICAL.md             ← Complete README
│   ├── IMPLEMENTATION_CHECKLIST.md    ← Verification
│   ├── IMPLEMENTATION_COMPLETE.md     ← Summary
│   └── MULTICAL_INDEX.md              ← This file
```

## 🚀 Quick Start Steps

1. **Choose your documentation**
   - Users: Read [MULTICAL_QUICKSTART.md](MULTICAL_QUICKSTART.md)
   - Developers: Read [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
   - Architects: Read [ARCHITECTURE_MULTICAL.md](ARCHITECTURE_MULTICAL.md)

2. **Get the configuration**
   - Copy [config.d/multical.yaml.example](config.d/multical.yaml.example)
   - Modify port and parameters
   - Save to `config.d/my_device.yaml`

3. **Start using it**
   - Restart meter2mqtt
   - Check MQTT topics
   - Verify Home Assistant entities

4. **Get help**
   - Troubleshooting: [MULTICAL_QUICKSTART.md#troubleshooting](MULTICAL_QUICKSTART.md)
   - HA issues: [HA_INTEGRATION.md](HA_INTEGRATION.md)
   - Tech questions: [ARCHITECTURE_MULTICAL.md](ARCHITECTURE_MULTICAL.md)

## 📞 Documentation Navigation

### By Audience

**👨‍💼 Managers/Non-Technical**
→ Start with: [README_MULTICAL.md](README_MULTICAL.md)

**👨‍💻 Users/Installers**
→ Start with: [MULTICAL_QUICKSTART.md](MULTICAL_QUICKSTART.md)

**🔬 Developers**
→ Start with: [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)

**📐 Architects**
→ Start with: [ARCHITECTURE_MULTICAL.md](ARCHITECTURE_MULTICAL.md)

### By Topic

**Configuration**
→ [config.d/multical.yaml.example](config.d/multical.yaml.example)
→ [MULTICAL_QUICKSTART.md#configuration](MULTICAL_QUICKSTART.md)

**Home Assistant Integration**
→ [HA_INTEGRATION.md](HA_INTEGRATION.md)
→ [ARCHITECTURE_MULTICAL.md#home-assistant-entity-creation](ARCHITECTURE_MULTICAL.md)

**Parameters**
→ [MULTICAL_QUICKSTART.md#available-parameters](MULTICAL_QUICKSTART.md)
→ [devices/ha_metadata.py](src/meter2mqtt/devices/ha_metadata.py)

**Troubleshooting**
→ [MULTICAL_QUICKSTART.md#troubleshooting](MULTICAL_QUICKSTART.md)
→ [MULTICAL_QUICKSTART.md#performance-tips](MULTICAL_QUICKSTART.md)

**Architecture**
→ [ARCHITECTURE_MULTICAL.md](ARCHITECTURE_MULTICAL.md)
→ [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)

## 📈 Documentation Statistics

| Metric | Value |
|--------|-------|
| Total documentation lines | 1,300+ |
| User guides | 3 |
| Technical documentation | 4 |
| Code examples | 15+ |
| Configuration templates | 2 |
| Parameters documented | 50 (32 Multical + 18 DSMR) |

## ✅ What's Included

- ✅ MulticalDevice class (full implementation)
- ✅ Home Assistant metadata (all 32 parameters)
- ✅ Configuration templates (ready to use)
- ✅ User guides (step-by-step)
- ✅ Technical documentation (architecture + details)
- ✅ Troubleshooting guide (common issues)
- ✅ Examples (3+ configuration scenarios)

## 🎓 Learning Path

```
Day 1: Get Started
├─ Read: README_MULTICAL.md (5 min)
├─ Read: MULTICAL_QUICKSTART.md (10 min)
└─ Action: Create config and restart

Day 2: Understand Integration
├─ Read: HA_INTEGRATION.md (15 min)
├─ Check: Home Assistant entities
└─ Explore: Device classes and state classes

Day 3: Go Deeper
├─ Read: ARCHITECTURE_MULTICAL.md (20 min)
├─ Review: Data flow diagrams
└─ Understand: Extension patterns

Day 4: Optimize
├─ Review: Performance tips in QUICKSTART
├─ Adjust: Parameters for your needs
└─ Monitor: MQTT traffic and logs
```

## 🔗 External References

- [Kamstrup Multical Protocol](https://github.com/wobwobrt/kamstrup2mqtt)
- [Home Assistant MQTT Discovery](https://www.home-assistant.io/integrations/mqtt/#mqtt-discovery)
- [Home Assistant Device Classes](https://developers.home-assistant.io/docs/core/entity/sensor#available-device-classes)
- [MDI Icon Library](https://pictogrammers.com/library/mdi/)

## 📝 Version Information

- **Implementation Date**: November 18, 2025
- **Status**: ✅ Complete & Ready to Use
- **Multical Support**: 402, 403, 603
- **Connections**: Serial port + Network (socket)
- **Parameters**: 32 available
- **Home Assistant**: MQTT Discovery ready

---

**Start Here**: [README_MULTICAL.md](README_MULTICAL.md) or [MULTICAL_QUICKSTART.md](MULTICAL_QUICKSTART.md)

**Questions?** See [IMPLEMENTATION_CHECKLIST.md](IMPLEMENTATION_CHECKLIST.md) for verification steps or [MULTICAL_QUICKSTART.md#troubleshooting](MULTICAL_QUICKSTART.md) for troubleshooting.
