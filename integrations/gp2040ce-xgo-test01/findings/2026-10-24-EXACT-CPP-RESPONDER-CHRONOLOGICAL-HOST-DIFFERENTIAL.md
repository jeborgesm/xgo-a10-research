# Exact protected C++ responder in a timed XGO host model — late DATA and missed-first-clock fault split

**Research date:** 2026-10-24. **Status:** exact C++ source [SRC], synthetic deterministic host [MODEL], repo GitHub Actions [CI], existing device reports [HW]; **live electrical cause OPEN**. No user firmware changed, no GP2040 UF2 candidate, no XGO host patch, no new hardware test.

## Why this experiment supersedes the earlier pure Python scenario

The previous two scripts `test_xgo_data_release_first_clock_phase.py` and `test_xgo_clock_first_sync_hypothesis.py` correctly modeled one possible control-flow failure, but implemented a separate Python state machine. This experiment instead **extracts the actual `emit_frame()` C++ body** from the protected user-tested source, compiles it with g++ under synthetic `data_level()`, `clock_level()`, `time_us_32()`, `data_sink()`, and `data_release()` functions, and reconstructs each host slot from the chronological DATA line. We rely on `test_responder_compiled_mock.py:extract()` to enforce the exact protected source function rather than copying the responder into a model.

