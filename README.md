# moku-models

[![GitHub](https://img.shields.io/badge/github-sealablab%2Fmoku--models--v4-blue)](https://github.com/sealablab/moku-models-v4)

Pydantic models for Moku device deployment and configuration. Define hardware specs once, use everywhere: deployment scripts, validation, simulation.

**Repository:** https://github.com/sealablab/moku-models-v4

## Quick Start

### Pull Configuration from Device

```bash
# Level 1: Basic info (instruments, routing) - non-invasive
python scripts/pull.py 192.168.1.100

# Level 2: Detailed settings (frontend, control registers, DIO)
python scripts/pull.py 192.168.1.100 --level 2

# Level 3: Force connect, maximum detail
python scripts/pull.py 192.168.1.100 --level 3 --force

# Custom output file
python scripts/pull.py 192.168.1.100 -o my_config.json

# Write to stdout (for piping)
python scripts/pull.py 192.168.1.100 --output -
```

**Features:**
- **Progressive escalation** (polite → detailed → maximum)
- **Platform auto-detection** (Go, Lab, Pro, Delta)
- **Control register introspection** (CloudCompile CR0-CR31)
- **Frontend/output settings** (Oscilloscope)
- **DIO configuration** (Go/Delta platforms)

### Push Configuration to Device

```bash
# Deploy from YAML or JSON (force connect, overwrites state)
python scripts/push.py config.yaml 192.168.1.100
python scripts/push.py curr_model.json 192.168.1.100
```

**WARNING:** Force connects and overwrites existing state without prompts!

**Features:**
- Force connect (disconnects existing sessions)
- Direct deployment (no safety checks)
- Supports YAML and JSON formats

### Validate Config Files

```bash
# Works with YAML or JSON
python scripts/validate_moku_config.py deployment.yaml
python scripts/validate_moku_config.py config.json --verbose
```

### Diagnose Environment

```bash
# Automatic environment troubleshooting
python scripts/diagnose_moku_env.py
```

**Checks:**
- UV package manager installation
- Virtual environment setup
- Moku package installation
- Git submodules (if in monorepo)
- Import tests

## Installation

```bash
# Minimal (Pydantic only)
pip install -e .

# With device operations
pip install -e ".[device]"  # Adds moku + pyyaml
```

## Define Configuration

```python
from moku_models import MokuConfig, SlotConfig, MokuConnection, MOKU_GO_PLATFORM

config = MokuConfig(
    platform=MOKU_GO_PLATFORM,
    slots={
        1: SlotConfig(
            instrument='CloudCompile',
            bitstream='instrument.tar',
            control_registers={0: 0xE0000000}
        )
    },
    routing=[
        MokuConnection(source='IN1', destination='Slot1InA'),
        MokuConnection(source='Slot1OutA', destination='OUT1'),
    ]
)

# Validate
errors = config.validate_routing()
if not errors:
    print("✓ Valid configuration")
```

## Available Platforms

| Platform | Slots | Analog I/O | Clock | DIO | Constant |
|----------|-------|------------|-------|-----|----------|
| Moku:Go | 2 | 2 IN / 2 OUT | 125 MHz | 16 | `MOKU_GO_PLATFORM` |
| Moku:Lab | 2 | 2 IN / 2 OUT | 500 MHz | - | `MOKU_LAB_PLATFORM` |
| Moku:Pro | 4 | 4 IN / 4 OUT | 1.25 GHz | - | `MOKU_PRO_PLATFORM` |
| Moku:Delta | 3 | 8 IN / 8 OUT | 5 GHz | 32 | `MOKU_DELTA_PLATFORM` |

## Documentation

- **[CLAUDE.md](https://github.com/sealablab/moku-models-v4/blob/main/CLAUDE.md)** - Architecture and integration guide
- **[llms.txt](https://github.com/sealablab/moku-models-v4/blob/main/llms.txt)** - LLM quick reference
- **[Platform Specs](https://github.com/sealablab/moku-models-v4/blob/main/docs/MOKU_PLATFORM_SPECIFICATIONS.md)** - Detailed hardware specifications

## Project Structure

```
moku_models/
├── platforms/          # Platform definitions (Go, Lab, Pro, Delta)
├── moku_config.py      # MokuConfig, SlotConfig
├── routing.py          # MokuConnection, routing validation
├── validation.py       # Shared validation utilities
├── device/             # Device operations (pull/push)
└── discovery.py        # Device discovery models

scripts/
├── pull.py             # Progressive device introspection (Level 1/2/3)
├── push.py             # Direct deployment (force mode, no safety checks)
├── diagnose_moku_env.py   # Environment diagnostics
└── validate_moku_config.py  # Validate YAML/JSON files
```


This is a standalone library used by:
- [forge-v4-workspace](https://github.com/sealablab/forge-v4) - Development environment

## License

MIT
