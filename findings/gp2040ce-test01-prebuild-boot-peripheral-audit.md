# Test01 prebuild audit: boot selection and peripheral ownership

Date: 2026-10-08. Source pin: GP2040-CE `3d1f32f7d02d418826b725b60208278d3be878c3`.

## Verified (UP)

1. `GP2040::setup()` loads storage and peripheral configuration, initializes GPIO and add-ons, resolves `getButtonMappedBootAction()` (or configured boot-mode action), and calls `DriverManager::setup(inputMode)`. If the boot action is `ENTER_USB_MODE`, it calls `reset_usb_boot(0, 0)` and returns before driver setup.
2. `DriverManager::setup()` initializes the selected driver before `GP2040::run()`.
3. `GP2040::run()` normally initializes the native TinyUSB device, then calls `USBHostManager::start()`; Web Config additionally initializes RNDIS.
4. `PeripheralManager::initUSB()` configures optional PIO USB from saved peripheral options; `USBHostManager::start()` starts host only when port 0 is enabled **and** a listener exists.
5. Stock Pico `BoardConfig.h` already contains the user's proven GP0/GP1 OLED, full arcade buttons, GP14 Turbo, and GP15 Turbo LED.

## Consequences / corrections

- **Do not disable or replace the upstream boot-action selection** to force XGO. A valid configuration recovery path already exists upstream, but its precise button combination and round-trip must be established for this integration.
- **The board macro `DEFAULT_INPUT_MODE INPUT_MODE_XGO` is a default, not an override** of previously saved settings or explicit boot actions.
- **The native TinyUSB bypass belongs only to XGO gameplay**; Web Config and other modes retain standard TinyUSB.
- **PIO USB host is conditional, not inherently incompatible**; actual peripheral config, listeners, and shared scheduling must be checked before declaring support or conflict.
- **Core1 display is separate from Core0 XGO output** but hardware responsiveness remains OPEN.

## Offline readiness checklist

- [x] Six exact-match source anchors checked against pinned upstream, one occurrence each (2026-10-08).
- [x] Stock Pico board label and GP0/GP1 display definitions checked.
- [x] Driver initialization order, USB host conditions and boot-mode branch reviewed.
- [ ] Run `apply.py` on an actual clean pinned checkout.
- [ ] Compile using pinned SDK, TinyUSB, PIO USB and other upstream dependencies.
- [ ] Review compiler diagnostics and generated firmware.
- [ ] Establish and test reliable Web Config recovery without XGO cable contention.
- [ ] Test display, input mapping, profiles and XGO transport on hardware.

No compiled UF2 or integrated hardware proof exists. Golden Caveman is unchanged.
