# GP2040-CE Test01 — interface closure (2026-10-08)

Upstream pinned revision: `3d1f32f7d02d418826b725b60208278d3be878c3`.

Verified directly against upstream:

- `headers/gpdriver.h` declares 13 pure virtual methods: initialize, initializeAux, process, processAux, get_report, set_report, vendor_control_xfer_cb, five descriptor getters, GetJoystickMidValue, and get_usb_auth_listener. An XGO driver must implement all of these; USB-specific callbacks can be inert because native TinyUSB device operation must be gated in XGO mode.
- `proto/enums.proto` has InputMode 0–17 and CONFIG=255. `INPUT_MODE_XGO=18` is unallocated at this pin.
- `configs/Pico/BoardConfig.h` is feature-rich (I2C display, turbo, LEDs, GPIO mappings). Copying it wholesale is a poor Test01 baseline: use a dedicated minimal XGO board configuration with exactly the known 12-button GPIO assignments and `DEFAULT_INPUT_MODE INPUT_MODE_XGO`.
- The caveman physical pin layout is GP2 R, GP3 Y, GP4 X, GP5 L, GP6 A, GP7 B, GP8 SELECT, GP9 START, GP10 UP, GP11 DOWN, GP12 LEFT, GP13 RIGHT. Translate these to GP2040 logical actions at board-config level, not in the XGO driver.
- Existing `GP2040::run()` passes processed `gamepad` directly to `GPDriver::process()`; no extra cross-core state fetch is necessary.

Important unresolved gate: the board configuration build selector and Core1 TinyUSB assumptions still need inspection before a firmware candidate can be called build-ready. No UF2 has been built or hardware-tested.
