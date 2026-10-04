# XGO happy-path A/B

No discovery logic, TinyUSB, HID, enumeration, PCB changes, or protocol experiments.

Both images run the hardware-proven Contra script directly using the RP2040 dedicated connector pads as raw single-ended conductors. TX values are permanently LOW; DATA assertion changes only output-enable LOW/Hi-Z.

- A: DP=CLOCK, DM=DATA
- B: DM=CLOCK, DP=DATA

These are the two possible assignments of the Pico connector's two signal contacts under the established model.