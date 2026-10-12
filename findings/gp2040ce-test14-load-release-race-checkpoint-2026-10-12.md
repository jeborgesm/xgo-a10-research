# Test14 LOAD/CLOCK transaction boundary — source-derived timing checkpoint (2026-10-12)

**Scope:** Read-only inspection of `integrations/gp2040ce-xgo-test01/src/drivers/xgo/XGODriver.cpp` on `research-gp2040ce-xgo-integration`, following HANDOFF-CURRENT and the cumulative Test14 audit. Golden Test14 unchanged. **Evidence: SRC / INF / OPEN; no hardware waveform and no Test15.**

## Newly isolated source-level timing ambiguity

`emit_frame(mask)` executes `wait_data(false, 20000)` **before** `save_and_disable_interrupts()` and then `wait_data(true, 12)`. The first function is a **level** check, not an edge timestamp. The following sequence is therefore possible at source level:

1. At t0 Core1's `wait_data(false)` observes host LOAD low and returns.
2. Between t0 and t1, before Core1 masks interrupts and enters `wait_data(true)`, the host releases LOAD high.
3. At t1 `wait_data(true)` immediately succeeds, without verifying any minimum LOAD-low duration or how long ago the release occurred.
4. Core1 drives slot 0 and begins waiting for CLOCK falling edges.

This is a *distinct* timing exposure from the already documented stale `published_mask` snapshot. Its importance depends on the unknown host LOAD-release-to-first-CLOCK interval and actual compiled instruction latency. The source does not establish whether the host samples slot 0 before or after the responder drives it. **No claim of a reproduced incorrect bit.**

## Consecutive-frame ambiguity

After the twelfth CLOCK falling edge, Test14 releases DATA, waits for final CLOCK high but ignores that wait's return, restores interrupts, updates several diagnostic atomics, returns to `runResponder()`, loads a new snapshot, and begins `emit_frame()` again. Success does not set `require_idle_high`. A host LOAD already low when the next `wait_data(false)` begins is accepted as a frame. Whether this is an erroneous reacceptance or a legitimate next frame cannot be decided without timing the host's LOAD-high idle interval and Core1's return/rearm latency. Conversely, unconditional edge-only rearm can miss a valid transaction (as the existing temporal model demonstrates).

## Deterministic waveform model requirements (not yet executed)

Model two separately driven electrical nets: host LOAD / DATA-low request and responder open-drain DATA sink; include host CLOCK and sampled bit value. For each transaction record t(LOAD falling), t(LOAD rising), t(CLOCK falling/rising for slots 1–12), t(host samples each slot), t(responder output changes), t(Core1 polls), t(IRQ mask/unmask), and t(next frame starts). Keep host sampling phase a parameter, not a Caveman-proven fact.

Enumerate: (a) LOAD release just before/after Core1 enters the 12us wait; (b) first CLOCK falling before/after slot-0 drive; (c) final CLOCK rise absent/delayed; (d) next LOAD during post-frame diagnostic work; (e) short LOAD-high gap entirely inside rearm overhead; (f) held constant mask across consecutive frames; (g) press/release pulses between Core0 publications and Core1 snapshots. Report independently: source-model `complete`, each host-sampled 12-bit mask, false release/reassert transitions, and mismatch against published mask. Sweep boundary orderings without inventing actual XGO timing constants.

## Root-cause discipline

- **SRC:** atomic mask publication, level-based LOAD acceptance, post-LOAD IRQ mask, ignored final CLOCK-high result, post-frame diagnostic overhead.
- **MODEL:** previous truth-table and temporal-rearm examples are synthetic, not physical validation.
- **HW:** missed HK taps, false held repeats, unintended LP/LK and history dependence; OLED input history does not show Turbo pulses.
- **INF:** delayed slot-0 drive or incorrect frame reacceptance could produce wrong host-decoded states under certain host timing; neither established.
- **OPEN:** original Caveman implementation provenance, host sampling phase and actual LOAD/CLOCK waveform, binary cycle timings, attack-to-slot assignments.

**Gate:** Do not construct Test15 until a host waveform model yields a concrete mismatch under a separately justified host protocol/timing contract, or a different root cause is independently verified. No additional user hardware test requested.
