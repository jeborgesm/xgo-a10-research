# Ghost-input investigation: missed CLOCK positions, reported slot12 errors and next-frame recovery

**Date:** 2026-10-24. **Source:** exact protected transparent GP2040-CE `emit_frame()` C++ body [SRC]. **Verification:** compiled host mock in GitHub CI [MODEL+CI]. **User evidence:** prior Test48/Test49 OLED and new Contra P1/P2 reports [HW]. **Electrical correlation:** OPEN. **Firmware edits:** NONE.

## Scope and evidence discipline

User requests continuation of GP2040-CE XGO external Handle ghost-input research. Existing successful transparent-controller firmware A must remain untouched: UF2 SHA-256 `94ea7228c774a67e8252e7e09d94938530e5d74572d985332e6840ae09fe8b84`, source Git blob `cccb985a05baa8bb9078b6e336eb5f991c1a7a8f`. Host XGO GOLD setup/Handle firmware likewise untouched: `bios/bisrv.asd` SHA-256 `75f858b6d9a1eb81235ae9e9c9b449a6a3052ad4365e5411b8ce041075e99d6b`.

A new [source-extracted deterministic chronological two-host-scan test](../tests/test_exact_xgo_rearm_two_frames.py) is wired into [fast offline CI](../../../.github/workflows/gp2040ce-xgo-fast-serial-offline.yml). It extracts exactly the C++ `emit_frame()` body via the preexisting `test_responder_compiled_mock.py:extract()` guard, compiles with g++ and independently simulates two XGO scans separated by **16,030 virtual microseconds**. During one scan, the host generates the regular twelve-clock waveform; injected faults affect either RP's ability to *observe* one CLOCK pulse or its observation of the trailing HIGH edge. The user is NOT asked for hardware tests.

### Verified runs

