# Hardware Test 04 — generic external-core save/load SUCCESS

Status: **HARDWARE CONFIRMED**

## Result

Generic-state Test 04 successfully saved and subsequently loaded an FCEUmm/Contra save state through the stock XGO save-state UI on real hardware.

Observed by hardware tester:

- external FCEUmm gameplay remained functional;
- Select+Start entered the stock XGO state UI;
- selecting a save slot successfully persisted state;
- loading that saved slot successfully restored the emulator state;
- the obsolete transient color diagnostic boxes were already confirmed absent in the preceding Test 03/04 line after removal of `XGO_DIAG` framebuffer writes.

This is the first hardware-confirmed proof that the external-core runtime can participate in the XGO's stock save/load lifecycle rather than merely run gameplay.

## Physical flight-recorder evidence

After the successful Save followed by successful Load, the diagnostic file recovered from the real SD card contained exactly:

```text
stage=L10-load-success
path=/mnt/sda1/FC/save/Contra 1.zfc.sa1
```

This is direct hardware evidence that the generic load adapter reached its final success checkpoint and that the stock frontend supplied the final slot pathname directly to the callback. The successful load used slot 1 (`.sa1`).

Preserve this observation together with the hardware-tested Test 04 core/package hashes below. The diagnostic file is intentionally redundant evidence: copies of copies are a feature.

## Hardware-proven state callback slots

The successful candidate uses the slot identities established by Test 03:

```text
0x80c33ac0 -> SAVE -> xgo_core_state_save -> xgo_state_save
0x80c33a70 -> LOAD -> xgo_core_state_load -> xgo_state_load
```

Operation identity is preserved by distinct callbacks. It is **not** inferred from the `.saN` pathname.

## Generic serialization path proven

Save success proves the following chain works sufficiently on hardware:

```text
stock XGO Save UI
 -> stock SAVE callback slot
 -> GP-safe reverse veneer
 -> retro_serialize_size()
 -> retro_serialize()
 -> stock-GP-safe compression helper
 -> state-file write
 -> success returned to stock frontend
```

Load success proves the inverse chain works sufficiently on hardware:

```text
stock XGO Load UI
 -> stock LOAD callback slot
 -> GP-safe reverse veneer
 -> state-file read
 -> stock-GP-safe decompression helper
 -> retro_unserialize()
 -> restored external-core state
```

The implementation is therefore structurally generic libretro state support, not an FCEUmm-specific state implementation. FCEUmm is the first hardware proof core.

## Candidate provenance

Branch: `research-generic-libretro-runtime`

Key source commits leading to the successful candidate:

- `1502264f4dfbc2aa5c6d1bc0a13beecb07a0822e` — swap state slots to hardware-proven identities
- `fc44068d5160e3c54f3bb0c6fe87afceba7e4f2d` — update generic-state CI for split state veneers

Successful generic-state workflow:

- run: `33709905341`
- artifact ID: `9876552847`
- artifact name: `xgo-generic-state-candidate`
- artifact digest: `sha256:9d8714b4a2a5bbfdba4189d0f31709d4d790679b8fa7221da0b2b87da32b9376`

Hardware-test core:

- path: `/cores/fceumm/core.xgc`
- SHA-256: `e98dcdddd925051cedd52c32db0e9fcaea9aafa76897103d8944bdc48149efd8`

User-facing Test 04 package:

- `xgo-generic-fceumm-save-state-test04.zip`
- SHA-256: `34e0a5e15f9e3b1e14357826677ece19a8873af7e3f7366a99ad1026c79bd37e`

The existing proven patched `bios/bisrv.asd` was retained; only `/cores/fceumm/core.xgc` was replaced for this test.

## Why the earlier tests failed

Test 02 demonstrated that `.saN` is not an operation discriminator: a Save operation itself received a final `.saN` pathname. The single path-based dispatcher therefore entered the load path incorrectly.

Test 03 split Save and Load but installed them according to the previously reversed slot labels. A Save attempt entered `xgo_state_load()` and produced `L2-fopen-fail` against a not-yet-existing `.saN` file.

Test 04 swapped the two slots according to the hardware evidence. Save and Load then both succeeded.

## Architectural conclusion

**Generic libretro serialization is now hardware proven on the XGO external-core runtime.**

The generic runtime now has hardware-confirmed support for:

1. external XGOC loading;
2. external libretro initialization and game loading;
3. stock XGO video/audio/input callbacks through GP-safe bridges;
4. normal gameplay and stock Select+Start lifecycle exit;
5. stock save-state UI integration;
6. generic `retro_serialize` / `retro_unserialize` persistence through distinct GP-safe Save/Load callbacks.

This materially reduces the remaining risk for Core #2 (SNES). A second core should be able to reuse the same state adapter if it implements the standard libretro serialization API correctly.

## Follow-up

The successful flight-recorder marker is now preserved. The diagnostic recorder can be removed from the normal generic runtime path after its historical implementation remains available in Git. Next steps are to update the README/handoff, preserve the successful milestone manifest, and proceed toward Core #2 while keeping the raised-black gameplay color issue as a separate investigation.
