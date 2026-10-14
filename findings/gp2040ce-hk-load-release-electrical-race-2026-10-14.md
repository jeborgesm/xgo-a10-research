# HK slot0: shared-DATA LOAD-release electrical race — 2026-10-14

## Evidence
BIN: original user-supplied XGoAnalisis.zip, bios/bisrv.asd, little-endian MIPS32 at offsets 0x35D810–0x35D894; inspected instruction words directly.
SRC: Test16 and Test24 XGODriver.cpp.
HW: user confirms physical HK displays correctly as RB on GP2040 OLED; tap often missed; hold first MP then repeated HK; repeated taps sometimes register HK. Tests23 and 24 did not resolve.

## Confirmed BIN sequence
At 0x35D834–0x35D844 host clears output-enable bit15 for first DATA stream. At 0x35D858–0x35D864 it clears output-enable bit0 for second stream. At 0x35D870 host reads first DATA stream and masks bit15 at 0x35D874; at 0x35D890 reads second and masks bit0 at 0x35D894. No shared CLOCK-low pulse occurs between DATA release and first samples. The two streams have different release/sample instruction windows.

## Confirmed SRC
Test16 and Test24 use the *same* USB DP PHY pin to detect host DATA-high release and then drive slot0 active-low by setting TX_DP_OE. Their response is reactive to detecting DATA-high, not clocked by a separate LOAD pin. The slot0 first-bit transition cannot be pre-driven low without risking suppressing the observed high release condition. Test24 reduces software polling overhead but does not eliminate the asynchronous shared-wire handoff.

## Engineering inference
The slot0 mechanism is a two-device bus-turnaround race: host releases its open-drain DATA driver, line must rise through pull-up and be sensed by RP2040, RP2040 must enable its sink, then line must fall and settle before host's first read. The unknown electrical rise/fall times, host instruction timing and exact stream pin can dominate the software optimization. This is consistent with unreliable HK; it does **not** prove the cause of MP substitution or held repeats.

## Important alternative to rule out
On RP2040, `USBPHY_DIRECT_RX_DP` reflects the input level. During host LOAD-low the responder cannot distinguish LOAD from an already-asserted slot0 without another independent signal. The output-enable operation after release must not hold DATA low through the next LOAD cycle. Current code releases after the 12th slot, but transaction misalignment could still create wrong samples.

## Required measurement (not yet available)
Use a logic analyzer or scope on XGO DATA and CLOCK referenced to ground, ideally with both original and GP2040 responder, to determine whether slot0 DATA reaches valid LOW before host's first sample. Without host first-sample strobe visibility, compare relative LOAD release, first clock falling edge, DATA settling and repeated frames. Establish which physical stream the controller uses. Avoid assuming that the OLED proves host-side signal correctness.

## Candidate design gate
A more deterministic first-bit solution likely needs a separate LOAD event, clock/PIO observation, or an externally latched first-bit signal; changing arbitrary software polling instructions again is not sufficient evidence. Preserve Test16 and direction slots1–11. No new firmware built.
