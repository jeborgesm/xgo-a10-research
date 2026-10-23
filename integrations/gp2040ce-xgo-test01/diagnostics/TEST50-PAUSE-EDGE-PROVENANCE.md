# Test50 — processed SELECT/START provenance after confirmed phantom jumps and pause

## Hardware chronology, corrected by firsthand witness 2026-10-23
While intentionally moving RIGHT and repeatedly tapping FIRE with NO intentional JUMP press in Contra, **multiple unintended jumps occurred before screenshot 2**. The GP2040-CE processed `P4` rising-edge counter was 0 in all three photos. The user then continued RIGHT + FIRE taps, fell from a bridge, and the game **paused on its own** without START. The user deliberately pressed START once to resume and took screenshot 3 after continuing.

| Counter | Photo 1 | Photo 2 (after phantom jumps) | Photo 3 (after unsolicited pause, intentional START) |
|---|---:|---:|---:|
| CLK | 59 | 172 | 320 |
| S12 FAIL | 40 | 126 | 226 |
| LO / HI | 48 / 11 | 140 / 32 | 259 / 61 |
| P0–P4 | 0 | 0 | 0 |
| P5 (B2) | 0 | 29 | 164 |
| RF / E | 0 / 0 | 29 / 6 | 169 / 28 |

**Conclusion boundaries:** If B1 is assigned to JUMP, a B1 rising-edge counter staying zero despite actual character JUMPS provides evidence against a spurious GP2040-CE *processed* B1 edge. This is stronger evidence for a downstream serial framing/decoding issue, not proof of root cause. The START-like spontaneous pause is not yet measured in Test49: S1/S2 were not instrumented. The later deliberate START press must be distinguished from the unsolicited pause.

## Test50 isolated diagnostics
- Clone Test49 GP2040-CE candidate, leave `emit_frame()`, map, bit order, serial PHY, 18 us timeout, 18 ms attack pulse, rearm and existing OLED reading unchanged except readout layout.
- Add read-only processed-system-edge counters on Core0 for S1 / Select (bit6) and S2 / Start (bit7); only increment on rising transitions of existing `snapshot`, never modify `snapshot` or queued attacks.
- OLED 0 heading, 1 OK/ERR, 2 CLK/S12, 3 LO/HI, 4 P4/P5, 5 S1/S2, 6 other attack edges P0-P3 sum, 7 RF/E.
- Unit/state model tests validate no system edges from RIGHT + FIRE, one START edge on intentional press, no repeats on hold, and PHY map/responder source identity.
- Do not falsely promise detection of what XGO decodes. An unsolicited pause accompanied by **no S2 rising edge** is evidence pointing downstream. If S2 increments, it identifies a processed GP2040-CE START transition, not necessarily physical GPIO; confirm user intentionally pressed START since last OLED photo.

## Protect
Test42 / Test44 rollback builds, Test48 / Test49 diagnostics and XGO console side unchanged. Test50 experimental until build and hardware evidence.
