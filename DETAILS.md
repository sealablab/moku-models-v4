# moku-models - Technical Details

## Project Overview

**moku-models** is a standalone Pydantic library defining type-safe data models for Moku device deployment and configuration.

**Purpose**: Single source of truth for Moku platform specifications that works across multiple contexts:
- **Hardware Deployment**: Real Moku devices via MCC API
- **CocotB Simulation**: Behavioral instrument models in test environments
- **YAML Configuration**: Human-friendly deployment specs

**Platform Specifications**: See `docs/MOKU_PLATFORM_SPECIFICATIONS.md` for detailed hardware specs and datasheet references

---

## Quick Start

```bash
# Install (development mode from parent project)
cd moku-models/
uv pip install -e .

# With device operations
uv pip install -e ".[device]"

# Format code
black moku_models/
ruff check moku_models/
```

---

## Core Models

### `MokuConfig` - THE Central Abstraction
Multi-instrument deployment specification:
- **Platform**: Which hardware (Go/Lab/Pro/Delta)
- **Slots**: What instruments go where (slot number → SlotConfig)
- **Routing**: How signals flow between slots and physical ports
- **Metadata**: Test campaign info, version tags, etc.

**Use this for all deployments** (hardware and simulation).

### `SlotConfig`
Per-slot instrument configuration:
- `instrument`: Type name ('CloudCompile', 'Oscilloscope', etc.)
- `bitstream`: Path to `.tar` bitstream (CloudCompile only)
- `control_registers`: CR0-CR31 initial values (CloudCompile only)
- `settings`: Instrument-specific settings dict

### `MokuConnection`
Signal routing between:
- Physical ports: `IN1`, `IN2`, `OUT1`, `OUT2` (up to 8 each on Delta)
- Slot virtual ports: `Slot1InA`, `Slot2OutB`, etc.

### Platform Models
Physical hardware specifications:
- `MokuGoPlatform`: 2 slots, 2 analog I/O, 125 MHz, 16 DIO pins
- `MokuLabPlatform`: 2 slots, 2 analog I/O, 500 MHz, no DIO
- `MokuProPlatform`: 4 slots, 4 analog I/O, 1.25 GHz, no DIO
- `MokuDeltaPlatform`: 3 slots, 8 analog I/O, 5 GHz, 32 DIO pins (flagship)

Each platform defines:
- Analog I/O specs (BNC connectors)
- Digital I/O (optional, varies by platform)
- Slot count
- Clock characteristics

---

## File Structure

```
moku_models/
├── __init__.py              # Public API exports
├── moku_config.py           # MokuConfig, SlotConfig
├── routing.py               # MokuConnection, MokuConnectionList
├── discovery.py             # MokuDeviceInfo, MokuDeviceCache
├── validation.py            # Shared validation utilities
├── device/                  # Device operations (pull/push)
│   ├── __init__.py
│   ├── pull.py             # Progressive introspection
│   └── push.py             # Direct deployment
└── platforms/
    ├── __init__.py
    ├── moku_go.py          # MokuGoPlatform, MOKU_GO_PLATFORM
    ├── moku_lab.py         # MokuLabPlatform, MOKU_LAB_PLATFORM
    ├── moku_pro.py         # MokuProPlatform, MOKU_PRO_PLATFORM
    └── moku_delta.py       # MokuDeltaPlatform, MOKU_DELTA_PLATFORM

scripts/
├── pull.py                  # Pull config from device (Level 1/2/3)
├── push.py                  # Push config to device (force mode)
├── validate_moku_config.py  # Validate YAML/JSON files
└── diagnose_moku_env.py     # Environment diagnostics
```

---

## Usage Examples

