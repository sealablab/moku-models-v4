# Example 03: Full I/O Utilization

**Difficulty:** Intermediate
**Platform:** Moku:Go (2 slots, 2 I/O)
**Use Case:** Maximum throughput - use all available I/O ports

## Overview

Demonstrates full hardware utilization:
- **Both** physical inputs used (Input1, Input2)
- **Both** physical outputs used (Output1, Output2)
- CloudCompile processes both channels
- Oscilloscope monitors CloudCompile OutC + Input2

## Configuration Summary

**Slot 1:** Oscilloscope (monitoring)
**Slot 2:** CloudCompile (dual-channel processing)

**Routing (6 connections):**
1. Physical Input1 → CloudCompile InputA
2. Physical Input2 → CloudCompile InputB
3. CloudCompile OutputA → Physical Output1
4. CloudCompile OutputB → Physical Output2
5. CloudCompile OutputC → Oscilloscope InputA (monitor processed signal)
6. Physical Input2 → Oscilloscope InputB (monitor raw input)

## Signal Flow Diagram

```
┌──────────────┐              ┌──────────────┐
│  Physical    │              │  Physical    │
│   Input 1    │              │   Input 2    │
└──────┬───────┘              └──────┬───────┘
       │                             │
       │                             ├───────────┐
       │                             │           │
       ▼                             ▼           │
┌──────────────────────────────────────────┐    │
│  Slot 2: CloudCompile                    │    │
│                                          │    │
│  InA ──┐                                 │    │
│        │                                 │    │
│  InB ──┴──►  [Processing]  ──┬─► OutA ──┼────┼──► Physical Output 1
│                              │           │    │
│                              ├─► OutB ──┼──┐ │
│                              │           │  │ │
│                              └─► OutC ──┼─┐│ │
│                                          │ ││ │
└──────────────────────────────────────────┘ ││ │
                                             ││ └───► Physical Output 2
                                             ││
                                             ▼│
┌────────────────────────────────────────────┼─┐
│  Slot 1: Oscilloscope                      │ │
│                                            │ │
│  InA ◄─── (Monitor CloudCompile OutC)     │ │
│  InB ◄─────────────────────────────────────┘ │
│           (Monitor raw Input2)               │
│                                              │
│  [Compare raw input vs processed output]    │
└──────────────────────────────────────────────┘
```

## Usage

### Validation
```bash
python scripts/validate_moku_config.py examples/03-full-io-utilization.json
```

### Deployment
```bash
python scripts/push.py examples/03-full-io-utilization.json 192.168.x.x
```

## Key Points

- **Maximum I/O utilization:** All physical ports engaged
- **Dual-channel processing:** Both inputs processed independently or together
- **Input/output comparison:** Monitor raw input vs processed output
- **Versatile monitoring:** OutC can be any internal signal you want to observe

## Use Cases

1. **Stereo/dual-channel processing:** Audio, RF I/Q, differential signals
2. **Compare input to output:** Verify processing correctness
3. **Multi-signal analysis:** Process one signal, monitor another
4. **Maximum bandwidth:** Fully utilize hardware capabilities

## Routing Patterns

**Pattern: Input monitoring**
```
Input2 → Slot2InB (processing)
Input2 → Slot1InB (monitoring)
```
This "fan-out" lets you see the raw input while it's being processed.

**Pattern: Output selection**
```
Slot2OutA → Output1 (primary)
Slot2OutB → Output2 (secondary)
Slot2OutC → Slot1InA (debug/internal)
```
OutC typically carries internal debug/monitor signals from your VHDL.

## Customization

**Process both inputs together:**
Your VHDL can combine InA and InB internally for correlation, mixing, etc.

**Change monitoring target:**
```json
{
  "source": "Slot2OutA",  // Instead of OutC
  "destination": "Slot1InA"
}
```
Monitor the actual output going to Output1.

## Platform Notes

- **Moku:Go:** 2 IN, 2 OUT (this example)
- **Moku:Lab:** 2 IN, 2 OUT (same routing works)
- **Moku:Pro:** 4 IN, 4 OUT (can extend with Input3/4, Output3/4)
- **Moku:Delta:** 8 IN, 8 OUT (can extend significantly)

## See Also

- **01-basic-cloudcompile.json** - Single channel baseline
- **02-dual-monitoring.json** - Monitor multiple outputs
- **04-with-waveform-gen.json** - Generate test inputs
