# XGO Archeology — authoritative new-chat handoff: CPS1 family stock-FBA pivot

Date: 2026-09-05
Active branch: `research-post-mapper-runtime`

## NEW-CHAT BOOTSTRAP RULE

When continuing XGO Archeology in a new/rolled-over chat:

1. Read this handoff from GitHub FIRST.
2. Treat GitHub branch history/findings as authoritative project state.
3. Conversation memory is supplementary only.
4. Do NOT reconstruct the CPS1 story from chat summaries.
5. Do NOT resume A68K per-ROM bisection unless family research produces a concrete mechanism requiring it.
6. Commit research/code/hardware results before advancing to the next experiment.

## Current project direction

We have deliberately pivoted from “replace stock CPS1 with an external core” to:

> **Family-wide stock-FBA comparative archaeology and optimization.**

Research target:
- XGO stock arcade/FBA
- SF2000 stock arcade/FBA
- GB300 v2 stock arcade/FBA
- other HC15xx-family firmware where useful

Goal:
identify proven vendor/family optimizations and determine whether XGO’s stock CPS1 implementation can be improved by understanding/transplanting:
- CPU backend choices
- CPS1 speed hacks
- frameskip/frame pacing
- audio timing/sample rate/synchronization
- scheduler/runtime integration
- later-family fixes
- driver/config differences

Do not assume an external emulator is superior. Family evidence indicates stock arcade is unusually optimized and difficult to beat.

## Why we pivoted

Hardware and family evidence now agree.

### XGO hardware

Stock XGO CPS1:
- functional
- generally best-performing baseline
- can become laggy

External FBA2012 / Musashi:
- corrected content handoff works
- SFII reaches CPS1 self-test
- stalls inside/under first `BurnDrvFrame()`

External MAME2000:
- boots and reaches gameplay
- controls repaired
- adaptive frameskip tested
- still slower than stock
- abandoned as primary replacement

External FBA2012 / native-MIPS A68K:
- intended as faster 68000 backend
- legacy register-context ABI defect found and repaired
- nevertheless stalls during second ROM-load pass before A68K CPU execution
- zero-I/O probes localized stall into first half of SFII 68000 program-ROM loading
- further ROM-by-ROM bisection is paused because it no longer serves the highest-value project goal

### Family research

SF2000 Multicore / sibling-family evidence indicates Arcade is the notable stock emulator without a clearly better multicore replacement. MAME2000 performance on related hardware is reported worse than stock FBA, matching our XGO hardware result.

Conclusion:
**study the stock family FBA implementation instead of blindly replacing it.**

Primary decision record:
`findings/family-wide-arcade-emulator-research-and-decision.md`

Commit:
`27146930334267e57e0baf5ad532239e33f1208a`

## External CPS1 progression preserved for reference

- Test08 — FBA2012 content path fixed; SFII reaches self-test.
- Test09 — input polling ruled out; FBA stalls in first frame.
- Test10 — MAME2000 boots/plays.
- Tests11-13 — MAME input/state/performance work; ultimately slower than stock.
- Test14 — FBA2012 native-MIPS A68K; Loading hang.
- Test15 — A68K legacy ABI repaired; Loading hang remains.
- Test16 — trace localized failure after `CpsInit()`, before `CpsRunInit()`; A68K had not executed.
- Test17 — deep `Cps1LoadRoms(1)` instrumentation; filesystem tracing itself proved invasive.
- Test18 — direct stock-FS trace also perturbed startup; filesystem tracing abandoned.
- Test19 — zero-I/O forced return after `Cps1LoadRoms(1)`; device remained on Loading.
- Test20 — immediate forced failure inside load pass produced Loading -> black -> freeze, calibrating visual reachability.
- Test21 — forced return after full 68000 program-ROM phase not reached.
- Test22 — forced return after first two SFII program-ROM pairs not reached; A68K path stall localized to first half of program-ROM phase.

Test22/decision-gate record:
`findings/hardware-test-22-first-half-program-rom-stall-and-decision-gate.md`

Commit:
`8027df53162320cc28a1a65d61fe6116e40017a7`

## Important earlier authoritative handoff

`findings/cps1-test17-authoritative-handoff.md`

This preserves the exact FBA -> MAME -> FBA+A68K progression and prevents accidental reinterpretation as stock fallback.

## Protected baseline / guardrails

Preserve unless an explicit experiment says otherwise:
- Mapper v19
- external NES work
- Snes9x2005 integration
- external-core runtime infrastructure
- stock CPS2 / IGS / Neo Geo fallthrough
- corrected CPS1 runtime/content-path discoveries

Do not casually replace the full SD package or shared firmware while testing one CPS1 variable.

## Current authoritative stock-FBA findings

Family-wide comparative archaeology has now established the following:

