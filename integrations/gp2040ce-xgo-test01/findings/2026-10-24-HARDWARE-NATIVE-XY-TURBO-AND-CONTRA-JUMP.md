# GP2040-CE XGO: X/Y native turbo hold and remaining Contra jump fault

**Date:** 2026-10-24  
**Branch:** `research-gp2040ce-xgo-integration`  
**Status:** new direct HW feedback; X/Y hold corrective source tested offline; phantom JUMP remains OPEN.

## 1. HW result from coherent Test44/SPSC single-trial UF2

The user installed the trial `XGO-Test44-Coherent-SPSC-HARDWARE-UNVERIFIED-TRIAL.uf2` produced by [build 40052163597](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40052163597), trial SHA-256 `79ebcff4f2bf5196ff986c68c1665eb315b9e7a6ef5d434d175741cab901abd6`, and reported:

- **Street Fighter:** controls seem responsive. This is a general subjective responsiveness observation, not a comprehensive attack/chord test.
- **Contra:** sporadic **unintended JUMP still happens**. Therefore the SRAM/spinlock and coherent-chord fixes did **not** eliminate the real symptom. The hardware acceptance test **FAILED**.
- **Holding physical X or Y:** fails to cause expected repeated shooting/jumping.
- User confirmed **the XGO native emulator/keymap itself produces those repeated actions when it sees a physical X or Y continuously held**; the RP2040 must *transmit a sustained held level*, not synthesize a turbo clock.

Do not promote the original coherent-SPSC trial as fixed. Retain original Test44 rollback. These are observed hardware results and user-confirmed desired semantics, not offline inferences.

## 2. Why the native X/Y turbo could not work (SRC, strong diagnosis)

The original protected Test44 driver and the trial both set `ATTACK_BITS = 0x003f`, covering all six wire attack slots:

```
slot 0 R   slot 1 Y   slot 2 X
slot 3 L   slot 4 A   slot 5 B
```

Core0 detects an attack **rising edge** and Core1 emits an **18ms bounded pulse**, deliberately dropping it thereafter even while physically held:

```cpp
const uint16_t attacks = snapshot & ATTACK_BITS;
const uint16_t mask = (physical & ~ATTACK_BITS) | attack_pulse_mask;
```

Thus even when Core0's physical snapshot continues to show X/Y pressed for hundreds of milliseconds, the wire mask goes released when the 18ms attack pulse expires. This directly prevents the host-native turbo generation.

The XGO stock embedded NES default table independently corroborates intent: physical X maps to NES A with turbo flag (`0x00010008`), Y maps to NES B with turbo (`0x00010000`). Evidence: `findings/embedded-default-keymap-patch-points.md` and `findings/keymap-runtime-behavior.md`. A per-game `.kmp` can override these defaults; this analysis assumes the embedded default when describing the logical output.

## 3. Isolated X/Y-level corrective candidate

Source: `candidates/offline-test44-spsc-xy-native-turbo-hold/XGODriver.cpp`.

The only functional differences from the previously ELF-verified coherent candidate (Git blob `9b23cd633635a400dcfb8257a9f874085857f9f5`) are:

1. Define `XGO_NATIVE_TURBO_HOLD_BITS = 0x0006` for physical Y slot1 and X slot2 and `ATTACK_PULSE_BITS = 0x0039` for R/L/A/B.
2. Core0 publishes edge queue generations for **R/L/A/B only**, not X/Y.
3. Core1's wire mask uses `(physical & ~ATTACK_PULSE_BITS) | attack_pulse_mask`, so physically held X/Y remain LOW continuously on the wire on **each XGO scan** until physical release.

**No RP2040 turbo timer.** XGO still determines turbo action cadence. R/L/A/B retain coherent SPSC generation handling and 18ms queued attack pulses. No serial bit order, GP2040 face mapping, clock timeout, USB PHY register initialization, pulse duration, OLED, LED shortcut, XGO firmware or Frankie change.

Regression `tests/test_xgo_native_xy_turbo.py` SHA-pins the exact ancestor and asserts only three substitutions, verifies stock NES turbo records, checks held Y/X/both through 128ms over repeated 16ms scans, immediate physical release, mixed held X/Y + one-shot B/FIRE, no invented R/START, no RP2040-generated oscillator. Existing extracted real-C++ `emit_frame()` and independently running simulated XGO CLOCK tests now also compile and test the candidate.

**Fast CI [40066164956](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40066164956): PASS.** Original compiled C++ serial tests passed 4096 masks and 22 abort/recovery pairs, and a new same-source repeated-frame test verified X/Y held across 18ms expiry and released instantly. Full Cortex-M0+ SRAM / masked-IRQ call graph comparison is handled by [workflow 40066165034](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40066165034): **do not call linked binary passed until CI finishes and logs inspected**. No flashed or bundled firmware for this follow-up yet.

## 4. Correcting the narrow R/slot0 interpretation of a jump

The physical wire bit for R is slot0, and earlier Contra fixed-R tests proved R reaches NES JUMP. **It is not the only input capable of jumping** under the stock NES fallback:

| Physical controller | Wire slot | Embedded FC action |
|---|---:|---|
| R | 0 | NES A/JUMP + turbo |
| X | 2 | NES A/JUMP + turbo |
| A | 4 | NES A/JUMP |
| Y | 1 | NES B/SHOOT + turbo |
| L | 3 | NES B/SHOOT + turbo |
| B | 5 | NES B/SHOOT |

Therefore Test49's *no processed R/P0 edge* does not identify which erroneous wire bit reached the XGO. No processed X/P2 or A/P4 edge was recorded either, but XGO could still have sampled a false LOW wire bit.

`tests/test_nes_jump_origins.py` verifies these physical-to-keymap assignments against the embedded-default evidence and exhibits a **hypothetical** DATA-high settling failure that also contaminates slot2 X. This requires a much longer modeled settling delay (~7.3µs from LOAD release under the virtual host's sample phases) than the R slot0 synthetic test (~0.1µs), and does **not** establish that such an electrical delay occurred on Frankie/XGO. A clock-phase error or native emulator/keymap state remains another possibility.

**OPEN:** exact physical cause of the sporadic jump, host-received raw 12-bit word, potential per-ROM `.kmp` overrides, and measured GPIO rise time. Avoid asserting the spinlock fix or X/Y correction solves jump. Do not modify `bios/bisrv.asd`, add hardware probes, alter Frankie wiring or take random new flashes.

## 5. Next decision

Wait for exact linked Cortex-M0+ audit of the minimal X/Y-held change, then prepare a single new physical trial only if it can be justified as validating a distinct proven controller semantic correction. Its success criterion must separately check **continuous native X/Y turbo**, **no unexpected jump during RIGHT+FIRE**, and intentional button mapping. Any remaining phantom jump is still a failed acceptance, even if X/Y turbo improves.
