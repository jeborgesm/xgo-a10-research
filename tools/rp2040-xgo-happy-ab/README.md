# XGO happy-path A/B

No discovery logic, TinyUSB, HID, enumeration, PCB changes, or protocol experiments.

Both images run the hardware-proven Contra script directly using the RP2040 dedicated connector pads as raw single-ended conductors. TX values are permanently LOW; DATA assertion changes only output-enable LOW/Hi-Z.

- A: DP=CLOCK, DM=DATA
- B: DM=CLOCK, DP=DATA

These are the two possible assignments of the Pico connector's two signal contacts under the established model.

## Hardware result
HW FAIL: neither happy-path permutation moved the Contra bot. A (DP=CLOCK, DM=DATA) failed; B (DM=CLOCK, DP=DATA) failed. This exhausts the two direct DP/DM assignments under the assumption that the XGO CLOCK/DATA pair reaches the Pico's two Micro-USB data pads through the ordinary cable. Combined with P6's failure to observe the known 12-pulse clock, the remaining contradiction is physical connector/cable routing or an RP2040 dedicated-pad electrical-access assumption—not the already hardware-proven 12-bit XGO responder protocol. Do not issue further DP/DM permutation firmware.
