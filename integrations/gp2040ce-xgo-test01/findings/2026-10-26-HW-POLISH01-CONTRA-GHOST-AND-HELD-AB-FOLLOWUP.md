# HW: Polish 01 still has unsolicited P2 jumps; A/B held actions sometimes repeat

**Date:** 2026-10-26. **Branch:** `research-gp2040ce-xgo-integration`.
**Evidence:** [HW] owner's latest direct report on installed paged-OLED Polish 01; [SRC] protected GP2040 direct-held serial output; [EXT] established gameplay behavior in NES Contra; [OPEN] exact RP-to-XGO DATA waveform and cause of intermittent false inputs.

## Owner correction: standard rifle, no weapon upgrade

The owner's repeated B shots occurred with the **initial single-shot weapon**, not the automatic Machine Gun. The previous conditional suggestion that repeated shots might be normal weapon autofire does NOT apply to this specific observation. A physical B hold causing repeated standard-rifle shots is an unwanted game action and remains a genuine reliability symptom. It may indicate repeated press edges reaching the game, but the physical serial waveform was not captured. Do not rewrite continuous held input into a synthetic one-shot pulse as a workaround.

## Actual hardware observation — current Polish 01

Owner reports verbatim:

> "contra still has the ghost jumps and when I hold a or b i get repeated jumps or repeated shots... there should be only one and no repeats when hold"

This is the latest explicit ghost result **on the hardware-positive paged-OLED Polish 01 build**. It supersedes the previous Polish 01 test note's narrower `ghost was not yet reported` status. Earlier owner report on same build: no missed inputs noticed during extended SFII gameplay; sporadic LP/MP repetitions during holds, minor; reached bonus car, destroyed it with three seconds left. Both observations must be retained accurately.

| Behavior | Current observation [HW] | Interpretation status |
|---|---|---|
| External P2 untouched | Intermittent unsolicited JUMP continues | **Confirmed unresolved controller reliability defect** |
| A held in Contra | Owner sees repeat JUMP | Repetitions are real observed behavior, but input state vs game reaction is unmeasured |
| B held in Contra | Owner sees repeat FIRE | With the owner's confirmed initial single-shot rifle, repeated FIRE under one B hold is abnormal; do not attribute this case to Machine Gun autofire |
| SFII gameplay | No missed inputs noticed; occasional held LP/MP repetition; beat opponents to bonus car | Paged OLED hardware-positive for practical responsiveness; not total correctness |

**Corrected nuance:** Contra's starting rifle is manually triggered. The owner confirmed the unwanted B repetition happens with that rifle, before a Machine Gun upgrade. This is an abnormal held-B game action; it must not be dismissed as intentional weapon autofire. A continuous GP2040 physical hold still must remain a continuous *wire-level* held state—its intermittent decoded release/re-press remains a hypothesis, not a captured frame. Idle phantom jumping independently remains abnormal.

## Generic physical transparency contract [SRC]

Current protected GP2040 transparent source blob `cccb985a05baa8bb9078b6e336eb5f991c1a7a8f` captures a coherent 12-bit physical state and publishes it without a one-shot generator:

```cpp
const uint16_t physical = published_mask.load(std::memory_order_acquire);
const uint16_t mask = physical;
```

At successive XGO polls, a physically held A or B **must remain asserted at its own serial position**. It is **not correct to rework physical button hold into exactly one artificial 16ms outgoing pulse then released** merely to make Contra jump/fire once; that would violate expected gamepad hold semantics, break sustained inputs in other games and reverse the intended transparent implementation. One on-screen action does not imply a one-frame electrical pulse should have been sent; games interpret level and transitions independently.

**If** the physical serial line momentarily loses a held bit then re-asserts it, games requiring a new press edge can register multiple actions. Such interruption is a plausible transport fault, **not proven** by repeated game animation. Likewise, physically idle false-LOW at XGO L0/Handle can create unsolicited actions without GP2040 publishing a pressed mask.

## Engineering status and next repair priority

- **Keep Polish 01 flashed as current HW-positive input responsiveness baseline** while it is usable; retain transparent A UF2 for rollback. Previous diagnosis that Core0 full OLED page transfer could stall inputs is supported by improved observed responsiveness. Do not regress this by adding heavy diagnostics to Core0.
- **Primary confirmed unresolved failure:** externally connected P2 generates ghost JUMPs with no physical input, including on Polish 01. Earlier owner HW comparison was connected→ghost / disconnected→no ghost / reconnected→ghost on the preceding A build, reinforcing external-connection association but not independently rerun on Polish 01.
- **Secondary:** rare holds / actions; check source-backed serial stability rather than inserting pulse/edge generation.
- **NO** game-specific ROM/keymap changes, masking JUMP/R, forced controller one-shots, additional probes/cable bridge work, speculative strong DP USB pull-up or active HIGH drive, or changing XGO GOLD BIOS. Transparent interface remains user goal for all games.
- **No new firmware candidate or hardware test is claimed completed in this report.** New observations refine priority, not establish a causal repair.
- Original ROOT protected GOLD `bios/bisrv.asd` SHA256 `75f858b6d9a1eb81235ae9e9c9b449a6a3052ad4365e5411b8ce041075e99d6b`. Polish 01 paged OLED candidate UF2 SHA256 `5dcc28132ca54293a3d27dc2a452269bc47a1e7f141bd49c2c7e296918071b5b`, paged display source blob `e441ecc441a1d495413fbd56171a9a72e7321883`; prior A rollback UF2 SHA256 `94ea7228c774a67e8252e7e09d94938530e5d74572d985332e6840ae09fe8b84`.

## Cited external game-behavior references (not XGO evidence)

- [1999 NES Contra controls / select weapon hold-to-fire](https://gamefaqs.gamespot.com/nes/563399-contra/faqs/2980) — explicitly notes some weapons autofire when B is held.
- [2007 NES Contra weapons guide](https://gamefaqs.gamespot.com/nes/563399-contra/faqs/49217) — explicitly says Machine Gun repeats when held, standard gun normally requires repeated B presses.
- [2014 Contra player control analysis](https://tomorrowcorporation.com/posts/retro-game-internals-contra-player-control) — documents button A jump and internal jump flags, but not a unique test of repeated grounded jumps from held A in this hardware setup.
