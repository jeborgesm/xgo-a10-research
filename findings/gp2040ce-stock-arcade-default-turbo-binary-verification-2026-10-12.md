# Original XGO Arcade default map — direct BIN verification

**Source:** user-supplied `XGoAnalisis.zip`, member `bios/bisrv.asd`, 12,768,452 bytes. Read-only binary extraction and `struct.unpack_from('<12I', image, 0x008ddc44)` performed 2026-10-12.

**BIN:** The twelve little-endian Arcade/FBA default map records at file offset `0x008ddc44` are:

```
0x0000000a 0x0000000b 0x00000009 0x00000008 0x00000000 0x00000001
0x0000000a 0x0000000b 0x00000009 0x00000008 0x00000000 0x00000001
```

**BIN:** All twelve records have bit `0x00010000` **clear**: no default Arcade turbo for either player. The supplied ZIP has **zero** `.kmp` members. This corroborates `findings/embedded-default-keymap-patch-points.md` with an independent read of the actual original binary.

**Limit:** The archive is not necessarily a complete/current SD card; absence of `.kmp` in this ZIP does not prove the currently installed SFII game lacks an override. The stock Arcade default does not imply CPS-1 frontend always chooses this table; that runtime path still requires verification. It also does not rule out game/core repeat behavior or a different mapping elsewhere.

**Decision:** Do not pursue stock Arcade default turbo as leading explanation for the observed World Warrior HP/HK fault. Prioritize tracing six-button translation and serial waveform, and establish whether the actual game uses a per-ROM override.
