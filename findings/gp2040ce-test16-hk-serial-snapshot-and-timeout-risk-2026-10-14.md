# Test16 HK timing: snapshot and timeout risk — 2026-10-14

## Scope
Read-only SRC audit of `integrations/gp2040ce-xgo-test01/candidates/test16-offline/XGODriver.cpp`; comparison with prior hardware Test23/Test24. No UF2, no changes to protected Test16.

## New concrete source-level observations
1. `emit_frame()` calls `wait_data(false, 20000)` to acquire LOAD low, **then** disables interrupts, loads `published_mask`, timestamps `low_start`, and starts `wait_data(true, 12)`. Therefore `low_start` does **not** mark actual LOAD falling edge; `xgo_diag_load_low_last_us` underreports true LOAD-low duration by acquisition and pre-timestamp overhead. It must not be used as an electrical pulse-width measurement.
2. The 12us release timeout starts **after** the snapshot and interrupt masking, not at the falling edge. It bounds the software wait, not the host's full LOAD pulse. A host release occurring during that pre-wait work is accepted immediately on first poll, but may have already consumed the host's slot0 setup window.
3. Snapshot is taken once per **serial transaction**. An HK press that arrives after snapshot cannot be reflected until a later transaction even if the OLED shows RB. This is a plausible missed-tap mechanism distinct from slot0 electrical turnaround; does **not** explain MP substitution alone.
4. `wait_data(true)` returns on observed high; Test16 performs post-release timestamp and diagnostics before asserting slot0. Test23 moved the assertion earlier but did not alter pre-release work. Test24 used inline polling, yet failed. Therefore simple source-order reductions are insufficient evidence of fix.
5. The source comment claims `save_and_disable_interrupts()` protects against 'Core0 IRQ preemption' but the responder is Core1 (`runResponder()`); local interrupt masking only affects the calling core. This comment is inaccurate. The cross-core `published_mask` atomic exchange is the intended data path.
6. Test16 waits for 11 clock-low/high cycles in the `slot=1..11` loop and then waits for **one additional** clock-low/high pair (`failed_slot=12`) before returning. Whether this matches the host's trailing CLOCK behavior must be established from the full scanner loop; do not remove it speculatively, since Test16 is playable.

## Consequences
A displayed RB confirms physical/processed input, **not** that the snapshot used by the XGO host scan contained bit0 or that the bus settled before host sampled. Distinguish three possible losses: input publication/snapshot phase, responder bus-turnaround latency, and host decode/frame alignment.

## Next offline gate
Disassemble the built Test16 UF2/ELF or build the identical pinned source to measure instruction counts and determine how often host scans occur relative to GP2040 process. Verify trailing clock in scanner binary. Physical DATA-stream identity still OPEN. No request for new hardware test.
