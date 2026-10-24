# Test48/Test49 OLED error counts: real RP2040 timeout evidence, NOT host-decoded wrong-button counts

**Date 2026-10-24, branch `research-gp2040ce-xgo-integration`. Status: HW retrospective + SRC causal boundaries. NO new hardware test, NO firmware changes.**

User correctly recalls that the prior OLED diagnostics repeatedly registered errors. This evidence matters to the current **Contra external Handle P1/P2 ghost jump and perceptually intermittent A/B hold** investigation, but we must classify WHAT was counted before declaring those numbers bad game inputs.

## 1. What hardware screenshots established [HW]

Source: [pinned chronological controlled diagnostic log](../diagnostics/CONTRA-RIGHT-FIRE-OBSERVATION.md). The most informative readings:

| Actual prior diagnostic | RP2040 CLK errors | S12 classifications | Non-S12 CLOCK errors | LO errors | HI errors | DATA-release errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Test48 final photo | 597 | 421 (70.5% CLK) | 176 | 480 | 117 | 31 |
| Test49 **controlled** run, final photo | 320 | 226 (70.6% CLK) | 94 | 259 | 61 | not displayed in controlled log |

Test48 `ERR` counts for photos 1,2,3 were **350, 543, 628** and always equal `CLK+REL` (339+11, 518+25, 597+31). Test49 controlled `LO+HI = CLK` at every photo (48+11=59; 140+32=172; 259+61=320). These are confirmed internal accounting identities, not proof that the XGO's game received wrong bits.

**Test49 controlled actual chronology [HW]:** multiple unsolicited Contra JUMPs **before photo 2** while RIGHT was held and FIRE tapped; subsequent unsolicited PAUSE, then one intentional START to resume before photo 3. Processed GP2040 attack-rising counters P0–P4 remained zero in the controlled snapshots while P5 increased. They count GP2040 **processed physical input transitions**, not the XGO's sampled serial word. Do not attach each phantom event to a particular timeout, or assume that R is the sole possible jump mapping without reading the ROM's loaded `.kmp`.

In the controlled Test49 run, among the photo-1→2 accumulated **113 new CLOCK timeout classifications, 86 were S12** (76.1%); between photo-2→3, **148 new CLOCK classifications, 100 were S12** (67.6%). The grouped RIGHT+attack condition finished at 169 classified attempts and 28 failures (16.6% classified fail fraction, NOT 16.6% corrupt game words). Do not confuse the separate preliminary Test49 OLED photos (other cumulative baselines) with these controlled results.

The deterministic [photographed counter reconciliation script](../tests/test_historic_error_counter_reconciliation.py) calculates and asserts these relationships using the documented numbers; a standalone local run passed. It is not a new capture or simulation of physical bit correctness.

## 2. Source of the error numbers [SRC]

These OLED numbers are **RP2040 firmware's own TIMEOUT counters**, NOT XGO hardware receipt acknowledgements. Review the exact recorded [Test48](../candidates/test48-right-fire-phantom-diag/XGODriver.cpp) and [Test49](../candidates/test49-attack-edge-provenance/XGODriver.cpp) source:

- `CLK`: incremental `xgo_diag_clock_timeouts`, when `wait_clock(expected level,18us)` gives up. Low/high classification is from whether code was waiting for CLOCK FALL (`LO`) or RISE (`HI`).
- `S12`: `xgo_diag_clock_failure_slots[12]`; in **both Test48 and Test49** this can mean the expected **terminal FALL** after transmitting 12 button positions was missed **OR the subsequent final HIGH wait** failed. It is NOT the index of a known incorrect XGO button. `LO+HI=CLK` because each classified error has one phase direction.
- `REL`: `wait_data(true,18us)` failed after the host's DATA/LOAD pulse; in these versions it aborts remaining bit emission and sets `require_idle_high`. A bad release is a more direct risk for false slot0 sampling or skipped later bits, though exact live wire voltages remain unmeasured.
- `ERR`: in Test48 screenshots, the accumulated categorized clock + release timeouts (not host CRC or decoded-button errors). `xgo_diag_frames_failed` would also include timeout(s) while waiting for host LOAD that may not be received game frames, so do NOT casually call its value an incorrect-controller-frame percentage.

