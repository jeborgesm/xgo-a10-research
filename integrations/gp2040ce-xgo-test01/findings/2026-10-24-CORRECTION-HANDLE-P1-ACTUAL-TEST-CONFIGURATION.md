# CRITICAL CONTEXT CORRECTION — recent GP2040-CE gameplay tests used Handle=P1

**2026-10-24. Evidence: user clarification [HW], verified GOLD routing source [SRC/BIN/HW], bounded fault classification [MODEL/INF/OPEN].**

## Binding new user observation (HW)

The user clarified after reporting the transparent-controller gameplay results:

> "An importat data point that I had not sahred before is that I am running these tests as a P1 using our new XGO firmware change that allows the xgo and the handle to control p1."

**The reported SFII/Dhalsim and Contra tests, and the intermittent SFII LP and Contra jump issues, were conducted with the XGO native Setup Handle selector in P1 mode.** Never describe their user-visible actions as libretro **Player 2** merely because the Handle uses the second physical serial line. Do not silently project this detail onto older P0/P3/P2 hardware sessions taken before the GOLD selector was available.

The external RP2040 transparent controller itself remains good/physical-state-correct in the user's direct observations. GP2040-CE does not know whether XGO ultimately uses its inputs as P1 or P2.

## Actual hardware/software provenance

The user-installed XGO **native Setup Handle P1/P2 + PAL** GOLD task was accepted on 2026-10-22:
- Gold package SHA-256 `42c3f05ab3365f3fb58016d770f89106378b9ecedc4741599927058af9d7eb6c`;
- GOLD `bios/bisrv.asd` SHA-256 `75f858b6d9a1eb81235ae9e9c9b449a6a3052ad4365e5411b8ce041075e99d6b`;
- verified source/hardware closure in `main:findings/2026-10-22-native-handle-pal-GOLD-closure.md`;
- complete generator `main:tools/handle/archive/build_xgo_native_handle_toggle.py`; exact fixed-P1 helper remains preserved in GOLD.

The original XGO scanner reads physical **P1/B15** and **Handle physical P2/L0** together on shared CLOCK/B7, with independent 12-button active-low DATA encoding. Pressed bits become positive masks in host RAM:
- physical local raw P1: `0x80C33A48`;
- physical Handle raw P2: `0x80C33A4C`;
- stock normalizer: `0x8035D4C4`, merge hook at `0x8035D53C`;
- protected HW-proven fixed P1 helper: `0x80A398E4`;
- GOLD mode-select conditional gate: `0x80A38664`, mode flag `0x80A39910`.

Exact **semantic** routing established by builder/verifier and tested in the GOLD selector:

```text
Mode P2 (stock/default):
    logical_P1 = raw_local_P1 | aux_RF_P1
    logical_P2 = raw_Handle_P2 | aux_RF_P2

Mode P1 (user's CURRENT gameplay configuration):
    logical_P1 = raw_local_P1 | raw_Handle_P2 | aux_RF_P1
    logical_P2 = aux_RF_P2
```

The helper redirects raw Handle **after** scanning; it does **not** alter RP2040 CLOCK/DATA, move the physical Handle wire to the P1 GPIO pin, or directly change the emulator's inputs. P2 raw contribution is suppressed in P1 mode, leaving independent auxiliary P2 unchanged. The XGO keymap compiler then processes the **logical P1 input**; the per-game P1 `.kmp` mapping/embedded fallback is the relevant comparison.

The original P1-first-bit branch at `0x8035D878` and P2-first-bit read at `0x8035D890` remain *physically applicable* even while the external gamepad controls logical P1. The P1-first-bit level comes from the built-in controller and affects how quickly physical Handle P2 slot0 is sampled [BIN], but exact voltage threshold, cycle time and its role in ghosting remain OPEN.

## What this changes in the fault tree

**Contra ghost JUMP [HW, cause OPEN]:** A bad pressed input may originate in **either** physical source before the OR:
1. false pressed bit from external physical Handle P2 DATA (e.g. unmeasured slow release of slot0 or other clock/PHY failure);
2. false pressed bit from the stock **built-in P1/B15** scanner;
3. nonzero auxiliary/RF input state in P1 (not established on this specimen);
4. valid logical P1 input reinterpreted by its actual loaded `.kmp`/game mapping.

