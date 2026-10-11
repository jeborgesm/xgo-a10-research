# Test14 comprehensive offline integration audit — 2026-10-10

**Scope:** Read-only review of the protected Test14 overlay at source commit `fb911825123f07ea8fe12e4bdf881583a76de146` against pinned GP2040-CE `3d1f32f7d02d418826b725b60208278d3be878c3`, using the current branch's `apply.py`, `XGODriver.cpp`, `preflight.py`, `audit_test14.py`, and CI workflow. No firmware candidate generated. The post-Test14 research files are audit-only changes.

## Evidence definitions
- **SRC**: explicitly present in inspected overlay.
- **UP**: behavior described in pinned-upstream investigation, requiring applied-tree trace for closure.
- **INF**: risk inferred from source.
- **HW**: user-reported Test14 boot/playability and responsive, unmixed inputs.
- **OPEN**: not yet demonstrated or exhaustively traced.

## Highest-priority findings

| ID | Severity | Evidence | Finding and consequence | Closure criterion |
|---|---|---|---|---|
| A01 | P1 | SRC/UP/OPEN | Core1 runs `runResponder()` continuously; upstream Core1 ordinarily initializes `multicore_lockout_victim_init()`. Pinned upstream `src/main.cpp` calls `multicore_lockout_victim_init()` as the first statement of `core1()`, BEFORE the exact anchor replaced by `apply.py`. Thus registration is preserved by the overlay. Remaining question: IRQ-disabled clock trains can delay lockout response, and lockout can suspend console response during flash writes. | **Registration subquestion CLOSED (SRC/UP)**. Trace SDK flash-safe lockout timeout behavior, Core1 interrupt-disabled duration, config save/reboot calls, and host recovery; no risky golden hardware test. |
| A02 | P1 | SRC/INF | `emit_frame()` disables Core1 interrupts through the 12-slot clock train, while incrementing multiple atomic counters inside time-critical failure branches. Clock edge timeout is 12us; cycle budget and worst-case IRQ-disabled duration have not been measured. | Compile/disassemble exact candidate and count cycles for hot/failure paths; check timeout under compiler optimization and cross-core contention. |
| A03 | P1 | SRC/INF | `emit_frame()` takes a snapshot before waiting up to 20ms for LOAD. A button transition during the wait may be delivered one frame late; not mixed-frame, but latency can increase. | Analyze maximum/typical poll interval and whether host LOAD idle can last 20ms; bench timing test against a synthetic host. |
| A04 | P1 | SRC/INF | After an active failure, `require_idle_high` waits for DATA high before rearming, but there is no explicit proof that the next DATA low is a *new* LOAD rather than unrelated signal activity. `wait_clock(true)` at frame end is ignored. | Model malformed/short/long LOAD, stuck-low/high CLOCK, truncated slot train, and recovery transitions. |
| A05 | P1 | SRC/UP/OPEN | Native TinyUSB device init/task is gated by current input mode; the Core1 mode choice is cached in `xgoMode` at startup. Runtime mode changes may leave cached scheduler/PHY ownership inconsistent until reboot. | Trace all `setInputMode` paths, Web Config/reboot/boot-hotkeys, and ensure no in-place transition reconfigures native PHY. |
| A06 | P2 | SRC/INF | `GP2040Aux::processOnce()` is invoked from Core0 after PostprocessAddons. Upstream aux/addons may assume Core1 ownership or read gamepad/display history concurrently; review each enabled addon and reentrancy/locking. | Applied-tree callgraph, memory ownership and bounded-time audit for all enabled Pico addons. |
| A07 | P2 | SRC/INF | `map_mask()` uses 12 `pressed*` methods and atomically publishes the 16-bit mask. Verify button semantics, simultaneous opposites, diagonals, hotkeys, mapping changes, turbo and SOCD postprocessing. | Exhaustive 4096-mask mapping test with independently specified expected slot order; inspect processed/raw data point. |
| A08 | P2 | SRC/INF | `raw_init()` writes USB controller main, SIE, mux and direct override registers without an explicit reversible teardown. This is valid only if XGO mode has exclusive ownership until reset. | Prove boot-mode and recovery paths; inspect Pico SDK and upstream native USB use. |
| A09 | P2 | SRC/OPEN | `USBHostManager` remains active in Core0. Optional PIO USB host and peripheral pin conflicts are not closed. | Board pin allocation and host/addon enabled-state audit; separate validation for connected peripherals. |
| A10 | P2 | SRC/INF | Existing audit script checks literal strings and key structural anchors, but cannot establish behavioral semantics, exception/error paths, timing, or exact binary identity. | Add read-only behavioral unit/model checks and a disassembly audit without modifying Test14. |
| A11 | P2 | SRC/INF | Overlay `apply.py` preflights anchors, then writes sequentially; an unexpected late anchor failure leaves a partially patched upstream checkout. CI starts from clean clone, but local reproducibility could suffer. | Precompute all edits in memory and write only after every anchor passes, in a future tooling-only change; leave proven firmware unchanged. |
| A12 | P2 | SRC/OPEN | Web Config mode appears separately gated, but mode selection from saved settings, first boot defaults, USB recovery and persistence have not been hardware tested. | Source-trace boot mode priority, config RNDIS init, save/reboot, fallback recovery. |
| A13 | P2 | SRC/OPEN | Non-XGO modes retain original Core1 scheduling by branch, but no full compile/functional regression matrix across USB modes has been performed. | CI matrix plus code review for non-XGO mode selection and display behavior. |
| A14 | P3 | SRC | Diagnostic counters are unsigned atomics; wraparound is expected eventually. Max counters and last-failure slots are telemetry, not protocol state. | Document wrap semantics and ensure diagnostics cannot block critical path. |
| A15 | P1 | OPEN | Uploaded Test14 ZIP matches reported original artifact size (1,018,276 bytes), not yet SHA-256 verified against original ZIP/UF2. | Download original Actions artifact 11687143460; hash ZIP and embedded UF2; compare to private vault. |

