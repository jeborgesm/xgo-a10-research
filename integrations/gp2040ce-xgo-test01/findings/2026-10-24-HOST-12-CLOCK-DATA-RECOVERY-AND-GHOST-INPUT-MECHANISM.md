# XGO ghost inputs — original 12-clock MIPS scanner versus transparent RP2040 DATA-high gate

**Date 2026-10-24; status [BIN original XGO] + [SRC GP2040] + [MODEL physically unmeasured] + [HW prior symptoms].** Research branch `research-gp2040ce-xgo-integration`. No new candidate firmware, no XGO BIOS write, no new hardware experiment. Protect the user-approved XGO GOLD host `bisrv.asd` SHA-256 `75f858b6d9a1eb81235ae9e9c9b449a6a3052ad4365e5411b8ce041075e99d6b` and transparent controller A UF2 SHA-256 `94ea7228c774a67e8252e7e09d94938530e5d74572d985332e6840ae09fe8b84`. Paged OLED B SHA-256 `5dcc28132ca54293a3d27dc2a452269bc47a1e7f141bd49c2c7e296918071b5b` remains unflashed.

## 1. Specific problem and controlling real HW

Recent actual user observations:
- GP2040 transparent physical holds/taps generally work and native X/Y turbo works; SFII played successfully, but occasional held LP weirdness/missed presses.
- Contra emits unsolicited JUMP. When XGO GOLD Setup `Handle=P1` is selected, the user can play using **built-in P1** while the connected but untouched external pad sometimes still contributes ghost jumps.
- External GP2040 as logical P2 is *worse*: unsolicited P2 Contra JUMPs, and held physical A/B produces visible jump/shoot at perceived intervals around 1–2 seconds, not continuous as expected. That interval describes **game behavior**, not a measured waveform or published-button period.
- Earlier Test48/49 diagnostic OLED firmware recorded many CLOCK/REL timeouts in sessions with unintended Contra JUMP and PAUSE; older source had 18ms synthetic attack pulse features absent from now-protected transparent A, so do not conflate firmware behavior.
- SF900 controllers work well on the user's separate SF2000, but **user confirms XGO has no wireless capability**. SF900 RF is a lineage comparator, not the actual transport.

The current question is: **can a missed clock caused by late host-driven DATA rise produce both a false early button AND loss/mapping corruption for held A/B?** A new source-derived phase model says **yes, under a narrow assumed timing condition**, without requiring GP2040 to publish a false physical press.

## 2. Original XGO firmware: exact clock sequence [BIN, verified on user ZIP]

The original `/mnt/data/XGoAnalisis.zip/bios/bisrv.asd` SHA-256 is `869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf`. The new [hash+opcode verifier](../tests/verify_original_xgo_12_clock_train.py) was run against those actual bytes and PASSed.

Original MIPS scanner `0x8035D770..0x8035DE10`:
- The host controls both data lines B15 physical built-in P1 and L0 physical Handle P2. The host forces LOW, invokes `jal 0x8030FED0` with immediate `4` at file `0x35D824`, returns both lines to input, then samples first bit R at `0x8035D870` (P1) and `0x8035D890` (external physical P2). **There is no separately identified 4us post-release settle delay.**
- It emits **exactly TWELVE distinct B7 shared CLOCK LOW→HIGH sequences**; each LOW is followed by `jal 0x8030FED0` with argument `2`. Delay-call addresses (ASD file offsets):

```
35D8C8 35D940 35D9B8 35DA30 35DAA8 35DB20
35DB98 35DC10 35DC84 35DCF8 35DD6C 35DDE0
```

- Both LOW and HIGH stores use MMIO `0xB8800354` via `s2`; the verifier checks 24 distinct stores bracket each delay. The scanner reads 12 positions `R,Y,X,L,A,B,SELECT,START,UP,DOWN,LEFT,RIGHT`. After 12th CLOCK LOW/HIGH the host calls its input-state helper and branches back to normalization.
- **Reject a missing-12th-clock-in-stock-firmware explanation**: the original firmware issues the 12th pulse. Whether a real RP2040 receiver *detects* all 12 short pulses is a separate electrical/runtime question.
- The previously BIN-verified P1 R-high/P1 R-low control branch changes the absolute instruction delay before L0/P2 slot0 read. That applies even in logical Handle=P1 mode, since physical sampling remains on L0. Exact time difference NOT measured.

**Source-limit:** MIPS delay arguments and ordering are proven from firmware; precise live analog edge widths/jitter were separately probed only under historical P0 and not on the latest Frankie V2 Jr.

## 3. Why responder acquisition is vulnerable to phase misalignment [SRC]

