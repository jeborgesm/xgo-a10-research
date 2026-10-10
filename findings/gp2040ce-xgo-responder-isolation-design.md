# XGO serial-responder isolation — engineering decision (post-Test13)

Status: SOURCE-REVIEWED DESIGN, NOT IMPLEMENTED, NOT HARDWARE-PROVEN.
Branch: `research-gp2040ce-xgo-integration`.
Pinned upstream: `OpenStickCommunity/GP2040-CE@3d1f32f7d02d418826b725b60208278d3be878c3`.

## Observed boundary
- Test10/11 diagnostic OLED: button RAW/PROC/output snapshot remained stable during held presses; Test10 playable, some unwanted repeat remained.
- Test13: full ButtonLayoutScreen and Input History restored; severe repeat and cross-button interpretation returned. OLED still displayed only the intended held button.
- Test12/13's idle-high recovery guard did not solve the behavior. Display workload correlation is observed, causation unproven.
- Do **not** attribute this to the GP2040-CE Turbo feature or adjust debounce as a serial fix.

## Source facts
- Overlay `integrations/gp2040ce-xgo-test01/src/drivers/xgo/XGODriver.cpp`: `XGODriver::process(Gamepad*)` maps processed inputs and synchronously calls `emit_frame(snapshot)`; `emit_frame` can block for 20 ms acquiring LOAD. The 12-slot train has 12 us edge timeouts and Core0 IRQ masking after LOAD detection.
- Pinned upstream `src/gp2040.cpp`: normal Core0 loop reads/processes gamepad, invokes `inputDriver->process(gamepad)`, and runs add-ons.
- Pinned upstream `src/main.cpp`: Core0 runs `GP2040`; Core1 runs `GP2040Aux`.
- Pinned upstream `src/gp2040aux.cpp`: Core1 processes auxiliary add-ons including the display. A simplistic move of `emit_frame` to Core1 would contend with this existing loop.
- RP2040 XGO protocol uses the USB PHY direct registers (`RX_DP`, `RX_DM`, `TX_DP_OE`), not ordinary GPIO; PIO is not a drop-in substitute.

## Required behavioral correction
Separate state production from console transmission:
1. GP2040-CE input pipeline produces the *latest complete* mapped 12-bit state and publishes it atomically; the responder never reads a partially updated Gamepad object.
2. A dedicated, continuously available responder owns all USB PHY direct access and LOAD/clock servicing. No OLED, Web Config, diagnostics counters, GPIO scanning, or add-on callback may execute in the responder's critical timing path.
3. Existing GP2040-CE services, display, Input History, configuration and non-XGO modes remain functional; preserve Xbox-style labels.
4. Startup and teardown must ensure exactly one core accesses PHY registers and prevent native TinyUSB device stack from reinitializing the PHY in XGO mode.
5. No frame may be restarted halfway through an already-active LOAD-low interval; release the line safely after failure and wait for an unambiguous new transaction boundary.

## Scheduling decision gate — do not bypass
Both RP2040 cores are already assigned: Core0 main input processing, Core1 auxiliary/display. The next implementation must first choose and validate a **complete** XGO-mode scheduler, not merely launch an extra core task:
- Preferred conceptual split: dedicated PHY responder on one core; GP2040 input and noncritical auxiliary/display processing on the other, with atomic state publication.
- Before editing, audit `GP2040Aux::setup/run`, `GP2040::setup/run`, `src/main.cpp`, storage and display ownership, watchdog and multicore lockout/flash-write semantics, and USB-host/peripheral dependencies.
- Check whether Core1's existing lockout victim handling and flash configuration writes can safely coexist with a time-critical responder. A dedicated responder may need to suspend safely for flash operations.
- If moving both GP2040 loops onto one core is unsafe, do not ship an unproven 'core swap'; design a different bounded scheduling strategy.

## Acceptance gate for next firmware candidate
- Source-level implementation with one explicit scheduling correction and no diagnostics-only release.
- CI build plus review of concurrency, USB PHY ownership, display state, Web Config, boot/config recovery, and all non-XGO modes.
- One focused hardware trial: SFII held Start, punch, and directions, while normal OLED/Input History remain active. Verify no unintended mixed buttons or rapid repeat. If failed, roll back to Test10.
- Test10 remains hardware-proven playable rollback; Test13 is NOT accepted as a gameplay baseline.

## Evidence limits
No claim yet that OLED alone causes the fault; Test12 recovery and Test13 display were different variables. No claim that the dual-core restructuring is safe until the startup, aux, flash, and PHY ownership contracts have been audited.
