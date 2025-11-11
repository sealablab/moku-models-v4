# Example 04: CloudCompile with Waveform Generator

**Difficulty:** Advanced
**Platform:** Moku:Go (2 slots, 2 I/O)
**Use Case:** Self-contained testing without external signal source

## Overview

Demonstrates Oscilloscope's built-in waveform generator feature:
- Oscilloscope generates test signal internally
- Signal routed to CloudCompile for processing
- No external signal source needed (self-test mode)
- Monitor processed output on Oscilloscope

**Key Feature:** Uses `waveform_output` extension field (optional, not validated)

## Configuration Summary

**Slot 1:** Oscilloscope (signal generator + monitor)
**Slot 2:** CloudCompile (signal processor)

**Routing (3 connections):**
1. Oscilloscope OutputA → CloudCompile InputA (test signal injection)
2. CloudCompile OutputA → Physical Output1
3. CloudCompile OutputC → Oscilloscope InputA (monitor processed signal)

**Waveform Generator Settings:**
- Type: Square wave
- Frequency: 1000 Hz (1 kHz)
- Amplitude: 2.5 V
- Offset: 1.25 V (centers at 2.5V: 0-5V range)
- Duty: 50% (symmetric square wave)

## Signal Flow Diagram

```
┌────────────────────────────────────────────────┐
│  Slot 1: Oscilloscope                          │
│                                                │
│  [Waveform Generator]                          │
│         │                                      │
│         │  1 kHz Square Wave                   │
│         │  2.5V amplitude, 1.25V offset        │
│         ▼                                      │
│       OutA ──────────────┐                     │
│                          │                     │
│                          │                     │
│       InA ◄──────────┐   │                     │
│         │            │   │                     │
│         ▼            │   │                     │
│  [Display/Monitor]   │   │                     │
└──────────────────────┼───┼─────────────────────┘
                       │   │
                       │   │
                       │   ▼
┌──────────────────────┼───────────────────────┐
│  Slot 2: CloudCompile│                       │
│                      │                       │
│  InA ◄───────────────┘                       │
│    │                                         │
│    │                                         │
│    └──►  [Processing]  ──┬─► OutA ──────────┼──► Physical Output 1
│                          │                   │
│                          └─► OutC ───────────┼──┐
│                                              │  │
└──────────────────────────────────────────────┘  │
                                                  │
                        (loops back to Slot1 InA)─┘
```

## Usage

### Validation
```bash
python scripts/validate_moku_config.py examples/04-with-waveform-gen.json
```

### Deployment
```bash
python scripts/push.py examples/04-with-waveform-gen.json 192.168.x.x
```

**Note:** The `waveform_output` field is handled by push.py, not part of core validation.

## Key Points

- **Self-test capability:** No external hardware needed for testing
- **Extension field:** `waveform_output` demonstrates optional field support
- **Loopback pattern:** Oscilloscope output feeds CloudCompile input
- **Verification:** Monitor shows processed signal vs generated signal

## Waveform Types

Change `waveform_type` to:
- `"Sine"` - Clean sinusoidal wave
- `"Square"` - Digital-like transitions (this example)
- `"Triangle"` - Linear ramp up/down

## Use Cases

1. **Automated testing:** Test instrument without external signal generator
2. **Characterization:** Measure frequency response, latency, etc.
3. **Development:** Test VHDL processing logic with known input
4. **Demo mode:** Self-contained demonstration without test equipment

## Configuration Details

### Waveform Generator Parameters

```json
"waveform_output": {
  "channel": 1,           // Which Osc output (1 or 2)
  "enable": true,         // Enable generator
  "waveform_type": "Square",  // Sine/Square/Triangle
  "frequency": 1000,      // Hz (1 kHz)
  "amplitude": 2.5,       // Peak-to-peak volts
  "offset": 1.25,         // DC offset (centers waveform)
  "duty": 50              // Duty cycle % (Square only)
}
```

### Voltage Calculations

For this example:
- **Range:** 0V to 5V (offset ± amplitude/2)
- **Low:** 1.25V - 1.25V = 0V
- **High:** 1.25V + 1.25V = 2.5V (Actually should be 1.25 + 2.5 = 3.75V)

*Note: amplitude is peak-to-peak, so actual swing is amplitude/2 on each side*

## Advanced Patterns

**Dual waveform generation:**
```json
"waveform_output": {
  "channel": 2,  // Use second output
  ...
}
```
Can generate different signals on OutA and OutB.

**Sweep testing:**
Programmatically change `frequency` to measure frequency response.

**Noise injection:**
Add offset variations to simulate noisy inputs.

## Customization

**Change to sine wave:**
```json
{
  "waveform_type": "Sine",
  "frequency": 10000,  // 10 kHz
  "amplitude": 1.0,    // ±0.5V
  "offset": 0.5        // Centers at 0.5V (0-1V range)
}
```
Remove `duty` field (only for square waves).

**Disable generator:**
```json
{
  "enable": false
}
```
Or remove entire `waveform_output` block.

## See Also

- **01-basic-cloudcompile.json** - External input version
- **02-dual-monitoring.json** - Monitor multiple channels
- **03-full-io-utilization.json** - Use external inputs instead
