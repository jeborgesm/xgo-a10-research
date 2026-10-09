# GP2040-CE XGO Test01 — Runtime and recovery audit

Status: **offline source audit, not hardware proven**. Baseline: pinned GP2040-CE `3d1f32f7d02d418826b725b60208278d3be878c3`, overlay branch `research-gp2040ce-xgo-integration`. Preserve the successful Test01 UF2 and standalone Caveman baseline.

## Source-confirmed execution order

1. `GP2040::setup()` initializes storage, GPIO, gamepad and add-ons, then evaluates boot actions.
2. Normal button boot: S1+S2+Up requests ROM USB boot; S2 requests Web Config unless locked. GPIO-mapped boot has a separate exact-mask path.
3. `DriverManager::setup(mode)` constructs and initializes the selected driver. In XGO mode this calls `XGODriver::initialize()`, taking direct control of the native USB PHY.
4. The overlay skips `tusb_init` and `tud_task` only for XGO mode. Other modes retain upstream TinyUSB device initialization.
5. `GP2040::run()` still starts and processes `USBHostManager`, whose host/peripheral allocation needs separate confirmation.

## Runtime risk (source-confirmed, hardware effect unproven)

`XGODriver::process()` calls synchronous `emit_frame()` from the main loop. Waiting for the initial DP load transition can consume up to 20,000 microseconds each invocation; subsequent edges have 12 microsecond timeouts. This can delay the next button scan, add-on processing, USB-host processing, and housekeeping when the console is disconnected or clocking unexpectedly. A failed frame returns false; the loop retries immediately. This is **not** a demonstrated device hang, but it is a concrete responsiveness risk.

The current 12-slot sink/release sequence comes from the hardware-proven Caveman work. Do not alter its edge ordering or PHY configuration without an isolated timing proof.

## Required design gates before first flash

- **No-console fast path:** bound the per-loop work when no load signal arrives. A simple reduction of the 20 ms timeout is *not* proven safe; assess polling cadence against real XGO frame timing and preserve acquisition of a valid start edge.
- **Active-frame timing:** do not interleave slow GP2040 work inside the 12-slot transfer; measure whether a dedicated state machine, interrupt/PIO approach, or isolated core is appropriate before implementing.
- **USB ownership:** confirm that the PIO USB host path, Web Config boot and reboot transitions never reinitialize the native USB PHY while XGO owns it.
- **Recovery:** validate physical BOOTSEL recovery independent of firmware, normal S1+S2+Up and S2 boot combinations, and the GPIO-mapped boot configuration. Existing stored options may override default XGO mode.
- **Preservation:** OLED defaults, Web Config, profile changes, remapping, Turbo and SOCD must remain available; compilation is not functional proof.

## Current disposition

Test01 is a **build-proven, unflashed research artifact**. Do not present the current runtime as nonblocking or hardware safe. Next engineering step: design and review bounded frame acquisition against Caveman timing evidence, then build a separate Test02 candidate; retain Test01 unchanged for comparison.