**The P1 OR cannot create an asserted bit not present in at least one source.** It can propagate a false bit from either source, and can preserve a bit when one source drops it. It cannot by itself explain a phantom jump with both streams released and aux P1 zero. The historical passive P3 ghost **P2** jump does NOT magically become direct proof of the current P1 gameplay fault or current Frankie cable, though it remains physical Handle electrical evidence.

**SFII occasional LP missed/three punches [HW, cause OPEN]:** Core0 OLED blocking can miss brief physical presses on the GP2040. The asynchronous XGO host scan can also miss short sampled presses. P1 OR *does not* turn one stable held bit into three input onsets; if external Hold appears to oscillate on the host wire or normalized state (and local P1 is not holding that same bit), false released frames might permit repeated logical press transitions. This is only a MODEL and depends on game event semantics. The specific SFII LP physical/button mapping and loaded `.kmp` are not established.

The user's observation that holds/taps generally behave correctly is a strong positive HW constraint. Do not reintroduce 18ms pulse synthesis, RP2040 auto-turbo, X/Y exceptions, button masking or game-aware translation.

## New offline regression

`tests/test_handle_as_p1_fault_isolation.py` checks 3,200 representative local/Handle/RF source combinations and both GOLD modes, the no-fabricated-bit OR invariant, raw local **or** Handle R false-positive propagation into logical P1, P1-mode suppression of Handle's contribution to logical P2, and a bounded model of two false releases creating three logical transitions. **MODEL only**; source-level semantic parity, not executing the full GOLD MIPS image or simulating a live cable. Independently ran locally: PASS.

## Next actions, no new physical test requested

1. **Rebase attribution:** all current gameplay symptoms are on logical P1, fed by both B15 and L0; earlier P2-port-only attribution and unqualified `P2 jump` diagnostics are misleading for this session.
2. Keep separately protected GP2040 transparent UF2 A SHA-256 `94ea7228c774a67e8252e7e09d94938530e5d74572d985332e6840ae09fe8b84`, and XGO native Setup GOLD BIOS `75f858b6d9a1eb81235ae9e9c9b449a6a3052ad4365e5411b8ce041075e99d6b`.
3. The OLED page-only GP2040 candidate B SHA-256 `5dcc28132ca54293a3d27dc2a452269bc47a1e7f141bd49c2c7e296918071b5b` remains **UNFLASHED**; it addresses a scheduling weakness, not a guaranteed solution to jump, triples, or the P1 merge.
4. Continue offline review of source-of-bit provenance, first-slot input phase, per-game **P1** mapper semantics, and the merge; explicitly distinguish P1+B15 input corruption vs Handle P2+L0 serial corruption vs downstream interpretation.
5. A future bounded discrimination *could* compare Handle P1 and P2 modes or read a real per-ROM `.kmp` after first specifying what differing result would distinguish. Do not ask for repetitive hardware trials or modify the XGO GOLD firmware merely to observe the symptom.

**Status:** important user-supplied HW context integrated. No new controller firmware or host BIOS edits, no new hardware claims, no fix released.

## Additional BIN correction: normalizer's branch-delay slot clears LOGICAL, not raw serial state

Hash-pinned direct reinspection of the original `XGoAnalisis.zip/bios/bisrv.asd` identified an error in the older main-branch Handle investigation note, which claimed that `0x8035D54C: sw zero,0(a0)` cleared the current player's **raw serial** word. In fact:

```text
0x8035D4FC  addiu s5,gp,-0xd2c    # raw serial base
0x8035D508  addiu fp,gp,-0xd18    # logical input base
0x8035D524  addu a0,t0,s5       # a0 points at raw serial[player]
0x8035D52C  lw s4,0(a0)         # consume raw serial
0x8035D534  addu a0,t0,fp       # a0 is REASSIGNED to logical[player]
0x8035D548  beq s2,zero,0x8035D558
0x8035D54C  sw zero,0(a0)       # branch delay: clears LOGICAL[player]
```

The new serial scanner explicitly clears the raw serial input pair earlier at `0x8035D780` (`gp-0xd2c`, P1) and `0x8035D788` (`gp-0xd28`, physical Handle/P2), *before acquiring their next bits*. The scanner tail at `0x8035DE10` branches back into the normalizer loop. An alternate path at `0x8035D764` re-enters normalizer without newly scanning; **this particular `0x8035D54C` write does not force the raw serial inputs to zero on that re-entry**.