**Important numerical lower bound from source and photos:** Since only 117 Test48 CLOCK errors were HI, of 421 S12 classifications **at least 304** must be terminal FALL timeout classifications. In controlled Test49, of 226 S12 versus only 61 HI, **at least 165** must be terminal FALL timeouts. The limit is rigorous as an accounting argument, but DOES NOT tell whether XGO already received the first 12 bits correctly.

The terminal edge happens **after** transmission of slots 0–11 in the source. Failure at this boundary can leave an otherwise correct word at XGO while making the responder mark it failed and enter rearm. It can also signal true loss of clock phase or a missed edge. In addition, Test48 had 176 non-S12 CLOCK classifications, Test49 controlled 94, so **not everything can be dismissed as harmless terminal bookkeeping**. Even a perfectly formed host word may be labeled failed by the responder; conversely a host-decoded false slot0 LOW could happen while all CLOCK waits are apparently successful.

## 3. Which prior evidence is transferable to the CURRENT firmware

The protected, physically playable [transparent controller A](../candidates/offline-test44-transparent-controller/XGODriver.cpp) is **NOT Test48 or Test49**: its SHA-256 is `94ea7228c774a67e8252e7e09d94938530e5d74572d985332e6840ae09fe8b84` and its source blob is `cccb985a05baa8bb9078b6e336eb5f991c1a7a8f`. Its 12-slot timing pattern and **18us wait-clock budget** are retained, with serious earlier hotpath spinlock/flash issues removed. The source still:
1. Releases DATA, waits for the host LOAD LOW.
2. If physical R/slot0 is released, waits for DATA to rise (`wait_data(true,18us)`) before serializing later held buttons.
3. Emits slots 1–11 on CLOCK falling edges, waits for high between them.
4. Waits for the **terminal falling edge slot12**, releases DATA, then waits for final HIGH.
5. Treats any failure as `complete=false` and requires DATA HIGH before rearming on the next cycle.

This is a plausible shared path for early false JUMP and later missed/phase-corrupted held A/B, but not independently established without current Frankie signal capture. There is an additional diagnostic-instrumentation difference: if current A times out on **final HIGH**, source sets `complete=false` but does **NOT** increment `xgo_diag_clock_timeouts`; in Test48/Test49 the same final-HIGH failure **is** incremented and counted as slot12. Therefore **current and old `CLK` counters would not even be definitionally identical**. Current A has no user-visible equivalent diagnostic photo data. DO NOT project Test49's ~70% terminal share or any failure rate into A as though measured there.

GP2040 source case-fixing OLED-page-only B is still **CI-verified/unflashed**, changes display transfer scheduling, NOT serial responder, so it is not a validated cure for historical CLK/REL faults, unsolicited P2 jumps, or sustained A/B appearance.

## 4. Updated evidence-weighted direction

- **HIGH confidence:** Prior Test48/49 firmware struggled with host CLOCK/DATA wait synchronization (repeated actual RP2040 timeout classifications). The user's new external-P2 Contra gameplay with unsolicited JUMPs even without the Handle-as-P1 merge increases interest in serial transport.
- **Plausible but OPEN:** Some classes of CLOCK/REL timing error could create missing/incorrect host inputs or trigger responder rearm. R/slot0 false LOW may evade CLK counters entirely. Correlation to a specific ghost JUMP or seconds-spaced visual A/B effect is NOT established.
- **Not justified:** saying 70% of XGO frames were wrong, that every S12 indicates a bad button, that 1–2s is an RP2040 pulse period, or that all faults originate from OLED/frame corruption rather than a loaded per-ROM keymap/game behavior.
- **Engineering priority:** compare live physical Handle P2 DATA rise and XGO first-bit sampling; separate early/terminal CLOCK wait integrity; identify actual ROM P2 mapping before adding any input filters or game-aware behavior. Avoid speculative timeout extension or serial remapping because failures may be caused by late edges vs genuine missing edges and a larger timeout could introduce late-slot phase acceptance.
- Preserve protected GP2040 A, XGO Setup GOLD host BIOS SHA-256 `75f858b6d9a1eb81235ae9e9c9b449a6a3052ad4365e5411b8ce041075e99d6b`, Frankie V2 Jr and exact current OLED. No new hardware test was requested to write this retrospective.

**Evidence tags:** HW historical user captures/chronology and present gameplay observations; SRC Test48/Test49/current A C++ branches; MODEL strictly arithmetic/accounting; INF timing and symptoms; OPEN host-decoded actual bits, current electrical waveform and root cause.
