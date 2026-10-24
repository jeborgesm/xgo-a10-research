# GP2040-CE / XGO — one-session hardware acceptance gate

## 2026-10-24 HARDWARE RESULT — FAILED, DO NOT PROMOTE

The user has now tested the coherent Test44/SPSC trial produced by GitHub Actions run 40052163597 (UF2 SHA-256 `79ebcff4f2bf5196ff986c68c1665eb315b9e7a6ef5d434d175741cab901abd6`). This procedure is no longer merely awaiting execution. **Contra's sporadic unintended jump persists**, despite apparently responsive Street Fighter controls. **Holding X/Y does not produce the host-native repeated shooting/jumping expected by the user**.

Source-level explanation for the missing native X/Y turbo: this specific firmware only sends an 18ms edge pulse for X/Y, even though XGO needs a continuous held level to generate turbo. This is fixed **offline only** in separate source `candidates/offline-test44-spsc-xy-native-turbo-hold/XGODriver.cpp`, not in the already-tested UF2.

The underlying phantom-JUMP root cause is still OPEN; fixing X/Y held semantics does not establish a jump fix. **Do not overwrite this result or label the tested firmware as approved.** See `findings/2026-10-24-HARDWARE-NATIVE-XY-TURBO-AND-CONTRA-JUMP.md` for evidence. Preserve original Test44 rollback and avoid additional flashing until the next controlled experiment is explicitly justified.

---


**Status:** PROCEDURE ONLY. Do not request or execute this hardware test until the coherent Test44-derived SPSC firmware compiles successfully and the linked ELF audit verifies SRAM placement with ZERO reachable FLASH/XIP calls while Core1 interrupts are masked.

**Protected baseline:** Test44 hardware-proven GP2040-CE, existing Frankie wiring, and unchanged XGO A10 console firmware. Keep the already-verified Test44 UF2 accessible for immediate restoration. Do not install a candidate over the only copy of the known-good file.

**Candidate:** `candidates/offline-test44-spsc-coherent-ram/XGODriver.cpp`, based on Test44 with SRAM serial hot path plus coherent SPSC attack-event transport. Retain the original Test44 OLED source and Test44 XGO diagnostics header. No clock timeout, slot mapping, 18ms attack pulse, input mode, USB PHY registers, start/menu or LED shortcut modification.

## Objective

One controlled firmware trial should answer the **specific hardware question** that offline compilation cannot: does eliminating flash/spinlock waits and partial-chord publication improve real RIGHT+FIRE stability without sacrificing intentional button presses?

Not a generic stress-testing session. No added logic-analyzer hardware, rewiring, or new on-device diagnostic counters.

## Single-session acceptance matrix

| Scenario | Inputs/action | Pass evidence | If it fails |
|---|---|---|---|
| Startup and frontend | Boot RP2040 candidate in existing XGO external-controller mode, open Contra | Normal menus, live controls, no lockup | Restore Test44; log failure point |
| Known phantom trigger | Hold RIGHT and tap FIRE repeatedly, matching the previous observed failing Contra bridge scenario | Every intended FIRE action recognized; **zero unintended JUMP and zero spontaneous PAUSE** | Record whether JUMP, PAUSE, or both were seen, and whether another button was held |
| Intentional first slot | Intentionally press and release mapped R/JUMP while otherwise neutral | Exactly one expected jump per deliberate press; no missed presses | Log first-press/short-tap symptom |
| Intentional system slot | Intentionally press START to pause, then press again to resume | Exactly one pause/resume per deliberate press | Log unsolicited versus missed START |
| Overlap/chords | Combine FIRE with one other intentional mapped attack button and release; repeat at normal speed | Both intended actions occur, no unexpected third action; no prolonged deferred response | Record the combination and whether only one was seen |
| Post-stress recovery | Resume normal directional control and fire after the burst | Responsive, no frozen menu, no stuck input | Restore Test44, retain observed symptom |

Treat very rapid button taps that do not intersect any processed Gamepad sample separately from reliable serial transmission: no downstream firmware can guarantee an event it never sampled. Avoid claiming electrical timing was measured; the test validates visible game behavior only.

## Evidence collection

Record only: candidate source commit and UF2 SHA-256; whether the six scenarios PASS/FAIL; for failures, the unexpected action and approximate circumstances. One screenshot/video only when it materially differentiates symptoms. Do not introduce another OLED-counter firmware before reviewing this result.

**Success criteria:** all rows PASS, no unsolicited jump/pause, no regression of responsiveness. **Rollback criteria:** any spontaneous JUMP, spontaneous PAUSE, repeated missed intentional presses, stuck input, menu freeze or boot regression; restore known-good Test44.

**Evidence discipline:** offline SRC/BIN/MODEL does not become HW until the user actually executes this single session. This procedure is not a booking, automation, flashing instruction, or a claim of hardware success.
