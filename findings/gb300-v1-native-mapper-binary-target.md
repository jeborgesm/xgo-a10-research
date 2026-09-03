# GB300 v1 native mapper binary target

Status: **BINARY SOURCE PINNED; FUNCTION LIFT PENDING**

## Target firmware

A public stock GB300 firmware repository contains the exact binary needed for the next mapper archaeology pass:

```text
repository: znx-x/gb300-firmware
path:       bios/bisrv.asd
Git blob:   971de36940e0648fc00fc495ddcf56127c176326
size:       7,299,832 bytes
```

The repository release identifies this as **GB300 Original Firmware v1.0.0** and provides a full firmware package. This is currently the strongest binary target because public GB300 documentation identifies the same `gpapi.bvs` pause-menu fifth position as the working `Joystick` / key-mapping slot.

## Why this target matters

XGO hardware has now proven that its otherwise-disabled fifth pause-menu position renders `gpapi.bvs`.

GB300 v1 documentation independently identifies:

```text
gpapi.bvs -> pause menu, fifth entry selected
```

and exposes a working native mapper from that bottom pause-menu position.

Therefore GB300 v1 is the best current candidate for lifting the missing action/controller logic rather than designing replacement behavior from scratch.

## Binary fingerprints for the lift

Search the GB300 v1 `bisrv.asd` for:

```text
gpapi.bvs
hctml.ers
lk7tc.bvs
mczwq.ikb
ztrba.nec
KeyMapInfo.kmp
```

Then trace code references to recover:

1. position-5 pause-menu dispatch;
2. six-state physical-button selection;
3. assignment-popup state;
4. logical-target + turbo encoding;
5. mapping-buffer mutation;
6. commit/cancel behavior;
7. `KeyMapInfo.kmp` writer path.

## XGO adaptation goal

Do not port GB300 persistence blindly.

The intended hybrid remains:

```text
GB300 native mapper interaction/state machine
        +
XGO hardware-proven gpapi.bvs position 5
        +
XGO 48-byte per-game mapping buffer
        +
XGO existing set_keymap()
        +
XGO existing /<system>/save/<rom>.kmp writer
```

This preserves the manufacturer's on-device workflow while retaining XGO's more useful per-game mapping model.

## Analysis automation

The branch now also contains:

```text
.github/workflows/xgo-gb300-mapper-lift.yml
```

which fetches the public GB300 binary in GitHub Actions, fingerprints the mapper strings, searches for direct pointer/address-materialization references, and disassembles candidate MIPS code windows into an artifact named:

```text
gb300-v1-mapper-lift
```

The next evidence milestone is the first concrete native code xref from one of these mapper resources or `KeyMapInfo.kmp` into the GB300 position-5 controller graph.
