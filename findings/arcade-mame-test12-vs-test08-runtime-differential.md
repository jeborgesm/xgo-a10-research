# Classic Arcade MAME differential — working Test12 vs golden Test08

Date: 2026-09-08
Branch: `research-game-list-arcade-expansion`

## Exact binary comparison

Private CI compared:

```text
working MAME2000 Test12 firmware
SHA-256 16233cbb0d7b7e5a90d72a0eed04b873a3754bcdbaaedcea64fc1b3b972e3f1f

golden Test08 firmware
SHA-256 45831b0ea3c9ae336d82b240e6afe27167e5e83b88037152af237ab758ca1444
```

The images differ by 4,114 bytes across 837 small ranges, largely because later golden work replaced the old CPS1 loader cave with Audio OSD code and added the scheduler/audio-OSD frontend changes.

## External MAME stock-service contract

64-byte windows at every service used directly by the external MAME frontend were compared.

Byte-identical between Test12 and Test08:

```text
fopen                 0x802b3524
fread                 0x802b3698
fclose                0x802b2f40
dly_tsk               0x8030f480
retro_video_refresh   0x8035e70c
retro_audio_batch     0x8035e7d8
retro_input_poll      0x8035ea30
retro_input_state     0x8035eb20
retro_environment     0x8035eb64
run_fba               0x80360848
arcade cleanup        0x80360e00
osd_region_write      0x8035c31c
```

Therefore those services are not the Test15/16 regression source.

## Low-memory map

Also exact/safe:

```text
mapper        0x800014a0..0x800018ff   identical
new cave      0x80001900..0x8000217f   zero in both images
SNES loader   0x80002230..0x8000277f   identical
```

The new Classic Arcade loader cave is therefore not colliding with mapper or SNES code.

The historical Test12 loader cave `0x80002780..` is no longer free because golden firmware uses it for Audio OSD/frontend helper code.

## Critical runtime divergence

`run_emulator @ 0x8035ed48` is not byte-identical.

The first changed instruction is:

```text
0x8035ed6c

Test12:
  addiu a0,sp,16

Test08:
  j Audio-OSD game-enter helper
```

Later in the same function, golden Test08 contains the hardware-confirmed sibling wall-time scheduler transplant that replaced the original XGO incremental-debt timing loop.

The scheduler transplant was proven beneficial for stock FBA/CPS1, but MAME2000 was hardware-proven only before that transplant existed.

Thus the external MAME runtime contract changed after Test12 even though the core and callback functions themselves did not.

## Leading hypothesis

Test15/16 are loading the exact proven MAME2000 core into a newer `run_emulator()` implementation that has never been validated with MAME2000.

The stock-FBA scheduler optimization must not be assumed generic to arbitrary external libretro cores.

## Test20 diagnostic

Build from golden Test08, keep:
- fifth Arcade/list 11;
- current Classic Arcade loader;
- exact hardware-proven Test12 MAME2000 core;
- current mapper/SNES/game-list/scanner state.

For one diagnostic only, restore the complete Test12 `run_emulator()` body before installing the list-11 MAME hook.

If Pac-Man reaches MAME gameplay, the regression is conclusively inside later run-emulator modifications. Then the final solution should gate the old runner policy only for Classic Arcade rather than globally reverting golden firmware.

If Pac-Man still freezes, the runner differential is ruled out and investigation returns to the loader/core transfer contract.
