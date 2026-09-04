# Family button-mapper reuse candidates

Status: **STRONG REUSE PATH IDENTIFIED; BINARY-LIFTING PASS NEXT**

## Headline

We should not design the XGO on-device mapping controller from scratch.

There are two distinct pieces of prior art in the same firmware family that can be reused as guides:

1. the public pre-May SF2000 button-mapping tool source, which fully describes the mapping data model and record semantics;
2. the later SF2000 / GB300 stock firmware generation, which contains a real on-device "Joystick" / button-mapping editor and matching UI assets.

The second item is the highest-value reference for the missing XGO position-5 controller because it is a later branch of essentially the same stock frontend family.

## Public source: SF2000 buttonMappingChanger

`vonmillhausen/sf2000/tools/buttonMappingChanger.htm` is actual readable source code for manipulating both the old firmware-embedded/per-ROM mappings and the newer `Resources/KeyMapInfo.kmp` format.

Useful facts directly encoded by the tool include:

- mapping record order for the original family: `X, Y, L, A, B, R`;
- six remappable physical controls per player;
- 4-byte records;
- target libretro ID in the low portion of the record;
- turbo/autofire in the following 16-bit flag field;
- per-ROM mapping allocation of 48 bytes;
- per-system button-value sets;
- firmware transition points and mapping-table locations for March / April firmware;
- May 15 and later transition to the external `KeyMapInfo.kmp` file;
- the later `KeyMapInfo.kmp` file length of 288 bytes on SF2000.

This source is useful for the XGO editor's **data model and assignment semantics**, but it is a PC/web UI, not the stock on-device menu controller.

## Native on-device mapper exists in later family firmware

The SF2000 May 15 and later firmware introduced a real on-device button-mapping feature.

The resource set documents its UI architecture:

```text
cketp.bvs   console-selection images used by the mapping screen
mkhbc.rcv   six vertically-stacked handheld images with different buttons highlighted
lk7tc.bvs   transparent current-assignment labels
ztrba.nec   non-transparent assignment labels shown while changing an assignment
KeyMapInfo.kmp  persisted global mappings
```

This is very close to the controller we need to restore behind XGO's surviving `gpapi.bvs` shell.

The later implementation should therefore be treated as a behavioral / binary template rather than inventing a new navigation model.

## GB300 is an especially useful sibling

The GB300 stock firmware is another branch of the SF2000 family and exposes an on-device key-map editor from the pause menu as `Joystick`.

Public GB300 archaeology confirms:

- users can reassign buttons on-device;
- the editor persists changes into `KeyMapInfo.kmp`;
- the physical save order remains family-related;
- mappings include autofire (`T`) state;
- the editor highlights physical buttons visually;
- GB300 preserves several known bugs inherited from / related to the SF2000 design, including L/R presentation confusion;
- the file is created only after a non-default assignment is made on GB300.

Although GB300 stores seven mappings in some contexts and is not byte-for-byte compatible with XGO, its **menu state machine and interaction model** are much more relevant than any generic UI we could invent.

## Why direct source transplant is unlikely

The actual stock SF2000 / GB300 firmware editor is closed-source. Public repos primarily contain:

- firmware archaeology and documentation;
- mapping tools;
- resources;
- multicore/core code;
- firmware patches.

A clean C source file implementing the manufacturer's stock mapping screen has not been located.

Therefore the realistic reuse path is **binary archaeology**, not source-copying.

## Best next step: binary-diff / function lifting

The preferred approach is:

```text
older SF2000 branch / XGO lineage
        vs
May+ SF2000 or GB300 firmware with working mapper
        ↓
locate new mapping UI strings/assets/file-path references
        ↓
isolate added menu/controller functions
        ↓
recover state machine and event handling
        ↓
adapt only the controller logic to XGO
```

We do not need to transplant the later persistence layer. XGO already has the better per-ROM path:

```text
/<system>/save/<rom>.kmp
```

and a hardware-proven-compatible 48-byte runtime buffer plus stock writer.

The ideal hybrid is therefore:

```text
XGO gpapi.bvs position 5
        +
interaction/state-machine logic modeled on later SF2000/GB300 mapper
        +
XGO 48-byte per-game buffer
        +
XGO existing .kmp writer
```

## Design elements worth copying from the later mapper

The later family UI already answers questions we otherwise would have to invent:

1. how the user enters/exits mapping mode;
2. how a physical button is selected;
3. how the current assignment is displayed;
4. how assignments are cycled/selected;
5. how turbo is represented/toggled;
6. when a mapping is committed;
7. how cancel/default behavior works;
8. how system/controller context is represented;
9. how the menu redraw loop reacts to navigation events.

Even if we choose a simpler first XGO implementation, those behaviors should be recovered before design decisions are made.

## Important architectural difference

Do **not** blindly port `KeyMapInfo.kmp` persistence.

The XGO lineage has the older and arguably more useful per-game architecture:

```text
48-byte game-specific .kmp
```

whereas later SF2000 firmware moved to a global per-system mapping file.

So the reusable part is the **editor/controller behavior**, not its storage backend.

## Recommended implementation path

1. Obtain a known May+ SF2000 firmware or closely related GB300 firmware with working on-device mapping.
2. Locate `KeyMapInfo.kmp` string references and mapping-screen resource-name references in its executable.
3. Identify the menu action handler leading to the mapper.
4. Recover the mapping-editor function graph and input-event state machine.
5. Compare that graph against XGO's surviving menu code to identify shared functions / ancestry.
6. Reimplement or lift the smallest compatible controller layer into XGO position 5.
7. Bind its commit operation to XGO's existing 48-byte buffer and `.kmp` writer rather than the later global file.
8. Hardware-prove one A/B swap, then add the complete six-button editor.

## Conclusion

There is a wheel already available.

It is not available as one neat `button_mapper.c` file, but the family gives us both halves needed to avoid inventing behavior:

- public source for the mapping data semantics;
- a later stock firmware implementation for the on-device interaction model.

The next archaeology target should therefore be the later SF2000/GB300 mapper binary, not a fresh XGO UI design.
