# Contra unsolicited JUMP — offline causal discrimination after Test44 coherent SPSC

**Date:** 2026-10-24  
**Branch:** `research-gp2040ce-xgo-integration`  
**Status:** `OPEN` for JUMP root cause; X/Y held-level transport is a distinct source-corrected issue.

## Current hardware evidence (HW)

1. **P0 passive loose-wire capture:** GREEN/DATA load LOW was observed for 7.8µs, with a GREEN rising edge at 13674.3µs and first YELLOW/CLOCK falling edge at 13675.5µs, just **1.2µs apart**. The no-pressed-controller reference maintained GREEN HIGH for the entire 12-clock burst. This is actual digital capture, not an analog threshold/rise-time measurement. Source: `experiments/rp2040-passive-probe-p0.md`.
2. **P3 passive USB-PHY probe:** when a Pico was attached through an ordinary native USB cable, the XGO sometimes made Player 2 JUMP **even though the Pico did not run an active serial transmitter**. Its `tools/rp2040-xgo-p3-usbphy/main.c` explicitly disables TX output-enable and has no `data_sink()`. This observation predates GP2040-CE attack queues. Source: `experiments/rp2040-usbphy-p3-passive.md`.
3. **Test49:** While holding RIGHT and repeatedly tapping FIRE in Contra, unsolicited JUMP and PAUSE occurred, although recorded processed rising-edge counters for R/P0 through A/P4 were zero in displayed snapshots. These counters represent processed rising edges, **not** the exact host-received 12-bit DATA word; absence of a processed edge does not prove host received a clean released bit. Source: Test49 hardware diagnostic observation and repository handoff.
4. **Coherent SPSC hardware trial on 2026-10-24:** Street Fighter controls seemed responsive, yet Contra still had sporadic unintended JUMP. Thus eliminating the two flash/spinlock calls and the concurrent partial-chord publication issue did **not** cure the physical symptom. Holding X/Y also failed native turbo because that firmware emitted only 18ms one-shot pulses.

**Cabling limitation:** P3 used an ordinary cable, while the active GP2040-CE unit uses the *Frankie V2 Jr* working cable with its unusual physically shared pads 2 and 4. The passive and active hardware configurations are not electrically identical. Do not infer they have the same analog loading or failure cause merely because both jumped.

## Firmware and source evidence (SRC/BIN)

- The P3 passive initializer and current active GP2040-CE responder use the **same ten `USB_USBPHY_DIRECT_OVERRIDE_*` flags**, identical main/sie zeroing and `TO_PHY | SOFTCON` mux setup. The P3 source clears both DATA/CLOCK TX OEs and never sinks DATA. The active responder sinks only LOW, otherwise releases to Hi-Z; it never actively drives DATA HIGH. Verified source-equivalence guard `tests/test_passive_phy_jump_baseline.py`, [fast CI 40067871264](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40067871264), **PASS**. Static register equality is not equality of cable impedance or board voltage behavior.
- The earlier shared atomic helper spinlock-13 hazard is real and was eliminated in the linked SPSC ELF. The coherent SPSC hardware failure therefore excludes that hazard as a *sufficient* explanation for all observed unsolicited jumps. It does not eliminate electrical timing, phase/skipped-clock events, host scanner behavior, or a different RP2040 bug.
- The new minimal X/Y hold correction `candidates/offline-test44-spsc-xy-native-turbo-hold/XGODriver.cpp` merely forwards physical wire bits X/2 and Y/1 continuously while held and excludes them from one-shot 18ms attack pulses. [ARM ELF verification 40066165034](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40066165034) **PASS**: `emit_frame()` in SRAM at `0x200000f0`, 1048 bytes, zero linked external calls while interrupts masked. This corrects native turbo semantics but does not claim to fix JUMP.

## Three possible physical jump inputs (SRC)

The XGO **embedded NES default map** (used only if no matching per-game `.kmp` override loaded) maps:

| Physical bit / wire serial slot | FC action under stock fallback |
|---|---|
| R / 0 | NES A / JUMP, turbo |
| X / 2 | NES A / JUMP, turbo |
| A / 4 | NES A / JUMP, normal |
| Y / 1 | NES B / SHOOT, turbo |
| L / 3 | NES B / SHOOT, turbo |
| B / 5 | NES B / SHOOT, normal |

These conclusions come from `findings/embedded-default-keymap-patch-points.md` and `findings/keymap-runtime-behavior.md`. Do **not** interpret a visual jump as an unambiguous false R/slot0. An unverified per-game `.kmp` can alter every mapping in this table.

## Timing hypotheses and their falsifiable predictions (MODEL/INF, not HW)

**H1: simple monotonic DATA-low settling tail after host LOAD-low.** With a continuously decaying/recovering LOW whose final HIGH crossing is delayed, false pressed bits must form a **prefix** of the serialized word: R0 alone, R0+Y1, R0+Y1+X2, etc. A tail that reaches X/slot2 must also contaminate earlier R0 and Y1; it cannot create an *isolated* false X2. The modeled host's assumed sample positions are 0.1µs, 3.3µs and 7.3µs after LOAD release for slots 0,1,2. These are **not** measured XGO exact sample timestamps. `tests/test_nes_jump_origins.py` and `tests/test_responder_free_running_clock.py` now assert this prefix implication. [fast CI 40067763322](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40067763322) PASS.

**H2: later DATA glitch, edge misalignment or wrong output phase.** A non-prefix erroneous bit—such as X2 without R0/Y1—would need a different timing/electrical mechanism than H1. Existing synthetic late-FIRE examples also show an unintended START/pause bit after phase loss, but **neither** a real X2 glitch nor a live bit shift has been measured.

**H3: GP2040-CE processed input/mapping state.** A physical state or gamepad mapping fault could publish jump bits despite no user's explicit R/X/A press. Test49's sampled P0-P4 processed-edge snapshots did not establish such a fault, but counters are insufficient to rule out transient/held masks at every host poll. P3 passive JUMP also cannot be caused by the SPSC queue, so any comprehensive diagnosis must allow a separate, earlier electrical mechanism.

**H4: host-side game mapping rather than transport.** A .kmp override or game-specific interpretation could make a different physical bit trigger JUMP. Do not assume the embedded defaults match the exact ROM until its actual per-game .kmp and filename have been inspected.

## Next discriminators (not yet requested of the user)

- *First offline:* continue comparing P0 hardware digital traces, P3 passive state, and original XGO host scanner's actual sampling instructions. Avoid synthesizing a measured analog rise curve; no such connected-controller waveform exists in the evidence.
- *If and only if needed later:* one reversible per-ROM `.kmp` **software-only** mapping probe could assign distinct actions to R/X/A to reveal which wire bit is falsely asserted without modifying `bisrv.asd`; the **exact user's ROM filename and loaded override** must be verified first. No diagnostic .kmp was generated or installed here, and changing mappings could itself affect gameplay.
- Do not alter Frankie, add pull-ups, flash new GPIO diagnostics, or patch XGO console firmware based on a modeled electrical fault.

**Evidence policy:** HW P3 phantom JUMP is real but not proof of the current cable's root cause. ARM ELF success is real but not proof of no electrical glitch. The X/Y hold fix is SRC/BIN proven but still needs its own physical test. Contra unintended JUMP remains OPEN.
