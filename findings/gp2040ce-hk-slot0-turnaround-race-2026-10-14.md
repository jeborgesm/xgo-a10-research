# HK / R slot-0 turnaround race — focused controller-only analysis

## Evidence
- BIN (existing XGO scanner reconstruction): `findings/handle-interface-protocol.md` documents host DATA0 B15 / DATA1 L0, shared CLOCK B7, load both DATA low ~4us, return to input, sample slot0 immediately before any clock.
- SRC: Test26/Test16-derived `emit_frame()` in `integrations/gp2040ce-xgo-test01/candidates/test26-hk-sequencer-offline/XGODriver.cpp` executes `wait_data(false)`, disables IRQ, `wait_data(true, EDGE_TIMEOUT_US)`, and **only then** `data_sink()` when `mask & 1`. Later slots are placed after CLOCK-low edges.
- HW: Test26 synthetic HK pulses spanning 10ms–2000ms mostly produced MP, rarely HK. Test16 other controls playable.

## Causal hypothesis (INF; not yet HW-validated)
For slot0, host samples shortly after releasing DATA; responder waits for DATA high before asserting low. Its detect-and-drive latency may exceed the host's sampling aperture. No analogous release-to-first-sample race applies to clock-delimited slots 1–11.

## Important implementation constraint
Blindly pre-sinking DATA while host still drives LOAD low is not safe as a drop-in fix: responder's existing `wait_data(true)` cannot detect release if it continues holding DATA low. Any early-drive design needs an independently proven release/clock or timed protocol contract; do not simply move `data_sink()` above `wait_data(true)`.

## Next narrow test
Determine the host release-to-first-sample budget from original scanner instructions and compare to RP2040 polling/PHY latency. Consider a controller-only slot0 transmission variant only after the release detection problem is solved. Preserve Test16; no XGO or emulator modifications.

## Separate issue
The Test26 SELECT+START+R1 hotkey collided with GP2040-CE LED Idle Rate handling; a narrowly scoped workflow patch now prevents LED handler consumption in XGO mode. This is distinct from the slot0 issue.
