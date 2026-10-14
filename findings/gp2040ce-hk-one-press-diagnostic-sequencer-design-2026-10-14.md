# HK one-press diagnostic sequencer — design proposal (2026-10-14)

## User idea
Like the previous Contra bot: press physical HK once and let the RP2040 execute a timed, distinguishable series of HK stimuli. Goal: gather several discriminating observations from one hardware session rather than repeated speculative firmware candidates.

## Safety and implementation boundaries
- Preserve protected Test16 unchanged and independently restorable.
- Experimental sequencer as isolated candidate; trigger on physical RB rising edge, ignore further RB while running; include abort and bounded timeout.
- Keep directions and other controls neutral during automated phases to prevent accidental menu/game actions.
- Run sequence scheduler outside the time-critical Core1 serial response loop; publish a precomputed synthetic 12-bit mask atomically at phase transitions. Core1 still owns PHY; never insert sleeps, display updates, or per-phase logic in clock train.
- Transition phases only at completed serial-frame boundaries if possible; publish the chosen mask before next LOAD; retain recovery and timeout rules.
- Include neutral gaps >=500 ms and OLED phase labels/counters; do not assume OLED can resolve individual 10ms events.
- Compare same Test16 serial engine first; an alternate slot0 engine requires a separately identified, compiled, frame-boundary-safe experiment, not a blind tweak.

## Suggested phase plan (not yet implemented)
0. Neutral 2s and display sequence ID; game positioned in safe training/idle state.
1. Continuous HK 1s; neutral 1s (baseline held behavior).
2. 5 x 100ms HK ON, 500ms OFF.
3. 5 x 50ms HK ON, 500ms OFF.
4. 5 x 25ms HK ON, 500ms OFF.
5. 5 x 10ms HK ON, 500ms OFF.
6. Continuous HK 2s; neutral 1s (held repeat/MP observation).
7. Optional isolated alternate responder timing, only after separate offline proof and compilation.
8. Restore neutral; require HK release before accepting another trigger.

## What the results mean and do not mean
- Phase-to-phase differences can reveal minimum reliable synthetic pulse duration and possible scan/snapshot aliasing.
- Identical long-hold MP-first behavior across phases points away from physical button debounce.
- Serial scan rate and game input sampling mean 10ms pulses may be missed for legitimate phase reasons; do not call that an electrical failure without frame accounting.
- Need telemetry per phase: serial frames attempted/successful, masks published, LOAD/clock timeouts, active failures. Counts do not prove host received bit0.
- Video of OLED/game plus phase labels is helpful but cannot replace waveform measurement for host first-sample setup.
- Never claim a given action in SFII uniquely identifies a particular serial bit without independent one-hot mapping.

## Open design decision
Use one press to trigger automated pulses, or require an explicit two-button arming chord to prevent accidental sequence during normal play. Prefer explicit arming with HK as start trigger and a visible OLED countdown. Avoid introducing an untested boot default.

## Status
DESIGN ONLY. No firmware, no CI, no hardware validation. Test16 protected.