**Code:** [`tests/test_exact_xgo_frame_phase.py`](../tests/test_exact_xgo_frame_phase.py). CI `xgo-fast-serial` verified on 2026-10-24: [successful source-extracted phase run #40129301560](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40129301560), commit `d4a79db7fe59023eb11fb62c2886efbd54cf7cf8`. The original untouched `offline-test44-transparent-controller/XGODriver.cpp` Git blob remains `cccb985a05baa8bb9078b6e336eb5f991c1a7a8f`. The only alternative is a **transient C++ string replacement inside the test's temporary compiler input**; it never writes the source file.

## Fake host contract and why it is not a measurement

The test feeds the actual source body a fabricated host with:
- host DATA driven/recovering LOW until parameterized `data_rise`;
- a synthetic first CLOCK FALL at virtual `+1.2us`, 12 CLOCK lows, 2us LOW and 4us period;
- slot0 host sample at virtual `+0.1us` and slots1–11 sampled after their corresponding HIGH transition;
- source's level-sensitive `wait_data(HIGH)` and `wait_clock(LOW/HIGH)` loops run against this independent clock rather than pre-scripted results;
- actual source `data_sink()` and `data_release()` transitions timestamped and used to reconstruct the **host-visible** 12-bit word.

The virtual time origin and submicrosecond offsets are MODEL parameters, **not hardware measurements on the current Frankie V2 Jr**. Earlier P0 observed approximately 1.2us DATA-rise-to-first-clock-FALL, which is **not** the XGO host-GPIO-release-to-first-CLOCK time. The test **does not prove** its modeled recovery intervals are electrically reachable on this specimen. Timed mock compilation also does not measure actual RP2040 USB-PHY read latency or cable threshold.

The two compared code branches:
1. **Protected A:** physically released R/slot0 waits `wait_data(true,18us)` before its first `wait_clock(false)`. Actual compiled source, not edited.
2. **Hypothetical CLOCK-first:** the source fragment `complete = wait_data(true, EDGE_TIMEOUT_US); if(complete) data_release();` is replaced **only within a tempfile** by `complete=true; data_release();`, allowing the existing for-loop to begin tracking CLOCK #1 without waiting for DATA HIGH. All other source C++ is identical. No policy change to physically held R/slot0 or to published GP2040 12-bit state.

## Executed results [CI/MODEL]

Each source policy passed **all 4096 12-bit masks** under the model's normal timing. The late-recovery cases deliberately hold physical A continuously (RP wire slot4, XGO raw `0x0080`) with physical R released, and vary the *fabricated host DATA recovery*:

| Mock DATA-high (virtual us) | Protected A: host raw, status | CLOCK-first: host raw, status | Explanation |
|---|---|---|---|
| `0.0` | `0x0080`, OK | `0x0080`, OK | Physical A correctly transmitted |
| `0.3`, `0.7`, `2.1`, `3.0` | `0x1080`, OK | `0x1080`, OK | **False R + real A**, zero CLOCK timeout; XGO's early R sampling is contaminated |
| `3.6` | `0x3040`, failed terminal slot12 | `0x3080`, OK | Protected source **misses first CLOCK**, shifts real A into B/slot5; alternate maintains A's slot, **but false R+Y persist** |

One separately checked **held physical R plus held physical A** mask with virtual DATA recovery at `3.6us`: BOTH policies produce `0x3080` (R+Y+A) and no CLOCK timeout. The existing early-sink R-pressed source path bypasses DATA-high wait and therefore retains clock synchronization here, yet the *host itself* still sees a false Y while DATA remains LOW into its Y sample. This distinct prediction helps demonstrate two failure mechanisms: electrical first-slot/early-slot contamination independent of RP normalizer mask, plus a DATA-high gate capable of delaying subsequent serial framing.

**Interpretation:** This is source-grounded MODEL reproduction of potential consequences, **not direct proof that current physical R ghosts or A hold failures follow the same timing**. The absolute numbers `0.3us`/ `3.6us` were chosen to cross hypothetical sample/clock windows; do not propagate as measured jitter tolerances or a GP2040 timing specification.

## Relation to older OLED CLOCK/REL errors and user's P1/P2 observations

- Prior Test48: total ERR628 = CLK597 + REL31; Test49 *controlled*: CLK320, S12 226, with actual uncommanded JUMP and PAUSE. These counters were **earlier diagnostic firmware** with source/runtime differences; not 320 current A clock failures or 226 confirmed wrong game frames. S12 can be a terminal edge wait and cannot identify the missing *first* edge alone.
- Here, **ghost R with an apparently complete responder frame** demonstrates why CLOCK timeout counters alone cannot exclude first-bit corruption. The lost-first-clock model ends with S12 timeout **after a corrupted 12-bit word** even though one input button was genuinely held continuously.
- The **Handle=P1** GOLD normalizer ORs physical built-in P1 with Handle L0 into logical P1, so an untouched external controller can still propagate a false host-decoded Handle bit. **Handle=P2** sends the same physical L0 to logical P2 without OR; user says external Contra P2 is worse and irregular held A/B is visible. No P1 merge is needed for that P2 symptom. **No actual P2 mode electrical waveform is recorded**.
- The XGO original stock BIN reads physical R **before any CLOCK** and produces **12 CLOCK pulses**. The RP2040 has to detect rather than generate those pulses. Physically the first R decision depends on host GPIO release and line analog recovery, which the RP cannot repair just by choosing an alternate ordering of its later CLOCK waits.

## Engineering decision from the experiment

**Reject the simplistic claim that a CLOCK-first-only software patch fixes ghost jumping.** It can remove one modeled source of missed/shifted held bits and terminal errors, *but false R/Y remain exactly as in the protected code*. It also still depends on detecting the real LOAD and arming before CLOCK #1; neither condition was stress-tested over a broad clock waveform/jitter family, and source-level ideal cases are insufficient for hardware promotion.

Continue to treat two related but distinguishable faults:
1. **False first-bit R/early slots when XGO samples an electrically LOW DATA line after releasing its own load drive**: no RP clock error required.
2. **Missed first CLOCK or later phase mismatch** under released-R DATA-high wait: can alter held A/B mapping, generate subsequent timeout/rearm.

The specific next evidence would be live DATA rising versus XGO's immediate first-slot sampling and CLOCK first fall (not easily measurable from counters alone); for source-only work, expand tests to reset/LOAD edge and aborted-frame recovery across clock phase boundaries. Do not solve these symptoms by adding GP2040 auto pulses, changing per-game mapping, driving the console's DATA line HIGH against possible host drive, or altering the protected GOLD `bisrv.asd` without direct evidence.

**Protected statuses remain unchanged:**
- XGO GOLD native Handle/PAL BIOS SHA `75f858b6d9a1eb81235ae9e9c9b449a6a3052ad4365e5411b8ce041075e99d6b`.
- User-flashed transparent controller A UF2 SHA `94ea7228c774a67e8252e7e09d94938530e5d74572d985332e6840ae09fe8b84`.
- Optional paged OLED B UF2 SHA `5dcc28132ca54293a3d27dc2a452269bc47a1e7f141bd49c2c7e296918071b5b` remains **unflashed**, changes Core0 display only, cannot be credited for ghost repair.
