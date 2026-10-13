# Core0-dedicated Caveman-style responder — architecture gate (2026-10-12)

**Status: source audit/design, NOT firmware candidate.** Branch research-gp2040ce-xgo-integration; protected Test14 unchanged.

## Hardware acceptance
Test16 FAILED: HK→MP, HP→MK, MP→LP, MK→Select/credit, unstable held inputs. One physical press must remain one continuous logical assertion until release, without spurious button identity or release/reassertion.

## Current architecture (SRC: overlay apply.py)
- Core0 GP2040::setup/run performs input GPIO scanning, mappings, USBHostManager processing, gamepad processing and GP2040Aux::processOnce (OLED/addons) in XGO mode.
- Core1 starts XGODriver::runResponder(), owns raw USB PHY and polls LOAD/CLOCK continuously.
- Shared input is a coherent atomic uint16_t published_mask.
- Core1 native responder disables interrupts during the clock train, but not while waiting for LOAD. Post-frame diagnostics execute outside IRQ-disabled region in Test16.
- Test14 and Test16 both share Caveman-derived level-polling frame code; Test16's new snapshot/final rise checks did not correct HW corruption.

## Why a naive core swap is UNSAFE (SRC/UP)
1. Pinned GP2040-CE ConfigUtils::save enforces Core0-only save; running GP2040::run on Core1 without moving the storage/save boundary violates this invariant.
2. Core0 runs input addons, TinyUSB/PIO USBHostManager, profile/boot/save logic and application state. Migrating GP2040::run to Core1 needs an explicit ownership review of IRQs, USB host, GPIO, flash, display, and singleton lifetimes.
3. Existing Core1 setup uses multicore_lockout_victim_init; a flash-safe redesign must preserve proper lockout roles and Core0-only flash ownership.
4. OLED and Web Config must remain functional. Web Config requires reboot to another input mode; native USB PHY cannot be driven simultaneously by responder and TinyUSB.
5. A dedicated Core0 loop cannot simultaneously run ordinary GP2040::run; simply swapping entry points would stall input publication.

## Candidate architecture to investigate
- Core0: *only in XGO mode*, initialize responder PHY and execute continuous bounded Caveman-style LOAD/CLOCK loop. No display drawing, logging, flash writes or shared resource work in critical frame segment.
- Core1: input acquisition, processing, mapping and auxiliary services, publishing a single atomic 12-bit current-state snapshot; never touches raw responder PHY.
- Cross-core control service: Core1 requests saves/reboots and Core0 performs any operations that must run on Core0 at explicitly safe frame boundaries. Verify IRQ and multicore-lockout ownership and preserve flash recovery.
- Non-XGO modes: preserve upstream Core0 GP2040::run / Core1 GP2040Aux::run, TinyUSB and Web Config.
- Startup: Core0 must complete core-specific setup before launching Core1; mode decision and core1 readiness must not deadlock on GP2040Aux::ready().

## Critical alternative hypothesis
Current Core1 responder already has a dedicated while(true) loop. Thus **moving the same bit-bang routine unchanged to Core0 does not prove a fix**. Need to identify differences in IRQ/flash/core-local execution and the exact host sampling phase. A 2us host CLOCK-low pulse and write-after-fall approach can still violate DATA setup time on either core. Compare actual compiled critical path and host BIN scanner before claiming core ownership as root cause.

## Gates before build
1. Pin exact GP2040::run, GP2040Aux::run, save/reboot, USB host and display call graph; classify Core0-only calls and interrupts.
2. Recover host sample position from XGO bisrv.asd around offset 0x35D770; compare bit-driving phase to sample instant.
3. Compile/disassemble native Caveman and current Test16 hot paths at matched clocks/optimization to compare cycles and memory placement; do not treat unmeasured timing as fact.
4. Implement isolated alternate scheduler on a NEW candidate path, preserving all Test14 files; test boot-mode gating and no dual USB PHY ownership.
5. Offline tests: constant one-hot input across arbitrary consecutive scans always yields identical 12-bit decoded state, with no zero gaps, extra bits or false transitions; exercise LOAD/CLOCK timeout/rearm and config-save handoff.
6. Build CI and audit UF2 separately; hardware validation only after gates pass.

**Evidence classification:** HW = Test16 user observations; SRC = repo source; UP = pinned upstream previously audited; INF = timing/core migration risks; OPEN = exact sampled waveform and feasibility of migrating GP2040 main loop.
