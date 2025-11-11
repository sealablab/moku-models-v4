# Example 01: Basic CloudCompile

**Difficulty:** Beginner
**Platform:** Moku:Go (2 slots, 2 I/O)
**Use Case:** Simplest custom instrument deployment

## Overview

Minimal working configuration demonstrating:
- CloudCompile custom instrument in Slot 2
- Oscilloscope monitoring in Slot 1
- Single input → processing → single output
- Monitoring pattern (Slot2 OutC → Slot1 InA)

## Configuration Summary

**Slot 1:** Oscilloscope (monitoring)
**Slot 2:** CloudCompile (custom instrument)

**Routing (3 connections):**
1. Physical Input1 → CloudCompile InputA
2. CloudCompile OutputA → Physical Output1
3. CloudCompile OutputC → Oscilloscope InputA (monitoring)

## Signal Flow Diagram

```
┌──────────────┐
│  Physical    │
│   Input 1    │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────┐
│  Slot 2: CloudCompile            │
│                                  │
│  InA ──►  [Processing]  ──► OutA├──────► Physical Output 1
│                           ├─► OutC├──┐
│                                  │   │
└──────────────────────────────────┘   │
                                       │
                                       │
┌──────────────────────────────────┐   │
│  Slot 1: Oscilloscope            │   │
│                                  │   │
│  InA ◄───────────────────────────┴───┘
│  (Monitor CloudCompile OutC)      │
└──────────────────────────────────┘
```

## Usage

### Validation
```bash
python scripts/validate_moku_config.py examples/01-basic-cloudcompile.json
```

### Deployment
```bash
python scripts/push.py examples/01-basic-cloudcompile.json 192.168.x.x
```

### Reading Back
```bash
python scripts/pull.py 192.168.x.x --level 2 -o current_config.json
```

## Key Points

- **Minimal routing:** Only 3 connections needed for basic operation
- **Monitoring pattern:** OutputC typically used for monitoring/debug
- **Control registers:** CR0-CR3 show minimal CloudCompile setup
- **Platform-agnostic:** Works on any Moku platform with 2+ slots and 2+ I/O

## Customization

1. **Change bitstream:** Update `bitstream` path to your custom instrument
2. **Add control registers:** Expand `control_registers` dict (CR0-CR31)
3. **Change platform:** Replace `"moku_go"` with `"moku_lab"` or `"moku_pro"`
4. **Add second input:** Route Input2 → Slot2InB for dual-channel processing

## See Also

- **02-dual-monitoring.json** - Monitor multiple outputs simultaneously
- **03-full-io-utilization.json** - Use all available I/O ports
- **04-with-waveform-gen.json** - Generate test signals with Oscilloscope
