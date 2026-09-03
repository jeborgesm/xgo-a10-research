# GB300 v1 pause-menu mapper is the closest native XGO template

Status: **STRONG LINEAGE/BEHAVIORAL MATCH; BINARY LIFT STILL PENDING**

## Headline

The closest known native implementation of the XGO's newly resurrected fifth pause-menu mapping screen is not the later SF2000 global Settings mapper. It is the **GB300 v1 pause-menu `Joystick` mapper**.

This distinction matters because GB300 v1 preserves the same pause-menu architecture and the same `gpapi.bvs` fifth-position role that XGO now hardware-proves.

The best current lineage model is therefore:

```text
older family / XGO branch
Select+Start pause menu
  0..3 active
  4 -> gpapi.bvs mapping shell, disabled in navigation and no action handler

GB300 v1 descendant
Select+Start pause menu
  five visible items
  bottom item -> Joystick
  fifth selected background -> gpapi.bvs
  working native key mapper behind that slot
```

This is substantially stronger than treating a generic later SF2000 Settings screen as the implementation template.

## Direct resource-role convergence

Public GB300 v1 archaeology identifies:

```text
gpapi.bvs  RGB565 640x480  pause menu, fifth entry selected
```

XGO independently contains:

```text
Resources/gpapi.bvs  RGB565 640x480
```

and XGO machine-code analysis found it as entry 5 in the pause-menu background table.

The one-instruction XGO hardware probe then made index 4 reachable and physically displayed that exact screen on the device.

So both branches agree at the same semantic point:

```text
pause-menu item 5 == gpapi.bvs == controller/key-mapping context
```

That makes GB300 v1 the highest-priority binary-lifting target.

## GB300 v1 pause-menu behavior

GB300 documentation describes a five-word pause menu and identifies the bottom item as `Joystick`.

A companion asset:

```text
mczwq.ikb  RGB565 640x336
```

contains six system/device logos and is shown or hidden depending on whether the pause-menu focus is at the bottom `Joystick` item.

That gives a useful behavioral fingerprint for the native handler:

1. pause-menu navigation reaches item 4;
2. selection state 4 causes mapping-specific overlays to appear;
3. confirm enters a mapping interaction rather than returning to gameplay/save-state logic.

XGO currently has only step 1 and the base `gpapi.bvs` renderer after our patch.

## GB300 v1 mapper resources

GB300 v1 exposes the same logical architecture as the later family mapper but in the pause-menu path we care about.

Important resources include:

```text
hctml.ers   six device images with one shoulder/ABXY button highlighted
lk7tc.bvs   current logical key-name labels, including turbo variants
mczwq.ikb   system/device context shown at the Joystick pause item
ztrba.nec   assignment names, normal/turbo, plus focused variants
gpapi.bvs   fifth pause-menu background
```

The exact file names differ from later SF2000 for the highlighted-handheld strip (`hctml.ers` vs `mkhbc.rcv`), but the state model is the same family design.

## Mapping data model still converges with XGO

GB300 v1 `KeyMapInfo.kmp` documentation describes each system map as:

```text
24 bytes Player 1
24 bytes immediate repeat for Player 2
```

with physical save order:

```text
X, Y, L, A, B, R
```

That is the same six-control ordering already established for the older SF2000/XGO per-ROM format.

XGO independently has:

```text
12 x 4-byte records = 48 bytes
low 16 bits = logical libretro target
bit 16 / upper flag field = turbo/autofire
```

Thus GB300 v1's UI controller can be adapted conceptually without importing its global `KeyMapInfo.kmp` persistence.

## The manufacturer's assignment vocabulary

GB300's current-assignment label resource exposes the UI vocabulary:

```text
B / TB
C / TC
START
SELECT
UP
DOWN
L / TL
R / TR
A / TA
Z / TZ
X / TX
Y / TY
```

The assignment popup exposes action choices such as:

