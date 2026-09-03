# XGO position-5 mapper: renderer survives, editor logic appears compiled out

Status: **STRONG STATIC CONCLUSION; HARDWARE VISUAL PROBE STILL PENDING**

## Headline

The XGO stock in-game menu retains a genuine five-entry background-resource table and can render hidden position 5 (`gpapi.bvs`) if its menu index reaches 4. However, a deeper whole-firmware cross-reference pass now shows no surviving position-4 action-dispatch body and no independent editor path that manipulates the 48-byte keymap buffer.

The best-supported conclusion is therefore:

> XGO retained the old position-5 mapping **screen/resource and generic `.kmp` persistence machinery**, but the interactive mapping editor itself was removed or compiled out.

This is better than the earlier uncertainty because it tells us exactly what remains available for reuse.

## Five-entry in-game background table is direct XGO data

At firmware file offsets `0x00a3c318..0x00a3c328` the stock binary contains five consecutive filename pointers:

```text
0x00a3c318 -> 0x809a2ff0 -> dism.cef
0x00a3c31c -> 0x809a2ffc -> d2d1.hgp
0x00a3c320 -> 0x809a3008 -> bisrv.nec
0x00a3c324 -> 0x809a3014 -> pwsso.occ
0x00a3c328 -> 0x809a3020 -> gpapi.bvs
```

The menu renderer at runtime `0x80354640` loads the current menu index, multiplies it by four, adds it to base `0x80a3c318`, obtains the filename pointer, and builds the resource path with:

```text
%s/Resources/%s
```

Therefore index 4 naturally selects `gpapi.bvs`; no new rendering code or resource injection is needed.

## Position 4 is hidden by one explicit navigation bound

At runtime `0x80354ec0` / ASD file offset `0x00354ec0`:

```asm
slti s0,v1,3
```

Raw stock instruction:

```text
03 00 70 28    # 0x28700003
```

The menu increments the current index only while the old index is `< 3`, so reachable values are:

```text
0, 1, 2, 3
```

Changing the immediate to 4:

```text
04 00 70 28    # 0x28700004
```

would permit index 4 and should reveal the already-wired `gpapi.bvs` background.

This remains an excellent one-instruction visual hardware probe.

## Renderer behavior at index 4

The renderer has extra overlay/detail branches for the currently reachable menu positions. After drawing the common background it tests the menu index against the known values 0..3.

For values outside those cases, including index 4, it returns cleanly rather than indexing another unsafe table.

This matters operationally: the one-instruction navigation probe is expected to display the base `gpapi.bvs` screen without requiring any position-4 overlay data.

## Action dispatch confirms position 4 has no handler

The stock confirm/action dispatch is explicit:

```text
index 0 -> dedicated branch
index 1 -> dedicated branch
index 2 -> dedicated branch
index 3 -> dedicated branch
other   -> return to menu loop
```

There is no fifth case for index 4.

Thus simply exposing position 5 should make the screen visible, but pressing the normal confirm/action button there will not enter a mapper.

## Whole-firmware keymap-buffer cross-reference pass

The 48-byte runtime mapping buffer is at:

```text
0x810a0f58
```

A whole-firmware disassembly search for construction of that address found references only in:

1. the `.kmp` persistence/writer routine around runtime `0x80353fac`;
2. the stock `run_emulator` setup/load path around runtime `0x8035edb0` and related setup branches.

No third editor routine was found manipulating the same buffer.

This is important negative evidence: if an interactive mapping editor survived intact, we would expect it to read/write the same 12 mapping records or a closely related staging buffer.

## `set_keymap()` has only two callers

A whole-firmware call-site search for:

```text
set_keymap() @ 0x8035e83c
```

found only two direct calls:

```text
runtime ~0x80354030  -> the `.kmp` writer/persistence routine
runtime ~0x8035edd8  -> stock emulator launch/keymap load path
```

No third call exists from a hidden mapping editor.

This strongly reinforces that the interactive editor path is not merely unreachable by the menu index; its apply/update logic is absent from this XGO build.

## What *does* survive and is reusable

The important pieces are still unusually complete:

```text
position-5 mapping artwork (`gpapi.bvs`)
        +
five-entry menu background table
        +
48-byte per-game mapping buffer
        +
`set_keymap()` compiler
        +
per-ROM `%s/save/%s.kmp` path
        +
working `.kmp` writer
```

So we do not need to invent the low-level mapping architecture. We only need to restore an editor/controller layer between the already-existing screen and mapping buffer.

## `.kmp` writer recap with direct machine-code details

The writer uses the 48-byte buffer and, when changes are present:

1. performs the known Player-2 mirroring/permutation step;
2. calls `set_keymap()`;
3. constructs `%s/save/%s.kmp`;
4. opens the file using `"wb"`;
5. writes `12` elements of size `4` bytes;
6. closes the file.

This is direct executable confirmation of the 48-byte on-disk format.

The mirroring permutation table at `0x808dd2e0` begins:

```text
02 01 00 05 04 03 08 07 06 0b 0a 09
```

which explains the historical P1/P2 mirroring behavior inherited from the SF2000 family.

## Practical architecture from here

Instead of trying to resurrect nonexistent editor code, the lowest-risk design is now:

```text
stock Select+Start menu
        |
        +-- positions 0..3 unchanged
        |
        +-- position 4: gpapi.bvs
                    |
                    +-- small injected XGO mapping controller
                              |
                              +-- edit 12 existing mapping records
                              +-- reuse stock input/events
                              +-- reuse stock writer
                              +-- return to stock menu/game
```

That is much smaller than building a standalone UI and preserves the stock visual language.

## Next hardware/static steps

1. Build the one-instruction `slti 3 -> 4` probe and hardware-confirm that position 5 renders safely.
2. Identify the stock event codes and exact highlight coordinates needed to move among the six physical controls on `gpapi.bvs`.
3. Determine whether the existing generic text/image primitives can render the current target labels over the background, or whether the background alone contains enough fixed labels for a first prototype.
4. Implement the smallest possible position-4 action handler that edits one mapping record in RAM and invokes the already-proven writer.
5. Hardware-prove one deliberate button swap before expanding to a full editor.

## Evidence boundary

We can now say:

> The XGO has a hidden fifth in-game-menu screen for controller mapping, and the stock renderer can select it. The `.kmp` compiler/writer infrastructure also survives.

We should **not** say:

> The original interactive mapping editor survives and merely needs its menu entry enabled.

Current whole-firmware cross-reference evidence argues the opposite: the editor logic appears to have been removed, leaving a particularly convenient shell for us to fill.