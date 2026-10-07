# GP2040-CE → XGO native transport integration feasibility

Status: **offline architecture investigation; no hardware candidate yet**  
Date: 2026-10-07  
XGO protected baseline: merge commit `5a133a1b2b3a72aebd1d45355a8650edea410204` (PR #59)

## Question

Can the hardware-proven minimal RP2040 "caveman controller" be integrated into the GP2040-CE environment without weakening or redesigning the proven XGO electrical/serialization contract?

## Short answer

**Yes; feasibility is high.** The cleanest design is an XGO output mode that consumes GP2040-CE's already-processed `GamepadState` and hands a 12-bit snapshot to the existing native XGO serializer. The serializer/electrical contract remains protected.

The main integration issue is not button mapping. It is ownership of the RP2040 native USB PHY: GP2040-CE normally initializes TinyUSB on that PHY, while XGO gameplay mode requires direct ownership of DP/DM with no USB enumeration.

## Evidence inspected upstream

Current upstream GP2040-CE `main` was inspected directly on 2026-10-07. Relevant files:

- `src/gp2040.cpp`
- `src/main.cpp`
- `src/gp2040aux.cpp`
- `src/drivermanager.cpp`
- `src/usbdriver.cpp`
- `headers/gpdriver.h`
- `headers/drivermanager.h`
- `headers/gamepad/GamepadState.h`
- `src/peripheralmanager.cpp`
- `proto/enums.proto`
- representative `MDMiniDriver` and `XInputDriver`

These are upstream observations, not XGO hardware facts.

## Upstream execution boundary

Core0 currently performs:

```text
GPIO debounce/read
    ↓
raw Gamepad state
    ↓
preprocess add-ons
    ↓
Gamepad::process() / MPGS / SOCD
    ↓
post-process add-ons
    ↓
hotkeys
    ↓
processed GamepadState copy
    ↓
GPDriver::process(gamepad)
    ↓
tud_task()
```

This is a strong insertion boundary. XGO does not need to replace GP2040-CE input processing.

`GamepadState` already contains digital d-pad and generic buttons B1/B2/B3/B4/L1/R1/L2/R2/S1/S2/etc. Therefore XGO serialization can consume normalized GP2040 state after remapping/SOCD/add-on processing.

## Protected XGO transport

Do not reinterpret this while integrating GP2040-CE.

Golden minimal responder behavior:

- native RP2040 USB PHY, not USB protocol
- DP = XGO DATA/load-like line
- DM = XGO CLOCK-like line
- DM receive-only
- DP only LOW sink or high-Z/released
- 12 active-low positions
- exact wire slots:
  0 R
  1 Y
  2 X
  3 L
  4 A
  5 B
  6 SELECT
  7 START
  8 UP
  9 DOWN
  10 LEFT
  11 RIGHT
- `LOAD_TIMEOUT_US = 20000`
- `EDGE_TIMEOUT_US = 12`
- state is snapshotted once before each transaction
- exact hardware-tested UF2 remains SHA-256 `313d9aefc078c09ffa363f6357b6a78f1c2582c5fce5333d88ec5a102a2ad503`

The later clean CI rebuild hash divergence is separately documented; do not silently substitute it for the HW-tested binary.

## Recommended logical mapping

First implementation should use GP2040-CE's generic controls rather than physical GPIO numbers:

```text
GP2040-CE       XGO slot
------------------------
R1          ->  R       0
B4          ->  Y       1
B3          ->  X       2
L1          ->  L       3
B1          ->  A       4
B2          ->  B       5
S1          ->  SELECT  6
S2          ->  START   7
UP          ->  UP      8
DOWN        ->  DOWN    9
LEFT        ->  LEFT   10
RIGHT       ->  RIGHT  11
```

This mapping is a proposed default, not yet HW-proven as a GP2040-CE mapping. The important architectural rule is that the XGO driver reads logical processed controls, so normal GP2040 profiles/remapping remain useful.

## Native USB PHY conflict

This is the primary integration seam.

In current `GP2040::run()`, GP2040-CE unconditionally:

1. calls `tusb_init(... TUSB_ROLE_DEVICE ...)`;
2. starts `USBHostManager`;
3. later calls the selected driver's `process(gamepad)`;
4. calls `tud_task()` every loop.

The golden XGO responder instead disables ordinary USB controller behavior and directly programs `usb_hw->main_ctrl`, `sie_ctrl`, `muxing`, `phy_direct` and `phy_direct_override`.

Therefore **TinyUSB device mode and XGO native mode must not own the native PHY simultaneously.**

### Recommended first architecture

Add an explicit XGO input/output mode and make native-USB servicing conditional:

```text
boot
 │
 ├─ WebConfig / BOOTSEL / normal USB mode
 │      └─ existing GP2040-CE TinyUSB path
 │
 └─ XGO mode
        ├─ initialize normal GP2040 input engine
        ├─ DO NOT tusb_init() native device PHY
        ├─ initialize XGO raw PHY transport
        ├─ process GPIO/add-ons/SOCD normally
        └─ XGODriver::process(Gamepad*) → 12-bit snapshot → emit_frame()
```

This preserves GP2040-CE configuration access as a **separate boot mode** instead of trying to multiplex USB and proprietary XGO signaling at runtime.

Holding the existing WebConfig boot combination can select `INPUT_MODE_CONFIG` before `GP2040::run()`; therefore a future XGO build can plausibly boot normally into XGO but reboot/boot into standard TinyUSB WebConfig when requested. This needs implementation proof, but upstream control flow supports it.

## GPDriver issue

`GPDriver` is currently USB-centric. It requires descriptor/report/vendor callback methods even for a protocol that is not USB.

Two implementation strategies:

### A. Minimal fork / first proof — recommended

Implement `XGODriver : GPDriver` with:

- real `initialize()`
- real `process(Gamepad*)`
- empty `initializeAux()` / `processAux()`
- harmless/null USB callback stubs
- `get_usb_auth_listener() == nullptr`

Then add a small capability check such as `usesUsbDevice()` or an explicit `INPUT_MODE_XGO` branch in `GP2040::run()` so XGO skips `tusb_init()` and `tud_task()`.

This changes little upstream architecture and is appropriate for the first proof.

### B. Cleaner long-term refactor

Separate "gamepad output protocol" from "USB device driver" interfaces so non-USB transports do not implement meaningless TinyUSB callbacks.

Architecturally cleaner, but too invasive for the first XGO proof and creates unnecessary upstream merge burden.

## Core ownership

Current GP2040-CE:

- Core0: button read, processing, USB host processing, output driver's `process()`, TinyUSB task.
- Core1: display/LED/rumble/etc add-ons and driver's `processAux()`.

The golden caveman responder is blocking/polling and waits up to 20 ms for XGO load before serializing a frame. XGO scans at about 16.032 ms (~62.37 Hz).

### First-proof recommendation

Keep XGO transport on **Core0** in `XGODriver::process()`.

Reason:

- closest to existing driver architecture;
- state can be snapshotted immediately after GP2040 processing;
- the blocking cadence naturally follows the XGO host poll;
- no new inter-core synchronization is required;
- preserves the exact known-good serializer as much as possible.

Cost: Core0 loop cadence becomes XGO-host-paced (~62 Hz) while connected. That can reduce servicing frequency for Core0 add-ons/USB-host features. For a first controller proof this is acceptable and measurable.

Do **not** move the serializer to Core1 merely for elegance before proving the simple design. Core1 already owns auxiliary add-ons, and a new cross-core state handoff/timing design would introduce unnecessary variables.

## USB host features

`USBHostManager::start()` and `process()` are part of current Core0 flow. Their exact relationship to native USB vs configured PIO USB peripherals needs care.

For the first XGO candidate, disable/avoid USB-host add-ons unless proven independent of the native PHY. They are not needed to prove the controller integration.

Do not infer that `PeripheralManager::initUSB()` itself conflicts with XGO: upstream uses a configurable peripheral USB abstraction and the direct native-device conflict is specifically established at `tusb_init()` / `tud_task()`. Confirm exact PIO/native resource use before enabling host features.

## Web Config strategy

A workable first product model is:

```text
normal boot        → XGO gameplay mode, native PHY belongs to XGO
WebConfig boot     → existing GP2040-CE config mode, native PHY belongs to TinyUSB
BOOTSEL/USB boot   → existing firmware update path
```

This avoids runtime PHY handoff. Configuration changes persist through GP2040-CE storage and are then consumed on the next XGO gameplay boot.

## What should remain available in XGO mode

Expected to retain with little/no XGO-specific work:

- GPIO mappings
- profiles
- debounce
- SOCD/MPGS processing
- hotkeys that do not require USB host/device semantics
- compatible input-processing add-ons
- Core1 display/LED features where they do not assume USB state

Needs explicit testing:

- profile changes/reinit while XGO transport is blocking
- turbo/macros at a ~62 Hz host scan
- display/LED behavior
- reboot hotkeys
- storage-save timing
- any add-on depending on USB host
- board LED behavior because our caveman test used GPIO25 as a transport heartbeat while GP2040-CE may own it differently

## Important implementation rule: lose the caveman GPIO numbers, keep the caveman transport

GP2..GP13 were only the minimal proof's direct physical inputs. They must **not** remain hardcoded inside the XGO transport after GP2040 integration.

The integrated path should be:

```text
arbitrary GP2040 board GPIO/profile
        ↓
GP2040 GamepadState
        ↓
XGO logical mapper
        ↓
12-bit immutable snapshot
        ↓
UNCHANGED XGO serializer
        ↓
native PHY
```

That is the actual benefit of GP2040-CE.

## Risk matrix

| Area | Current assessment | Reason |
|---|---|---|
| Logical button integration | LOW | GamepadState already provides normalized controls |
| XGO serialization | LOW | hardware-proven and should be transplanted unchanged |
| Native PHY ownership | MEDIUM | requires explicit TinyUSB bypass in XGO mode |
| Web configuration | LOW-MEDIUM | separate config boot is already architecturally supported |
| Core scheduling | MEDIUM | blocking ~16 ms XGO poll changes Core0 cadence |
| USB-host add-ons | MEDIUM/OPEN | resource interaction needs proof |
| Upstream maintainability | LOW-MEDIUM | small mode/driver patch if first design stays isolated |
| Electrical cable contract | CLOSED for prototype | Frankie V2 Jr topology reproduced; mechanical quality remains implementation concern |

## Feasibility conclusion

**GO.**

The GP2040-CE integration is technically reasonable. The evidence does not justify a large fork or scheduler rewrite. The smallest credible proof is:

1. branch from the merged XGO golden baseline;
2. pin an upstream GP2040-CE revision before importing code;
3. add `INPUT_MODE_XGO`;
4. add a minimal `XGODriver`;
5. conditionally skip native TinyUSB init/task in XGO mode;
6. translate processed logical state to the proven 12-bit XGO mask;
7. transplant the golden `raw_init()/emit_frame()` transport with behavior unchanged;
8. boot WebConfig separately for configuration;
9. build first; only then request hardware testing.

## First candidate acceptance criteria

Before calling any GP2040-CE candidate hardware-worthy:

- build succeeds from a pinned upstream revision;
- no TinyUSB device initialization/task executes in XGO gameplay mode;
- XGO raw PHY init is byte/behavior-equivalent to golden transport where practical;
- DM is never driven;
- DP remains LOW-sink/high-Z only;
- one immutable 12-bit state snapshot is serialized per XGO transaction;
- all 12 logical mappings are auditable;
- WebConfig/BOOTSEL path remains reachable separately;
- original merged caveman source and HW-tested hash remain untouched;
- candidate is clearly marked experimental and does not replace the golden baseline.

## Open questions for next investigation

1. Pin exact upstream GP2040-CE revision and determine best vendoring/fork strategy.
2. Locate all native TinyUSB initialization/callback assumptions that must be gated for XGO mode.
3. Determine whether `USBHostManager` can remain completely disabled in XGO mode without affecting ordinary GPIO controller operation.
4. Check generated protobuf/storage implications of adding `INPUT_MODE_XGO`.
5. Check Web Config UI implications: unknown enum values vs explicit XGO option.
6. Determine whether a board-config-only default can select XGO before Web Config knows about the new mode.
7. Measure/estimate consequences of the blocking serializer for turbo/macros/profile switching.
8. Only after those close: implement a build-only Test01 candidate.
