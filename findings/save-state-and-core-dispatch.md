# XGO Save-State Container and Core Dispatch

Status: **save-state wrapper format and core-specific dispatch confirmed by static analysis**.

## Scope

This pass follows the XGO save/load path around `0x8035f3f0..0x80360840` and the game launcher around `0x80360b88..0x80360e48`. No hardware probing was required.

## Save-state file format

The frontend constructs state paths with:

```text
%s/save/%s.sa%d
```

The save routines for the individual emulator families all use the same outer file wrapper.

The generic sequence is:

1. call the active core's state-size/serialize-size function;
2. allocate a working buffer (the code reserves roughly twice the reported state size);
3. invoke that core's serializer into the buffer;
4. open the `.saN` file with `wb`;
5. write one 32-bit state-size value;
6. write exactly that many serialized-state bytes;
7. close the file and free the buffer.

Therefore the XGO `.saN` outer container is:

```c
struct XgoStateFile {
    uint32_t serialized_size;   // little-endian on this MIPS target
    uint8_t  serialized_state[serialized_size];
};
```

There is no separate frontend screenshot/thumbnail block written by this wrapper.

## Load behavior

The matching load routines:

1. open the `.saN` file;
2. read the leading 4-byte size;
3. allocate a buffer of that size;
4. read the serialized payload;
5. close the file;
6. pass the payload to the active core's unserialize/load-state callback;
7. free the buffer.

This explains why state files on the preserved card have highly variable sizes: the outer XGO format is only a four-byte length prefix around each emulator's own serialized state.

## Core-specific save/load implementations

The frontend does not use one universal emulator serializer. It installs different callback sets for each core family and then routes them through the same XGO wrapper.

Repeated save/load wrapper pairs are visible for the embedded cores, with the same logging strings:

```text
memsize:%d
save_state:%s
load_state:%s
load_state complete
```

The launcher chooses the emulator family using the bitmask accumulated by the extension dispatcher. Confirmed native family bits remain:

```text
0x01 NES / FCEUmm
0x04 Sega / PicoDrive
0x08 SNES / Snes9x 2005
0x10 GBA / gpSP
0x20 GB/GBC / TGB Dual
0x40 Arcade / FBA
```

This is useful for a future firmware port because the XGO frontend is effectively an adapter layer around six independent core callback sets rather than a monolithic emulator implementation.

## Preview implication

Because the frontend save wrapper writes only `uint32 size + serialized core state`, the save-slot preview artwork is **not stored as a distinct XGO thumbnail appended to `.saN`**.

Possible preview sources therefore narrow to:

- rendering/deriving a frame from emulator state at runtime;
- a core-specific framebuffer or video-memory component contained inside serialized state;
- a generic/static slot background when no preview can be reconstructed.

The exact preview-generation path remains open and should not yet be claimed.

## `.skp` path is runtime-active

The main emulator loop constructs:

```text
%s/skp/%s.skp
```

and attempts to open it after a periodic/event condition in the running-game path. This confirms `.skp` is not merely a dead filename string. The card inventory contains 167 such files under `ARCADE/skp`, strongly associating this mechanism with FBA/arcade per-game auxiliary state/configuration.

The exact `.skp` payload semantics remain to be decoded.

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
   +-- common XGO save wrapper
          +-- path: <folder>/save/<rom>.saN
          +-- uint32 payload length
          +-- core-native serialized bytes
```

This modularity is one reason an SF2000/HC15xx multicore-style firmware is technically plausible on XGO: the vendor firmware already separates frontend services from emulator-specific state callbacks.

## Confidence

### CONFIRMED

- `.saN` outer wrapper begins with a 4-byte serialized payload size;
- the remaining bytes are the core serializer output;
- save and load wrappers are repeated for different emulator families;
- no separate frontend thumbnail block is appended by the XGO state writer;
- `.skp` path construction/opening is active at runtime.

### OPEN

- exact save-slot preview-generation mechanism;
- exact `.skp` format and purpose;
- whether state payloads are byte-compatible with the corresponding upstream libretro core revisions on another platform.