- ordinary CPS1/68000 stock execution strongly points to **C68K**, not A68K;
- the stock family conserves the vendor FBA audio configuration **22050 Hz / 367 samples**;
- XGO does not expose `fba-cpu-speed-adjust` through its stock environment callback;
- stock FBA installs a private `gfn_frameskip` hook;
- `frameskip(1)` sets the FBA draw buffer / `pBurnDraw` path to NULL while `retro_run()` and audio continue;
- `frameskip(0)` re-enables drawing and alternates between two stock frame buffers;
- this render-only skip mechanism is conserved in SF2000 08/03, SF2000 1.71, GB300 v2, and XGO;
- the earlier interpretation that `3528/2940` imposed a hard 44.1-kHz scheduler budget is superseded; stock FBA explicitly advertises and runs at 22050 Hz through the libretro/sound-driver boundary.

Most important scheduler result:

```text
SF2000 08/03  -> wall-time / ideal-frame-count scheduler
SF2000 1.71   -> same wall-time / ideal-frame-count scheduler
GB300 v2      -> same wall-time / ideal-frame-count scheduler
XGO           -> different incremental drift/debt scheduler
```

The siblings continuously anchor pacing to total elapsed wall time and can issue up to three catch-up frames, using the private FBA draw-skip hook during catch-up.

XGO instead uses incremental PAL/NTSC frame-period state (PAL 20 ms; NTSC 17/17/16 ms cadence), carries residual overrun debt, asserts frameskip only after sufficient lateness, and discards sufficiently large debt.

This is currently the **leading XGO-specific lag-recovery hypothesis** because the major FBA engine-side optimizations are otherwise conserved across the family.

Primary finding:

`findings/stock-fba-cpu-backend-and-frontend-timing-comparison.md`

Latest reconciliation commit:

`dc426946e27d5a636d4a5d790f9da5781630f3cc`

## Current hardware candidate — scheduler v1

Family research has now produced a concrete scheduler-only XGO candidate.

Primary record:

`findings/xgo-cps1-scheduler-v1-hardware-candidate.md`

Versioned implementation:

```text
tools/cps1/xgo_stock_scheduler_v1.S
tools/cps1/xgo_stock_scheduler_v1.ld
tools/cps1/patch_mapper_v19_stock_scheduler.py
tools/cps1/PATCH-SCHEDULER-V1.cmd
tools/cps1/README-SCHEDULER-V1.txt
```

Successful assembler/patcher identity audit:

```text
workflow run 33986173065
PATCHER_MACHINE_CODE=PASS
FIT=PASS

main helper:
  0x8035eee8..0x8035ef67
  0x80 bytes

early-wait island:
  0x8035f070..0x8035f07f
  0x10 bytes
```

The candidate:

- keeps stock FBA;
- keeps C68K;
- keeps 22050-Hz / 367-sample stock FBA audio;
- keeps the stock private FBA draw-skip hook;
- keeps XGO input/video/audio/menu/keymap behavior;
- changes only the frame pacing/catch-up policy.

The scheduler policy is derived from SF2000 08/03, SF2000 1.71 and GB300 v2:

```text
absolute wall-time anchor
ideal-frame-count comparison
bounded catch-up, max 3
existing gfn_frameskip used during catch-up
```

No new executable cave and no new BSS are required.

Scheduler state reuses three timing-owned XGO words:

```text
0x80c33a74  start_tick
0x80c2d12c  completed_frame_count
0x80c2d114  catchup_count
```

The user-facing patcher deliberately accepts only exact mapper-v19 firmware:

```text
SHA-256
466b336ee601f16314b73fbc66f0135a7090942157fce77c749391fbaa4189ab
```

It never modifies the input in place.

## Immediate next work — HARDWARE OBSERVATION

The static gate is now passed.

Do **not** resume A68K ROM bisection.

Next step is the first scheduler-v1 hardware observation.

Test order:

1. Build candidate from the currently hardware-confirmed mapper-v19 `bios/bisrv.asd`.
2. Verify normal boot/menu.
3. Verify Mapper still opens/saves/resumes.
4. Verify ordinary non-CPS1 behavior is unchanged enough to establish frontend stability.
5. Test the same CPS1 titles used for stock baseline, especially SFII and Cadillacs and Dinosaurs.
6. Observe whether transient slowdowns recover faster and whether catch-up appears as short render-drop bursts instead of prolonged slow-motion.
7. Record result in GitHub before changing any additional variable.

Reject candidate if there is any new:

- Loading stall;
- black-screen regression;
- mapper/menu failure;
- audio instability;
- compatibility loss;
- return-to-menu failure.

Rollback is the exact mapper-v19 `bios/bisrv.asd`.

The candidate does not touch SPI NOR and does not use `Firmware.upk`.