```text
A B X Y C Z L R
```

with turbo variants and focused-state duplicates.

This strongly supports a two-stage native interaction:

```text
physical-button browse
        |
      confirm
        v
logical-assignment browse/popup
        |
      confirm
        v
mapping record updated
```

The precise event buttons still need executable lifting; they should not be guessed.

## Why GB300 v1 outranks SF2000 v1.5 as the first binary target

SF2000 May 15 / v1.5 absolutely remains useful because it introduced the manufacturer's working mapping UI and provides clean family chronology.

However, its well-known mapper is associated with the newer global settings architecture and `KeyMapInfo.kmp` transition.

GB300 v1 is a closer structural match to XGO because public archaeology explicitly ties:

```text
gpapi.bvs
```

to:

```text
pause menu, fifth entry selected
```

and ties the fifth pause item to:

```text
Joystick
```

That is the exact slot we have now exposed on XGO hardware.

Therefore binary-lifting priority becomes:

```text
1. GB300 v1 stock BIOS (Dec 15 2023 family)
2. SF2000 May 15 / v1.5 for comparison
3. SF2000 v1.6/v1.71 only if later symbols/structure are easier to isolate
```

## Additional older lineage clue

A Super Drive Mini 2 / SG800 SD backup also contains a file named `gpapi.bvs` among a 2020-era resource family together with familiar names such as:

```text
bisrv.nec
d2d1.hgp
gpapi.bvs
pwsso.occ
```

That device keeps its executable firmware internally rather than on SD, so it does not immediately give us code to lift. Its resource reuse nevertheless confirms that these opaque pause/menu filenames predate the SF2000 and belong to a broader OEM software lineage.

This explains why XGO can contain a half-implemented mapping screen that SF2000 later replaced and GB300 later completed differently: these devices are inheriting and selectively compiling pieces of a much older shared frontend codebase.

## Practical lift plan

Once a GB300 v1 `bisrv.asd` is available locally:

1. locate string/resource references to `gpapi.bvs`, `hctml.ers`, `lk7tc.bvs`, `mczwq.ikb`, `ztrba.nec`, and `KeyMapInfo.kmp`;
2. find the five-entry pause-menu renderer and compare its structure to XGO `0x80354640`;
3. isolate the index-4 confirm/action branch absent from XGO;
4. trace the mapper's six-state physical-button selector;
5. identify its logical-target popup state and event handling;
6. identify the exact mapping-buffer write operation;
7. stop before the GB300 `KeyMapInfo.kmp` writer and substitute XGO's existing 48-byte per-ROM writer;
8. hardware-prove a single deliberate mapping change before importing the full UI behavior.

## Desired hybrid

```text
XGO stock Select+Start menu
        |
        +-- existing positions 0..3
        |
        +-- position 4: gpapi.bvs
                    |
                    +-- controller behavior lifted/modelled from GB300 v1 Joystick handler
                              |
                              +-- active XGO game supplies system context
                              +-- edit XGO 48-byte per-ROM map
                              +-- XGO set_keymap()
                              +-- XGO stock .kmp writer
```

That preserves the part of each branch that is best:

- GB300: completed native pause-menu editor behavior;
- XGO: older per-game mapping semantics and persistence.

## Evidence boundary

Hardware-proven on XGO:

- fifth pause-menu position can be exposed safely;
- it renders `gpapi.bvs`;
- no editor action survives in the XGO binary.

Publicly documented for GB300 v1:

- `gpapi.bvs` is the fifth selected pause-menu background;
- bottom pause-menu item is `Joystick`;
- on-device mappings are editable and persisted;
- mapping UI has six physical-button highlight states and logical/turbo assignment labels.

Still pending:

- direct machine-code ancestry between GB300 v1's index-4 handler and XGO's removed branch;
- exact native input-event state machine;
- exact commit/cancel behavior.

Those are now the next binary-archaeology targets.