### Basic Deployment Config (Moku:Go)
```python
from moku_models import MokuConfig, SlotConfig, MokuConnection, MOKU_GO_PLATFORM

config = MokuConfig(
    platform=MOKU_GO_PLATFORM,
    slots={
        1: SlotConfig(
            instrument='CloudCompile',
            bitstream='emfi_probe.tar',
            control_registers={0: 0xE0000000}  # Enable probe
        ),
        2: SlotConfig(
            instrument='Oscilloscope',
            settings={'sample_rate': 125e6}
        )
    },
    routing=[
        MokuConnection(source='IN1', destination='Slot1InA'),
        MokuConnection(source='Slot1OutA', destination='OUT1'),
        MokuConnection(source='Slot1OutA', destination='Slot2InA')
    ]
)

# Validate before deployment
errors = config.validate_routing()
if errors:
    print(f"Validation errors: {errors}")
else:
    print("✓ Configuration valid")
```

### Multi-Slot Config (Moku:Lab)
```python
from moku_models import MOKU_LAB_PLATFORM

config = MokuConfig(
    platform=MOKU_LAB_PLATFORM,  # 2 slots available
    slots={
        1: SlotConfig(instrument='WaveformGenerator'),
        2: SlotConfig(instrument='CloudCompile', bitstream='custom.tar')
    },
    routing=[
        MokuConnection(source='Slot1OutA', destination='Slot2InA'),
        MokuConnection(source='Slot2OutA', destination='OUT1')
    ]
)
```

### Platform Queries
```python
from moku_models import MOKU_GO_PLATFORM, MOKU_LAB_PLATFORM, MOKU_PRO_PLATFORM

# Compare platforms
for platform in [MOKU_GO_PLATFORM, MOKU_LAB_PLATFORM, MOKU_PRO_PLATFORM]:
    print(f"{platform.name}: {platform.slots} slots @ {platform.clock_mhz} MHz")

# Check port specs
in1 = MOKU_GO_PLATFORM.get_analog_input_by_id('IN1')
print(f"IN1: {in1.resolution_bits}-bit @ {in1.sample_rate_msa} MSa/s")
```

### Device Operations - Pull Configuration
```python
from moku_models.device import pull_config_from_device

# Level 1: Basic info (non-invasive)
config = pull_config_from_device('192.168.1.100', level=1)

# Level 2: Detailed settings (frontend, CR, DIO)
config = pull_config_from_device('192.168.1.100', level=2)

# Level 3: Maximum detail (force connect)
config = pull_config_from_device('192.168.1.100', level=3, force=True)

# Export to file
config_dict = config.to_dict()
with open('current_config.json', 'w') as f:
    json.dump(config_dict, f, indent=2)
```

### Device Operations - Push Configuration
```python
from moku_models.device import push_config_to_device
from moku_models import MokuConfig

# Load config from file
with open('deployment.yaml') as f:
    data = yaml.safe_load(f)
config = MokuConfig.from_dict(data)

# Deploy to device (force connect, overwrites state)
push_config_to_device(config, '192.168.1.100')
```

---

## Design Principles

1. **Type Safety**: Pydantic validation catches config errors before deployment
2. **Moku API Alignment**: Port naming matches 1st-party `moku` library conventions
3. **Platform Agnostic**: Same `MokuConfig` works for Go/Lab/Pro/Delta (different platform instances)
4. **Simulation-Ready**: CocotB tests use identical configs as hardware deployment
5. **Pure Data Models**: No deployment logic, just validated data structures

---

## Common Tasks

### Add New Platform
1. Create `moku_models/platforms/moku_xxx.py`
2. Define `MokuXxxPlatform(BaseModel)` with appropriate specs
3. Export `MOKU_XXX_PLATFORM` constant
4. Add to `platforms/__init__.py` and main `__init__.py`

### Export to YAML
```python
import yaml
config_dict = config.to_dict()
with open('deployment.yaml', 'w') as f:
    yaml.dump(config_dict, f, default_flow_style=False)
```

### Load from YAML
```python
import yaml
from moku_models import MokuConfig

with open('deployment.yaml', 'r') as f:
    data = yaml.safe_load(f)
config = MokuConfig.from_dict(data)
```

### Validate Configuration File
```bash
# Validate any YAML or JSON configuration file
uv run python scripts/validate_moku_config.py config.yaml
```

---

## Integration Examples

**Import in code generators:**
```python
from moku_models import MokuConfig, MOKU_GO_PLATFORM
```

