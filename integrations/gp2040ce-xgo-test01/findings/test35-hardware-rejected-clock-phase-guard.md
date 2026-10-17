# Test35 hardware verdict — REJECTED (2026-10-17)

## HW — owner report

> hold no reps, directions are very chhoppy (like if the character was being electrocuted) start stop start stop fast, the taps are missing most off the tap, I need to tap really fast for the device to recognize a button.

## Classification

- **HW PASS:** Holds still do not repeat.
- **HW FAIL:** Directions rapidly start/stop; movement is severely choppy.
- **HW FAIL:** Most attack taps are missed; rapid tapping needed to get recognized.
- **HW FAIL:** Gameplay regresses severely versus Test32.

## Source change and inference

Test35 added a strict `if (!clock_level())` guard before `wait_clock(false)` for slots 1–11. Source suggests the guard may reject valid transactions when CLOCK is already low upon entering the slot. **INF:** This is a plausible explanation for missing inputs and choppy movement, not measured electrical proof. Do not treat the guard as a validated synchronization fix.

## Decision

**REJECT Test35.** Do not promote, reuse or compound the guard. Restore protected Test32 (CI 38798316411, artifact 12003102743) as best gameplay candidate. Test28 remains serial-timing baseline. Test34 preserved holds but had HP→MK and direction anomalies; Test33 severely mixed attacks. Next investigation should be offline, evidence-driven, and avoid strict clock-phase gating or further pulse-duration changes without a concrete basis. Controller-only modifications; no XGO BIOS, emulator, mapping or turbo changes.
