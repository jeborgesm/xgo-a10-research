# XGO ghost-input investigation — stock IRQ-gated scanner and host clock-stretch discriminator

**Date:** 2026-10-24 local. Branch: `research-gp2040ce-xgo-integration`. **Evidence:** original user XGO image [BIN], host RP2040 transparent `emit_frame()` [SRC], scripted virtual XGO host [MODEL], GitHub CI [CI], archived user OLED observations [HW]. **Current physical cause OPEN.** Protected XGO GOLD / controller A / Frankie V2 Jr unchanged. No firmware candidate or hardware test requested.

## Why revisit the host itself?

Earlier source-extracted tests showed that a complete missed *observed* clock pulse can shift slots and often cause the responder to report `last_failure_slot=12`, with no evidence that the XGO physically omitted the pulse. The earlier P0 passive capture showed exactly 12 pulses, each ~2us LOW and ~2us HIGH, every ~16.03ms **under its captured normal conditions**. But the original stock XGO scanner calls IRQ control helpers around each GPIO transition and before the earliest Handle R read. This detail was previously visible as unexplained `jal` instructions but had not been systematically verified to the actual CP0 Status handlers or differentiated from RP observation loss.

## 1. Original `bisrv.asd` — exact verified IRQ helper behavior [BIN]

Actual user archive: `XGoAnalisis.zip`, original `bios/bisrv.asd` SHA256 `869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf`. The read-only, hash-pinned [MIPS IRQ-window verifier](../tests/verify_xgo_irq_windows_original_bin.py) was executed on those exact bytes and **PASS**. Offsets below are original `.asd` file offsets, virtual MIPS address = file offset + `0x80000000`.

Scanner range `0x35D770..0x35DE04` contains **30 calls** to `0x802E0750` (disable helper), **30 calls** to `0x802E0778` (re-enable helper), and 13 calls to `0x8030FED0` (one load delay with immediate 4, and twelve clock LOW-phase delays with immediate 2).

The helper chain was decoded down to actual CPU status operations, **not assumed from function names**:

- `0x802E0750`: calls `0x80049DA4`, increments a nesting counter at `gp-0x64F0` (instruction `lw v0,-25840(gp)`).
- `0x80049DA4`: `mfc0 t0,Status`; inspect bits `0x06` (EXL/ERL); in the ordinary unexceptional path, mask Status IE bit0 via immediate `-2`, `mtc0 t0,Status`. If CPU exception flags indicate exceptional state, that path can skip the write.
- `0x802E0778`: decrement the same nesting counter. If result is still positive, leave interrupts disabled; otherwise call `0x80049DF4` and zero the nesting counter.
- `0x80049DF4`: `mfc0 t0,Status`, inspect `0x06` EXL/ERL bits; ordinary path sets Status IE `0x01` with `ori` and `mtc0 t0,Status`.

Thus the scanner is **not documented to keep interrupts masked over the entire 12-bit transaction**. It deliberately permits interrupts between short critical GPIO write regions **when global conditions allow**. An `enable` helper call is NOT proof an interrupt actually ran, and the counter may reflect nesting; record both facts.

Exact slot0 sequence:

```
35D844  release native B15 DATA output drive
35D848  IRQ-enable helper
35D850  IRQ-disable helper
35D864  release external Handle L0 DATA output drive
35D868  IRQ-enable helper
35D870  sample native B15 R bit
35D878  branch on native R HIGH (released), skips four instructions
35D890  sample external L0 R bit
35D8A8  IRQ-disable helper before next CLOCK phase
```

The previously verified P1 condition remains: built-in R HIGH/released takes **shorter** path to external R; built-in R LOW/pressed executes four more instructions and samples L0 later. The enable helper occurs after L0 release **before both first-bit reads**. Therefore the exact host release→R sample window is not guaranteed constant when interrupts can run. A runtime interrupt would generally **lengthen** the window, which could decrease rather than increase risk of an *early* false R caused solely by late DATA rise. This distinction prevents declaring IRQ latency the cause of Jump without measured samples.

Representative CLOCK LOW window (original MIPS):

```
35D8BC  GPIO CLOCK LOW store
35D8C0  IRQ-enable helper
35D8C8  nominal 2us delay helper
35D8D0  IRQ-disable helper
35D8E4  GPIO CLOCK HIGH store
35D8E8  IRQ-enable helper; sample DATA bit(s)
```

The next two clock-low windows have the same order. An interrupt, if taken during an enabled region, can **extend an electrical LOW or HIGH interval** beyond the nominal 2us or extend the interval before the next clock edge. An RP receiver with `EDGE_TIMEOUT_US=18` could time out even if no host pulse was missing. **Whether any live XGO interrupts last long enough is OPEN.** We have no IRQ timestamps or current Frankie CLK capture.

## 2. Exact C++ responder versus 24 synthetic clock-stretch scenarios [SRC+MODEL+CI]

Code: [`tests/test_xgo_irq_stretched_clock_exact_cpp.py`](../tests/test_xgo_irq_stretched_clock_exact_cpp.py). Uses the source-extraction guard from `test_responder_compiled_mock.py`, **compiles the unchanged protected `emit_frame()` function as real C++**, and substitutes only the simulated XGO host clock. Synthetic host generates all twelve clock positions; adds a **25us wait** within a selected CLOCK LOW or HIGH phase, continuing with the remainder of the waveform afterward. Earlier tests simulated pulses that *existed* but the RP input never saw; those are a **different** fault class.