**Use cases:**
- VHDL build scripts query platform specs (clock frequency, I/O count)
- CocotB tests import `MokuConfig` for behavioral models
- Python TUI apps use `MokuConnection` for routing visualization
- Code generation uses platform specs for validation

---

## Development Workflow

```bash
# Make changes to models
vim moku_models/moku_config.py

# Validate
ruff check moku_models/

# Format
black moku_models/

# Commit (in submodule)
git add moku_models/
git commit -m "Add validation for routing cycles"
```

---

## Available Platforms

| Platform | Slots | Analog I/O | Clock | DIO Pins | Constant |
|----------|-------|------------|-------|----------|----------|
| Moku:Go | 2 | 2 IN / 2 OUT | 125 MHz | 16 | `MOKU_GO_PLATFORM` |
| Moku:Lab | 2 | 2 IN / 2 OUT | 500 MHz | None | `MOKU_LAB_PLATFORM` |
| Moku:Pro | 4 | 4 IN / 4 OUT | 1.25 GHz | None | `MOKU_PRO_PLATFORM` |
| Moku:Delta | 3 | 8 IN / 8 OUT | 5 GHz | 32 (2×16) | `MOKU_DELTA_PLATFORM` |

**Notes**:
- Lab/Pro do NOT have DIO headers (only Go and Delta)
- Delta has 2 separate 16-pin DIO headers (32 pins total)
- Delta specs shown are for 3-slot standard mode (8-slot advanced mode available but not modeled)

---

## Platform-Specific Details

### Port Naming Conventions

**Physical Ports:**
- Analog inputs: `IN1`, `IN2` (up to `IN8` on Delta)
- Analog outputs: `OUT1`, `OUT2` (up to `OUT8` on Delta)
- Digital I/O: `DIO0`-`DIO15` (Go), `DIO0`-`DIO31` (Delta)

**Slot Virtual Ports:**
- Format: `Slot{N}In{A|B|C|D}`, `Slot{N}Out{A|B|C|D}`
- Example: `Slot1InA`, `Slot2OutB`, `Slot3InC`

**Important:** Use `IN1` not `Input1`, `OUT1` not `Output1` (aligns with MCC API)

### Routing Validation

The `MokuConfig.validate_routing()` method checks:
- All source/destination ports exist on the platform
- Slot numbers are within platform limits
- No duplicate connections
- Port compatibility (analog/digital)

```python
config = MokuConfig(...)
errors = config.validate_routing()
if errors:
    for error in errors:
        print(f"❌ {error}")
else:
    print("✓ Routing valid")
```

---

## Device Scripts

### pull.py - Progressive Introspection

**Three levels of detail:**

**Level 1** (Non-invasive, quick):
```bash
python scripts/pull.py 192.168.1.100
```
- Platform type and slot count
- Deployed instruments
- Basic routing topology
- No connection required if device idle

**Level 2** (Detailed):
```bash
python scripts/pull.py 192.168.1.100 --level 2
```
- All Level 1 data
- Frontend/output settings (Oscilloscope)
- Control register values (CloudCompile)
- DIO configuration
- May require brief connection

**Level 3** (Maximum detail, force connect):
```bash
python scripts/pull.py 192.168.1.100 --level 3 --force
```
- All Level 2 data
- Additional introspection
- Force connects (disconnects existing sessions)

### push.py - Direct Deployment

```bash
python scripts/push.py config.yaml 192.168.1.100
```

**Behavior:**
- Force connects to device
- Overwrites existing state
- No safety prompts (use with caution)
- Supports YAML and JSON formats

**WARNING:** This script is destructive and will disconnect any active sessions!

---

## Future Enhancements

- [ ] Advanced routing validation (cycle detection, fanout limits)
- [ ] Instrument-specific settings models (Oscilloscope, WaveformGenerator)
- [ ] DIO pin configuration models
- [ ] Support for Delta 8-slot advanced mode
- [ ] Cross-platform configuration migration
- [ ] Routing diagram visualization (SVG/GraphViz)
- [ ] PyPI package publication

---

**Last Updated**: 2025-11-10
**Maintainer**: Sealab Team
**License**: MIT
