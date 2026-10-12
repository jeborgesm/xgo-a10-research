# Test14 Caveman comparison and fault discrimination — 2026-10-12

**Branch:** `research-gp2040ce-xgo-integration`. Golden Test14 unchanged.

## Actual available Caveman-family source (SRC)

Inspected `tools/rp2040-xgo-native-contra/main.c` directly, alongside `integrations/gp2040ce-xgo-test01/src/drivers/xgo/XGODriver.cpp`. The former is the hardware-proven loose-wire Contra P2 responder **derived from Caveman**, not proof of possession of the original upstream Caveman implementation. Do not conflate them.

Both implementations use USB PHY DP/DM, 20,000us LOAD acquisition, 12us edge waits, DATA-low then high, slot0 drive, 11 clocked slots, trailing falling edge, DATA release, and an unchecked final clock-high wait. Therefore the final-rise omission and level-based acquisition **are not GP2040-only deviations**; they already occur in the known working reference. Their mere existence cannot explain Test14 failures. They remain candidate edge-case hazards.

## Differences with causal relevance (SRC)

- Reference `main.c` drives a scripted mask; its phase changes **only after a successful frame**, after `emit_frame()` returns. Test14's `runResponder()` loads an atomic Core0-published mask **before** waiting for LOAD, which may make an otherwise available newly published state stale for an entire transaction.
- Test14 disables interrupts after seeing LOAD low, with an interrupt-enabled handoff interval; reference has no such `save_and_disable_interrupts` call. This can be a source of added timing latency; the effect requires cycle and scheduling evidence.
- Test14 has success/failure diagnostics and a failure-only high-level rearm rule. Reference simply loops and reacquires LOAD. Both may be vulnerable to level-based reacceptance; Test14's additional bookkeeping changes inter-frame scheduling.
- Both reference and Test14 ignore final CLOCK-high result; this is shared behavior, not a discovered regression.

## Executable classification

New `tests/test14_multiframe_fault_classifier.py` distinguishes (MODEL):
1. Two short taps occurring between snapshots: zero delivered bits, even though button state was present at host LOAD times.
2. Late slot0 drive: host can read released bit despite requested pressed bit.
3. Hypothetical missed clock falling edge: intended slot1 may be decoded as slot2, e.g. mask `0x002` becomes `0x004` in the *synthetic* shifted-index model. This **is not proof that Test14 skips edges without aborting**; its clock wait code may time out or resynchronize differently. It demonstrates the *class* of error necessary to produce a foreign slot bit, unlike pure stale-snapshot latency.

An equivalent slot-index calculation was executed independently: aligned `0x002`, shifted `0x004`. The repository test is committed; a full Python test-suite run has **not** been established in this tool session.

## Narrowed conclusions

- **SRC proven:** early snapshot permits stale frames; strongest current code-level explanation for short taps vs holds.
- **SRC proven:** Test14 and hardware-proven native responder share much of the PHY frame protocol; do not assume Caveman itself had no timing edge cases.
- **INF only:** LOAD handoff and/or skipped edge may produce frame decode faults; not measured on device.
- **OPEN:** original Caveman upstream exact code; exact XGO host waveform/sampling; why HK is disproportionately affected; causal link to LP/LK contamination; per-core cycle budgets.
- **No firmware candidate** and no new hardware test until these gates are addressed.
