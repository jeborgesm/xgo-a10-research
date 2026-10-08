# GP2040-CE XGO output — product goal and acceptance contract

Date: 2026-10-08
Status: user-confirmed requirements / architecture decision
Branch: `research-gp2040ce-xgo-integration`

## The critical distinction

**We are not upgrading Caveman to communicate better with XGO. We are adding XGO as an output protocol to the existing GP2040-CE controller platform.**

The standalone RP2040 Caveman firmware already proves the twelve-button XGO wire contract in hardware. Replicating those twelve buttons inside GP2040-CE without retaining GP2040-CE's display and configuration capabilities offers little value.

Caveman is therefore the **reference transport**, not the product architecture.

The target product is **GP2040-CE + XGO output mode**, preserving its existing controller experience.

## First-class requirements

1. Preserve display support, including the existing display subsystem, visualizations, and configuration options on supported hardware.
2. Preserve the familiar Web Config server and normal workflows for remapping, profiles, display settings, and add-ons.
3. Preserve GP2040-CE logical GPIO mapping, profiles, SOCD processing, turbo/macros and compatible add-ons.
4. Add XGO as an output mode using the proven twelve-slot serializer and protected DP/DM electrical rules.
5. Retain an understandable, reliable transition into Web Config / USB boot and back into XGO gameplay.
6. Keep the standalone hardware-proven Caveman source and binary untouched as a regression reference.

## Non-goal

A twelve-button GP2040-CE firmware that loses the display or Web Config is **not a completed integration**. It may be labeled a *transport-only experiment*, never a successful product deliverable.

## Ownership model

```text
GP2040-CE platform
 ├─ configurable GPIO, profiles, SOCD, add-ons
 ├─ display subsystem (existing)
 ├─ Web Config server (existing, separate USB boot mode)
 └─ XGO output driver (new)
      ├─ logical GamepadState → 12-bit mask
      └─ Caveman-derived native-PHY responder (protected)
           └─ Frankie cable → XGO
```

The native RP2040 USB PHY cannot be owned simultaneously by the proprietary XGO DP/DM protocol and TinyUSB USB-device Web Config. Separate boot modes are the current design. A different configuration transport is outside the scope of Test01.

## Evidence classes

- **HW**: standalone Caveman twelve-button XGO transport works on physical hardware.
- **SRC**: upstream GP2040-CE implements display/add-on and Web Config paths; existing driver consumes processed Gamepad state.
- **INF**: display features can coexist with the host-paced XGO driver without functional regression.
- **OPEN**: exact display responsiveness, Web Config entry/re-entry, config persistence, macros/turbo cadence, recovery and cross-mode behavior on the integrated build.

Do not promote INF or OPEN to HW before validation.

## Acceptance gates

### Gate A — transport proof (intermediate only)

- Reproducible build from pinned upstream GP2040-CE revision.
- Native USB PHY exclusivity in XGO gameplay mode.
- No DM drive, DP only LOW sink/high-Z.
- Correct twelve logical controls, unchanged serialization semantics.
- No changes to Caveman golden.

**Passing Gate A does not mean integration is complete.**

### Gate B — GP2040-CE preservation (required for completion)

- Existing display works and stays responsive during XGO gameplay.
- Existing Web Config can be entered predictably, used to edit and save settings, and exited back to XGO gameplay.
- Profile and button remapping configured in Web Config changes XGO behavior.
- Supported display options and controller add-ons are not silently removed.
- SOCD and other expected processing continue to operate.
- All twelve controls work in XGO games without freezing or unsafe electrical behavior.
- Recovery and firmware update path remains available.

**Only Gate A + Gate B together constitute a successful integration.**

## Implementation implications

- Keep existing GP2040-CE Core1/display architecture intact initially; audit scheduling instead of deleting display functionality.
- Use a display-capable board configuration rather than a permanently stripped Pico build.
- Preserve Web Config native-USB initialization in its separate mode; bypass it only in XGO gameplay.
- Prefer a small new output driver over restructuring the entire GP2040-CE platform.
- Label all intermediate firmware artifacts experimental until both gates pass.

## Current status

Requirements and acceptance contract documented. No integrated UF2 built or hardware-tested as of this document.
