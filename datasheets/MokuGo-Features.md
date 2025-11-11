# Moku:Go Platform Specifications

**Status:** #datasheet #hardware #platform #api-reference
**Model:** M0 (base) | M2 (with Ethernet + power supplies)
**Manufacturer:** Liquid Instruments
**Version:** v24-0815
**Platform ID:** `2` (for API connection)

---

## Overview

Portable design and test tool for engineers and students. Features **2-slot Multi-instrument Mode** for simultaneous instrument deployment. Platform specifications align with upstream `moku` Python API.

**API Connection:**
```python
from moku.instruments import MultiInstrument
m = MultiInstrument('192.168.x.x', platform_id=2, force_connect=True)
```

---

## Physical Characteristics
> **Note:** These are informational specs - NOT programmable via API

| Property | Specification |
|----------|---------------|
| **Dimensions** | 9.45 in × 1.47 in (24 cm × 3.73 cm) |
| **Weight** | 1.7 lb (750 g) |
| **Colors** | 6 standard options |
| **Connectors** | Integrated BNC, DIO ribbon cable |
| **Security** | Kensington Lock Slot |
| **Base** | High-grip rubberized (anti-slip) |

---

## Analog I/O Specifications

### Inputs (2 Channels)
**Port IDs:** `Input1`, `Input2` (for routing and `set_source()`)

| Parameter | Value | API Programmable? |
|-----------|-------|-------------------|
| **Resolution** | 12-bit ADC | No (fixed hardware) |
| **Sample Rate** | 125 MSa/s | No (queryable via `get_samplerate()`) |
| **Analog Bandwidth** | 30 MHz (-3 dB) | No (fixed hardware) |
| **Voltage Range** | ±25 V maximum | **Yes** (`range` in `set_frontend()`) |
| **Coupling** | AC or DC | **Yes** (`coupling='AC'` or `'DC'`) |
| **Impedance** | 1 MΩ or 50 Ω | **Yes** (`impedance='1MOhm'` or `'50Ohm'`) |
| **Connector** | BNC | No (physical connector) |

**API Example:**
```python
osc.set_frontend(channel=1, impedance='50Ohm', coupling='DC', range='4Vpp')
```

### Outputs (2 Channels)
**Port IDs:** `Output1`, `Output2` (for routing)

| Parameter | Value | API Programmable? |
|-----------|-------|-------------------|
| **Resolution** | 12-bit DAC | No (fixed hardware) |
| **Sample Rate** | 125 MSa/s | No |
| **Analog Bandwidth** | 20 MHz (-3 dB, low impedance) | No (fixed hardware) |
| **Voltage Range** | ±5 V maximum | **Yes** (instrument-dependent) |
| **Impedance** | 50 Ω | No (fixed hardware) |
| **Connector** | BNC | No (physical connector) |

---

## Digital I/O

| Parameter | Value | API Programmable? |
|-----------|-------|-------------------|
| **Channels** | 16 bidirectional | No (fixed hardware) |
| **Sample Rate** | 125 MSa/s | No (fixed hardware) |
| **Logic Level** | 3.3 V (5 V tolerant) | No (fixed hardware) |
| **Connector** | Ribbon cable | No (physical connector) |
| **Configuration** | Per-pin input/output | **Yes** (Logic Analyzer instrument) |

---

## Programmable Power Supplies
> **M2 Model Only - NOT part of platform model**

**Available on:** M2 model only
**Channels:** 4 independent outputs
**Connector:** Integrated banana jacks
**API Programmable:** Yes (separate from platform model)

| Channel | Voltage Range | Current |
|---------|---------------|---------|
| **1** | +5 to -5 V | 150 mA |
| **2** | 0 to 16 V | 150 mA |
| **3** | 0.6 to 5 V | 1 A |
| **4** | 0.6 to 5 V | 1 A |

**Note:** Power supplies are a separate hardware feature (M2 only), not captured in the core `MokuGoPlatform` Pydantic model.

---

## System Clock

| Parameter | Value |
|-----------|-------|
| **Frequency** | 125 MHz |
| **Period** | 8 ns |

---

## Connectivity
> **Note:** Hardware features - NOT programmable via API (used for connection only)

| Feature | M0 | M2 | Purpose |
|---------|----|----|---------|
| **Wi-Fi Hotspot** | ✓ | ✓ | Portable operation, device discovery |
| **USB-C** | ✓ | ✓ | Data and control |
| **Ethernet** | ✗ | ✓ | Bench use with network integration |

**API Usage:** These are used for initial connection (`MultiInstrument('IP_ADDRESS', ...)`) but are not controllable features.

---

## Multi-Instrument Architecture
> **API-Programmable Feature**

**Slots:** 2 simultaneous instruments
**Slot Port IDs:** `Slot1InA`, `Slot1InB`, `Slot1OutA`, `Slot1OutB`, `Slot2InA`, `Slot2InB`, `Slot2OutA`, `Slot2OutB`