The protected transparent RP2040 `candidates/offline-test44-transparent-controller/XGODriver.cpp` publishes exactly the processed physical 12-bit mask, without synthesized attack pulses. Core1:
1. Calls `data_release()` and `wait_data(false,20000us)` to find XGO host LOAD LOW.
2. Loads stable `published_mask`, blocks interrupts through the active scan.
3. If R0 **pressed**, pre-drives LOW after an estimated 3us interval; if R0 **released** (typical A/B gameplay), calls `wait_data(true,18us)` **BEFORE** waiting for the first CLOCK FALL.
4. For slots 1..11 waits CLOCK LOW, asserts/releases DATA according to that slot, waits CLOCK HIGH.
5. Expects another terminal CLOCK FALL (clock #12), releases DATA, checks final HIGH; on failure `complete=false` and `require_idle_high=true` before next frame.

The input sampling counter can record an error for skipped edges. But the P2 **host** samples the external DATA electrical signal independently; a false LOW read for R0 may happen *even when the RP has faithfully published mask R=0*. The GP2040 `xgo_diag_output` and even error counters do not reveal what XGO actually received.

### Three timing classes (not measured on latest cable)

- **A. Timely DATA HIGH before slot0 sample and before CLOCK fall:** RP follows CLOCK #1, all later buttons correctly indexed, XGO samples expected mask.
- **B. DATA HIGH after XGO's immediate R0 sample, but before CLOCK #1 is missed:** host falsely sees **R/slot0** LOW. RP still serializes slots1..11 correctly. This can produce a wrong Jump **without any CLOCK timeout**.
- **C. DATA remains LOW until after CLOCK #1 has already RISEN:** the RP cannot enter `wait_clock(false)` until HIGH was seen, so the first accepted falling edge is **CLOCK #2** (the wait is a *level* predicate and has no past-edge history). It transmits physical slot1 during host-clock slot2, physical slot4/A during host slot5/B, etc. At the end RP waits for a **13th** falling edge which XGO never sends and registers terminal clock error. The first R (and possibly Y) can simultaneously be sampled LOW from lingering host LOAD. A held physical bit can be **assigned to the wrong host button even though the GP2040's physical mask is stable throughout**, and its local timeout occurs too late to undo the already received bad inputs.

**Crucial nuance:** This is not evidence that 70% of previous S12 errors are this class C. Most S12 errors in Test48/49 may be terminal edge detection failures unrelated to initial phase loss. Source-level phase sensitivity simply offers a concrete explanation for *a subset* of possible cases.

## 4. Reproducible offline phase model (real physical masks, synthetic timestamps) [MODEL]

New local/committed [phase model](../tests/test_xgo_data_release_first_clock_phase.py) constructed from exact XGO button masks and exact responder **ordering**, under synthetic timestamps:
- first host CLOCK falling at virtual `+1.2us`, CLOCK LOW `2.0us`, period `4.0us`;
- XGO R sample at virtual `+0.10us`, later samples `+0.20us` after each RISE;
- DATA recovers high at assumed `0, 0.7, 2.1, 3.6us` after a conceptual host release;
- `+1.2us` is informed by historical P0 **observed DATA RISE→first CLOCK FALL** delta only, **NOT a measured real host-GPIO-direction-release→CLOCK delta**. The virtual time origin is freely chosen, so **all numerical threshold values are model parameters, not measured hardware timing**.

With physical **A held continuously**, physical R released, and no GP button switching during the frame, local execution:

```
Scenario                         RP first FALL  Host decoded raw   RP terminal-fall timeout
Healthy                          #1             0x0080 (A)        NO
Early false R                    #1             0x1080 (R+A)      NO
DATA still LOW into first CLK    #1             0x1080 (R+A)      NO
DATA only rises after CLK #1     #2             0x3040 (R+Y+B)    YES
```

All assertions passed locally. **This is a falsifiable mechanistic demonstration, NOT actual proof Frankie produces `0x3040` on any scan**. It shows that the same host-visible delayed recovery can create a ghost first-bit and shift a real held input without software injecting any press.

## 5. Model of a narrowly scoped change, including what it CANNOT cure [MODEL only]

A second [policy differential](../tests/test_xgo_clock_first_sync_hypothesis.py) compares current R-released behavior `wait_data(HIGH)`→`wait_clock(FALL)` with a hypothetical direct `wait_clock(FALL)` after confirmed host LOAD LOW.

In the synthetic **DATA HIGH at 3.6us** case:
- current DATA-high-gated code: `0x3040`, wrong held-button mapping, terminal-fall timeout;
- CLOCK-first hypothetical: `0x3080` (R+Y+A), **A remains correctly indexed**, terminal-fall timeout avoided **if the responder was armed before CLOCK #1**;
- false R and Y from the still-low physical DATA line **REMAIN** even in CLOCK-first.
- if RP Core1 only *starts* waiting for CLOCK after clock #1 has passed, both approaches lose phase.

The model tests PASS; **no source patch was installed, compiled as a firmware candidate, flashed, or authorized**. The differential establishes only that CLOCK-driven framing could mitigate one *class* of held-button corruption under this example. It does NOT solve ghost JUMP, prove electronics, or establish that DATA-first gating is unsafe under all host conditions. Immediate RX after LOAD may itself be vulnerable to false LOAD triggers or different edge timing. Do not silently adopt this model as a hardware fix.

## 6. Historical OLED ERROR evidence in correct context [HW/SRC]

See [photographed Test48/49 counter retrospective](2026-10-24-OLED-ERROR-COUNTERS-RETROSPECTIVE.md). Test48 final `ERR=628=CLK597+REL31`, `S12=421` of CLK597; Test49 controlled final `CLK=320`, `S12=226`. Most CLOCK timeouts were terminal-classified, but Test48 had **176** and controlled Test49 **94** nonterminal clock classifications, real evidence of imperfect mid-transaction clock observation in those *earlier* firmware versions. Historical Test49 phantom JUMP and PAUSE occurred while processed physical input edge counters for R0–A4 stayed zero. No diagnostic photograph captures the current transparent firmware's actual serial word or DATA voltage. The current transparent A's final-HIGH failure can be omitted from `CLK` even when `complete=false`, so **old and current error metrics differ**.

### Distinguish what each observation supports

| Observation | Demonstrated | Still unknown |
|---|---|---|
| XGO original 12 CLOCK pulses | [BIN] Exactly 12 intended 2us LOW phases | Actual timing variation across real connected wire |
| Test48/49 high CLK/REL counts | [HW] RP2040 code frequently timed out | Wrong-bit frequency at XGO under CURRENT transparent A |
| Test49 uncommanded JUMP/PAUSE with P0..P4 input edges 0 | [HW] Game action without those new physical edges in interval | Which wire slot was falsely read and when |
| P3 passive Pico connected caused P2 ghost Jump | [HW] Native USB-PHY connection can perturb P2 even without active DATA writes | Same fault on Frankie V2 Jr active controller |
| Contra external P2 worse and A/B actions irregular | [HW] Visible P2 gameplay and hold complaint | Serialized RP transmitted state every scan / loaded .kmp / game-native behavior |
| Slower XGO bit0 DATA recovery model | [MODEL] Can produce ghost R with no CLK timeout | Whether DATA really crosses threshold late |
| Missed first clock model | [MODEL] Can shift held-bit slots and create a terminal timeout | Whether such phase slips really happen |

## 7. Decision checkpoint

Maintain original investigative direction: **two related fault classes to isolate, not automatically one root cause**:
1. first R/slot0 false LOW (could occur with no timeout);
2. serial CLOCK phase loss, partial 12-bit corruption or unnecessary rearm (could affect sustained held buttons).

No changes to user-approved button transparency (no fabricated 18ms pulses, no turbo on RP, no per-game button masks), no GP2040 output-high/pullup hardware guesses, and no XGO GOLD firmware edits. The user had asked for continued *investigation*, not a forced new firmware release.

For future targeted forensic observation, useful discriminators are actual DATA recovery relative to XGO first sample, which CLOCK phase was lost, and exact per-ROM `.kmp`; avoid interpreting LED/OLED `ERR` as captured corrupted host bits. The next source-only option would be to evaluate CLOCK-first early arming on all 12-bit masks and missing-edge recoveries, keeping **slot0 R pressed** semantics untouched, before any compile/test candidate is justified. This is not a new user-facing test request.

## Provenance

- User original XGO firmware ZIP `XGoAnalisis.zip` and verified original `bios/bisrv.asd` hash above.
- `candidates/offline-test44-transparent-controller/XGODriver.cpp`, unchanged Git blob `cccb985a05baa8bb9078b6e336eb5f991c1a7a8f`.
- `tests/verify_original_xgo_12_clock_train.py` [BIN PASS on original ZIP].
- `tests/test_xgo_data_release_first_clock_phase.py` [MODEL PASS local].
- `tests/test_xgo_clock_first_sync_hypothesis.py` [MODEL PASS local with corresponding source model].
- [Older error-counter truth table](2026-10-24-OLED-ERROR-COUNTERS-RETROSPECTIVE.md), [Handle logical P1/P2 HW observations](2026-10-24-CORRECTION-HANDLE-P1-ACTUAL-TEST-CONFIGURATION.md).