## Verified upstream flash-lockout subfinding (2026-10-10)

The pinned upstream `src/main.cpp` contains `multicore_lockout_victim_init();` at the start of `core1()`, before the two lines (`gp2040Core1->setup(); gp2040Core1->run();`) that the Test14 `apply.py` replaces with the XGO branch. Therefore **Test14 does not remove lockout-victim registration**. This resolves the feared missing-initialization defect; it does **not** prove that the responder can meet its 12-us clock deadlines during an actual flash save. Upstream `src/gp2040.cpp` calls `Storage::save(true)` on boot mode/profile changes, and `checkSaveRebootState()` calls `Storage::save(forceSave)` for requested saves. `src/storagemanager.cpp` forwards to `ConfigUtils::save(config)`. Exact flash-safe SDK behavior and timing are not yet traced. This is **UP/SRC evidence**, not a hardware flash-save test.

## Specific code observations

1. `XGODriver::initialize()` deliberately does not initialize USB PHY; `runResponder()` calls `raw_init()` on Core1. This is consistent with exclusive PHY ownership (**SRC**).
2. Core0 publishes `published_mask.store(snapshot, std::memory_order_release)`; Core1 acquires before `emit_frame`. This prevents torn masks (**SRC**), not latency spikes or timing failures.
3. In `emit_frame`, failure counters increment while interrupts are disabled; the previously filed offline audit already called this out, and it remains unresolved (**SRC**).
4. The overlay retains the stock Pico board config/I2C mapping and changes display layout defaults; existing stored configuration can override default XGO mode (**SRC**).
5. Test14 HW result is a gameplay acceptance checkpoint, not proof of flash-save, Web Config, USB host, long-duration operation or other modes (**HW/OPEN**).

## Closure sequence — offline only

1. Reconstruct exact pinned upstream + overlay in an isolated checkout; preserve Test14 source and firmware.
2. Trace startup/boot modes, `multicore_lockout_victim_init`, `flash_safe_execute`, storage save, restart, watchdog and USB PHY ownership. Record call sites with file/line.
3. Inspect the generated build/disassembly and worst-case Core1 critical-path timing. Do not substitute source-string checks for machine-level timing evidence.
4. Build a deterministic software host model for all 4096 masks and malformed LOAD/CLOCK sequences; check latching, release and rearm.
5. Trace each enabled Pico addon, OLED history, input mode, host USB pin use, event and configuration paths for ownership and latency.
6. Add regression assertions or read-only test harnesses only on the research branch, and rerun CI.
7. Classify every finding as closed, mitigation needed, or hardware-only. Any firmware change gets a separately named Test15 candidate, never an overwrite of Test14.

## Additional pinned-upstream execution trace (2026-10-10)

- `src/config_utils.cpp:2256-2263`: `ConfigUtils::save` asserts and enforces Core0-only saves; lines 2291-2299 call `EEPROM.commit()`. FlashPROM implementation and lockout wait duration remain **OPEN**.
- `src/gp2040aux.cpp:27-51`: setup creates Display, NeoPicoLED, PlayerLED, BoardLED, Buzzer, Rumble and ReactiveLED addons, then sets `isReady=true`. Test14 moves setup to Core0 before launching Core1; main's wait for ready is already satisfied.
- `src/gp2040.cpp:265-315`: ordinary loop runs USBHost process, input addons, driver, TinyUSB, PostprocessAddons and save check. Test14 Core0 auxiliary tick executes after PostprocessAddons; save occurs afterward.
- `src/gp2040.cpp:519-525`: Web Config and BOOTSEL hotkeys call `System::reboot`, rather than directly switching USB PHY in place. Full reset implementation remains **OPEN**.

## Current conclusion

**Not audit-closed.** Test14 is hardware-proven for observed gameplay, and the structural CI passed, but P1 flash lockout, timing and malformed-transaction recovery remain open. This is a documented risk inventory and initial source review, not a claim of exhaustive upstream tracing or simulated timing validation.
