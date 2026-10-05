# XGO raw connector wire identifier

Purpose: one-flash, passive identification of what the stock Pico's two dedicated Micro-USB receiver pads actually see from the XGO. No USB protocol, TinyUSB, HID, enumeration, controller serialization, or active bus drive.

The firmware observes DP for 250 ms and DM for 250 ms independently. TX values are LOW but both output enables remain OFF (Hi-Z); pulls are disabled. It then repeats a marked report forever:

**1 marker blink -> ~0.7 s pause -> DP group -> ~0.9 s pause -> DM group -> ~2.5 s pause -> repeat**

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


## Hardware result
HW result: repeated LED report **3 blinks -> pause -> 1 blink -> long pause**. Under this firmware's code table, the RP2040 DP receiver saw sparse/load-DATA-like activity while the RP2040 DM receiver remained static LOW. This is decisive evidence against the working assumption that the ordinary stock-Pico cable path presents the proven GREEN DATA and YELLOW 12-pulse CLOCK on the two native DP/DM receivers. In particular, no native receiver observed the YELLOW/CLOCK fingerprint. Preserve this result before any further active test.


## True five-conductor custom-cable checkpoint
HW: after correcting the custom cable power pair, XGO powers the stock Pico through its native Micro-B receptacle at about 3.15 V. Direct Pico continuity established Orange -> GND and Brown -> VBUS. With the true five-conductor Micro-B-to-Micro-B cable, the pre-marker wire-id firmware reported **1 blink -> pause -> 4 blinks -> long pause**, i.e. DP static LOW and DM CLOCK-like activity. This supersedes the earlier ordinary USB-A adapter-chain interpretation: that chain omitted Micro-B physical contact 4 and therefore was not a valid test of the complete five-contact transport.

The marked build does not change receiver configuration or classification. It only adds a one-blink report marker so DP and DM groups remain unambiguous during the next hardware observation.

## Marked five-wire hardware result
HW: verified marked UF2 (SHA-256 `bb476f2e83861229b9362295513a07734da86efe6feb6e3745f85ffd75619f71`) flashed with the direct custom five-conductor cable. Observed repeating LED report: **two long marker pulses -> 3 short -> 4 short**. Under the firmware's unchanged classifier this is **DP = load/data-like** and **DM = clock-like**. This is the first unambiguous simultaneous native-receptacle observation of both required XGO P2 transport signals. It supersedes the earlier ambiguous/unmarked observations while preserving them as historical checkpoints.

Implication: the one-cable stock-Pico-receptacle architecture is electrically viable for reception: the RP2040 native USB PHY can observe XGO DATA/load on DP and CLOCK on DM through the custom cable. Next stage is an active DATA sink/release responder using DP while DM remains the clock input; no USB protocol/TinyUSB is involved.
