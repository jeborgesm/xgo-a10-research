# Generic external-core save-state contract

Status: **stock callback contract and slot paths confirmed; implementation path identified; hardware implementation pending**.

## Headline

The XGO stock in-game save-state UI delegates state persistence through two function-pointer slots. A fresh trace of the preserved firmware corrected an earlier label reversal:

```text
GFN_STATE_LOAD = 0x80c33a70   (gp - 0x0d04)
GFN_STATE_SAVE = 0x80c33ac0   (gp - 0x0cb4)
```

This matters now that the two callbacks are about to become distinct. The first hardware-proven external FCEUmm frontend installed the same disabled veneer into both addresses, so the reversal could not affect the successful gameplay test.

The firmware also confirms the stock four-slot state pathname policy rather than leaving it to inference:

```text
%s/save/%s.sa%d
%s/%s/save/%s.sa%d
```

The preserved card inventory contains matching `.sa0` through `.sa3` files, including examples under both `ROMS/save` and system-specific `FC/save`, `GB/save`, `GBA/save`, and `SFC/save` directories.

## Callback-address proof

Stock NES launcher `run_nes @ 0x8035f63c` installs its two core-specific state functions as follows:

```text
0x8035f674  t0 = 0x8035f50c
0x8035f678  a3 = 0x8035f3f0
0x8035f680  sw t0, -0x0d04(gp)   -> 0x80c33a70
0x8035f684  sw a3, -0x0cb4(gp)   -> 0x80c33ac0
```

The target semantics are unambiguous:

- `0x8035f50c` references `load_state:%s`, opens the state for reading, reconstructs/decompresses the payload, and invokes the core restore path;
- `0x8035f3f0` references `save_state:%s`, obtains the core state payload, compresses it, and writes the state file.

Therefore:

```text
0x80c33a70 = gfn_state_load
0x80c33ac0 = gfn_state_save
```

This ordering also matches the corresponding SF2000-family symbol ordering even though the absolute addresses differ.

## Current external-core path

The successful external frontend currently writes one shared disabled callback into both slots:

```text
GFN_STATE_LOAD = xgo_core_state_io;
GFN_STATE_SAVE = xgo_core_state_io;
```

and the reverse GP bridge currently targets:

```c
int xgo_disabled_state_io(const char *path)
{
    (void)path;
    return 0;
}
```

This exactly explains the hardware result:

```text
Select+Start
  -> external core exits normally
  -> stock save-state UI appears
  -> actual save/load operation fails
```

The frontend lifecycle is working. Serialization was intentionally absent.

## Stock slot pathname contract

The state UI constructs ordinary slot files with the firmware strings:

```text
%s/save/%s.sa%d
%s/%s/save/%s.sa%d
```

Observed preserved-card examples include:

```text
ROMS/save/Super Mario Bros 2 (J) [p1].NES.sa0
ROMS/save/Legend of Zelda, The - A Link to the Past (USA).SFC.sa1
FC/save/Mega Man 1.zfc.sa3
GB/save/Batman.zgb.sa0
GBA/save/Final Fight One.zgb.sa0
SFC/save/Battletoads In Battlemaniacs.zsf.sa0
```

The normal slot number is `0..3`.

This means the generic external runtime should **accept the stock pathname passed by the frontend**. It should not invent SF2000 Multicore's alternate `.state<slot>` naming scheme.

## XGO save-state bundle

Existing XGO firmware archaeology already established that `.saN` is not merely a raw libretro serializer dump. The XGO frontend/state path uses an outer bundle containing compressed emulator state plus separately compressed RGB565 preview metadata/image and a trailing thumbnail metadata offset.

That finding remains authoritative:

- `findings/save-state-and-core-dispatch.md`

The important implementation distinction is therefore:

```text
libretro serializer payload != complete XGO .saN file
```

A generic state bridge must preserve compatibility with the XGO's stock state-file expectations if we want stock slot previews and existing UI behavior to remain correct.

## Libretro core contract

A generic libretro core provides:

```c
size_t retro_serialize_size(void);
bool retro_serialize(void *data, size_t size);
bool retro_unserialize(const void *data, size_t size);
```

These are the emulator-specific operations needed below the XGO state container layer.

Conceptually:

```text
SAVE
stock save UI
  -> gfn_state_save(stock .saN path)
  -> stock->external GP veneer
  -> generic XGO state writer
       -> retro_serialize_size()
       -> retro_serialize()
       -> XGO-compatible compression/container handling
       -> stock path

LOAD
stock load UI
  -> gfn_state_load(stock .saN path)
  -> stock->external GP veneer
  -> generic XGO state reader
       -> parse/decompress XGO state bundle
       -> retro_unserialize()
```

## SF2000 Multicore comparison

Pinned SF2000 Multicore `core_api.c` independently confirms the high-level architecture: it assigns `gfn_state_load = state_load` and `gfn_state_save = state_save`, then uses `retro_serialize*` underneath those callbacks.

However, its implementation deliberately rewrites the frontend path to:

```text
/mnt/sda1/ROMS/save/<basename>.state<slot>
```

and writes its own raw serializer-oriented state file.

That is useful lineage evidence, but it is **not the XGO stock persistence contract**. For XGO we already have stronger device-specific evidence: `.sa0`..`.sa3` filenames and the stock bundle/preview format.

## Implementation design

The generic runtime should expose two distinct external functions and two distinct reverse GP veneers:

```c
int xgo_core_state_load(const char *frontend_path);
int xgo_core_state_save(const char *frontend_path);
```

The generic layer should:

1. preserve the frontend-supplied `.saN` path;
2. keep load and save slots distinct (`0x80c33a70` load, `0x80c33ac0` save);
3. use standard libretro serialize/unserialize below the XGO container layer;
4. verify every allocation, compression/decompression, file read/write, and libretro result;
5. keep stock filesystem calls behind GP-safe veneers;
6. return the stock `1` success / `0` failure convention;
7. avoid importing SF2000 path rewriting where XGO firmware evidence already defines the path;
8. preserve stock thumbnail/preview compatibility if practical rather than generating a private state format invisible to the stock UI.

## Why this belongs in the generic runtime

Nothing about the libretro serialization side is NES- or FCEUmm-specific. Once the XGO container adapter is implemented correctly, any core with working `retro_serialize*` support can participate in the stock save-state UI.

That makes it an ideal abstraction test before SNES:

```text
hardware-proven FCEUmm
  -> generic XGO state-container adapter
  -> verify NES save/load + slot preview
  -> reuse the same adapter for SNES Core #2
```

## First hardware validation

The first real implementation should be tested on the known-good FCEUmm path:

1. launch the same known-good NES ROM;
2. reach a visually unmistakable state;
3. Select+Start into the stock state UI;
4. save to one slot;
5. confirm a `.saN` file appears/changes at the expected stock location;
6. confirm the slot preview is generated correctly;
7. resume and alter the game state;
8. load the saved slot;
9. verify restoration;
10. reboot/relaunch and verify persistence.

The file size and outer bundle structure should then be compared against a stock-created NES state from the original card.

## Conclusion

The save-state feature gap is now narrower than it first appeared. We have:

- hardware-confirmed stock save-state UI entry;
- corrected load/save callback addresses;
- confirmed `.sa0`..`.sa3` pathname policy;
- documented XGO state bundle and preview format;
- standard libretro serialization primitives;
- already-proven bidirectional GP crossings.

The remaining task is implementation of the generic XGO state-container adapter, not discovery of an unknown save-state architecture.
