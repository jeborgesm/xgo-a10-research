# Generic external-core save-state contract

Status: **stock callback contract, scratch-file flow, and slot paths confirmed; implementation path identified; hardware implementation pending**.

## Headline

The XGO stock save-state path is more structured than a simple `state_save(.saN)` / `state_load(.saN)` pair.

A fresh trace of the preserved firmware establishes three important facts:

```text
gfn_state_load = 0x80c33a70   (gp - 0x0d04)
gfn_state_save = 0x80c33ac0   (gp - 0x0cb4)
```

and the stock save flow uses a **temporary `.kmp` scratch file** before producing the final `.sa0`..`.sa3` state bundle.

The first external FCEUmm gameplay build installed the same disabled callback in both state slots, so none of these distinctions affected the successful gameplay proof. They become critical now that real serialization is being implemented.

## Callback-address proof

Stock NES launcher `run_nes @ 0x8035f63c` installs:

```text
0x8035f674  t0 = 0x8035f50c
0x8035f678  a3 = 0x8035f3f0
0x8035f680  sw t0, -0x0d04(gp)   -> 0x80c33a70
0x8035f684  sw a3, -0x0cb4(gp)   -> 0x80c33ac0
```

The target semantics are unambiguous:

- `0x8035f50c` references `load_state:%s`, reads and decompresses state, then restores the active core;
- `0x8035f3f0` references `save_state:%s`, obtains the active core state, compresses it, and writes it.

Therefore:

```text
0x80c33a70 = gfn_state_load
0x80c33ac0 = gfn_state_save
```

The earlier opposite naming in parts of the research symbol map is superseded by `findings/state-callback-address-correction.md`.

## Current external-core path

The hardware-proven external frontend currently installs one disabled callback into both slots:

```c
GFN_STATE_LOAD = xgo_core_state_io;
GFN_STATE_SAVE = xgo_core_state_io;
```

`xgo_core_state_io` crosses from stock GP to external GP and reaches:

```c
int xgo_disabled_state_io(const char *path)
{
    (void)path;
    return 0;
}
```

Thus the observed hardware behavior is completely explained:

```text
Select+Start
  -> external FCEUmm exits normally
  -> stock save-state UI appears
  -> actual state operation returns failure
```

## The important scratch-file discovery

The stock save frontend around `0x80354150` constructs:

```text
%s/save/%s.kmp
```

then invokes the active callback through the save trampoline at `0x8035e5bc`.

For NES, that trampoline reaches `gfn_state_save @ 0x80c33ac0`, which `run_nes()` has pointed at `0x8035f3f0`.

So the callback invoked during the save path initially receives a temporary path such as:

```text
<root>/save/<game>.kmp
```

The frontend then reopens that temporary file and continues the common save/bundle/preview path.

This explains an otherwise odd artifact of the preserved card inventory: final `.saN` files exist, but no persistent `.kmp` state files remain. `.kmp` is scratch space used while constructing the final state bundle.

## Final slot paths

The frontend also contains and actively uses:

```text
%s/save/%s.sa%d
%s/%s/save/%s.sa%d
```

with normal slots `0..3`.

Preserved-card examples include:

```text
ROMS/save/Super Mario Bros 2 (J) [p1].NES.sa0
ROMS/save/Legend of Zelda, The - A Link to the Past (USA).SFC.sa1
FC/save/Mega Man 1.zfc.sa3
GB/save/Batman.zgb.sa0
GBA/save/Final Fight One.zgb.sa0
SFC/save/Battletoads In Battlemaniacs.zsf.sa0
```

The load UI path around `0x803558c8` constructs a `.saN` pathname and invokes the load trampoline at `0x8035e5b0`, which reaches `gfn_state_load @ 0x80c33a70`.

Therefore the stock callback contract is asymmetric:

```text
SAVE callback: temporary .kmp path
LOAD callback: final .saN path
```

## XGO state-file prefix and outer bundle

The NES state saver `0x8035f3f0` does not write a raw FCEUmm serializer dump. It obtains the core state, compresses it, and writes at least the state prefix:

```text
uint32_t compressed_state_size
uint8_t  compressed_state[compressed_state_size]
```

The surrounding stock frontend then completes the normal XGO save-state bundle, which existing archaeology has already shown contains a separately compressed RGB565 preview plus a trailing thumbnail metadata offset.

See:

- `findings/save-state-and-core-dispatch.md`

The corresponding loader `0x8035f50c` reads the state prefix from the final `.saN`, decompresses it, and passes the reconstructed emulator-state payload to the active core restore routine. The appended preview data is frontend metadata and does not need to be passed to the core.

This gives a clearer layering model:

