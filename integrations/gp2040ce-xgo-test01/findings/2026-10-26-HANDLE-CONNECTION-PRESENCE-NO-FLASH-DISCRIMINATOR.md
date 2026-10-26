# Controller reliability — connected vs disconnected Handle electrical isolation gate

**Created 2026-10-26**. Experimental protocol **PROPOSED, NOT YET EXECUTED**, designed after verifying original XGO L0 low-drive/input release, RP2040 DP pull-up forced OFF/Hi-Z idle and HC15xx GPIO family source. **No firmware, cable wiring, probes or external resistors modified.**

## Why this comparison is informative

The earlier P3 receive-only PHY made XGO P2 produce spontaneous actions even with the controller not driving button bits, but it used an ordinary cable and is **not physically equivalent** to currently working Frankie V2 Jr. Latest user native-R HELD/RELEASED test confirmed no obvious ghost-rate change from XGO instruction-path latency. We therefore need a hardware observation distinguishing **unreliable XGO Handle L0 DATA input without a controller attached** from **an electrical interaction introduced by the specific Frankie/RP2040 connection** before considering strong RP USB DP pull-up or other hardware modification.

## Minimal reversible connected–unplugged–connected test

**No hot-plugging.** Keep existing tested GP2040 transparent A and GOLD BIOS exactly as-is, and **do not detach/open/rework the soldered Frankie bridge**. Use only the normal plug at XGO's external Handle port, with both devices fully powered down before every connection change.

1. **A1, CONNECTED:** Start normally with Frankie+RP2040 attached, GOLD `Handle=P2`. In the same two-player game mode already known to show P2 spontaneous actions, leave GP2040 physically idle. Observe idle P2 for a reasonably comparable window; note whether ghost presses happen and optionally their rough frequency.
2. **B, DISCONNECTED:** Power everything down. Unplug the external Handle cable from the XGO port only (do not disassemble or change Frankie). Start XGO in the *same P2/two-player mode* with no Handle device attached. Observe whether P2 character still produces spontaneous actions with nobody pressing external buttons. **If the software will not display/enable P2 without a connected pad, this result is INCONCLUSIVE**, not a zero-ghost pass.
3. **A2, RECONNECTED:** Power everything down, reattach the original Frankie/Pico normally. Restart same setup, again leave the external controller untouched. Check whether idle P2 ghost inputs return. If the A cases have no spontaneous events, this trial lacks a positive control and is inconclusive.

The game is only an **observable input witness**, not a ROM/keymap investigation. The user should not need to install anything, add probe loading, identify pinouts or modify the controller.

## Interpretation [INF], not conclusions

| Pattern | Supported direction | NOT proved |
|---|---|---|
| A1 ghost, B quiet, A2 ghost | Connection/Frankie/Pico electrical presence is a necessary condition **for the observed session behavior** | Which pullup/capacitance/pin or whether the Pico firmware itself drives a bit |
| A1 ghost, B ghost, A2 ghost | XGO Handle input can generate phantom P2 events without the RP/F cable attached, suggesting board-side idle bias, native scanner, or game/input path | Exact electrical GPIO fault; serial host word absent |
| A1 ghost, B quiet, A2 quiet | Neither reliable repeatability nor connection-only cause established; power cycle or intermittent fault possible | Successful fix |
| A1 quiet or software hides P2 in B | Uninterpretable test; do NOT assert electrical root cause excluded | Nothing about DATA pull-up |
| Different symptoms and counts without timed observation | Qualitative clue only | Statistically different event frequency |

**Do not force a two-player session if absent P2 makes it impossible.** Merely performing a safe powered-down normal cable disconnect is not an electrical measurement. If normal connector insertion is mechanically precarious or the previous damaged connector makes repeated changes risky, **skip the trial** and treat the question as OPEN; no hardware action is required before software archaeology can continue.

## Safety and broader engineering gate

This comparison is substantially safer than attaching an unknown pull-up, changing RP DP USB resistor override (nominal USB Rpu ~1.2k/2.3k, not a weak general GPIO pull), adding a second RP probe (past P3 itself caused ghost), hot-plugging an unusually wired cable, changing GOLD firmware or modifying the working bridge.

Even an A/B/A pattern **cannot establish DATA line voltage** or prove a floating pin. Actual rise-time/host threshold measurement is still required before a physical pull-up repair.

**Protected baseline:** GP2040 A UF2 SHA256 `94ea7228c774a67e8252e7e09d94938530e5d74572d985332e6840ae09fe8b84`, source Git blob `cccb985a05baa8bb9078b6e336eb5f991c1a7a8f`; XGO GOLD BIOS SHA256 `75f858b6d9a1eb81235ae9e9c9b449a6a3052ad4365e5411b8ce041075e99d6b`; paged OLED B unflashed. User's negative native-R A/B/A result stands; do not repeat that test.
