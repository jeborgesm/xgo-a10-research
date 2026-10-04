# XGO raw connector wire identifier

Purpose: one-flash, passive identification of what the stock Pico's two dedicated Micro-USB receiver pads actually see from the XGO. No USB protocol, TinyUSB, HID, enumeration, controller serialization, or active bus drive.

The firmware observes DP for 250 ms and DM for 250 ms independently. TX values are LOW but both output enables remain OFF (Hi-Z); pulls are disabled. It then repeats two LED groups forever:

**DP group -> ~0.9 s pause -> DM group -> ~2.5 s pause -> repeat**

The startup single blink occurs only once and is not part of the report.

Each report group is:
- 1 blink = static LOW
- 2 blinks = static HIGH
- 3 blinks = load/data-like sparse activity
- 4 blinks = clock-like dense ~microsecond activity
- 5 blinks = electrically active but not matching either broad fingerprint

Reference from hardware-proven loose-wire capture:
- GREEN/P2 DATA: host load LOW about 7 us, frame cadence about 16.03 ms.
- YELLOW/CLOCK: 12 pulses per frame, about 4 us period / ~2 us half-cycle, same ~16 ms cadence.

This test intentionally does not drive either signal contact. Its job is to answer whether either RP2040 receiver sees static level, GREEN-like activity, YELLOW-like activity, or other transitions. It does not assume DP/DM correspond to GREEN/YELLOW.

A result of static/static despite the known XGO scanner proves the ordinary cable/native-pad path is not exposing the same proven GREEN/YELLOW activity to these RP2040 receiver inputs under this configuration; do not respond by changing controller serialization.
