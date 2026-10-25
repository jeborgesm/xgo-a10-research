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

## 2026-10-24 forensic DATA/CLOCK frame analyzer — host-side only

The original `decode_capture.py` reports raw runs and the first transitions. A new complementary `analyze_frames.py` classifies **every** repeated XGO scan and exports timing evidence without modifying the Pico/P0 firmware or connecting another electrical device.

```sh
python3 tools/rp2040-xgo-p0/analyze_frames.py capture-p0-live.txt
python3 tools/rp2040-xgo-p0/analyze_frames.py capture-p0-live.txt --json p0-frames.json --csv p0-frames.csv
python3 tools/rp2040-xgo-p0/test_analyze_frames.py
```

The analyzer reads the original P0 `BEGIN XGO_P0 rate=...` and 32-bit hex words using the **existing** two-bit sample packing. It groups CLOCK LOW runs into bursts and provides: actual number of pulses, per-pulse LOW lengths, intervening HIGH lengths (including the minimum, unlike earlier aggregate analysis), host DATA/LOAD LOW duration, DATA-rise-to-first-CLOCK-fall offset, and DATA state/transitions during the burst. It flags non-12-pulse bursts, stretches longer than the protected responder's 18us wait, and unusually short HIGH gaps. A 150us grouping gap is an **analysis heuristic**; it preserves a 25us synthetic IRQ stretch but does not establish why a physical signal varied. A missing `END` marker is reported rather than silently claiming a complete transfer.

**Critical evidence limit:** XGO first R/slot0 is sampled **before CLOCK #1**; P0 has no signal representing that CPU read. Therefore DATA at the first CLOCK FALL is **not** an actual decoded R value. Similarly DATA samples after CLOCK RISE are only wire-level proxies, not the actual host decoded button word. These are 10MHz digital GPIO threshold captures, **not voltage slew-time or analog impedance measurements**. The analyzer cannot determine which side electrically caused a pulse alteration without controlled comparative capture.

**Cable/electrical safety:** P0 was a separately powered loose-wire passive instrument attached to the established **RED reference / GREEN DATA / YELLOW CLOCK** harness. The current working Frankie V2 Jr connects through its *own* native Micro-B path and has a documented physical pad-2/pad-4 bridge. A historical P0 capture is **not electrically equivalent to Frankie**. Do not casually connect a second Pico, alter the Frankie bridge, short DATA to reference, or assume an added probe is non-invasive: previous probes caused P2 ghost inputs. A future connected-controller trace needs a specifically reviewed high-input-impedance tap and an independently established reference. No new hardware test is requested by the software decoder.

The source and all four synthetic scenarios are checked by the fast XGO CI workflow. This analyzer does **not** produce or modify `.uf2` or `bisrv.asd`.
