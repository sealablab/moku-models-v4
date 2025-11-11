# Example 02: Dual Output Monitoring

**Difficulty:** Intermediate
**Platform:** Moku:Go (2 slots, 2 I/O)
**Use Case:** Debug/monitor two signals simultaneously

## Overview

Demonstrates parallel monitoring pattern:
- CloudCompile outputs to both physical outputs
- **AND** routes same signals to Oscilloscope for real-time monitoring
- Two-channel oscilloscope visualization during operation

## Configuration Summary

**Slot 1:** Oscilloscope (dual-channel monitoring)
**Slot 2:** CloudCompile (custom instrument with 2 outputs)

**Routing (5 connections):**
1. Physical Input1 → CloudCompile InputA
2. CloudCompile OutputA → Physical Output1
3. CloudCompile OutputB → Physical Output2
4. CloudCompile OutputA → Oscilloscope InputA (monitor)
5. CloudCompile OutputB → Oscilloscope InputB (monitor)

## Signal Flow Diagram

```
┌──────────────┐
│  Physical    │
│   Input 1    │
└──────┬───────┘
       │
       ▼
┌────────────────────────────────────────┐
│  Slot 2: CloudCompile                  │
│                                        │
│  InA ──►  [Processing]  ──┬─► OutA ───┼───┬──► Physical Output 1
│                           │            │   │
│                           └─► OutB ───┼─┐ │
│                                        │ │ │
└────────────────────────────────────────┘ │ │
                                           │ │
                                           │ └───► Physical Output 2
                                           │
                ┌──────────────────────────┼─────┐
                │                          │     │
                │                          ▼     ▼
┌───────────────┴──────────────────────────────────┐
│  Slot 1: Oscilloscope                            │
│                                                  │
│  InA ◄─── (Monitor OutA)                         │
│  InB ◄─── (Monitor OutB)                         │
│                                                  │
│  [2-Channel Display]                             │
└──────────────────────────────────────────────────┘
```

## Usage

### Validation
```bash
python scripts/validate_moku_config.py examples/02-dual-monitoring.json
```

### Deployment
```bash
python scripts/push.py examples/02-dual-monitoring.json 192.168.x.x
```

## Key Points

- **Fan-out routing:** One output goes to multiple destinations (physical output + monitor)
- **Non-invasive monitoring:** Signals still reach physical outputs
- **Real-time debug:** See both outputs live during operation
- **Control registers CR4-CR5:** Configure second output channel

## Use Cases

1. **Hardware validation:** Verify both outputs during development
2. **Timing analysis:** Compare relative timing of two signals
3. **Debugging:** Catch transient issues on either channel
4. **Production monitoring:** Observe operation without interrupting outputs

## Customization

**Add third channel monitoring:**
```json
{
  "source": "Slot2OutC",
  "destination": "Slot1InA"  // Can't use InC (only 2 Osc inputs)
}
```
Note: Oscilloscope only has 2 input channels (InA, InB)

**Monitor input as well:**
```json
{
  "source": "Input1",
  "destination": "Slot1InA"  // See input signal
}
```

## See Also

- **01-basic-cloudcompile.json** - Single channel monitoring
- **03-full-io-utilization.json** - Use all I/O including dual inputs
- **04-with-waveform-gen.json** - Generate signals for testing
