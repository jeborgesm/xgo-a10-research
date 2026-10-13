# Held-action-button defect: first-priority isolation (2026-10-13)

## Hardware contract (HW)
User confirms Test14 **also** exhibits the defect: directions can be held normally; action buttons appear to release/repress repeatedly. A tap must assert the correct slot and then release; a hold must keep exactly that slot asserted on **every host poll** until physical release. Game repeat/animation behavior is outside controller scope.

## Source and prior evidence
- SRC: `process(Gamepad*)` publishes `map_mask(gamepad)` atomically. `runResponder()` reads a snapshot before waiting up to 20ms for LOAD. Thus a *transition* can be stale, but if a hold has stabilized and publication remains constant, the early snapshot alone cannot produce periodic release pulses.
- SRC: `emit_frame` releases DATA before waiting for LOAD and after the trailing CLOCK falling edge. Timeout paths also release DATA. `require_idle_high` applies only after failures. A dropped/corrupt frame could decode as a released action bit; no physical trace yet establishes this.
- SRC: button bits 0..5 are actions, 8..11 directions. The difference between direction and action behavior is a useful discriminator, but is not itself proof of a particular electrical failure.
- ARCHIVE: `findings/gp2040ce-test14-caveman-source-comparison-fault-classification-2026-10-12.md` documents that the reference and integrated responder share essential 12-slot serial ordering and 12us edge timeout. Do not assume changing final CLOCK-high validation fixes a held-button problem.
- ARCHIVE: `findings/gp2040ce-test14-source-order-counterexamples-2026-10-12.md` proves snapshot staleness for taps, **not** repeated false releases during a stable hold.

## Diagnostic decision tree (not yet HW-proven)
1. If processed published mask drops while the physical action button remains down, investigate GP2040 input processing/add-ons/SOCD/turbo or pin state. Do not change serial code.
2. If published mask stays asserted but a host poll decodes the bit released, investigate PHY frame acquisition, slot sampling, timeout/rearm, and host-side sampling phase. Do not remap GPIO.
3. If every host-decoded poll stays asserted but the game repeats an attack, the repetition is game behavior, not a controller-generated press event. User reports that direction holds behave differently; no host decoded traces are yet available to distinguish this case.

## Deterministic offline oracle
`tests/test19_hold_level_contract.py` checks 10,000 consecutive polls for each of the 12 one-hot slots, release, simultaneous LP+MP, and deliberately injected one-frame false releases. This is a **specification and fault detector**, not a firmware timing simulation and not proof of hardware correctness.

## Release gate
No Test19 UF2 until an implementation-level test demonstrates a concrete mechanism for an action bit to be falsely released and a targeted correction that removes that mechanism without changing the configured mapping, GPIO ownership, direction handling, or OLED/Web Config. Test18 remains unvalidated and is **not** the hold fix.