- [Two-frame initial CI #40129886422](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40129886422) **PASS** after correcting an unused fake-host fixture declaration (first fixture-only compilation failed; no production defect or firmware change).
- [Expanded per-CLOCK-position CI #40129993336](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40129993336) **PASS**, git revision `2dc11e8eb6457369d24fa15cadf80ea5593d2268`. This is the canonical regression.

**Validity boundary:** The model provides *ideal 16.03ms frame cadence*, no real noise, RP read cycle costs approximated, and sampled host bits computed from virtual source-driven DATA changes. It deliberately suppresses one RP2040-observed clock while leaving host clock operation intact. It does **not** measure whether Frankie V2 Jr physically suppresses CLOCK, DATA rise time, real RP IRQ latency, live host bitword, or P1/P2 mapping. Therefore this is a *conditional failure-mechanism proof for the protected C++ control flow*, not a root cause closed by a logic analyzer.

## Source-grounded recovery branch

For actual GP2040 transparent A:
- `emit_frame` sets DATA output to Hi-Z, may call `wait_data(true,20000us)` if the previous attempted transaction failed, and then waits for `wait_data(false,20000us)` to acquire XGO host LOAD.
- For R/slot0 released, `wait_data(true,18us)` must complete before clock tracking begins.
- Every slot1–11: `wait_clock(false,18us)`, change DATA sink according to the stored physical mask, `wait_clock(true,18us)`.
- After 11 slots, it waits terminal FALL (slot12), releases DATA, then waits for final HIGH.
- If `complete=false`, `require_idle_high=true` on next invocation and the RP waits for DATA to be HIGH before accepting another LOW.

**Counter nuance:** An absent intermediate/terminal FALL increments `xgo_diag_clock_timeouts`, but a **failed final HIGH** sets `complete=false` WITHOUT incrementing that same CLOCK counter in protected A. It does increment `xgo_diag_active_failures` and `xgo_diag_frames_failed` at the caller. Older Test48/Test49 versions counted final-HIGH as CLK slot12. Thus the currently protected source has a **diagnostic classification gap**; absence of CLK error does not mean no frame completion/rearm failure.

## Exact C++ versus fabricated host: results

In every scenario, GP2040's published physical state is **A held continuously** (physical serial slot4, XGO raw `0x0080`), with physical R unpressed. Scenario0 has no injected PHY observation errors. In cases 1–11 the host still emits the pulse, but RP2040's fake `clock_level()` observation **misses one particular pulse**, then continues with normal observations of the others. The XGO's own sampling is based on *its* full clock train and the virtual responder's DATA changes.

| Artificial RP missed CLK pulse | First host raw word | First `emit_frame()` result | Reported last failure | Next host scan |
|---|---|---|---|---|
| None | `0x0080` = A | success | none | correct A |
| 1–4 | `0x0040` = B instead of A | failure | slot12 | correct A |
| 5 | `0x00C0` = A+B | failure | slot12 | correct A |
| 6–11 | `0x0080` = correct A | failure | slot12 | correct A |
| Final CLOCK HIGH only | `0x0080` = correct A | failure | **no CLK counter increment** | correct A |

All 13 modeled modes (normal + 11 individually hidden clock pulses + false terminal HIGH) passed source-based C++ assertions under [CI #40129993336](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40129993336). Each mid-frame missed pulse yielded a *single* `xgo_diag_clock_timeouts=1` and `xgo_diag_last_failure_slot=12`, even when the physical missed pulse was #1. All failing first scans set `xgo_diag_active_failures=1` and **next scan decoded correctly**.

### Two evidence upgrades

1. **S12 error position alone does NOT locate the original physical error.** In a receiver that waits on *levels* with no frame-start slot counter independent from the host, missing any observed clock can shift all subsequent slot assignments and be detected only when no thirteenth pulse arrives. Earlier OLED Test48/Test49 had S12 dominating classified CLK errors. That historic concentration is consistent with multiple mechanisms: missed earlier pulses, missed true terminal FALL, and old firmware counting missed final HIGH as S12. There is no way to partition these with cumulative counters alone. **Do not infer that 421 Test48 S12 means 421 errors physically happened at pulse #12.**
2. **One isolated failure is not enough to explain persistent inter-frame unreliability in the ideal host model.** The failed frame cleanly rearmed on the next host LOAD for all twelve injected faults. Thus an observed irregular held input over seconds would need recurring source/noise/timing failures, game-state/port/keymap interpretation, or an unmodeled departure from the reliable host idle-high gap. Neither repetitive real faults nor exact 1–2-second error periodicity has been measured. **Do not patch or delete `require_idle_high` based solely on the historical errors.**

## Relation to phantom JUMP

The new rearm sweep uses a **clean initial DATA turnaround** (released R reads as unpressed); it independently tests mid-frame faults. It **does not reproduce the user's phantom R** in this sweep. The immediately preceding exact-C++ [first-bit DATA recovery model](2026-10-24-EXACT-CPP-RESPONDER-CHRONOLOGICAL-HOST-DIFFERENTIAL.md) separately demonstrated how a late DATA rise could create *false R* while returning a successful CLK status. Both classes can be related by physical line/PHY effects, but this sweep does not prove a common root cause.

Potential relationship to actual Contra: physical A is under the embedded FC fallback jump button; a missed early CLOCK could make physical A appear to be B/fire (or add B). The user's actual per-ROM `.kmp` is UNKNOWN, so this hypothetical action identity is not hardware-proven. The observed spontaneous Jump while the external pad is connected but untouched still requires first-slot false bit, other physical glitch, upstream processed button, or other decoder behavior. The simultaneous problem must not be explained by a shift model alone.

The earlier Test35 strict `if (!clock_level())` guard was [HW REJECTED](test35-hardware-rejected-clock-phase-guard.md): severely choppy directions and missed taps. Do not reintroduce strict phase policing as an untested fix.

## Decision

Retain controller firmware A unchanged, keep XGO GOLD native Setup firmware unchanged, and keep optional OLED-paged candidate B unflashed. Next offline discriminators: broaden timing model to distinguish LOAD re-acquisition from an in-progress pressed DATA slot after a failure, and inspect actual RP2040 USB-PHY direct-path receive/override behavior versus available prior P0/P3 passive electrical evidence. A subsequent physical test would only be worthwhile if it provides a discriminator not already covered by these source-only models. No hardware trial or speculative fix requested here.

**HW/BIN/SRC/MODEL/OPEN:** All fault injections above are MODEL; the function tested and its counter branches are SRC; prior OLED counts and Contra symptoms are HW; original stock XGO 12-clock program is BIN; actual current wire behavior remains OPEN.
