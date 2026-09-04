# MAME2000 CPS1 offline closure — fully linked, CRC-compatible ROM lookup

Status: **OFFLINE LINK PASS; HARDWARE CANDIDATE JUSTIFIED**

## Cross-platform reason for the switch

The sibling HC15xx project `madcock/sf2000_multicore` explicitly classifies:

```text
MAME2000   fully working
FBA2012    working but major issues, not to release
```

Hardware Tests 08/09 on XGO independently reproduced a serious FBA2012 first-frame failure, with input ruled out and the stall narrowed to `BurnDrvFrame()` / CPU-device execution.

## Exact MAME2000 lineage

```text
madcock/libretro-mame2000
231929ab69e7538bc1d98f59634b8d7fee2ddde7

SF2000 libco support lineage:
madcock/libretro-common
9362316bf1da38160b324a1515bfb83e44ebd7af
```

The XGO build uses the exact SF2000 `sjlj_sf2000.c` coroutine backend selected by `-DSF2000`.

## Offline link result

GitHub Actions run:

```text
33904072463
```

Result:

```text
undefined symbols   0
payload             9,127,984 bytes
runtime             10,510,824 bytes
reserved window     13,479,424 bytes
headroom             2,968,600 bytes
```

XGOC:

```text
core-mame2000-cps1.xgc
SHA-256 353a749f677b68edf67dba52bea571b10de54e7c781cf675be6dfb69dd576761
```

The image is much larger than dedicated FBA2012 CPS1 but still fits the proven XGO external-core region with ~2.83 MiB free.

## Runtime model

Unlike FBA2012, MAME2000's SF2000 port does not execute the entire emulated frame directly inside a flat `retro_run()` call.

It uses libco:

```text
retro_load_game()
 -> co_active()
 -> co_create(0x10000, run_thread_proc)
 -> co_switch(core_thread)

retro_run()
 -> co_switch(core_thread)
```

This coroutine runtime is the same model the sibling SF2000 project marks fully working.

## XGO frontend policy

The external MAME2000 candidate reuses the already-closed XGO arcade path:

```text
0x810a0eb0 current arcade directory
0x8109fce8 current archive/game filename
-> <directory>/bin/<filename>
```

Environment policy:

```text
RGB565
audio 11025 Hz
stereo enabled
frameskip disabled initially
skip disclaimer enabled
game-info screen disabled
```

CPS1-only list discrimination remains outside the core.

## ROM-set compatibility — important closure

MAME2000's CPS1 driver is MAME 0.37b5-era and therefore names SFII ROM members using historical names such as:

```text
sf2e_30b.rom
sf2e_37b.rom
sf2gfx01.rom
...
```

However this does **not** require those exact filenames inside the XGO ZIP.

The MAME2000 ROM loader behaves as follows:

1. `readroms()` first calls `osd_fopen(driver, expected_name, ROM)`.
2. If that fails and the ROM has an expected CRC, it formats that CRC as 8 lowercase hex characters and retries `osd_fopen(driver, crc_string, ROM)`.
3. `load_zipped_file()` accepts an archive entry when either:
   - its filename matches the requested string, or
   - its CRC32 formatted as eight hex digits matches the requested string.

Therefore a newer/FBA-style `sf2.zip` can remain compatible even when member names differ, provided the actual ROM data CRCs match the MAME2000 driver requirements.

This significantly lowers the risk of testing against the existing XGO `ARCADE/bin/sf2.zip`.

## Save-state limitation

MAME2000 exposes libretro serialization stubs with size zero. The first hardware candidate should test gameplay and QUIT, not treat stock save-state support as an acceptance criterion.

If MAME2000 becomes the chosen CPS1 core, pause-menu state behavior will need a separate policy.

## First hardware strategy

Do **not** modify firmware again for the first MAME2000 test.

Use the already-tested CPS1-only loader and current hook, and place the MAME2000 XGOC at the loader's existing external-CPS1 path:

```text
/cores/fbalpha2012_cps1/core.xgc
```

The directory name is temporarily misleading but this makes the experiment core-only.

If hardware passes, move the loader to a clean generic CPS1/MAME2000 path in a separately audited follow-up.
