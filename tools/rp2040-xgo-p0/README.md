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


## Windows capture helper — avoid false 10-second timeout

The 16,384-word text dump is about 147 KiB before serial framing. At 115200 baud it can exceed 10 seconds even though the RP2040 acquisition itself already completed. Do not use a 10-second total-operation timeout.

With miniterm closed so COM5 is free, this PowerShell/Python command captures until the firmware's END marker and gives the serial transfer up to 30 seconds:

```powershell
python -c "import serial,time; p='capture-p0-live.txt'; s=serial.Serial('COM5',115200,timeout=1); time.sleep(.25); s.reset_input_buffer(); s.write(b'c\r\n'); s.flush(); out=[]; deadline=time.time()+30; found=False
while time.time()<deadline:
    x=s.readline()
    if x:
        out.append(x)
        if b'END XGO_P0' in x:
            found=True; break
s.close(); open(p,'wb').write(b''.join(out)); print(('COMPLETE' if found else 'TIMEOUT'), p, len(out), 'lines')"
```

Then decode:

```powershell
python tools/rp2040-xgo-p0/decode_capture.py capture-p0-live.txt
```

This changes only the host-side logging procedure. The flashed passive P0 UF2 does not need to be rebuilt or reflashed.
