# moku-models

Pydantic models for Moku device deployment and configuration. Define hardware specs once, use everywhere: deployment scripts, validation, simulation.


## Quick Start

### Deploy an Example Configuration

```bash
# Push one of the reference examples to your device
python scripts/push.py examples/01-basic-cloudcompile.json 192.168.1.100

# Pull the configuration back to verify
python scripts/pull.py 192.168.1.100 -o pulled_config.json

# Validate any configuration file
python scripts/validate_moku_config.py pulled_config.json
```

**WARNING:** `push.py` force-connects and overwrites existing device state!

### [Available Examples](https://github.com/sealablab/moku-models-v4/blob/main/examples/README.md)
- [01-basic-cloudcompile](https://github.com/sealablab/moku-models-v4/blob/main/examples/01-basic-cloudcompile.md) - Minimal setup (3 routes)
- [02-dual-monitoring](https://github.com/sealablab/moku-models-v4/blob/main/examples/02-dual-monitoring.md) - Dual output monitoring (5 routes)
- [03-full-io-utilization](https://github.com/sealablab/moku-models-v4/blob/main/examples/03-full-io-utilization.md) - All I/O ports used (6 routes)
- [04-with-waveform-gen](https://github.com/sealablab/moku-models-v4/blob/main/examples/04-with-waveform-gen.md) - Self-test with signal generator

## Installation

```bash
# Minimal (Pydantic only)
pip install -e .

# With device operations
pip install -e ".[device]"  # Adds moku + pyyaml
```

## Available Platforms

| Platform | Slots | Analog I/O | Clock | DIO | Constant |
|----------|-------|------------|-------|-----|----------|
| [Moku:Go](https://liquidinstruments.com/products/hardware-platforms/mokugo/) | 2 | 2 IN / 2 OUT | 125 MHz | 16 | `MOKU_GO_PLATFORM` |
| [Moku:Lab](https://liquidinstruments.com/products/hardware-platforms/mokulab/) | 2 | 2 IN / 2 OUT | 500 MHz | - | `MOKU_LAB_PLATFORM` |
| [Moku:Pro](https://liquidinstruments.com/products/hardware-platforms/mokupro/) | 4 | 4 IN / 4 OUT | 1.25 GHz | - | `MOKU_PRO_PLATFORM` |
| [Moku:Delta](https://liquidinstruments.com/products/hardware-platforms/mokudelta/) | 3 | 8 IN / 8 OUT | 5 GHz | 32 | `MOKU_DELTA_PLATFORM` |

## Documentation

- **examples/README.md** - Example configurations and patterns
- **DETAILS.md** - Architecture and integration guide
- **llms.txt** - LLM quick reference
- **docs/MOKU_PLATFORM_SPECIFICATIONS.md** - Hardware specifications

## Project Structure

```
moku-models-v4/
├── moku_models/              # Core Pydantic library
│   ├── platforms/            # Platform definitions (Go, Lab, Pro, Delta)
│   ├── device/               # Device operations (pull/push)
│   ├── moku_config.py        # MokuConfig, SlotConfig
│   ├── routing.py            # MokuConnection, routing validation
│   ├── validation.py         # Shared validation utilities
│   └── discovery.py          # Device discovery models
├── examples/                 # Reference configurations (JSON + docs)
│   ├── 01-basic-cloudcompile.json
│   ├── 02-dual-monitoring.json
│   ├── 03-full-io-utilization.json
│   └── 04-with-waveform-gen.json
├── scripts/                  # CLI tools
│   ├── pull.py               # Read config from device
│   ├── push.py               # Deploy config to device
│   ├── validate_moku_config.py
│   └── diagnose_moku_env.py
├── docs/                     # Specifications and patterns
├── datasheets/               # Hardware PDFs
└── README.md
```

## License

MIT
