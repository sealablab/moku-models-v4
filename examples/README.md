# Moku:Go Reference Configuration Examples

Self-contained, validated reference configurations demonstrating common deployment patterns.

**All examples use:** CloudCompile (Slot 2) + Oscilloscope (Slot 1)
**Platform:** Moku:Go (2 slots, 2 I/O) - adaptable to Lab/Pro/Delta

---

## 📚 Available Examples

| Example | Difficulty | Connections | Description |
|---------|------------|-------------|-------------|
| [01-basic-cloudcompile](01-basic-cloudcompile.md) | Beginner | 3 | Minimal setup: 1 input → process → 1 output + monitoring |
| [02-dual-monitoring](02-dual-monitoring.md) | Intermediate | 5 | Monitor 2 CloudCompile outputs on both Osc channels |
| [03-full-io-utilization](03-full-io-utilization.md) | Intermediate | 6 | Use all I/O ports (2 IN, 2 OUT) + monitoring |
| [04-with-waveform-gen](04-with-waveform-gen.md) | Advanced | 3 | Self-test mode with Oscilloscope signal generator |

---

## 🚀 Quick Start

### Validate Example
```bash
python scripts/validate_moku_config.py examples/01-basic-cloudcompile.json
```

### Deploy Example
```bash
# Replace IP with your Moku device
python scripts/push.py examples/01-basic-cloudcompile.json 192.168.x.x
```

### Read Configuration Back
```bash
python scripts/pull.py 192.168.x.x --level 2 -o pulled_config.json
```

### Test All Examples
```bash
# Automated testing script (see below)
./scripts/test-all-examples.sh 192.168.x.x
```

---

## 📖 Example Details

### 01: Basic CloudCompile ⭐ *Start Here*
**Pattern:** External input → CloudCompile → External output
- Simplest possible deployment
- Single input/output pair
- CloudCompile OutC monitored on Oscilloscope
- 3 routing connections

**Use case:** First custom instrument deployment, baseline testing

---

### 02: Dual Output Monitoring
**Pattern:** Process → Output + Monitor both channels
- Both CloudCompile outputs used (OutA, OutB)
- Both routed to physical outputs
- Both monitored on Oscilloscope (2-channel display)
- 5 routing connections

**Use case:** Debug two signals simultaneously, timing analysis

---

### 03: Full I/O Utilization
**Pattern:** Maximum hardware engagement
- **Both** physical inputs used
- **Both** physical outputs used
- Oscilloscope monitors CloudCompile OutC + raw Input2
- 6 routing connections

**Use case:** Dual-channel processing, input/output comparison

---

### 04: With Waveform Generator ⚡ *Advanced*
**Pattern:** Self-contained testing loop
- Oscilloscope generates test signal (Square wave, 1 kHz)
- Signal routed to CloudCompile for processing
- Processed output monitored back on Oscilloscope
- Uses `waveform_output` extension field
- 3 routing connections

**Use case:** Automated testing, characterization, no external signal source needed

---

## 🎯 Common Patterns

### Monitoring Pattern
```
CloudCompile OutputC → Oscilloscope InputA
```
Used in all examples. OutputC typically carries debug/internal signals.

### Fan-out Pattern
```
CloudCompile OutputA → Physical Output1
CloudCompile OutputA → Oscilloscope InputA
```
One output goes to multiple destinations (seen in example 02).

### Loopback Pattern
```
Oscilloscope OutputA → CloudCompile InputA
CloudCompile OutputC → Oscilloscope InputA
```
Self-test mode (seen in example 04).

---

## 📐 Signal Flow Conventions

### Port Naming
- **Physical ports:** `Input1`, `Input2`, `Output1`, `Output2`
- **Slot virtual ports:** `Slot1InA`, `Slot2OutC`, etc.

### Slot Assignments (All Examples)
- **Slot 1:** Oscilloscope (monitoring/signal generation)
- **Slot 2:** CloudCompile (custom instrument)

This convention makes examples consistent and easy to compare.

---

## 🔧 Customization Guide

### Change Platform
```json
{
  "platform": "moku_lab"  // or "moku_pro", "moku_delta"
}
```

### Change Bitstream
```json
{
  "bitstream": "./path/to/your_instrument.tar"
}
```

### Add Control Registers
```json
{
  "control_registers": {
    "0": 0,
    "1": 0,
    "2": 3300,
    // ... up to CR31
  }
}
```

### Add Oscilloscope Waveform Generator
```json
{
  "waveform_output": {
    "channel": 1,
    "waveform_type": "Sine",  // or "Square", "Triangle"
    "frequency": 1000,
    "amplitude": 2.5,
    "offset": 1.25
  }
}
```
See example 04 for complete demonstration.

---

## ✅ Testing & Validation

All examples:
- ✅ Validated with `validate_moku_config.py`
- ✅ Use only ports A, B, C (avoid OutputD - not universal)
- ✅ Work on Moku:Go (minimum 2 slots, 2 I/O)
- ✅ Include markdown documentation with signal flow diagrams
- ✅ JSON format for explicit typing

### Automated Testing
Use the provided test script to verify all examples on real hardware:
```bash
./scripts/test-all-examples.sh 192.168.13.147
```

This will:
1. Push each example to the device
2. Pull configuration back
3. Validate the pulled config
4. Report any discrepancies

---

## 🗂️ File Organization

```
examples/
├── README.md                      (this file)
├── 01-basic-cloudcompile.json     ─┬─ Minimal setup
├── 01-basic-cloudcompile.md       ─┘
├── 02-dual-monitoring.json        ─┬─ Dual output monitoring
├── 02-dual-monitoring.md          ─┘
├── 03-full-io-utilization.json    ─┬─ All I/O ports used
├── 03-full-io-utilization.md      ─┘
├── 04-with-waveform-gen.json      ─┬─ Signal generator demo
└── 04-with-waveform-gen.md        ─┘
```

Each example includes:
- `.json` - Machine-readable configuration
- `.md` - Human-readable documentation with diagrams

---

## 🎓 Learning Path

1. **Start:** 01-basic-cloudcompile.json
2. **Practice:** Modify control registers, try different routing
3. **Expand:** 02-dual-monitoring.json (add second output)
4. **Master:** 03-full-io-utilization.json (use all I/O)
5. **Advanced:** 04-with-waveform-gen.json (self-test mode)

---

## 📝 Notes

- **OutputD avoided:** Not available on all platforms
- **JSON format:** Explicit typing, no YAML ambiguity
- **Self-contained:** No external hardware references
- **Validated:** All examples pass `validate_moku_config.py`

---

**Last Updated:** 2025-11-11
**Platform:** Moku:Go (2 slots, 2 I/O)
