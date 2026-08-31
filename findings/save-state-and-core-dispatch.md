# XGO Save-State Container and Core Dispatch

Status: **save-state bundle format, preview thumbnail, Arcade auto-state behavior, and core-specific dispatch confirmed by static analysis and SF2000-family corroboration**.

## Scope

This analysis follows the XGO save/load path, its zlib compression path, the pause-menu preview reader, the game launcher, and the runtime `.skp` loader. No hardware probing was required.

## Correction to the initial trace

An earlier pass stopped too early in the state writer and incorrectly concluded that `.saN` contained only a four-byte size followed by raw serialized emulator state. That interpretation was incomplete.

Following the compression and thumbnail writer shows that XGO uses the same general save-state bundle architecture documented for the SF2000 family: compressed emulator state followed by a compressed RGB565 preview image and a final offset pointing back to the thumbnail metadata.

The earlier statement that no thumbnail was appended is therefore withdrawn.

## Save-state file format

The frontend constructs state paths with:

```text
%s/save/%s.sa%d
```

with four ordinary slots, `.sa0` through `.sa3`.

The complete outer bundle is:

```c
struct XgoStateFile {
    uint32_t compressed_state_size;
    uint8_t  compressed_state[compressed_state_size];

    uint32_t thumbnail_width;
    uint32_t thumbnail_height;
    uint32_t compressed_thumbnail_size;
    uint8_t  compressed_thumbnail[compressed_thumbnail_size];

    uint32_t thumbnail_metadata_offset;
};
```

The final offset points to the thumbnail metadata beginning at the width field, allowing the preview reader to find the image without decoding the emulator-state block first.

The firmware contains zlib 1.2.5 and the save path reaches the compressor around `0x80365e64`.

**CONFIRMED:** emulator state is compressed before being stored in the `.saN` bundle.

**CONFIRMED:** the bundle contains a separately compressed raw RGB565 thumbnail.

## Save-slot preview

The pause-menu preview path around `0x80354150` reopens the selected `.saN`, locates the thumbnail metadata using the trailing offset, reads its width/height and compressed length, decompresses the RGB565 image, and renders it in the save/load UI.

This directly explains the visible per-slot preview behavior and removes the earlier need to hypothesize reconstruction from emulator RAM or a static background.

## Load behavior

The normal state loader reads the compressed emulator-state block, decompresses it, and passes the resulting serializer payload to the active core's load/unserialize callback.

The thumbnail is frontend metadata; it is not required to restore the emulated machine state.

## Core-specific save/load implementations

The frontend does not use one universal emulator serializer. It installs different callback sets for each core family and routes them through the common XGO state-bundle layer.

The launcher chooses the emulator family using the bitmask accumulated by the extension dispatcher. Confirmed native family bits remain:

```text
0x01 NES / FCEUmm
0x04 Sega / PicoDrive
0x08 SNES / Snes9x 2005
0x10 GBA / gpSP
0x20 GB/GBC / TGB Dual
0x40 Arcade / FBA
```

This is useful for a future firmware port because the XGO frontend is effectively an adapter layer around independent core callback sets rather than one monolithic emulator implementation.

## Arcade `.skp` files are automatic save states

The main emulator path constructs:

```text
%s/skp/%s.skp
```

checks whether the file exists, and if present invokes the active core callback through the trampoline at `0x8035e5b0`.

For the Arcade/FBA path this callback is the state loader.

Therefore `.skp` files are not generic configuration blobs: they are **automatic Arcade save states loaded immediately after game startup**.

The preserved card inventory contains:

- 185 Arcade `bin/*.zip` archives;
- 167 `.zip.skp` files under `ARCADE/skp`.

This behavior is independently consistent with documented SF2000-family firmware, where the stock Arcade library ships with per-game `.skp` states that are automatically loaded, often placing the game into a vendor-prepared state such as having a credit already inserted.

The exact vendor motivation can vary by title and should not be overstated; plausible reasons include skipping boot/setup sequences, avoiding problematic startup behavior, or presenting a known ready-to-play state.

Inventory mismatches remain useful archaeology:

- some current Arcade ZIPs have no matching `.skp`;
- some `.skp` names have no matching current ZIP;
- at least one malformed-looking inherited name exists (`gaia.zipip.skp`).

These are consistent with an inherited/revised stock game set rather than a perfectly regenerated XGO-specific inventory.

## Architecture implication

The software structure is now clearer:

```text
XGO frontend
   |
   +-- extension dispatcher -> system/core bitmask
   |
   +-- installs core callback set
   |      +-- init/run
   |      +-- state-size
   |      +-- serialize
   |      +-- unserialize
   |      +-- shutdown
   |
   +-- common save-state bundle
   |      +-- zlib-compressed core state
   |      +-- zlib-compressed RGB565 thumbnail
   |      +-- trailing thumbnail metadata offset
   |
   +-- Arcade startup path
          +-- optional <rom>.skp
          +-- automatic FBA state load
```

This modularity is one reason an SF2000/HC15xx multicore-style firmware is technically plausible on XGO: the vendor firmware already separates frontend services from emulator-specific state callbacks.

## Confidence

### CONFIRMED

- four ordinary `.sa0`-`.sa3` slots;
- compressed emulator-state block;
- appended compressed RGB565 thumbnail and dimensions;
- final offset to thumbnail metadata;
- pause-menu preview reads/decompresses that thumbnail;
- save/load wrappers dispatch through core-specific callbacks;
- `.skp` path is active at runtime;
- Arcade/FBA `.skp` files are automatically loaded save states.

### OPEN

- whether XGO state payloads are byte-compatible with state files generated by corresponding upstream/libretro core revisions on another platform;
- title-by-title reason the vendor supplied or omitted each Arcade `.skp`;
- whether any XGO-specific state metadata differs subtly from other SF2000-family revisions.