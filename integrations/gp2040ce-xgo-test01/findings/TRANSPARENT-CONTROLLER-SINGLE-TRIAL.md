# XGO A10 / GP2040-CE transparent controller — single-trial acceptance

**Test candidate status:** compiled/tested offline only until the user explicitly reports results.  
**Hardware baseline:** original Test44 UF2 must remain available for immediate rollback.  
**Physical setup:** existing Frankie V2 Jr wiring only; no new equipment or XGO SD/BIOS modifications.

## Controller architecture

The controller publishes the actual coherent state of all 12 physical buttons and directions:

- **Press** → XGO wire asserted while physical Gamepad reports pressed.
- **Hold** → XGO wire stays asserted throughout every host scan during the hold.
- **Release** → XGO wire is released on the next scan using the new physical snapshot.
- **The XGO owns** logical mapping, turbo/repeat rate, and all game-specific meaning.

No local 18ms attack pulse, no special X/Y treatment, and no controller-generated turbo oscillator.

## OLED restoration

The normal GP2040-CE Test13 button-layout screen returns. Left side shows the selected directional layout, right side displays selected physical buttons, each highlights according to the processed Gamepad state. XGO mode enables the pressed-button input history along the bottom (row 7). No XGO serial-diagnostic text rows or counters displayed. Other input modes retain their stored display preferences and stock layout behavior.

## One controlled hardware session

| Check | Physical action | Acceptance |
|---|---|---|
| Boot/UI | Boot existing RP2040 controller, inspect OLED | Normal direction/button graphics and pressed-button history in bottom row; no diagnostic clutter |
| All physical holds | Individually hold and release X/Y/A/B/L/R | Button shown pressed throughout hold, released afterward; no controller-side one-shot behavior |
| Street Fighter II | Hold X/Y and each remaining attack; then tap ordinary attacks | OLED reflects real holds; XGO decides any repetitions; all mapped presses responsive |
| Contra native turbo | Hold Y to shoot, hold X to jump, then release | Repetition and stop-on-release controlled by XGO game/keymap, not RP2040 timer |
| Contra transport fault | Hold RIGHT, tap B/FIRE without touching jump buttons | **Separately** record any unsolicited JUMP or PAUSE; existing fault may persist |
| D-pad and system | Hold each direction; SELECT and START | States follow physical press/hold/release; no stuck buttons |
| Multi-button | Hold several buttons together then release one at a time | Correct simultaneous states and independent release |

If any button fails to follow physical press/hold/release on the OLED, freeze/stuck input appears, or baseline functionality regresses, revert to the protected Test44 UF2.

**Two independent verdicts:** (1) `transparent physical controller = PASS/FAIL`; (2) `Contra spontaneous jump = PRESENT/ABSENT`. Passing the first does not establish the cause of the second. Neither source testing nor linked SRAM audits are physical evidence.

This procedure never requires modifications to XGO `bios/bisrv.asd`, Frankie rewiring, additional hardware, or a chain of diagnostic OLED flashes.