- One normal scan.
- Twelve separate cases: XGO CPU "pause" adds 25 virtual microseconds in the LOW interval of each host pulse #1 through #12.
- Eleven separate cases: adds 25us HIGH gap after host pulse #1 through #11.
- The second host scan is normal, scheduled after a virtual 16,030us cadence; physical RP `published_mask` remains A held for both.

The first Actions execution [run #40160312569](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40160312569) was **GREEN** with all assertions. Afterward the test corrected an output label from "23" to "**24**" because there are 1+12+11 cases; no algorithm/expected-outcome change. CI is triggered again for that label-only commit. **All virtual times/lengths are constructed tests, not real measurements.**

### Classification results

| Injected virtual host condition | Protected RP status | Diagnostic location (slot numbering) | Subsequent clean scan |
|---|---|---|---|
| none | `complete=true` | none | held A correct |
| CLOCK #1..#11 LOW stretched +25us | `complete=false` | `xgo_diag_clock_timeouts=1`; `last_failure_slot=1..11` respectively | held A correct |
| CLOCK #12 LOW stretched +25us | `complete=false` | **0 CLOCK-error increments**; final HIGH timeout not classified | held A correct |
| HIGH after CLOCK #1..#11 stretched +25us | `complete=false` | `xgo_diag_clock_timeouts=1`; `last_failure_slot=2..12` respectively | held A correct |

**Diagnostic interpretation:**
- RP completely *missing an otherwise normal host clock pulse*: earlier exact-source model produced **terminal S12 timeout** even when the missed pulse was early.
- Host legitimately *holding CLK LOW beyond RP budget*: error is classified at the corresponding mid-slot HIGH wait (or final HIGH uncounted).
- Host legitimately *holding CLK HIGH too long before next FALL*: error is classified at the following slot's LOW wait, potentially S12 if preceding host pulse #11.
- These categories can produce some overlapping terminal outcomes; a single cumulative S12 counter does NOT identify actual analog fault origin.

The script does **not** reconstruct the first host's button word after a host CPU interruption (host MMIO sampling deadlines shift); it asserts the next host word only, keeping the model's limitations explicit.

## 3. Revisit historical OLED diagnostics, cautiously

Old Test48 final [HW]: `ERR=628=CLK597+REL31`, `LO=480`, `HI=117`, `S12=421`. Controlled Test49 final: `CLK320`, `LO259`, `HI61`, `S12=226`.

These were **RP watchdog error classifications from older diagnostic source builds**, not current transparent A and not captures of XGO interrupt events. Their `LO` and `HI` counters represent failure while waiting for a CLOCK FALL or RISE, respectively. Under the current conditional model, a HOST **long HIGH** can produce LO timeout and a HOST **long LOW** can produce HI timeout. A missed *observed* pulse can also cause a late terminal LO timeout, and older diagnostic code counted final HIGH failures as clock errors unlike current A. Thus **no valid attribution or fraction of old errors to host IRQs** is possible from those counters.

This does not supersede the separate, more direct **electrical first-bit R false LOW** hypothesis: passive P3 native USB PHY attached with TX disabled still made the user's physical XGO issue unsolicited P2 Jump, and an instrument probe on GREEN P2 DATA also produced jumping. Real clock interruptions would tend to alter sample timing rather than fabricate an early LOW by themselves.

## 4. Safe engineering next step and preservation

The offline evidence supports a broader hypothesis set: (a) delayed DATA recovery/receiver loading may cause ghost R even on an error-free clock; (b) RP PHY input observation can miss a real host edge; (c) **the XGO host might stretch a real CLOCK phase** through IRQ processing. Hypothesis (c) is now original-BIN-compatible and exactly source-modeled, but **not measured on current hardware**.

Do not "fix" this by arbitrarily increasing 18us EDGE_TIMEOUT: doing so could permit late acceptance of a wrong slot and longer stall in IRQ-disabled RP scan; strict clock-phase Test35 was already hardware REJECTED. Do not change XGO GOLD IRQ logic; it may guard critical interactions and firmware image modifications carry separate integrity risk. No RP game-specific turbo, pulse synthesis, input masking, or unauthorized Frankie rewiring. Only a future actual DATA/CLOCK electrical capture could discriminate physical jitter/bias; no new device test requested as part of this offline investigation.

**Protected:** XGO GOLD `bios/bisrv.asd` SHA-256 `75f858b6d9a1eb81235ae9e9c9b449a6a3052ad4365e5411b8ce041075e99d6b`; transparent GP2040 A UF2 SHA-256 `94ea7228c774a67e8252e7e09d94938530e5d74572d985332e6840ae09fe8b84`; its source Git blob `cccb985a05baa8bb9078b6e336eb5f991c1a7a8f`. Optional paged-OLED B remains unflashed.

## Reproducible provenance

- [Stock XGO MIPS interrupt-helper and scan verification](../tests/verify_xgo_irq_windows_original_bin.py) — **ran locally** on original user ZIP (not available in Actions).
- [Source-extracted virtual host-clock stretching test](../tests/test_xgo_irq_stretched_clock_exact_cpp.py) — **ran in CI** with earlier 23→24 output-label fix noted above.
- [Earlier loss-of-clock and next-frame recovery test](../tests/test_exact_xgo_rearm_two_frames.py).
- [P0 physical DATA/CLOCK captures](../../../experiments/rp2040-passive-probe-p0.md).
- [Test48/Test49 timeout counter retrospective](2026-10-24-OLED-ERROR-COUNTERS-RETROSPECTIVE.md).
