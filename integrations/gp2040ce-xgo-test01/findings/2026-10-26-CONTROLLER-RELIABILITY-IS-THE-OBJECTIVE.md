# Controller reliability is the objective — scope correction (2026-10-26)

**Owner correction (binding):** “why are you checking the Contra Rom ??/ what we need is to make the controller work reliably.”

## Decision

**Stop treating the Contra ROM, embedded NES fallback, or per-game `.kmp` as the next investigative gate.** Contra is a convenient *witness* to controller corruption, not a debugging target or workaround. No game-specific profile edits, selective suppression of jump-capable buttons, emulator fixes, or per-game pulse policies are acceptable substitutes for correct universal controller transport.

## Generic acceptance contract

With the hardware-approved XGO GOLD firmware, existing Frankie V2 Jr wired Handle interface, and GP2040-CE in transparent mode:

1. **All buttons released:** host sees zero external pressed bits, repeatedly over many scans. No unsolicited game actions, menus or movement in **any** game.
2. **Each button held:** exactly that physical button's wire slot remains active for every complete XGO scan; it is neither lost, translated to a neighboring slot, nor replaced by pulses. Native XGO turbo X/Y semantics must remain intact.
3. **Transition:** a physical press propagates promptly; a release genuinely clears the slot. No added oscillation, 18ms synthetic press, arbitrary debouncing of outgoing mask, or remapping.
4. **Synchronization:** clock pulse observation, slot assignment and frame re-arm remain correct under the real host's short HIGH windows and occasional GPIO timing variation.
5. **Across player routing:** when GOLD Handle=P1 or Handle=P2, the same external serial transport is correct; logical routing is not an explanation for wrong physical input.

These are *hardware acceptance requirements*, not a claim that they are now satisfied.

## What existing evidence actually directs us toward

- **[HW]** User's logical Handle=P2 native-R RELEASED→HELD→RELEASED A-B-A still had spontaneous P2 jumps at about the same rate. Therefore the original MIPS four-instruction R-conditioned P2 sample path did not materially affect the symptom; **do not repeat**.
- **[HW]** Historical receive-only P3 native USB-PHY attached by an ordinary cable caused unsolicited P2 jump while never asserting DATA, and instrument probes previously changed P2 behavior. This supports investigating electrical load/line ownership, not a particular game's ROM mapping. Frankie V2 Jr has different bridged physical pads; no claim of identical analog cause.
- **[BIN]** XGO stock physical Handle DATA load/release and R0 sampling precede a twelve-pulse shared CLK burst; real P0 observations measure DATA-to-first-FALL margin around 0.9–1.3us, and one burst's average intervening CLOCK HIGH around 1.36us.
- **[SRC]** Protected A's RP Core1 serial output is the direct physical 12-bit published mask; RX/clock polling occurs in SRAM, masked interrupts, with no deliberate HIGH drive on DATA. For released R0 it waits DATA HIGH *before arming the first falling clock*. Original XGO physically samples R0 independently, so that first-bit error cannot be repaired after-the-fact by game logic.
- **[MODEL]** Source-extracted simulated missed clock can shift held bits, and delayed DATA recovery can make host see false R even when RP reports a completed frame. These are potential mechanisms, **not proven current cable behavior**.
- **[OPEN]** Which physical DATA bit XGO reads erroneously, which actual CLK edges RP misses, what DATA analog threshold/timing occurs on Frankie, whether the current RP receives exactly what the host sends.

## Next technical priority — one transport layer at a time

1. **Controller-only causal isolation:** first audit active DATA low-sink/release vs native USB-PHY receiver configuration, and the known P3 receive-only ghost using a physical/electrical equivalent or non-intrusive setup when possible. Do not claim the user's P2 jump requires RP to publish a jump bit; the historical passive test contradicts that as a universal explanation.
2. **Real on-wire signal integrity:** qualify a capture method that does not alter the XGO's fragile DATA bias or the existing Frankie pad bridge; observe DATA during host load/release and CLOCK during slots. Existing P0 decoder is a read-only tool, not proof of current electrical cause.
3. **Responder synchronization:** use actual protected source and linked disassembly to evaluate recovery from lost first CLOCK (and host clock stretching) without affecting idle DATA. An alternative clock-first synchronization only addresses modeled slot shift, **not** the root false-bit issue by itself.
4. **Only then** consider one isolated reversible controller-side repair, with regression across all 4096 masks, repeated idle/held frames, and a hardware A/B comparison. Keep protected A UF2 and GOLD BIOS as rollback baselines. Never blindly alter XGO `bisrv.asd`, DM pull-up overrides (HW froze XGO), active HIGH drive, or Frankie pads.

## Anti-drift rule

**Do not ask for the user's Contra ROM, FC/save .kmp, or any game's keymap as a prerequisite for fixing transport.** Prior `.kmp` tooling remains secondary forensic infrastructure, not an active research workstream. A controller must work reliably for every game before map-specific interpretation matters.

**Preservation:** protected GP2040 transparent A source Git blob `cccb985a05baa8bb9078b6e336eb5f991c1a7a8f`; UF2 SHA256 `94ea7228c774a67e8252e7e09d94938530e5d74572d985332e6840ae09fe8b84`. XGO GOLD `bios/bisrv.asd` SHA256 `75f858b6d9a1eb81235ae9e9c9b449a6a3052ad4365e5411b8ce041075e99d6b`. Paged OLED B unflashed. This scope correction changes **documentation only**, not firmware.
