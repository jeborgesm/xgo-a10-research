# Test14 offline audit — post-hardware-success

Date: 2026-10-10
Protected firmware: CI run 38098786893, commit `fb911825123f07ea8fe12e4bdf881583a76de146`, artifact ID 11687143460.
Status: **HW gameplay PASS (user reported)**; offline structural checks added in later commits; **no Test14 firmware-source changes**.

## Evidence categories
- **HW**: User reported normal boot, Xbox-style OLED button display, responsive inputs, and no mixed/rapid-fire actions.
- **SRC**: Overlay source and pinned GP2040-CE source inspected.
- **INF**: Risk assessment from source behavior; not hardware-proven.
- **OPEN**: Tests/audits still required.

## SRC: what the architecture actually does
- GP2040 Core0 reads buttons, runs processing/add-ons, publishes a `std::atomic<uint16_t>` snapshot with release ordering.
- Dedicated Core1 loop loads snapshot with acquire ordering and handles USB PHY direct LOAD/CLOCK/data transactions.
- GP2040Aux setup and cooperative OLED/add-on tick moved onto Core0 in XGO mode; non-XGO retains stock Core1 auxiliary loop.
- XGO mode skips TinyUSB device initialization/task; native USB PHY is controlled by the responder.
- The responder latches a snapshot before each `emit_frame` call; button changes arriving during a frame apply to a later frame, preventing mixed-frame bit snapshots.

## SRC/INF: remaining hazards, ranked

### P1 — flash/config saves and Core1 lockout (OPEN)
The pinned upstream main Core1 entrypoint calls `multicore_lockout_victim_init()`, and Core0 may call `Storage::save()` from boot-mode changes and event handling. RP2040 flash programming typically coordinates the other core. The XGO responder masks interrupts for the clock train; lockout timing and recovery during active console transactions must be traced and verified. A stalled or missed transaction during a settings save is possible; this is **not** evidence of a present failure.

### P1 — responder critical-path diagnostics (SRC)
`emit_frame` still updates multiple atomic diagnostic counters, including on clock/LOAD failures while interrupts are disabled. These operations are not display work, but they add execution to an approximately 12-us edge budget. Static audit checks ownership but cannot certify worst-case latency. Do not modify proven Test14 to remove diagnostics without a separately versioned candidate and test.

### P1 — Web Config and recovery (OPEN)
The native USB device stack is intentionally disabled in XGO mode, and the XGO uses the USB PHY directly. Web Config should be evaluated as a distinct boot mode, including entry/reboot and settings persistence. Do not infer that the Web Config USB device can run simultaneously with XGO PHY transactions.

### P2 — USB host/add-ons (OPEN)
`USBHostManager::start/process` still runs on Core0; its PIO-USB interactions, pins and runtime effects are not validated for every optional peripheral. Display and other GP2040Aux add-ons now execute on Core0 in XGO mode, potentially increasing input sampling jitter, though hardware response is currently reported excellent.

### P2 — concurrency/visibility (OPEN)
The 16-bit snapshot is atomic and ordered. However, GP2040-CE's processed gamepad copy and display history structures were designed for different core ownership. The XGO scheduling removes some cross-core reads, but complete addon thread-affinity, event, and storage review remains open.

### P2 — non-XGO regression (OPEN)
The source retains non-XGO scheduling, but other input modes, USB device operation, and boot-mode switching need separate validation.

## Offline enforcement

Added `integrations/gp2040ce-xgo-test01/audit_test14.py` to CI after applying the overlay. It fails closed on missing structural contracts for Core1 responder ownership, atomic publication/acquisition, USB PHY signaling, XGO-specific TinyUSB gating, 12-slot mapping, Core0 auxiliary tick, and preservation of the non-XGO path.

These are source-level assertions, not cycle-accurate timing tests or functional USB PHY emulation.

## Baseline protection

Do not overwrite or silently re-label the Test14 UF2. Any behavioral change must receive a new test number, separate artifact and hardware validation. Test10 remains earlier rollback.
