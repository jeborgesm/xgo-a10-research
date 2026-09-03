# Family native mapper UI/state model

Status: **STRONG CROSS-FAMILY RECONSTRUCTION; NATIVE FIRMWARE LIFT STILL PENDING**

## Headline

The later SF2000 / GB300 button mapper is not merely generic inspiration for XGO. Its resource organization and documented behavior line up strongly with the exact dormant fifth pause-menu slot now hardware-proven on XGO.

The best-supported interpretation is:

> XGO retained an earlier position-5 button-mapping shell (`gpapi.bvs`) while later SF2000-family firmware completed/replaced that shell with the working `Joystick` editor.

That makes the later family mapper the natural behavioral template for rebuilding XGO position 5.

## Direct pause-menu convergence

Public GB300 archaeology explicitly describes a five-item pause menu whose bottom item is `Joystick`.

A separate resource, `mczwq.ikb`, contains six system/device images and is shown/hidden depending on whether the pause-menu selection is at the bottom `Joystick` item.

This is extremely significant because the XGO stock pause menu has now been hardware-proven to contain a hidden fifth position whose background is the controller-mapping screen `gpapi.bvs`.

The lineage therefore converges as:

```text
XGO / older branch
Select+Start pause menu
  position 0
  position 1
  position 2
  position 3
  position 4 -> dormant gpapi.bvs mapping shell

later SF2000 / GB300 branch
Select+Start pause menu
  ...
  bottom item -> Joystick
                  |
                  +-- working native mapper
```

This is stronger than a generic same-family similarity. It suggests the later `Joystick` implementation is a descendant of the exact feature slot that survives dormant in XGO.

## Later native mapper resource decomposition

The SF2000/GB300 resource tooling gives exact slice metadata for the mapping UI.

### Physical-button highlight strip

`mkhbc.rcv` is six vertically stacked 640x240 images.

For later SF2000 the visual slice order is:

```text
0 X
1 Y
2 R
3 A
4 B
5 L
```

For GB300 the visual slice order is:

```text
0 X
1 Y
2 L
3 A
4 B
5 R
```

This is valuable because the normal stored mapping order remains:

```text
X, Y, L, A, B, R
```

The SF2000 visual order therefore encodes the documented L/R presentation bug directly: the stock editor's physical highlight image swaps L and R relative to storage order.

This is an excellent discriminator when lifting the real firmware state machine: a six-state selection index feeding `mkhbc.rcv` should use the visual order above while the persistence index uses the mapping-record order.

## System-selection strip

`cketp.bvs` is six vertically stacked 640x136 platform-tab images.

Later SF2000 order:

```text
0 FC
1 SFC
2 MD
3 GB/GBC
4 GBA
5 MAME
```

GB300 family order differs where PCE replaces/extends systems, but the structural model remains six system tabs.

For XGO we do not need this global system selector for the first implementation because the active game already identifies the system and the desired persistence target is per-ROM.

However, this resource proves the manufacturer's mapper state machine had at least two independent selectors:

```text
selected system
selected physical button
```

XGO can collapse the first dimension by binding it to the currently running game/system.

## Current-assignment labels

`lk7tc.bvs` contains 24 tiny label slices: 12 logical targets, each with normal and turbo/autofire representation.

The decoded label vocabulary is:

```text
B / TB
C / TC
ST / ST
SL / SL
U / U
D / D
L / TL
R / TR
A / TA
Z / TZ
X / TX
Y / TY
```

This corresponds naturally to the libretro-style target space already recovered from XGO machine code.

Important implication:

> The manufacturer's UI model displays a physical button and its current *logical target*, rather than merely swapping fixed pairs.

That matches XGO's `set_keymap()` semantics exactly: each physical record stores a target libretro ID plus turbo flag.

## Assignment popup

`ztrba.nec` decomposes into 32 slices:

- eight logical action names, normal/turbo;
- the same eight names again in focused/highlighted form.

Base choices are:

```text
A, B, X, Y, C, Z, L, R
```

with `T` variants for autofire.

The focused duplicates strongly imply an explicit assignment-choice mode rather than direct one-button cycling:

```text
browse physical button
       ↓ confirm
assignment popup/selection
       ↓ browse logical target / turbo variant
       ↓ confirm
return to physical-button browse mode
```

