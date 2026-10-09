# GP2040-CE XGO — core ownership and native PHY event audit

Evidence: upstream GP2040-CE pinned `3d1f32f7d02d418826b725b60208278d3be878c3` (`src/main.cpp`, `src/gp2040aux.cpp`, `src/usbhostmanager.cpp`); Pico SDK 2.3.1 RP2040 `hardware/regs/usb.h`; local Caveman `tools/rp2040-xgo-native-contra/main.c`. Offline source audit only.

## Core ownership: confirmed

- Core0: `GP2040::setup()`, then `GP2040::run()` scanning GPIO, processing add-ons, processing USB host and calling input driver `process()`.
- Core1: `GP2040Aux::setup()` and infinite `GP2040Aux::run()`; processes DisplayAddon, LEDs, speaker, rumble, reactive LEDs, and `inputDriver->processAux()`.
- Core1 is **not idle**. A second `multicore_launch_core1` is not an option; moving XGO work requires a cooperative `processAux()` implementation or a larger ownership redesign.
- Core0 copies processed gamepad state for Core1 after add-on processing. Any core1 responder would need an explicit concurrency-safe snapshot strategy. Reading Gamepad live state on core1 without synchronization is not acceptable.

## USB host: confirmed conditional

`USBHostManager::start()` calls `tuh_configure` and `tusb_init` for `BOARD_TUH_RHPORT` only if USB peripheral 0 is enabled and at least one USB listener exists. It then calls `tuh_task()` from core0. This is the PIO USB host path; it is not automatically the native PHY device path. Audit host pin/peripheral assignments and listener registration for XGO separately.

## Native PHY event mechanism: negative source finding, not proof of impossibility

RP2040 Pico SDK 2.3.1 exposes `USB_USBPHY_DIRECT_RX_DP_BITS` and `USB_USBPHY_DIRECT_RX_DM_BITS` as *read-only pin-state fields*. The standard USB interrupt status fields include protocol/controller events such as `TRANS_COMPLETE` and `HOST_CONN_DIS`, but no named `USB_INTS_RX_DP` edge interrupt is exposed in this register header. Thus **no documented raw DP/DM edge IRQ was found in this register surface**. This does not establish that no hardware workaround exists; no interrupt-driven XGO acquisition should be claimed without separate proof.

## Consequence for Test02

Do **not** simply repurpose core1 or shorten the 20 ms load timeout. Next investigate whether `XGODriver::processAux()` can perform an isolated responder while preserving the core1 addon loop and meeting the slot-0 deadline. A continuously blocking `processAux()` would itself starve OLED/LED updates, so a valid design must demonstrate measured timing or an alternative event mechanism. If core1 cannot satisfy these constraints, instrument the dedicated Caveman responder to capture host timing before attempting Test02.

Status: **design gates open; Test01 preserved and untested on hardware**.