```text
core serialization payload
  -> core-specific/generic state callback compresses prefix
  -> temporary .kmp during save
  -> stock frontend appends/assembles preview bundle
  -> final .saN

final .saN
  -> state-load callback reads/decompresses emulator-state prefix
  -> core unserialize
```

## Libretro contract below this layer

A generic libretro core provides:

```c
size_t retro_serialize_size(void);
bool retro_serialize(void *data, size_t size);
bool retro_unserialize(const void *data, size_t size);
```

The generic XGO callbacks can use these standard operations while preserving the stock file/container behavior.

### Generic save callback

Conceptually:

```text
stock save frontend
  -> gfn_state_save(temp .kmp path)
  -> stock->external GP veneer
  -> retro_serialize_size()
  -> retro_serialize(raw_state)
  -> compress raw_state using XGO-compatible zlib stream
  -> write [compressed_size][compressed_state] to .kmp
  -> return success
  -> stock frontend finishes .saN + preview
```

### Generic load callback

```text
stock load frontend
  -> gfn_state_load(final .saN path)
  -> stock->external GP veneer
  -> read compressed-state size/prefix
  -> decompress raw state
  -> retro_unserialize(raw_state)
  -> ignore trailing frontend preview metadata
  -> return success
```

## Stock compression helpers identified from calling convention

The stock NES save/load implementation provides two useful candidate services for a generic bridge.

Save path `0x8035f3f0` calls `0x80365e64` with:

```text
a0 = destination compressed buffer
a1 = pointer to destination length
a2 = raw serializer buffer
a3 = raw serializer length
```

This has the zlib `compress`/`compress2` family shape and is the compressor used by the stock state path.

Load path `0x8035f50c` calls `0x8021dcc0` with:

```text
a0 = raw destination buffer
a1 = pointer to raw destination length
a2 = compressed source buffer
a3 = compressed source length
```

This has the zlib `uncompress` shape and is the decompressor used by the stock state path.

Before production use, these two helpers should receive explicit GP-safe bridge names and a small ABI audit rather than being called as anonymous absolute addresses.

## SF2000 Multicore comparison

Pinned SF2000 Multicore confirms the same high-level state indirection and libretro serialization primitives, but its external-core implementation rewrites paths to its own `.state<slot>` files.

That implementation is useful lineage evidence, not the XGO persistence contract. XGO-specific firmware analysis now gives us the stronger model above: temporary `.kmp`, final `.saN`, compressed state prefix, and stock preview metadata.

## Implementation design

The generic runtime should expose two distinct external functions and two distinct stock->external GP veneers:

```c
int xgo_core_state_load(const char *frontend_path);
int xgo_core_state_save(const char *frontend_path);
```

The implementation should:

1. correct all remaining source labels so `0x80c33a70` is load and `0x80c33ac0` is save;
2. preserve the exact path supplied by the stock frontend;
3. expect `.kmp` scratch paths on save and `.saN` final paths on load;
4. serialize/unserialize through standard libretro functions;
5. reproduce the stock compressed-state prefix exactly;
6. let the existing stock frontend continue to own final preview/bundle construction;
7. verify all allocation, compression, file I/O, and libretro return values;
8. use GP-safe filesystem and compression veneers;
9. return the stock `1` success / `0` failure convention.

## Why this is better than writing a private state format

If we simply wrote an external-core `.stateN` file as SF2000 Multicore does, save/load could potentially work, but the XGO stock UI would no longer own the complete state artifact and its preview semantics.

Using the XGO's native callback contract instead gives us a stronger result:

```text
external libretro core
+ stock XGO save UI
+ stock slot naming
+ stock previews
+ stock persistence behavior
```

That is exactly the kind of generic integration we want before SNES.

## First hardware validation

The first real implementation should be tested on the known-good FCEUmm path:

1. launch the same known-good NES ROM;
2. reach a visually unmistakable state;
3. Select+Start into the stock state UI;
4. save to one slot;
5. confirm a final `.saN` is created/updated and no stale `.kmp` remains;
6. confirm the slot preview renders;
7. resume and alter the game state;
8. load the slot;
9. verify restoration;
10. reboot/relaunch and verify persistence;
11. compare resulting `.saN` structure against a stock-created NES state.

## Conclusion

The save-state gap is now an implementation problem with a well-defined contract, not an unexplored subsystem.

We have confirmed:

- state load/save callback addresses and corrected their labels;
- save trampoline -> temporary `.kmp` behavior;
- load trampoline -> final `.saN` behavior;
- four normal state slots;
- compressed emulator-state prefix;
- stock preview/bundle ownership;
- standard libretro serializer primitives;
- already-proven bidirectional GP crossings.

The next step is to add GP-safe compression helpers and implement this generic adapter on FCEUmm before reusing it for SNES.
