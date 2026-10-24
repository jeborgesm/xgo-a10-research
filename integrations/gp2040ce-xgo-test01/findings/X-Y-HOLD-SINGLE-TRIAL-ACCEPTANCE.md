# XGO GP2040-CE — X/Y native turbo hold: single controlled trial

**Hardware status: NOT TESTED.** This is the *new* X/Y-hold firmware, distinct from the coherent-SPSC UF2 whose Contra jump and X/Y hold behavior FAILED on October 24, 2026.

**Immutable rollback:** retain your already hardware-proven Test44 UF2 unchanged and immediately available. Do not touch XGO `bios/bisrv.asd`, SD resources or Frankie wiring. This firmware is RP2040/Pico controller-side only.

## Why this trial is justified

The XGO generates turbo itself on the FC emulator when physical X/Y remain held. The prior RP2040 driver transmitted X/Y as a single 18ms pulse, so a long hold could not reach XGO's native turbo generator. This trial changes **only** the physical X/Y transport to continuous held levels; the other R/L/A/B attack buttons keep the 18ms coherent event queue and existing 18µs CLOCK timeout.

The sporadic unintended Contra jump remains a separate, previously observed hardware failure. This trial is **not** presented as its fix. Older passive native-PHY hardware produced jumps without an active DATA serializer, which argues against claiming that SPSC logic is the exclusive cause.

## One-session observation table

| Observation | Action | Interpretation |
|---|---|---|
| Startup and menu | Boot RP2040 in existing mode and navigate | Must remain fully functional |
| XGO turbo SHOOT | In Contra, **hold Y** for several seconds then release | Repeated shooting during hold, stops at release |
| XGO turbo JUMP | In Contra, **hold X** for several seconds then release | Repeated jumping during hold, stops at release |
| Ordinary attack | Short deliberate B/FIRE and A/JUMP presses | Same immediate actions, no held turbo introduced on B/A |
| Earlier phantom trigger | Hold RIGHT, tap B/FIRE repeatedly, without X/R/A | Record *any* unintended jumps or pauses separately |
| Street Fighter | Brief normal play and multi-button chord | No noticeable lost actions, stalls, wrong moves or stuck inputs |

For any failure, record the specific failed row, whether inputs were held or tapped, and whether the unintended action was JUMP, PAUSE or another behavior. You do **not** need new OLED counters, rewiring, or additional tests.

**Acceptance is two independent verdicts:** `X/Y native hold = PASS/FAIL` and `Contra spontaneous JUMP = PRESENT/ABSENT`. A PASS on turbo does not erase the known jump failure. Return to Test44 if stability or responsiveness regresses; keep even a partly successful trial clearly labeled experimental.

The controller's exact UF2 filename, SHA-256, source Git blob and GP2040-CE upstream commit are included in the build package's `PROVENANCE.json` and `SHA256SUMS.txt`.