**Consequences:** the P1 merge helper reading physical Handle raw P2 at `0x80C33A4C` is **not** automatically defeated by a preceding P1 normalizer iteration clearing that raw address; the older "consumes and clears raw" wording is wrong. Nor is a phantom periodic release established from this code path. Other global writes and exact runtime scheduling are not fully excluded by this limited original-image analysis. This correction comes from **original unmodified XGO BIN**, not a direct disassembly of current GOLD modified BIOS. The GOLD helper's own semantic provenance remains pinned separately.

A reproducible [13-opcode original BIOS verifier](../tests/verify_xgo_raw_vs_logical_clear.py) was executed offline against the actual user-supplied original ZIP and PASSed, without modifying any binary. The original older note is retained for archaeology; this new evidence supersedes its incorrect pointer interpretation.

## ADDENDUM — Contra ghost JUMP also occurs when user operates BUILT-IN P1 and leaves external GP2040 UNTOUCHED (2026-10-24)

**NEW HW observation from user, narrowly scoped:** With the XGO native `Handle=P1` setting still selected and the external GP2040-CE connected, the user actively plays Contra with the **built-in XGO controls**, **does not touch the external controller**, and still observes the spontaneous P1 JUMP. The user describes the external P1 function as "hijacking" P1. This explicitly rules out *intentional contemporaneous external button presses* as a necessary trigger for the ghost jump. It does **not** rule out electrical/serial false-pressed bits from that physically connected but idle external controller, built-in stream faults, a mapped key, or game interpretation. No P2-mode, unplugged, or other comparison has been reported in this new clarification: DO NOT invent one. The SFII LP behavior was not retested or attributed to built-in versus external by this clarification.

**Verified routing explanation [SRC/BIN]:** The GOLD firmware's Handle-P1 helper ORs the two **pressed** masks. It does not give the local controls exclusive priority or temporarily disable the Handle when built-in buttons are pressed. In the absence of RF activity:

```text
user drives built-in P1; external RP2040 physically idle/connected
       host raw local P1 (B15) -------+
                                      OR ---> game-visible logical P1
       host raw Handle P2 (L0) -------+
          (should be zero if truly clean)
```

Thus the model's distinction is *physical GP2040 buttons idle* != *XGO host successfully sampled Handle raw P2 as all-zero*. A transient false pressed bit from L0 is transmitted through the OR as logical P1. Under embedded FC defaults, R, X, and A can all map to Jump; exact loaded Contra `.kmp` unknown. If physical local P1/B15 or auxiliary P1 yields the erroneous bit instead, that too reaches logical P1. The OR cannot generate a one when every input source was zero.

**Prior passive P3 corroboration [historical HW with different cable]:** An RP2040 connected via an ordinary passive-USB-PHY configuration had already caused unintended P2 jumps without sending intentional active DATA. It supplies precedent for connected-but-not-actively-pressed electrical perturbation, **not** proof that the current transparent firmware, Frankie V2 Jr, and P1-mode test share the same root cause.

### Single high-value *future* logical-mode discriminator (not a request for new testing now)

Keep the **same connected, untouched external controller and same built-in P1 Contra gameplay**, change **only** the GOLD Setup setting between Handle=P1 and Handle=P2. The serial reader still polls physical L0 in both cases; mode changes the logical destination for its decoded pressed state.

- Ghost jump appears with Handle=P1 but disappears when set to P2: consistent with a spurious Handle raw P2 bit being merged into P1 (or a mode-specific normalizer defect). Does NOT prove electrical cause.
- Ghost jump persists with Handle=P2 while playing built-in P1: external-to-P1 merge is not necessary; prioritize local B15/aux/P1 mapping or other common input path. It does NOT prove external cable electrically harmless.
- No ghost during a limited run in either mode: **inconclusive** for an intermittent symptom; do not mark fixed based only on absence.

This is a targeted **conditional discriminator**, not a completed test, new firmware candidate, or user instruction to repeatedly reproduce the issue.

**Immediate engineering direction:** prioritize idle-L0 DATA/LOAD recovery and false-positive bit attribution, not SFII tap sampling, and *do not* patch one-sided R/button filtering, physical holds, native P1 mode, Frankie wiring, BIOS, or PHY pull-up based on this one observation. Preserve protected XGO GOLD SHA `75f858b6d9a1eb81235ae9e9c9b449a6a3052ad4365e5411b8ce041075e99d6b` and transparent GP2040 A UF2 SHA `94ea7228c774a67e8252e7e09d94938530e5d74572d985332e6840ae09fe8b84`. Paged OLED B remains unflashed and cannot be credited for curing ghosting.
