# HW witness — Handle P2 ghost jumping unaffected by native R (A–B–A)

**2026-10-25.** Branch `research-gp2040ce-xgo-integration`. The owner's reported observations are **HW**; MIPS control-flow is **BIN**; explanations are **INF/OPEN**. This is the RESULT of the previously proposed no-flash physical experiment, not another proposal. No firmware, controller or wiring changes were made for this test.

## Experiment performed [HW]

The owner executed the reversible three-phase procedure from [the experiment gate](2026-10-25-NATIVE-R-HANDLE-P2-NO-FLASH-AB-GATE-AND-DMA-VERDICT.md) and reported:

> A — Native R released: Spontaneous P2 jumps.
>
> B — Hold native R: Spontaneous P2 jumps.
>
> A — Release native R again: Spontaneous P2 jumps.
>
> "The p2 spontaneous jumps don't seem to be affected by the native R. P2 still jumps no matter if the Native R is held or not in about the same rate"

The gate specifies XGO GOLD Setup **Handle=P2**, a two-player Contra session with external GP2040 left physically untouched, and no changes to Frankie V2 Jr or the transparent UF2. The user's explicit report establishes **P2 ghost jumps in all three phases, without an obvious rate change**. Exact event counts, elapsed duration for each window, actual serial mask, and wire voltage were **not supplied**. Do not manufacture numeric rates, statistical confidence or exact timestamps. P1's intentional response to holding its R is not a P2 event.

| Controlled variable | A1 | B | A2 |
|---|---|---|---|
| Native XGO R | released | held | released again |
| Physical external controller | untouched per test protocol | untouched | untouched |
| Reported logical P2 | spontaneous JUMP | spontaneous JUMP | spontaneous JUMP |
| Apparent P2 jump rate | about same | about same | about same |

**Outcome:** **NO OBSERVABLE DIFFERENCE** in the P2 ghost phenomenon when native R controls the extra four instructions before the physical Handle R0 read. This is a supported negative result, not a demonstration of an ideal electrical waveform and not an upper bound on any true tiny rate difference.

## What original BIN does and does not imply [BIN]

The SHA-pinned original XGO MIPS scanner samples native B15 R and, at `0x8035D878`, branches to external L0 R0 sampling at `0x8035D890` **when native R is released/high**. Native R pressed/low follows four additional instructions. This branch polarity has been checked on original `XGoAnalisis.zip` `bios/bisrv.asd` SHA256 `869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf`.

The *physical* P2 scanner still makes this decision in both logical Handle=P1 and Handle=P2 modes; the GOLD selection routes logical players after raw scans. The manipulation was therefore well grounded. But **four additional instructions are not a calibrated settle delay**. Their elapsed time relative to the real DATA analog rise threshold is unknown and could be too small to influence the observed error. An XGO interrupt or peripheral wait also can affect duration. This test **does not disprove electrical loading or first-bit LOW errors**, only the proposed *observable sensitivity to this particular branch-path timing perturbation*.

## Revised causal ranking, including prior independent evidence

**Lower priority after this test:** The narrowly formulated H1 in which intermittent ghost JUMPs happen primarily because native-R-released samples external R0 a few instructions too early, and pressing native R would measurably reduce them. The predicted difference did not appear. Do not propose another native R A–B–A as if this were untested, nor patch the original GOLD `bisrv.asd` to add a speculative delay on this evidence.

