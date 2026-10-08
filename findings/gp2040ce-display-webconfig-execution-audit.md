# Display and Web Config execution audit — 2026-10-08

Upstream source pin: `OpenStickCommunity/GP2040-CE@3d1f32f7d02d418826b725b60208278d3be878c3`.

## Source-verified Core1 display ownership (UP)

`src/main.cpp` initializes GP2040 on Core0, launches `core1()` using `multicore_launch_core1`, waits for Core1 ready, then enters `GP2040::run()`. `src/gp2040aux.cpp` creates `DisplayAddon` and other auxiliary add-ons on Core1. `GP2040Aux::run()` repeatedly calls add-on Preprocess/Process and optional driver `processAux()`.

Consequently, a blocking XGO transport in Core0's `GPDriver::process()` does not directly block the Core1 display loop. **This is a source-level architectural advantage, not hardware proof of display responsiveness.** Shared state, storage locks, interrupt interactions, and scheduling still require integration testing.

## Web Config mode (UP)

`DriverManager::isConfigMode()` checks `inputMode == INPUT_MODE_CONFIG`. `GP2040::run()` starts the standard TinyUSB device stack and calls `rndis_init(WEB_CONFIG_HOSTNAME)` when config mode is selected. Its config-mode loop calls the selected driver, reboot-hotkey logic, and save/reboot processing.

Proposed XGO gating must be scoped to **only** `INPUT_MODE_XGO`; it must not accidentally suppress TinyUSB or RNDIS for `INPUT_MODE_CONFIG`. Normal GP2040 USB modes must also remain unchanged.

## New integration checkpoint

A display-preserving implementation should keep the upstream `GP2040Aux::setup()`, `GP2040Aux::run()`, `DisplayAddon`, and `main.cpp` lifecycle unchanged in Test01. The new XGO driver can have empty `initializeAux()` and `processAux()` while existing display processing continues on Core1.

The first combined test should explicitly confirm display refresh while XGO polls and configuration round-trip (Web Config → save mappings/display settings → reboot XGO → display and mappings persist).

## Evidence labels

- UP: Core1 display/add-on lifecycle and separate Web Config path verified from upstream source.
- INF: Core1 display should remain scheduled while Core0 waits for XGO.
- OPEN: actual display frame rate, add-on compatibility, reliable Web Config entry, configuration persistence, and hardware test on integrated firmware.

No build or hardware verification claimed.
