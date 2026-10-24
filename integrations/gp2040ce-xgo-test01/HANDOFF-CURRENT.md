# XGO A10 / GP2040-CE controller serial integration — CURRENT HANDOFF

**Updated 2026-10-24. Read the CURRENT ADDENDUM first, then the historical record.**

## 2026-10-24 VERIFIED X/Y HOLD SOURCE/BINARY, CONTRA PHANTOM JUMP STILL OPEN

**Current HW verdict (user's real testing):** The 2026-10-23 coherent SPSC hardware trial (UF2 SHA-256 `79ebcff4f2bf5196ff986c68c1665eb315b9e7a6ef5d434d175741cab901abd6`) **FAILED complete gameplay acceptance**: Street Fighter feels responsive but Contra still has sporadic unintended JUMP, and sustained X/Y input fails to cause stock XGO's expected native turbo actions.

**Critical corrected protocol interpretation:** Stock NES keymap maps physical X/slot2 to A+turbo (JUMP) and Y/slot1 to B+turbo (SHOOT); R/slot0 also maps A+turbo and physical A/slot4 maps normal A. Therefore unintended JUMP is NOT uniquely R/slot0. XGO provides turbo internally from the **held** physical X/Y bit. The RP2040 controller must NOT synthesize repeated pulses, and its inherited Test44/SPSC 18ms one-shot pulse on X/Y was a definite source-level error. Earlier no-held-repeat acceptance applies only to other button semantics; it does not override the new user-confirmed requirement for native X/Y turbo.

**New isolated X/Y correction:** `candidates/offline-test44-spsc-xy-native-turbo-hold/XGODriver.cpp`, SHA blob `dff1a7b344655e2614f371325a21767d11a455a2`, exact three substitutions from protected coherent SPSC candidate. X/Y (slots1/2, mask `0x0006`) directly reflect **physical held level** in every host frame; other R/L/A/B press events (mask `0x0039`) retain 18ms coherent SPSC pulses. No clock timeout, serial slots, OLED, XGO firmware, Frankie or embedded XGO turbo changes.

**FAST CI PASS:** [40066164956](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40066164956) included exact source diff, actual C++ 4096 masks, 22 abort/recoveries, repeated held-X/Y frames past 18ms, release timing, mixed X/Y+FIRE and free-running HOST model.
**FULL LINKED ARM CI PASS:** [40066165034](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40066165034) compiled in pinned Test44 GP2040-CE+Pico SDK. `emit_frame()` at SRAM `0x200000F0`, 1048 bytes, 290 statically reachable instructions from IRQ masking, **zero reachable calls while IRQ-masked, zero XIP**. Linked disassembly artifact ID 12549665877. Hardware still untested for THIS corrective version; no UF2 has been published.
**SOURCE/MODEL JUMP CORRECTION PASS:** [fast CI 40066648722](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40066648722), `tests/test_nes_jump_origins.py`, and patched free-running clock simulation show the stock NES mapping can visibly JUMP from R/slot0, X/slot2 or A/slot4. An **artificial 7.5us DATA-low settling tail** can create false X/slot2 in that model, but this timing has **NEVER been physically measured**; don't promote MODEL to HW cause.

**Authoritative detailed record:** `findings/2026-10-24-HARDWARE-NATIVE-XY-TURBO-AND-CONTRA-JUMP.md`, marked actual old trial HW-failed. Do not restart old X/Y edge-queue work, announce the prior hardware trial as successful, apply firmware to XGO/bisrv.asd, request Frankie rewiring, or send an unjustified chain of controller flashes. The user's Test44 rollback remains protected. The next physical trial requires an explicit reason and must still classify any phantom jump as FAIL.

---
## 2026-10-24 ACTUAL HARDWARE — PREVIOUS COHERENT SPSC TRIAL FAILED, X/Y TURBO SEMANTIC FOUND

**Newest user-supplied HW evidence, overriding the 2026-10-23 offline confidence:**
- The coherent Test44/SPSC UF2 SHA-256 `79ebcff4f2bf5196ff986c68c1665eb315b9e7a6ef5d434d175741cab901abd6` was hardware-tested. **Street Fighter felt responsive; Contra still had sporadic unintended JUMP.** Do NOT promote the old candidate as fixed.
- Sustained X or Y buttons **did not produce continuous shooting/jumping**. User clarified **XGO itself provides the turbo/repeat behavior when it sees X or Y continuously held**. The controller must send a held level on wire slots1/2, not generate its own turbo pulses.
- Original Test44 and coherent SPSC had `ATTACK_BITS=0x003f`, queuing X/Y with the other four through an 18ms one-shot pulse. That explains the missing X/Y held behavior at SRC level. Older Test44 "held no-repeat PASS" criteria were valid for those earlier Street Fighter attack semantics but are superseded for X/Y native XGO turbo.
- Default embedded NES `.kmp` fallback maps physical **R/slot0, X/slot2 and A/slot4** to NES A (jump), of which R/X are turbo. Physical **Y/slot1, L/slot3 and B/slot5** map NES B (shoot), of which Y/L are turbo. The previous statement "an unintended JUMP uniquely identifies R/slot0" is incorrect. Test49 P0/P4 processed-edge zeros do not exclude host receiving a false X/slot2. Per-ROM `.kmp` may override defaults; do not guess user-specific file content.
- Detailed HW/SRC/MODEL evidence: `findings/2026-10-24-HARDWARE-NATIVE-XY-TURBO-AND-CONTRA-JUMP.md`. New mapping test: `tests/test_nes_jump_origins.py`.

**New isolated controller-only candidate, NOT flashed:** `candidates/offline-test44-spsc-xy-native-turbo-hold/XGODriver.cpp`, ancestor exact coherent SPSC Git blob `9b23cd633635a400dcfb8257a9f874085857f9f5`; new candidate blob `dff1a7b344655e2614f371325a21767d11a455a2`. Only THREE substitutions: define X/Y held wire bits `0x0006`, narrow existing attack-edge queue to R/L/A/B `0x0039`, and compose outbound mask preserving the continuous physical X/Y levels. No XGO BIOS, ROM, turbo generator, Frankie, serial timing or button bit order changes.

**New fast CI VERIFIED PASS** [run 40066164956](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40066164956), source commit `5718eeb03b7e3413286400969aead02d73949980`: exact limited-source-diff and native NES turbo mapping checks; held X/Y through 128ms with immediate release; held X/Y plus 18ms B/FIRE pulse; actual compiled C++ `emit_frame()` 4096 masks/22 abort-recovery cases; repeated C++ frames with X/Y held past 18ms; independent free-running CLOCK simulations. No firmware hardware test.

**Full pinned ARM build/IRQ-window audit** [run 40066165034](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40066165034) **still running at this edit**. Must verify final status from CI before binary promotion; no new test UF2 has been bundled. The previous coherent candidate was ELF-proven but HW-failed. The X/Y hold fix addresses the second failure only; unintended Contra jump is STILL OPEN. In the meantime, protect Test44 UF2 rollback, XGO SD/BIOS, Frankie, previous observations, and do not conflate speculative DATA-line settling models with measured physical cause.

---


## 2026-10-23 COMPLETED — COHERENT TEST44 SPSC ELF GATE AND ONE HARDWARE-UNVERIFIED UF2

**This supersedes the earlier full ARM gate OPEN / packaging pending notes. DO NOT RESTART THE INVESTIGATION.**

**Full coherent ARM binary gate passed:** [GitHub Actions run 40034765464](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40034765464), commit `fa4377cc4c5b8ee901d3e5cb562094c6af1a2d3d`, **SUCCESS**. Actual linked `emit_frame()` resides at SRAM `0x200000F0`, **1048 bytes**; CFG traversal under Core1 masked interrupts found **zero reachable subroutine calls and zero XIP/flash calls**. The exact source `candidates/offline-test44-spsc-coherent-ram/XGODriver.cpp` is blob `9b23cd633635a400dcfb8257a9f874085857f9f5`; original hardware-proven Test44 source blob remains `f445a1a6d8f9c871a80532e25cc5b1a3ac3b32a0`. [Quick CI run 40034765433](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40034765433) **SUCCESS**, including actual extracted C++ 4096 button masks, 22 mid-frame abort/recoveries, free-running model and 130680 exhaustive sequential-consistency chord publication schedules; the previously identified 67426 partial-chord model snapshots are all rejected by the coherent commit marker.

**FINAL OFFLINE OUTPUT NOW PREPARED AND CHECKSUM-VERIFIED:** [controlled trial packaging build 40052163597](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40052163597), source commit `fe8a5e169e89c3986ea0650268eb0862a1217611`, **SUCCESS**. New packaging workflow `.github/workflows/gp2040ce-xgo-test44-coherent-trial-package.yml` rebuilds the exact protected source and pinned upstream after source blob checks, re-runs complete ELF/IRQ-window check, then creates ONE UF2 trial and uploads it **only after** the audit passes. Published artifact ID **12543324833**, `XGO-Test44-Coherent-SPSC-SINGLE-TRIAL-HARDWARE-UNVERIFIED`.

**Packaged UF2 details, verified by opening the ZIP and hashing the bytes locally:** filename `XGO-Test44-Coherent-SPSC-HARDWARE-UNVERIFIED-TRIAL.uf2`, size **2518528 bytes**, SHA-256 **`79ebcff4f2bf5196ff986c68c1665eb315b9e7a6ef5d434d175741cab901abd6`**. ZIP also contains `SHA256SUMS.txt`, `PROVENANCE.json`, `README-FIRST.txt`, and `HARDWARE-ACCEPTANCE.md`. UF2 magic verified. GitHub packaging and artifact download verified. The linked binary evidence remains available separately in artifacts from the CI runs. No XGO `bios/bisrv.asd`, XGO SD card, RP2040 hardware or Frankie wiring changed, and nothing was flashed. The *user* retains the physical Test44 baseline.

**Next action if user elects hardware test:** Only ONE controlled trial as described in `findings/COHERENT-SPSC-SINGLE-HARDWARE-ACCEPTANCE.md`: preserve the original known-working Test44 UF2 for immediate rollback, then check boot, Contra RIGHT+rapid FIRE (zero unintended JUMP/PAUSE), deliberate R/JUMP, deliberate START, deliberate dual-attack chord, and post-stress recovery. Do not ask for extra OLED screenshots or a chain of diagnostic firmware images. On any regression, restore Test44. A successful source/ELF test is **not** proof these physical gameplay symptoms are fixed. Do not claim root cause is demonstrated; actual early-slot DATA-level timing remains OPEN.

---
## 2026-10-23 NEWEST — CHORD-COHERENT TEST44 SPSC; FULL ARM GATE OPEN

**Protected baseline unchanged.** Test44 hardware-proven, Test49 diagnostic witness preserved, no controller/UFP/XGO console flash, Frankie unchanged. Do NOT request physical hardware testing at this point.

**First lean Test44/SPSC candidate fully verified offline:** `candidates/offline-test44-spsc-ram-playable/XGODriver.cpp` is exactly the earlier verified SPSC minus Test49-only diagnostics. Full pinned RP2040 [run 40033843466](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40033843466) **SUCCESS**: same original Test44 OLED/header, candidate `emit_frame()` SRAM address `0x200000F0`, 952 bytes, zero reachable BL/BLX calls while IRQ-masked, no UF2 distributed. Fast exact source/compiled C++ 4096-mask and fault simulations PASS [40033843426](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40033843426). Its remaining issue: six per-bit generation counters are published/read independently and may admit only part of a simultaneous attack chord if Core0 publishes while Core1 takes its snapshot.

**New concurrency proof and guarded correction:** `tests/test_spsc_chord_atomicity.py` enumerates **130,680** sequentially consistent producer/consumer schedules across **all 63 nonempty attack combinations**. Unguarded per-bit snapshot admits incomplete chords in **67,426 MODEL schedules**; the coherent variant admits **zero** incomplete chords. These numbers do NOT imply live hardware event rates. Source `candidates/offline-test44-spsc-coherent-ram/XGODriver.cpp` uses a Core0-owned odd/even `seq_cst` commit marker around all per-button generation updates, and Core1 uses before/after sequence loads to either accept the full stable batch or defer the entire batch to a subsequent host scan. No Core1 exchange/fetch-or, no serial mapping/18us timeout/18ms pulse changes. All source-guard and actual compiled host-C++ mask/abort/free-running timing regressions **PASS** [fast CI 40034765433](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40034765433).

**Current build gate:** [full coherent ARM ELF run 40034765464](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40034765464) rebuilds protected Test44 and coherent source in same pinned GP2040-CE checkout, and must establish SRAM function placement + zero reachable XIP under Core1 IRQ mask. **Status still IN PROGRESS at this note; do not assume pass.** An earlier run 40034701038 failed on the source guard mistakenly searching post-IRQ diagnostic atomic increments; guard now correctly checks only between Core1 `save_and_disable_interrupts()` and `restore_interrupts()`. This was not a firmware failure.

**Evidence:** `findings/ATOMIC-CRITICAL-WINDOW-AND-SPSC-2026-10-23.md` sections 7–8 distinguish SRC, BIN, MODEL, HW, OPEN and pin prior linked disassembly artifact. Actual live DATA threshold/jump and START/PAUSE root cause remain unproven. The +4.75us slot0 artificial delay is a simulator threshold, not observed CPU timing. No new equipment, firmware distribution or new hardware session.

---
## 2026-10-23 LATEST — TEST44-DERIVED SPSC LEAN PLAYABLE CANDIDATE (OFFLINE)

**No hardware changed. Test44 remains the protected proven baseline, Test50 START provenance hardware run is on hold.** The preceding SPSC RAM correction at `candidates/offline-spsc-ram-hotpath/XGODriver.cpp` was successfully compiled and verified to have no flash-resident helper calls during the Core1 IRQ-masked serial response ([full verified run 39985794456](https://github.com/jeborgesm/xgo-a10-research/actions/runs/39985794456)). That conclusion remains SRC/BIN, **not** a proven fix for the actual observed unwanted Contra JUMP and PAUSE.

**New controlled next step:** The Test49 SPSC prototype still inherited extra diagnostic provenance instrumentation. Source diff confirms Test44 and Test49 share button mapping, slot0 pre-drive, attack-pulse timing, and 18us serial CLOCK timeout; Test49 only adds extra per-bit/clock classification counters and right+attack counters. A new `candidates/offline-test44-spsc-ram-playable/XGODriver.cpp` reuses the proven SPSC+SRAM queue but strips **exactly nine diagnostic-only differences** to restore Test44 driver/display/header contract. The two original baselines are unchanged.

**Guarded ancestry:** `tests/test_test44_spsc_lineage.py` pins Test44 original blob SHA `f445a1a6d8f9c871a80532e25cc5b1a3ac3b32a0` and earlier compiled SPSC blob SHA `68301b47e4b815cff4cfd5b24bf760d875875492`, and asserts new candidate is exactly SPSC minus Test49-only diagnostics. Stable Test44 OLED `ButtonLayoutScreen.cpp` and `XGODiagnostics.h` are selected when compiling the candidate, rather than Test49 instruments.

**Fast offline CI VERIFIED PASS:** [run 40033843426](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40033843426), commit `ea589bee0363876d023531646e5ef2905a132901`. Includes source-lineage, 4096-mask exact extracted Test44/SPSC C++ function, 22 abort/recovery pairs, independently advancing host CLOCK, six-slot queue stress/25k events. The model still demonstrates false R/JUMP and false S2/START when **artificial** bad timing is injected; those are not physical measurements.

**Full pinned RP2040 ELF gate:** [run 40033843466](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40033843466) compares original Test44 complete firmware with new driver in the same pinned GP2040-CE 3d1f32f and Pico SDK 2.3.1. The new driver MUST have SRAM `emit_frame()` and 0 reachable BL/BLX calls while IRQ-masked; retain linked nm/objdump evidence. No UF2 uploaded. **At handoff edit: job in progress. Do not declare full binary success or offer firmware until CI result is verified.** Source details in `findings/ATOMIC-CRITICAL-WINDOW-AND-SPSC-2026-10-23.md` section 7.

**Real machine-code timing caveat:** Prior SPSC ARM disassembly (artifact ID 12516859458 from run 39985794456) shows 19 Thumb instructions in a six-iteration counter snapshot loop, including a DMB per acquire-load; accepted-generation conditional update adds further branches. There are no flash calls in the IRQ-masked region, but absolute timing relative to the very early XGO slot0 DATA sample is still OPEN. Do not treat static instruction counts or synthetic +4.75us R pre-drive sensitivity as an actual timing measurement.

**Decision:** Do not revive random timeout, postamble-only, or diagnostic-counter-only hardware patches. Evaluate true final linked Test44 candidate, preserve tests, then scope ONE validation session only when justified. No Frankie rewiring, new equipment, XGO BIOS change, or new GPIO instrumentation requested.

---
## 2026-10-23 LATEST VERIFIED — SPSC FULL LINKED ARM AUDIT PASSED

**This supersedes all earlier pending/uncertain SPSC build statuses.**

- **Full RP2040 Build and IRQ-window CFG:** [GitHub Actions run 39985794456](https://github.com/jeborgesm/xgo-a10-research/actions/runs/39985794456), commit `6cd5acd4a7faa54638e80eb18a6ea175353c538f`, **SUCCESS** (`xgo-spsc-ram/offline-irq-audit`). Same pinned GP2040-CE upstream and SDK for both compiled variants. Actual RAM-only Test49 has **two reachable flash-resident atomic calls** inside the Core1 IRQ-masked `emit_frame()` window, including `__atomic_exchange_2` and conditional `__atomic_fetch_or_2`, both using RP2040 SIO spinlock 13. Actual SPSC+RAM has **ZERO reachable BL/BLX calls** before any PRIMASK restore. The audit covers branch paths, not only linear disassembly. Source and binary results match.
- **ELF evidence:** artifact `xgo-gp2040ce-SPSC-IRQ-ELF-EVIDENCE-NOT-FLASHABLE` ID **12516859458**, with disassemblies and symbol tables for both variants. SRAM `emit_frame()` is **1028 bytes baseline**, **1148 bytes SPSC**. The SPSC code uses a six-element aligned 32-bit atomic generation snapshot with acquire barriers, and is longer than original. **No elapsed time was measured**, so zero flash calls does not alone establish full early-slot timing compliance.
- **Fast behavior tests:** [39986453935](https://github.com/jeborgesm/xgo-a10-research/actions/runs/39986453935): actual SPSC C++ `emit_frame()` passed 4096 input masks, 22 abort/recovery pairs, plus slot0 injection; [39991908964](https://github.com/jeborgesm/xgo-a10-research/actions/runs/39991908964): same function also passed 4096 masks with a free-running synthetic XGO CLOCK; [39992215627](https://github.com/jeborgesm/xgo-a10-research/actions/runs/39992215627): synthetic injected prep delay of **+4.75us** first misses a deliberately asserted R/Contra-JUMP in the model. **This is NOT a physical measured delay or confirmed available margin** and applies to all three simulated variants at identical modeled overhead.
- **Source of truth:** `findings/ATOMIC-CRITICAL-WINDOW-AND-SPSC-2026-10-23.md`, with SRC/BIN/MODEL/HW/OPEN separated and linked CI evidence.
- **Protected remains:** Test44 hardware golden, original Test49 witness/diagnostic source, all serial mappings, 18ms attack pulse, 18us CLOCK timeout, Frankie, XGO console firmware. The isolated candidate is `candidates/offline-spsc-ram-hotpath/XGODriver.cpp`. **No UF2 packaged or approved. No hardware test requested. Test50 still on hold.**
- **Next sensible gate:** Check the six-load/branch pre-slot0 timing margin without moving event capture one host poll earlier. Avoid trading away tap responsiveness just to shorten the critical path. If that check cannot be resolved offline, only one targeted hardware test should be proposed after review, not a new sequence of diagnostic flashes. Do not claim phantom R/JUMP or START/PAUSE are confirmed fixed based solely on the absence of XIP calls.

---
## 2026-10-23 NEWEST — PROVEN ARM SPINLOCK HOTPATH; SPSC CANDIDATE OFFLINE

**Highest-priority confirmed SRC/BIN issue:** Original Test49 has `pending_press_edges.exchange(0)` and conditionally `pending_press_edges.fetch_or(pending)` **after detecting host LOAD-low and before slot0 / CLOCK**, with Core1 IRQ disabled. The linked Cortex-M0+ ELF, build [39971706120](https://github.com/jeborgesm/xgo-a10-research/actions/runs/39971706120), shows both calls go through SRAM veneers to `__atomic_exchange_2` at `0x100829e0` and `__atomic_fetch_or_2` at `0x10082a38` **IN FLASH**. Their real disassembly uses `cpsid i`, a polling loop on hardware SIO spinlock **13** (`0xD0000134`), then a DMB and memory update. The conditional fetch-or path at `0x200003be` is **reachable before IRQ restoration**, despite being laid out after its main linear restore address. The only way to establish that accurately is CFG branch traversal. The original RAM-only variant is consequently NOT flash-independent: veneer-aware full audit **correctly FAILED**. Source-linked evidence stored in [finding](findings/ATOMIC-CRITICAL-WINDOW-AND-SPSC-2026-10-23.md), pinned to its exact CI run and ELF artifact ID 12509287881.

**Corrective engineering experiment:** `candidates/offline-spsc-ram-hotpath/XGODriver.cpp`, isolated and NOT flashable. Derived from SRAM candidate, it changes ONLY pending-attack transport: six Core0-owned per-button `std::atomic<uint32_t>` increasing edge generations, six plain aligned acquire loads on Core1, and Core1-local consumed generations acknowledged only when an attack is admitted into the protected **18ms** output pulse. No Core1 atomic RMW exchange/fetch-or inside the LOAD-to-clock window. Core0 diagnostics and GPIO/HK/12-bit serial order/18us CLOCK timeout preserved. Core0 increments still use atomic helpers outside the Core1 frame-critical section. This does not prove first-slot electrical rise timing or full hardware gameplay correctness.

**Fast CI VERIFIED PASS:** [39985359052](https://github.com/jeborgesm/xgo-a10-research/actions/runs/39985359052) exercises seven exact-source-diff and queue equivalence tests, 25,000 deterministic events, overlapping rapid taps, simultaneous/held presses, deferred pulse, race after snapshot, wraparound. [39986453935](https://github.com/jeborgesm/xgo-a10-research/actions/runs/39986453935) additionally extracted and host-compiled actual **SPSC C++ `emit_frame()`**, passing 4096/4096 12-bit input masks, 22 midframe failure/recovery pairs, and slot0 injected false sample, alongside original Test49 and postamble candidate. These are MODELS/HOST C++ tests, not physical timing.

**Full linked RP2040 critical-window CI gate:** `.github/workflows/gp2040ce-xgo-spsc-ram-offline.yml` [run 39985794456](https://github.com/jeborgesm/xgo-a10-research/actions/runs/39985794456). Compares actual RAM-only original `emit_frame()` binary (must have XIP helper calls; `EXPECT_DIRTY`) versus the SPSC candidate compiled within the **same pinned upstream protected GP2040-CE overlay**. New `tests/test_irq_window_elf.py` traverses linked Thumb control flow from `cpsid i` through all reachable branches before all PRIMASK restores, following linker veneers to real destinations. Candidate is accepted at BIN stage ONLY if **every reachable call under IRQ mask resolves into SRAM** (`EXPECT_CLEAN`). Saves disassembly/nm evidence as an artifact, NO UF2 uploaded. **Status as of this addendum: build still in progress, not yet verified.** Check the actual run and log; never assume PASS.

**Not fixed yet:** Real Contra phantom JUMP while P0/R processed edge count remained zero, and spontaneous PAUSE/START remain HW-observed and unexplained by a measured physical trace. The corrected Contra jump binding is HW R/slot0, not B1/P4. A source-supported global spinlock hazard can cause delay but it is NOT proven to have caused those exact incidents. Test50 START provenance hardware experiment remains on hold. Do not request a hardware test, flash candidate, modify Frankie, or touch Test44.

---
## 2026-10-23 LATEST — REAL ARM ATOMIC VENEERS, SRAM AUDIT FIX

**Protected baseline unchanged:** Test44 remains the hardware-proven controller; no XGO firmware, wiring, or physical tests have occurred during this offline effort. Test49 and Test50 source remain preserved.

**Real linked GCC/RP2040 finding:** Full Test49-vs-offline-ram-hotpath firmware workflow [run 39970119162](https://github.com/jeborgesm/xgo-a10-research/actions/runs/39970119162) compiled both successfully. The annotated `(anonymous namespace)::emit_frame()` landed in SRAM at **0x200000F0**, size **1028 bytes**. `wait_clock`/`wait_data` were optimized away or inlined. The production C++ responder makes real linked calls to `____atomic_exchange_2_veneer` (0x20005A38), `____atomic_fetch_or_2_veneer` (0x20005BB8), and `____atomic_fetch_add_4_veneer` (0x20005A18). These veneer call destinations are in SRAM, **but a veneer can branch onward to an actual helper in XIP FLASH**. The first ELF audit mistakenly treated veneer-in-SRAM as sufficient and reported PASS. Do NOT equate that result with a flash-independent responder.

**Source/Clang check verified:** `tests/test_armv6m_atomic_codegen.py` on [fast CI 39969730063](https://github.com/jeborgesm/xgo-a10-research/actions/runs/39969730063) demonstrated Test49 does `std::atomic<uint16_t>` LOAD/EXCHANGE (and conditional FETCH_OR) after XGO LOAD-low while Core1 interrupts are disabled and **before** DATA-high/slot0 and subsequent CLOCK. Cortex-M0+ Clang reference compilation emits out-of-line `__atomic_load_2`, `__atomic_exchange_2`, `__atomic_fetch_or_2` helper calls. The real GCC ELF above independently confirms atomic-helper veneers exist. Their actual target placement and worst-case multicore synchronization delay are OPEN until the corrected audit.

**Correction committed:** `tests/audit_ram_hotpath_elf.py` now resolves every observed `*_veneer` to the actual linked helper symbol using nm and classifies that target, failing closed if it is XIP or unresolved. The corresponding full offline CI preserves linked `nm`/objdump evidence as an artifact (no UF2). `tests/test_ram_audit_veneer_resolution.py` adds the synthetic safety regression to detect FLASH behind an SRAM veneer. Latest corrected commit `e846f422d8c8d77d2b185156334c7781e6209ae2`; [full corrected ELF audit](https://github.com/jeborgesm/xgo-a10-research/actions/runs/39971706120) and [quick veneer regression](https://github.com/jeborgesm/xgo-a10-research/actions/runs/39971706050) were QUEUED at this checkpoint, not yet verified PASS. Never promote test artifacts based solely on their queued status.

**Engineering significance:** Plain Core1 interrupt masking cannot guarantee flash instructions or shared ARMv6-M atomic helpers never stall. These calls in the LOAD-to-slot0 window are a source-supported suspect for early-clock phase loss, but NO measured actual >~7.75us stall has been established. Moving pending-press exchanges out of that window might introduce an additional ~16ms of input latency if naively implemented and must NOT be done without verifying short taps and the protected 18ms pulse behavior. No firmware fix is approved.

**CI efficiency:** The broad historical Test14 rebuild trigger has been narrowed to actual Test14 overlay dependencies. The RAM audit reuses cached ARM toolchain packages and cancels superseded RAM-only runs on push. Avoid writing routine analysis to `diagnostics/**`: many older Test27-49 workflows match that broad path and launch unnecessary full builds. Update THIS handoff or a separate findings document outside `diagnostics/**` instead. The unrelated legacy `build-xgo-p0.yml` failure is not evidence about GP2040-CE responder.

---
## 2026-10-23 — OFFLINE CLOCK-FAULT CLASSIFICATION + ISOLATED RAM EXPERIMENT

**Fast regression verified green:** [run 39968607396](https://github.com/jeborgesm/xgo-a10-research/actions/runs/39968607396) from commit `5f8bf28bcec49a977b125793cf000b83a160b3ee`. Free-running XGO virtual-clock model compiles **actual Test49 and postamble candidate C++** and injects hypothetical post-FIRE and post-LOAD stalls. The simulation distinguishes decoded masks from *reported failure slots*:
- In the **selected LOAD-preparation delay sweep**, 16 synthetic S12 failures were accompanied by wrong host words, **none included START**. All 16 false-START cases instead reported a slot-11 failure. This specific model does NOT support claiming hardware S12 errors caused spontaneous pause.
- After a hypothetical FIRE-slot high-wait delay of ~7.75us in this model, FIRE persists into future SELECT/START host samples and false START occurs; the responder can report failure AFTER host action sampling. No measured Core1 stall of that duration has been established.
- 18us and virtual 8us CLOCK timeout behave alike for that failure; tighter virtual 6/4us timeouts reject nominal frames. Timeout-only and final postamble-only fixes remain unproven/rejected as standalone remedies.

**Isolated RAM hot-path experiment:** Source-only annotation candidate `candidates/offline-ram-hotpath/XGODriver.cpp` is literally Test49 with `pico/platform.h` include and SRAM function-placement attributes on `wait_clock`, `wait_data`, `emit_frame` (plus explanatory comments). *No input, IRQ, queue, pulse, timing or GPIO logic changed.* Source exact-diff guard `tests/test_ram_hotpath_source_contract.py` passed in CI. SDK has supported SRAM placement to avoid instruction-fetch XIP latency; this is a plausible improvement for a **hypothesized** CPU instruction-fetch stall, not evidence actual stalls occurred.

Dedicated `.github/workflows/gp2040ce-xgo-ram-hotpath-offline.yml` compiles the complete protected Test49 firmware, substitutes the annotations in a temporary upstream checkout, rebuilds, and audits resulting ELF symbol addresses and direct XIP calls. Initial run [39966848467](https://github.com/jeborgesm/xgo-a10-research/actions/runs/39966848467) compiled the Test49 baseline but failed on an over-strict harness query for one ELF in the whole build tree (not a firmware-source defect). The corrected workflow chooses ELF via its corresponding unique UF2 stem, commit `d5e73f96d8cb2a1f601d5ff399ddaf13d507e919`, run [39967524306](https://github.com/jeborgesm/xgo-a10-research/actions/runs/39967524306). **Do NOT declare the RAM ELF audit passed until CI independently reports success and call graph reviewed.** No UF2 artifact is published by this experiment.

**Preserve** original Test44 golden, Test49 witness/source, Test50 on hold, Frankie cable, and XGO BIOS. No user hardware test, no purchases, no flash. Avoid filling time with more arbitrary firmware tests.

---
## 2026-10-23 UPDATE — TIMEOUT SWEEP CLOSES RANDOM THRESHOLD-TUNING PATH

Current fast offline CI **PASS**: [run 39963557253](https://github.com/jeborgesm/xgo-a10-research/actions/runs/39963557253), commit `f387e00edbd0e51ef2dd1709ad2751dfc90d5223`. Exact Test49 and postamble-candidate C++ `emit_frame()` compiled with independent synthetic XGO CLOCK/DATA sample timings:
- 18us and 8us timeout: 4096/4096 ideal nominal masks PASS; BOTH allow synthetic START/PAUSE when FIRE DATA stays low due >~7.75us injected post-FIRE delay; synthetic LOAD-prep delay first creates START at ~13.75us; errors occur after host already sampled false START. Tightening from 18 to 8 **does NOT fix** that modeled mechanism.
- 6us timeout: 2048/4096 nominal masks FAIL under mock; 4us: 4096/4096 nominal masks FAIL. These counts are **chosen virtual CPU schedule**, not hardware error forecasts. Source-only timeouts are not a safe next firmware candidate.
- Hypothetical DATA-high recovery lag at immediate LOAD release yields false R/Contra JUMP despite zero `pressedR1()` edge; separate from false START. Neither modeled failure is cured by final-CLOCK postamble policy.
- New source audit of minimal native and Test49 `raw_init()`: ordered 12 mux/PHY override constants and register assignments are equivalent (SRC). No obvious changed USB-PHY register config explains GP phantom input. Electrical recovery still OPEN.
- All new analysis documented under `diagnostics/SERIAL-BOUNDARY-OFFLINE-AUDIT-2026-10-23.md` (latest source comparison commit `1b0a07fa0aab6909cacf077fe6585a3f033f3496`).

**Do not change protected Test44, do not flash the terminal-postamble experimental file, and do not request a new tester session yet.** Further source-level timing work must distinguish actual possible runtime gaps from the hypothetical 7.75us fault injection before claiming a firmware fix.

---
## 2026-10-23 LATEST — FREE-RUNNING CLOCK CI PASS; NO FIRMWARE CHANGED

**Fast CI PASS:** [run 39963557253](https://github.com/jeborgesm/xgo-a10-research/actions/runs/39963557253), commit `f387e00edbd0e51ef2dd1709ad2751dfc90d5223`.

`tests/test_responder_free_running_clock.py` compiles actual Test49 and isolated postamble-candidate `emit_frame()` C++ functions against an independent virtual XGO CLOCK and host sampler, not a scripted next-expected-edge mock. With 7.2us LOAD, 1.2us LOAD-release-to-first-CLOCK and 4.0us CLOCK periods (representative **HW P0** values), both variants serialize all **4096 masks** correctly in ideal timing. **Hypothetical** 0.35us DATA high-recovery delay at immediate slot0 host sample makes an unsolicited R/Contra JUMP while processed R remains absent. **Hypothetical** 9us delay after B2/FIRE slot5 output leaves DATA asserted through S1/SELECT and S2/START host samples: observed synthetic word `0x0e0`, the function eventually flags CLOCK failure but START has already been sampled. A 0.25us-step sweep first shows false START after a ~7.75us injected FIRE-gap or ~13.75us injected LOAD-prep gap. These gaps are **NOT measured physical Core1 delays**; interrupts are masked during the serial train.

Tightening EDGE_TIMEOUT_US from 18 to 8 within the **offline mock** does not prevent the synthetic false START. At virtual 6/4us timeouts, even ordinary nominal frames fail in the chosen model, showing why arbitrary tightening is risky but not quantifying actual RP2040 failure rates. Postamble-only candidate has identical simulated phantom R and START outcomes; **NOT** a standalone fix. Detailed evidence: `diagnostics/SERIAL-BOUNDARY-OFFLINE-AUDIT-2026-10-23.md`, updated in commit `7bb1f2451c316da96cda66fa2eb37c032674aee9`.

**Next decision:** no flash yet. Examine actual code execution between FIRE high and subsequent CLOCK handling, and whether a physically plausible phase skip can occur without an injected artificial stall; separately source-audit native PHY DATA-high recovery/slot0. Preserve Test44, protect Frankie, and DO NOT modify XGO console firmware. START edge provenance Test50 hardware test remains on hold at user's request for fewer hardware sessions.

---
## 2026-10-23 CRITICAL CORRECTION — CONTRA JUMP = R/SLOT0; NEW FAST CI PASS

Hardware-proven **Contra P2 JUMP is R/serial slot0**, NOT B1/P4. In prior P1 fixed-R hardware test, asserting R alone repeatedly caused Contra jump; the successful P2 scripted Contra bot also used R as jump. Sources: `experiments/rp2040-responder-p1-fixed-r.md`, `tools/rp2040-xgo-p2-contra/README.md`. In the latest Test49 hardware screenshots, **P0 and P4 were BOTH zero** during reported unwanted JUMPS. Earlier P4-specific inference and "B2 FIRE advances one slot to B1 JUMP" labels were **WRONG** and have been corrected in the offline regression suite. Do not reintroduce this mapping error.

Earlier P0 passive capture (HW) measured XGO DATA/load LOW **6.8–7.5us** and only **0.9–1.3us from DATA release to the first CLOCK-low**; scanner samples R/slot0 immediately on DATA release, *before CLOCK*. An unpressed-R host input may therefore be contaminated by slow DATA recovery across the slot0 sampling aperture, even when the GP2040-CE processed R/P0 counter is zero. This is a **plausible modeled mechanism, NOT verified root cause** for Test49. Earlier GREEN passive-probe loading itself caused jump-only P2 contamination, strengthening relevance of physical DATA release; analog timing in Igor+Frankie was not measured. Spontaneous PAUSE/START slot7 is separate and not explained by this R0 mechanism.

Tests corrected:
- `tests/test_serial_boundary_faults_offline.py` labels R/slot0 as Contra jump, separates B1/slot4 as an unrelated button.
- `tests/test_responder_compiled_mock.py` samples slot0 on modeled host DATA release (instead of incorrectly assuming first CLK-fall), and deliberately injects a simulated slow-release false-low sample; both exact source C++ variants pass correctly.
- `tests/test_slot0_release_settle_offline.py` explores only synthetic threshold/sample delays constrained by the proven first-CLOCK timing. It cannot prove the hardware's actual rise time.
- **Latest CI PASS:** [run 39950134069](https://github.com/jeborgesm/xgo-a10-research/actions/runs/39950134069) at `1fd3ebcee891612a7f6e71e16fc4edfa27fb518c`: **14** Python source/boundary tests, **6** slot0 release timing-model tests, and actual compiled C++ Test49 and postamble candidate tests (4,096 ideal masks + 22 midframe fault/recovery pairs EACH + slot0 early-sample injection).
- Detailed corrected audit: `diagnostics/SERIAL-BOUNDARY-OFFLINE-AUDIT-2026-10-23.md`, with correction commit `ef0d0cb8a03b290737105eb5df7cedbcf7da800a`.

**NO NEW HARDWARE TEST, NO NEW DEVICE, NO XGO CONSOLE PATCH.** Test44 protected; Test50 on hold. Postamble-only correction is NOT established as the phantom-JUMP remedy. Next focus must discriminate host slot0 DATA recovery/sampling versus LOAD/frame misalignment from existing evidence and source, offline first.

---
## 2026-10-23 — COMPILED ACTUAL C++ RESPONDER TESTS PASS; HARDWARE STILL UNTOUCHED

Verified fast CI [39949251664](https://github.com/jeborgesm/xgo-a10-research/actions/runs/39949251664) at `7c3c4e5206fd6900102b2f7b7ad6897a1a9addff`: `xgo-fast-serial/verified-models = success`. It runs existing Test49 rising-edge Python regression, 13 Python fault/source regression unit tests, and `tests/test_responder_compiled_mock.py`, which **extracts and compiles the actual Test49 and one-line offline-candidate `emit_frame()` functions** under host g++, replacing only pin/time/IRQ operations with scripted inputs. Both variants passed 4096 idealized complete masks, 22 mid-frame abort+recovery pairs, and the final-high timeout + next-frame recovery semantics. Hardware signal timing is NOT simulated; this does not prove the host would decode correctly with shifted/missed pulses. This is not an RP2040 UF2 compile.

Investigate one source-grounded early timing difference next: minimum proven Pico pre-reads button mask before LOAD, while Test49 GP2040-CE does atomic mask reads, edge queue and pulse logic **after seeing LOAD low but before waiting for DATA high and CLOCK fall**. Given the short LOAD and early slot timing, this could reduce margin, but no measured timing or direct causal link to phantom JUMP and PAUSE is established. Use the existing host waveform models and short CI, not another OLED counter firmware. Detailed evidence: `diagnostics/SERIAL-BOUNDARY-OFFLINE-AUDIT-2026-10-23.md`.

**Do not ask user for a hardware test yet. Test50 on hold; protected Test42/Test44 and Frankie unchanged.** The postamble-only candidate is NOT a verified wrong-button fix.

---
## 2026-10-23 — OFFLINE-FIRST SERIAL INVESTIGATION, NO HARDWARE REQUEST

User requested a simpler, faster approach using existing GP2040-CE, GitHub Actions, known source and existing OLED findings; **no new analyzer, Pico, wiring, serial logger or flashing per hypothesis**.

- Corrected HW witness stands: accidental Contra JUMPS while B1/P4 processed counter remained zero; later spontaneous PAUSE, then one deliberate START. User's tapped FIRE is P5/B2. Test49 legacy Python regression wrongly modeled FIRE as bit4; corrected in test-only commit `1c0f5c047597809b4b4c6031464ff78021ebefd5`. Controller mapping unchanged.
- Source discrepancy: hardware-proven minimal Pico responder ignores failure of *final* CLOCK-high wait after slot12 low, but Test49/Test50 marks it a failed transaction and invokes `require_idle_high` recovery. The corrected HW photo series reports 186 additional cumulative slot12 failures across 261 additional CLK failures, but slot12 counts merge failed terminal low and failed terminal high. Do not claim cause of phantom input from this count.
- Offline Python source-guard plus timing/slot-alignment regression `tests/test_serial_boundary_faults_offline.py`; dedicated short non-compiling CI workflow `.github/workflows/gp2040ce-xgo-fast-serial-offline.yml`. Detailed evidence with HW/SRC/MODEL/OPEN in `diagnostics/SERIAL-BOUNDARY-OFFLINE-AUDIT-2026-10-23.md`.
- Isolated candidate `candidates/offline-terminal-postamble/XGODriver.cpp` differs by **one line only** from Test49: ignore final CLOCK-high wait timeout for transaction success, matching native contract. This is **NOT built, NOT hardware-tested, NOT approved as a fix for jumps/pauses**. Literal source diff guarded by regression. Commit `ffd59f39a6df058b8e15a5b1e667091b58c8e9ab`; fast status publishing workflow updated afterward.
- The previous CI-pending note is superseded by the verified fast CI result in the newest addendum. Synthetic models and host-compiled source tests are NOT electrical proof.
- Test50 hardware run ON HOLD. Protected hardware baselines Test42/Test44 untouched; XGO firmware untouched.

---
## 2026-10-23 IMPORTANT — CORRECTED TEST49 USER-WITNESS ACCOUNT

The user **DID experience multiple unintended JUMPS before photo 2**, while moving RIGHT and repeatedly tapping FIRE without ever intentionally pressing JUMP. The P4 (processed B1) attack rising-edge count was **0 in all photos**, including after the phantom jumps. Continued RIGHT+FIRE, fell off a bridge, then Contra **PAUSED ON ITS OWN** without pressing START. The user pressed START intentionally ONCE to resume and later took photo 3. The assistant initially misread this as "no jumps" and corrected the primary record in `diagnostics/CONTRA-RIGHT-FIRE-OBSERVATION.md` commit `843c26324139c9386bb94f2b0289a603adacede7`. Do not repeat the false interpretation.

Test49 counters photo 1/2/3: CLK 59/172/320; slot12 failures 40/126/226; LO 48/140/259; HI 11/32/61; P0-P4 0/0/0; P5 (processed B2) 0/29/164; RIGHT+attack RF 0/29/169; RF errors E 0/6/28. **Superseded binding interpretation:** JUMP is hardware-confirmed as R/slot0, NOT B1. P0 also remained zero, so the relevant mismatch is real host JUMP/R0 behavior versus zero processed R0 edges. Never claim causality to slot12 alone.

Test50 commit `b7693af7f17a0f39e318cd098775bd6ae598492b` is an isolated **processed S1/SELECT and S2/START rising-edge provenance** diagnostic, to localize spontaneous pause. Serial responder and map_mask are unchanged from Test49. OLED labels S1/S2. Dedicated workflow `.github/workflows/gp2040ce-xgo-test50-pause-edge-provenance.yml`, expected status `xgo-test50/verified-uf2`; build not yet verified at handoff time. Preserve Test44/Test48/Test49.

---
## 2026-10-22 ADDENDUM — CURRENT PRIORITY (supersedes stale 2026-10-20 snapshot below)

**Do not restart.** Branch `research-gp2040ce-xgo-integration`; protected controller hardware baselines Test42 and Test44. Never modify XGO console firmware. All subsequent candidates are GP2040-CE controller only.

- Test45 failure-aware pulse delivery was compiled but felt slower and did not improve the Street Fighter II car benchmark; rejected for playability.
- Test46 clock LOW/HIGH diagnostics preserved Test44 timing and cleared Street Fighter II car with ~1 second left. Test46 incorrectly classified slot 1–11 CLOCK-high timeouts as LOW; its LO/HI breakdown is not trustworthy.
- Test47 fixed the classification (source committed and CI workflow present); no claim of separate hardware success.
- Test48 Contra diagnostic compiled, verified and *hardware tested*. When user holds RIGHT while **tapping** FIRE, Contra intermittently produces unsolicited JUMP. One or two phantom jumps occurred before third diagnostic photo; fewer than in prior tests, not solved. Photos before/after: ERR 350→628, CLK 339→597, REL 11→31, LO 299→480, HI 40→117, RF 0→179, E 0→21. `RF` is RIGHT plus **any** attack output bit, not necessarily game's FIRE. Last photo S12 FAIL 421 of CLK 597 accumulated. See `diagnostics/CONTRA-RIGHT-FIRE-OBSERVATION.md`.
- Source-level insight: slot 12 is the terminal CLOCK handshake **after all twelve button-bit slots have been transmitted**. An S12 timeout does not itself prove the XGO decoded a wrong bit; it may nonetheless disrupt rearming. Do not infer phantom-JUMP causality from aggregate CLOCK errors.
- Test49 (source commit `4bbebb277aae0af24f9b1e6c9dfdca1cb332f92c`, CI verification commit `8771532babc74e732b05aad1bf242e6e97e81a8b`) introduces six `P0–P5` *processed Gamepad attack rising-edge* counters, plus OLED layout. Test48's entire timing-critical `emit_frame()` function and `map_mask()` are byte-for-byte identical in Test49. Source audit passed. The workflow is `.github/workflows/gp2040ce-xgo-test49-attack-edge-provenance.yml`; check **`xgo-test49/verified-uf2`** commit status, then retrieve and verify artifact before any user flashing. The CI result was not available when this addendum was written. Test49 is diagnostic, not a fix.
- Test49 OLED rows: 0 header; 1 OK/ERR; 2 CLK/S12; 3 LO/HI; 4 P0/P1; 5 P2/P3; 6 P4/P5; 7 RF/E. `P0–P5` record processed button edge transitions, **not direct GPIO voltage or XGO's decoded inputs**. Avoid assigning FIRE or JUMP to a particular P bit without empirical mapping.
- User should **not watch OLED while playing**. Take initial OLED photo; play Contra normally moving RIGHT and tapping FIRE; note occurrence of unwanted JUMP; take final OLED photo. Compare `P` counter deltas to determine if the source detects an unintended second attack button. Pure FIRE edge sequences cannot synthesize JUMP in the source-level queue model; this is not proof of wire-level integrity.
- Preserve every tested candidate; no changes to Test44/Test48. When build is verified, deliver direct UF2 and ZIP if possible, not unsupported links or promises. Any hardware followup should be short and focused.

---

## Mandatory first action in next chat
Resume branch `research-gp2040ce-xgo-integration` of `jeborgesm/xgo-a10-research`. **Do not restart archaeology.** The user explicitly asks for **actual engineering work on missed attack inputs**, not a status narrative or another unsupported promise. The immediate work is offline source analysis and implementation planning of attack event delivery across failed serial transactions. Preserve tested builds. Do not request another hardware test until there is a genuine compiled candidate and a clear reason for testing it.

## Immutable scope and contract
**ALL modifications GP2040-CE controller-side ONLY**. Do not modify XGO firmware, BIOS, emulator, game, mappings, or turbo. Every physical rising edge for LP/MP/HP/LK/MK/HK should cause exactly ONE correct attack; physical hold never repeats, release re-arms. A bounded serial pulse (currently 18 ms) is needed for game polling; avoid wrong/mixed attacks and directional reversals. Do not regress controller's existing SELECT+START+R1 LED shortcut or hardware baseline. Do not revive strict CLOCK high-phase guard (Test35), independent per-button pulse (Test33), or next-slot predrive (Test30).

## Current state: playable, NOT complete
- **Test42** (16 µs CLOCK timeout, 18 ms attack pulse): best established responsiveness and protected playable rollback. All six taps work, no held repeats, defeated Zangief. Occasional brief crouch stand-up hiccup, some remaining serial errors. CI success https://github.com/jeborgesm/xgo-a10-research/actions/runs/39526930281 artifact 12313413278. Source `integrations/gp2040ce-xgo-test01/candidates/test42-clock-timeout-16us/`.
- **Test43** (20 µs, 18 ms): no crouch hiccup but slower-feeling kicks, failed car destruction before timer. Not promoted. CI https://github.com/jeborgesm/xgo-a10-research/actions/runs/39529198311 artifact 12315311345. Source `.../candidates/test43-clock-timeout-20us/`.
- **Test44** (18 µs, 18 ms): **user actually flashed and tested**. Street Fighter II car bonus save point, same fixed kick sequence used as practical throughput benchmark: **car destroyed with 1 second remaining**, **no directional reversals**, **some kicks appeared missed**, **held attack buttons DO NOT repeat** (explicit follow-up confirmation). OLED snapshot **OK 2600 ERR 58 CLK 52 REL 13**. Playable, but NOT final. Build success https://github.com/jeborgesm/xgo-a10-research/actions/runs/39533151131 artifact **12316690668** `xgo-gp2040ce-test44-OFFLINE-UNVALIDATED-DO-NOT-FLASH` (artifact label was created before hardware validation; user subsequently tested). Source `integrations/gp2040ce-xgo-test01/candidates/test44-clock-timeout-18us/`, results `HARDWARE-RESULTS.md`. DO NOT overwrite Test44.
- **Test36** (12 µs, 18 ms): older protected playable fallback; occasional wrong attack/direction; CI https://github.com/jeborgesm/xgo-a10-research/actions/runs/39075369513 artifact 12116143787.
- **Test41** diagnostics: LOW/HI indicate CLOCK phase already present at wait entry, NOT proof of missing edges. Failures distributed across slots even with no buttons; don't attribute every ERR to kick losses. 

## CONFIRMED source-level vulnerability requiring next work
Read `integrations/gp2040ce-xgo-test01/ATTACK-PULSE-FAILURE-ANALYSIS.md` and **Test44 XGODriver.cpp**. Current implementation Core0 latches physical rising edges:
```cpp
const uint16_t snapshot = map_mask(gamepad);
const uint16_t attacks = snapshot & ATTACK_BITS;
const uint16_t rising = attacks & ~previous_physical_attacks;
previous_physical_attacks = attacks;
if (rising) pending_press_edges.fetch_or(rising, std::memory_order_release);
published_mask.store(snapshot, std::memory_order_release);
```
Core1 in `emit_frame()` after LOAD low, with IRQ masked, **BEFORE knowing whether serial frame succeeds**:
```cpp
const uint32_t now = time_us_32();
if (attack_pulse_mask && (uint32_t)(now - attack_pulse_start_us) >= ATTACK_PULSE_US)
 attack_pulse_mask = 0;
const uint16_t pending = pending_press_edges.exchange(0, std::memory_order_acq_rel);
if (pending && !attack_pulse_mask) {
 attack_pulse_mask = pending;
 attack_pulse_start_us = now;
} else if (pending) pending_press_edges.fetch_or(pending, std::memory_order_release);
const uint16_t mask = (physical & ~ATTACK_BITS) | attack_pulse_mask;
```
`ATTACK_PULSE_US = 18000`; `EDGE_TIMEOUT_US = 18` in Test44. Then slots 0–11 are transmitted, and `complete` only determined at end. **A failed frame can consume a pending edge and age out its 18ms pulse without any successful delivery**. Code comment 'A failed serial transaction cannot acknowledge the physical press' is **not implemented**. A completed serial frame also does not prove the game's poll sampled the pulse. This is a proven CODE defect/vulnerability, NOT yet a proven sole cause of observed missed kicks.

## Immediate engineering instructions
1. Inspect Test44 complete source and dedicated workflow, plus prior candidate behavior; preserve source byte-for-byte in protected folders.
2. Design/implement a **new isolated candidate** (next Test45 if appropriate) fixing the attack event commit/retry lifetime across failed serial frames while preserving strict one-shot physical hold and bounded game-visible pulse. Crucial edge cases: failure on first frame, several failures, long physical hold, release/re-press, second attack during first pulse, simultaneous presses, transient serial idle, timer rollover. A simple unconditional retry on every failed frame could cause long-held repeats; avoid. Avoid claiming that one successful transaction guarantees game observation. Consider bounded grace/retry and counters for attempts/success/expiry; distinguish host scans vs game polls. Avoid adding heavy work in timing-critical IRQ-disabled section.
3. **Do actual repository edits and compile using dedicated GitHub Actions**, fix build failures, check final artifact before asking user to flash. Do not promise asynchronous progress or say 'working' without actual tool activity. If design not sufficiently safe, commit rigorous design analysis and identify unresolved conditions honestly instead of creating unsafe firmware.
4. For user hardware tests use **the same saved Street Fighter II car stage and same kick sequence**: completion/time remaining, missed kicks, crouch direction, six correct attacks, held no-repeat, diagnostics. Test44 car success +1 second, Test43 fail, Test42 responsive. User values playability over lowering counters.
5. Never alter XGO side. Keep Test42/Test44 intact and rollbackable.

## Tool operations
GitHub connector through `functions.exec`: `tools.mcp__GitHub__fetch_file({repository_full_name:'jeborgesm/xgo-a10-research',ref:'research-gp2040ce-xgo-integration',path:'...'})`; `create_file`, `update_file`. Dedicated workflows at `.github/workflows/gp2040ce-xgo-test44-clock-timeout-18us.yml`. Use GitHub Actions API to check runs/artifacts; generic `build-xgo-p0.yml` may fail independently and is not authoritative for this controller candidate.

## Previous experiments / rejected regressions
Test28 stable original HK slot0 open-drain asserted after 3µs LOAD-low; others repeat/mix. Test29–31 timing variations rejected (Test31 HK repeats). Test32 first six-attack physical edge 24ms, occasional HP→MK and direction artifacts. Test33 independent pulses severe mixed inputs. Test34 extra release scan no fix. Test35 strict CLOCK high guard caused choppy movement/missed attacks. Test36 Test32 pulse 24→18ms improved. Test37 counters unreadable; Test38 wrong OLED screen; Test39 active screen diagnostics overlap, stable DIR:A despite Ken reversal; Test40 clean OLED eight-row diagnostics; Test41 phase counters, errors distributed; Test42 16µs significant improvement; Test43 20µs directional stability but poor throughput; Test44 18µs playable +1sec car, possible missed kicks.

## User expectations and recent interaction
User explicitly asked 'now seriously are you doing any actual work to check the missing inputs?' after joking about management deadlines. Do not respond with banter instead of code. User is frustrated by conversation limits and lost momentum. This handoff is intended to allow next chat to begin immediately with actual implementation. Be candid: at handoff time **only source-level vulnerability analysis has been committed; no Test45 or corrective build exists**.