**API Example:**
```python
# Deploy instruments to slots
wg = m.set_instrument(1, WaveformGenerator)
osc = m.set_instrument(2, Oscilloscope)

# Configure routing between slots and physical ports
connections = [
    dict(source="Input1", destination="Slot1InA"),
    dict(source="Slot1OutA", destination="Slot2InA"),
    dict(source="Slot2OutA", destination="Output1"),
]
m.set_connections(connections=connections)
```

**Cloud Compile Deployment:**
```python
mcc = m.set_instrument(1, CloudCompile, bitstream="path/to/bitstream.tar.gz")
```

---

## 14 Built-In Instruments
> **Note:** Software instruments - NOT part of platform hardware model

### Signal Generation
- Arbitrary Waveform Generator
- Waveform Generator

### Measurement & Analysis
- Oscilloscope / Voltmeter
- Spectrum Analyzer
- Logic Analyzer
- Phasemeter
- Time & Frequency Analyzer

### Signal Processing
- Digital Filter Box
- FIR Filter Builder

### Control Systems
- PID Controller
- Lock-in Amplifier
- Laser Lock Box

### System Analysis
- Frequency Response Analyzer
- Data Logger

**Note:** These are deployable to the 2 available slots. See Multi-Instrument Architecture section for deployment examples.

---

## Software & APIs
> **Note:** Software features - NOT part of platform hardware model

### Python API (Primary)
**Package:** `moku` (from Liquid Instruments)
**Key Modules:**
- `moku.instruments.MultiInstrument` - Platform and routing
- `moku.instruments.Oscilloscope` - Oscilloscope instrument
- `moku.instruments.WaveformGenerator` - Waveform generator
- `moku.instruments.CloudCompile` - Custom FPGA bitstreams

### Other API Support
- MATLAB
- LabVIEW
- Additional languages

### GUI Applications
- Desktop: Windows, macOS
- Mobile: iPadOS, visionOS
- Web interface for device management

---

## Included Accessories

### All Models (M0 & M2)
- 2 oscilloscope probes
- DIO ribbon cable
- Power adapter
- USB-C cable

### M2 Model Additional
- Ethernet cable
- Power supply cables (banana jack)

---

## Electrical Protection

**Enhanced protection** for lab safety:
- Robust input protection circuits
- Overvoltage tolerance
- ESD protection

---

## Key Use Cases

### Education
- Circuits fundamentals
- Senior design projects
- Industry-standard platform training (Python/MATLAB APIs)

### Engineering
- Portable prototyping
- Field testing
- Benchtop replacement
- FPGA-based custom instruments

---

## Platform Comparison Notes

**Related Platforms:**
- [[Moku Lab]] - 2 slots, 500 MHz, benchtop
- [[Moku Pro]] - 4 slots, 1.25 GHz, advanced
- [[Moku Delta]] - 3 slots, 5 GHz, flagship

**Moku:Go Advantages:**
- Most portable (1.7 lb)
- Wi-Fi hotspot (no network required)
- Integrated power supplies (M2)
- Budget-friendly for education

---

## References

**Datasheet:** Moku:Go Datasheet v24-0815
**Manufacturer:** Liquid Instruments
**Contact:** info@liquidinstruments.com
**Website:** liquidinstruments.com

---

## API Alignment Summary

### ✓ Correctly Modeled in `moku_models/platforms/moku_go.py`
- Platform ID: `2`
- Analog I/O: 2 inputs, 2 outputs (BNC connectors)
- Port naming: `Input1`, `Input2`, `Output1`, `Output2`
- Slot architecture: 2 slots with virtual ports (`Slot1InA`, etc.)
- Resolution: 12-bit ADC/DAC
- Sample rate: 125 MSa/s
- Voltage ranges: ±25V (input), ±5V (output)
- Impedance: 1 MΩ (input default), 50 Ω (output)
- DIO: 16 pins, 3.3V logic (5V tolerant)
- Clock: 125 MHz

### ⚠ Missing from Pydantic Model (API-Accessible)
- **AC/DC coupling modes** - Programmable via `set_frontend(coupling='AC'|'DC')`
  - Recommendation: Add `coupling_modes: list[Literal['AC', 'DC']]` to `AnalogPort`

### ✓ Correctly Omitted (Not API-Programmable)
- Analog bandwidth (30 MHz in, 20 MHz out) - fixed hardware spec
- Physical dimensions, weight, colors - marketing specs
- Connectivity features (Wi-Fi, USB-C, Ethernet) - connection method, not programmable
- Built-in instruments list - software, not platform hardware
- Power supplies (M2 only) - separate feature, not core platform

---

## Tags

#moku-go #api-reference #platform-model #multi-instrument #cloud-compile #125mhz #12bit #pydantic
