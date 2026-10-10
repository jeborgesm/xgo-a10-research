# GP2040-CE XGO responder scheduling — Test01/Test02 findings (2026-10-09)

## Hardware observations

- Test01 (Web Config XGO mode): OLED registers separate inputs, XGO reacts, Contra X/Y cause jump+shoot, Street Fighter P2 Start does not register.
- Test02 (skip USBHostManager::process() in XGO mode): OLED still registers inputs, XGO does not react in either game.
- Test02 change was reverted in commit b6f13cd7449e95f1966f0104c2ffdd9c38cb8db1.
- Test01 remains the last hardware-confirmed *communication* baseline, not a correct-input baseline.

## Pinned upstream source observations

GP2040-CE SHA 3d1f32f7d02d418826b725b60208278d3be878c3:

- src/gp2040.cpp GP2040::run(): debounce/read, USBHostManager::process(), add-on pre/process/post, gamepad->process(), hotkeys, processed-state copy, inputDriver->process(gamepad), tud_task(), postprocess, save checks.
- src/usbhostmanager.cpp USBHostManager::process(): calls tuh_task() when tuh_ready.
- src/gp2040aux.cpp GP2040Aux::run(): busy core1 add-on processing and inputDriver->processAux().
- XGO Test01 overlay suppresses native TinyUSB device init and tud_task in XGO mode, but retains USBHostManager::process().
- tools/rp2040-xgo-native-contra/main.c: dedicated polling loop with emit_frame(script[phase].mask) and no GP2040-CE input/add-on processing.
- integrations/gp2040ce-xgo-test01/src/drivers/xgo/XGODriver.cpp: same 12 slots, DATA load handshake and clock edge waits; calls emit_frame(map_mask(gamepad)) once per GP2040 main loop.

## Interpretation and limits

- Test02's no-response regression is consistent with altered loop pacing, but does NOT prove USB host processing is required for the electrical protocol.
- Matching source-level frame skeleton does NOT prove timing alignment, especially if polling begins during a host frame.
- OLED's correct individual indicators do NOT prove the XGO receiver samples correct bits.
- Do not randomly swap the proven 12 slot order, alter user's GPIO mapping, or disable USB-host processing again.

## Next engineering gate

Design a responder service that maintains the native PHY polling contract independently of variable input-processing work. Before implementing, audit RP2040 core1 ownership (OLED/add-ons), gamepad snapshot handoff and interrupt latency. Preserve all existing GP2040-CE functionality. Any candidate must be explicitly experimental, built by CI, and compared to Test01.
