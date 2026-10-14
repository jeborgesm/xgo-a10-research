# Test25 successful build and runtime gate (2026-10-14)

## Verified CI
GitHub Actions run 38581082353 completed SUCCESS; host-side scheduler tests, overlay application, pinned upstream compile, packaging, and artifact upload all passed. Artifact ID 11903302009, name `xgo-gp2040ce-test25-OFFLINE-UNVALIDATED-DO-NOT-FLASH`. A successful compile is not hardware validation.

## Source review of committed Test25 driver
- Test16 Core1 `emit_frame()` path retained; sequencer invoked in Core0 `process(Gamepad*)` using `to_ms_since_boot(get_absolute_time())`.
- `snapshot = synthetic` suppresses **every non-HK control at all times**, including outside the sequence. This is intentional isolation for testing but eliminates normal navigation and can strand the user in menus; cannot treat as a normal playable controller.
- HK physical rising edge starts a two-second countdown. The physical HK is **not passed through** as a normal attack. The sequencer returns neutral outside an active sequence.
- There is **no abort gesture** or phase indication on the OLED. User cannot tell which pulse phase is running without a synchronized external timer/video. This misses two originally documented design gates.
- Diagnostic counters track mask changes/frames but are **not tagged by phase**. Per-phase correlation requires instrumentation or visual phase indication.
- The host test asserts scheduler logic only; it does not validate button press integration, display, or timing on the XGO.

## Decision
Do not ask for hardware test or recommend flashing Test25 artifact yet. Next candidate should add explicit arming/abort and phase visibility while preserving Test16's Core1 responder. Prefer safe idle pass-through or a deliberate diagnostic mode that can be exited without reflashing; add compile/static checks before release. Keep Test16 protected.
