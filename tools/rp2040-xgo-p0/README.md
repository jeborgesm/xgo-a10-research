# XGO P0 passive RP2040 capture

Purpose: simultaneously observe the two strongest current Handle Interface candidates without driving the XGO.

## Fixed v1 mapping

- Pico GP26 <- harness YELLOW (strong CLOCK candidate)
- Pico GP27 <- harness GREEN (P2-coupled / DATA candidate)
- Pico GND <- harness RED (measured reference)

Do **not** connect BROWN or BLUE to the Pico for P0 v1.

## Safety properties

- GP26/GP27 are explicitly initialized GPIO inputs.
- Internal pulls are disabled.
- PIO program contains only `in pins, 2`.
- There is no PIO `set`, `out`, sideset, or pindir-changing instruction.
- Firmware has no runtime mode that drives GP26/GP27.
- Pico is powered only from its own USB connection.
- XGO supplies no power to Pico.

This is a passive digital sampler, not an active controller.

## Capture format

Sampling is 10 MHz. Each PIO instruction reads GP26 and GP27 simultaneously. Autopush emits one 32-bit word after 16 two-bit samples. A capture contains 262,144 samples (~26.2 ms).

USB serial command `c` takes one capture and prints it between `BEGIN XGO_P0` and `END XGO_P0`.

Save the terminal output to a text file, then:

```
python decode_capture.py capture.txt
```

The decoder reports edge counts and run lengths and prints the first transitions with YELLOW/GREEN states.

## Build

Requires Raspberry Pi Pico SDK. This project targets the original Raspberry Pi Pico / RP2040.

```
export PICO_SDK_PATH=/path/to/pico-sdk
cmake -S . -B build -DPICO_BOARD=pico
cmake --build build -j
```

The resulting `xgo_p0.uf2` is the only binary intended for the P0 hardware test.
