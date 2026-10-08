# GP2040-CE XGO Test01 implementation manifest

Date: 2026-10-07  
Status: **design frozen for build-only prototype; no hardware candidate yet**

## Upstream base

Pin exactly:

`OpenStickCommunity/GP2040-CE@3d1f32f7d02d418826b725b60208278d3be878c3`

Do not build Test01 from a floating `main`.

## Protected XGO reference

Source of truth for electrical/timing behavior:

`tools/rp2040-xgo-live-controller/main.c` from XGO merged golden baseline.

Do not modify that file for GP2040 work. Copy only the raw-PHY/serializer behavior into the integration experiment and keep provenance comments.

## Exact upstream patch surface for Test01

### 1. `proto/enums.proto`

Append only:

`INPUT_MODE_XGO = 18;`

Do not renumber existing modes.

### 2. `headers/drivers/xgo/XGODriver.h`

New class satisfying current `GPDriver` interface.

Real responsibilities:

- initialize raw XGO PHY
- convert processed `Gamepad` logical state to 12-bit XGO mask
- emit one XGO frame
- release DATA on all timeout/failure paths

USB descriptor/report methods are inert compatibility stubs only.

### 3. `src/drivers/xgo/XGODriver.cpp`

Two explicit layers:

- `mapStateToXgoMask(Gamepad*)`
- golden-derived `xgoEmitFrame(uint16_t)`

Proposed default logical map:

```text
R1 -> slot 0 R
B4 -> slot 1 Y
B3 -> slot 2 X
L1 -> slot 3 L
B1 -> slot 4 A
B2 -> slot 5 B
S1 -> slot 6 SELECT
S2 -> slot 7 START
UP -> slot 8
DOWN -> slot 9
LEFT -> slot 10
RIGHT -> slot 11
```

No direct button GPIO reads are allowed in this driver.

### 4. `src/drivermanager.cpp`

Include XGO driver and add:

`case INPUT_MODE_XGO: driver = new XGODriver(); break;`

### 5. `src/gp2040.cpp`

Determine XGO mode before native TinyUSB device initialization.

In XGO gameplay mode:

- skip native-device `tusb_init(TUD_OPT_RHPORT,...)`
- skip `tud_task()`

Do not globally remove TinyUSB. Config/other modes retain stock behavior.

For Test01, leave USBHostManager code structurally present but use a board configuration with PIO USB disabled.

### 6. Root `CMakeLists.txt`

Add `src/drivers/xgo/XGODriver.cpp` to explicit executable source list.

No need to remove TinyUSB libraries for Test01; runtime native-device ownership is what must be gated.

### 7. New XGO test board config

Prefer a dedicated `configs/XGOA10Test01/` derived from Pico rather than editing upstream Pico defaults.

Goals:

- default input mode XGO if board-config machinery supports the relevant macro/default path;
- ordinary GP2040 logical GPIO mappings;
- disable unnecessary USB-host peripheral configuration/add-ons for first proof;
- avoid claiming GPIO25 heartbeat ownership from caveman build;
- preserve a documented WebConfig boot route.

Board config **can** set the default mode at this revision: `src/config_utils.cpp` uses `DEFAULT_INPUT_MODE` when supplied by `BoardConfig.h`, otherwise falling back to XInput. Therefore the dedicated XGO Test01 board config should define `DEFAULT_INPUT_MODE INPUT_MODE_XGO`. Do not hardcode physical button GPIOs inside XGODriver.

## Web Config

Test01 does not require XGO to appear in the normal dropdown.

For later polished integration, update:

- Settings input-mode lists / validation
- boot-mode selection list
- localization label(s)

Separate WebConfig boot must continue to use stock TinyUSB.

## Static safety checks before hardware

Reject Test01 if any check fails:

1. XGO mode can reach `tusb_init(...DEVICE...)`.
2. XGO mode can reach `tud_task()`.
3. XGO serializer ever enables DM output.
4. DP behavior differs from LOW sink / high-Z release.
5. serializer reads physical GPIOs rather than supplied logical mask.
6. frame mask can mutate while 12 slots are being serialized.
7. timeout path leaves DP driven.
8. golden caveman source is modified.
9. build is not pinned to upstream commit.
10. config/BOOTSEL recovery route is lost.

## First hardware test, when eventually authorized

Keep it intentionally boring:

1. boot disconnected from XGO and verify expected startup/recovery behavior;
2. enter WebConfig/recovery separately to prove USB mode remains available;
3. connect through known-good reinforced Frankie V2 Jr;
4. verify idle does not freeze XGO;
5. verify LEFT/RIGHT first;
6. verify one face button;
7. verify all 12 using Street Fighter II;
8. verify at least one GP2040 remapping/profile change actually changes the logical XGO result;
9. only then exercise turbo/macros/add-ons.

## Non-goals for Test01

- runtime switching between USB device and XGO PHY ownership
- GPDriver framework refactor
- moving serializer to Core1
- USB-host controller passthrough
- polished Web Config XGO UI
- analog-to-digital policy beyond existing GP2040 processing
- replacing or deleting the caveman golden

The purpose of Test01 is one question only:

> Can stock GP2040-CE input processing feed the already-proven XGO native transport without corrupting its electrical/timing contract?


## Board-default mechanism confirmed

Pinned upstream `src/config_utils.cpp` explicitly provides:

```cpp
#ifndef DEFAULT_INPUT_MODE
#define DEFAULT_INPUT_MODE INPUT_MODE_XINPUT
#endif
```

and consumes board configuration through `BoardConfig.h`. Therefore Test01 can boot XGO by default from its dedicated board configuration without altering generic storage semantics or requiring the Web Config UI to understand XGO before the first proof.

This closes manifest open item #6 from the feasibility document.


## User requirement update — display and Web Config preservation (2026-10-08)

The user regularly uses displays on their GP2040-CE controllers and frequently uses the web configuration interface. These are **first-class requirements**, not expendable optional features.

Test01 may isolate transport variables temporarily, but must not be presented as the final feature target. Preserve the GP2040-CE display/add-on architecture and keep a reliable boot/reboot path into the standard Web Config server. XGO gameplay owns the native USB PHY; Web Config owns it only in a separate boot mode. Do not claim simultaneous native-USB gameplay and USB Web Config access.

Implementation stages:
1. Prove XGO transport with GP2040 input processing while leaving display subsystem code intact.
2. Validate existing I2C/SPI display initialization and Core1 rendering during XGO host-paced gameplay; do not assume success without tests.
3. Validate reliable entry into Web Config, setting persistence, return to XGO mode, and continued display operation.
4. Only disable specific display or add-on features if a measured conflict is established and documented.

Review previous minimal-board advice: a dedicated board configuration should retain usable display wiring/options (or a display-capable variant), rather than permanently omit display support. Document how Web Config is entered without assuming the XGO cable can act as a USB data connection at the same time.