Even before lifting the executable, the resource design therefore gives us a probable two-level state machine.

## Data-model convergence with XGO

The public SF2000 mapping tool independently states:

```text
presentation order: A, B, X, Y, L, R
storage order:      X, Y, L, A, B, R
record size:        4 bytes
per-player:         6 records = 24 bytes
per-ROM:            48 bytes
```

XGO machine-code archaeology independently recovered:

```text
12 x 4-byte records
low 16 bits = target libretro ID
bit 16 / second 16-bit field = turbo/autofire state
stock set_keymap()
stock 48-byte .kmp writer
```

Thus the later native mapper's UI model and the older XGO persistence model are structurally compatible even though later firmware moved persistence to global `KeyMapInfo.kmp`.

## Manufacturer interaction model we can reuse

The surviving resource architecture now supports this reconstructed native flow:

```text
pause menu -> Joystick / position 5
        |
        v
show active system context
        |
        v
physical-button browse mode
  X -> Y -> L/R -> A -> B -> R/L
        |
      confirm
        v
logical-assignment selection mode
  A/B/X/Y/C/Z/L/R + turbo variants
        |
      confirm
        v
update mapping record
        |
        v
redraw current-assignment labels
        |
 exit/commit
        v
persist mapping
```

The precise button events for enter/cancel/commit still need to be lifted from firmware; this document does not guess those controls.

## XGO adaptation: copy behavior, keep older persistence

The lowest-risk XGO design is now:

```text
hardware-proven hidden XGO position 5
        |
        +-- use current game/system; no global system selector required
        |
        +-- six-state physical-button selector
        |
        +-- logical target selector modeled on later family mapper
        |
        +-- edit XGO 48-byte runtime mapping buffer
        |
        +-- call existing XGO set_keymap()
        |
        +-- call existing XGO per-ROM .kmp writer
```

This preserves the manufacturer's interaction model while retaining the older per-game capability that later SF2000 firmware removed.

## First implementation can be much smaller than later firmware

For hardware proof we do not need to port every later asset or global-system feature.

A first faithful subset can be:

```text
position 5 enters mapper
UP/DOWN or LEFT/RIGHT selects one of six physical buttons
confirm enters assignment mode
assignment mode selects one of valid targets
confirm writes one 32-bit record
exit invokes stock XGO writer
```

The exact event mapping should be taken from the later native implementation once its executable handler is isolated, not invented.

## Firmware targets available for binary lift

Public preserved release assets exist for known mapper-capable SF2000 firmware, including:

```text
v1.5 (May 21/22 family)
  bisrv-V1.5-20230521.zip

v1.6 (Aug 03 family)
  bisrv.zip

v1.71 (Oct 13 family)
  bisrv-v1.71-10_13.zip
```

The v1.5 binary is the most attractive first diff target because it is closest to the May-era introduction/fix of the native mapping feature and therefore should contain less unrelated evolution than v1.6/v1.71.

## Binary-lifting fingerprints

Once a mapper-capable firmware image is available locally, search for these resources/strings first:

```text
KeyMapInfo.kmp
mkhbc.rcv
cketp.bvs
lk7tc.bvs
ztrba.nec
```

Then trace:

1. callers that load the physical-button strip;
2. six-state index arithmetic selecting 640x240 slices;
3. callers that load/render current-assignment labels;
4. the assignment-popup focus index;
5. writes to the KeyMapInfo mapping buffer;
6. the pause-menu `Joystick` dispatch branch;
7. exit/commit path and file writer.

The SF2000 L/R presentation bug gives a particularly useful fingerprint: UI state order and persistence order should differ at positions 2 and 5.

## Evidence boundary

Strongly supported now:

- later SF2000/GB300 has a real native mapper;
- it is exposed as/bound to the bottom `Joystick` position in the pause-menu family;
- XGO's newly hardware-proven hidden position 5 is a mapping screen;
- later mapper resources encode six physical-button states, system context, assignment labels, focused assignment choices and turbo variants;
- later UI state and XGO old mapping records are structurally compatible.

Still inference until native firmware binary lifting:

> The later mapper function is literally descended from the same position-5 handler source branch as XGO's dormant shell.

The pause-menu/resource convergence makes that the leading lineage hypothesis, but exact code ancestry should be proven by executable comparison.