**Still viable (not proven):**
- **Physical DATA line/USB PHY input loading or short unwanted LOW glitches**: P3 passive transmit-disabled RP2040 via ordinary cable caused unsolicited P2 jumps [HW]. The active Frankie V2 Jr has a different physically bridged connector, so identical analog root cause is not demonstrated. A small native-R sample-path difference may be irrelevant if voltage error lasts longer, appears later, or occurs independently.
- **Wrong later serial bit or CLOCK phase**: Original XGO embedded FC fallback maps **R/slot0, X/slot2, A/slot4** to NES A/jump (R and X turbo); see existing `tests/test_nes_jump_origins.py` and `findings/embedded-default-keymap-patch-points.md`. A visible Contra jump therefore **does not identify R0**. The actual loaded per-ROM, per-player `<rom>/save/<romname>.kmp` was not verified in this experiment, so even fallback mapping is conditional.
- **Multiple-bit or wider timing disturbance:** In controlled Test49 (historical older diagnostic responder), owner also observed unsolicited **PAUSE** with no intentional START action before it. That cannot be attributed to R0 alone under default mappings. Earlier RP CLOCK/S12 errors were abundant but do not tell where a real XGO sampled a bad bit. The test firmware/cabling and current A are not identical; do not assert that Test49 PAUSE has the same root cause as this A–B–A P2 JUMP.
- **Physical controller published state, game mapping, or normalizer behavior**: no actual current RP `published_mask` and host-decoded serial word were synchronously captured during a ghost. Prior Test49 processed B1-rise remained 0 across phantom JUMPs but does not cover every possible physical jump-capable button nor the current transparent A build.

**Logical isolation achieved:** Because GOLD Handle=P2 supplies the external raw L0 stream to independent logical P2 rather than OR-merging it into P1, the contemporary P2 ghost persists **without relying on the Handle=P1 P1 merge**. Native P1 button presses do not eliminate it. This is stronger than previous P1-or-P2 ambiguity and argues against the merge being the sole cause. It does **not** exclude stock XGO P2 keymap/core processing.

## Updated next engineering decision

Do not make a GP2040 firmware change, XGO GOLD sampling-delay patch, DM pull-up override change (previously froze XGO), or Frankie wiring adjustment based on the A–B–A result. No need to repeat this exact experiment.

The next offline discriminator should inspect the **actual active P2 Contra keymap** if the matching 48-byte `.kmp` becomes available, and distinguish jump-capable physical R/X/A bits and START-related anomalies. **Local artifact inventory this turn:** the mounted `XGoAnalisis.zip` contains **115 entries, zero `.kmp` files and zero `Contra`-named paths**; the other three mounted ZIPs (the controller baseline, paged OLED candidate, and linked ELF audit) also contain no `.kmp` or `Contra` paths. No actual active SD save-directory `.kmp` has been supplied here. Therefore **the loaded Contra mapping remains OPEN**; do not silently substitute the embedded NES fallback for it.

For direct root-cause closure, instrument real raw XGO L0 and CLK during a ghost under a non-perturbing capture setup, or obtain a verified per-frame host decoded word. The now-green P0 per-frame analyzer can process a valid clock/data dump but cannot see the host's first R sample strobe. Current Frankie V2 Jr self-DMA tracing has not been cleared as noninterfering and must not be silently flashed.

**Protect baselines:** XGO GOLD `bios/bisrv.asd` SHA256 `75f858b6d9a1eb81235ae9e9c9b449a6a3052ad4365e5411b8ce041075e99d6b`; user-flashed GP2040 transparent A UF2 SHA256 `94ea7228c774a67e8252e7e09d94938530e5d74572d985332e6840ae09fe8b84`; linked source blob `cccb985a05baa8bb9078b6e336eb5f991c1a7a8f`; paged OLED B is unflashed.

## Prior records
- [Original experiment design, now executed with negative outcome](2026-10-25-NATIVE-R-HANDLE-P2-NO-FLASH-AB-GATE-AND-DMA-VERDICT.md).
- [Contra jump causal discriminators; NES fallback gives three JUMP sources](2026-10-24-CONTRA-JUMP-CAUSAL-DISCRIMINATORS.md).
- [Test49 hardware phantom JUMP/PAUSE details](../diagnostics/CONTRA-RIGHT-FIRE-OBSERVATION.md).
- [Current first-bit/PHY evidence](2026-10-24-USBPHY-PASSIVE-GHOST-AND-P1-CONDITIONED-P2-R-WINDOW.md).
