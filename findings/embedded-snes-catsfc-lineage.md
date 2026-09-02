# XGO embedded SNES core: CATSFC / Snes9x2005 lineage

Status: **core ancestry confirmed; libretro-layer source window strongly bounded to August-December 2016**.

Firmware fingerprint:

`869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf`

## Exact XGO strings

The preserved XGO firmware contains the SNES core identity:

```text
Snes9x 2005
v1.36
smc|fig|sfc|gd3|gd7|dx2|bsx|swc
```

It also contains the old core variable:

```text
catsfc_VideoMode
```

and the exact libretro pixel-format diagnostic:

```text
Frontend supports RGB565 - will use that instead of XRGB1555.
```

The core uses the historical 32-kHz Snes9x/CATSFC audio setup and retains multiple other Snes9x v1.36-era internals.

## CATSFC ancestry is direct, not merely conceptual

Historical `CATSFC-libretro` source exposes exactly:

```c
info->library_name    = "CATSFC(SNES9x)";
info->library_version = "v1.36";
info->valid_extensions = "smc|fig|sfc|gd3|gd7|dx2|bsx|swc";
```

and contains the same RGB565 negotiation text, 32-kHz playback configuration, ROM loader structures and Snes9x v1.36 internals visible in XGO.

The modern `libretro/snes9x2005` repository is historically descended from this CATSFC tree. Its history contains commit:

```text
545c5d00d6a1ee596d6992c498108cb3977a1b9a
2014-10-30
Merge branch 'master' of https://github.com/libretro/CATSFC-libretro
```

This confirms the source-lineage relationship independently of the XGO strings.

## The surviving `catsfc_VideoMode` variable gives a lower bound

The historical Snes9x2005 repository added the old Video Mode core option in:

```text
ab91b8e2097e84dc215c192584eddbfecac1a1f8
2015-11-01
add "Video Mode" core option.
```

The option retained the CATSFC-era key name:

```text
catsfc_VideoMode
```

XGO's stock environment callback explicitly recognizes this exact key, so its SNES integration is at least descended from a source state that includes this option.

## The displayed library name gives a tighter August 2016 lower bound

At historical commit:

```text
f17c30ecfb60f085cf928724d19d8c3ab693801f
2016-08-05
Lower-case x for name
```

`retro_get_system_info()` reports exactly:

```c
info->valid_extensions = "smc|fig|sfc|gd3|gd7|dx2|bsx|swc";
info->library_version  = "v1.36";
info->library_name     = "Snes9x 2005";
```

and the same source still contains:

```text
catsfc_SwapJoypads
catsfc_VideoMode
Frontend supports RGB565 - will use that instead of XRGB1555.
```

This matches the XGO identity tuple extremely closely.

Therefore a stock upstream state from **August 5, 2016 or later** is needed to naturally explain the XGO-visible library name while retaining the old CATSFC variable namespace.

## December 2016 gives an upper bound unless Data Frog removed the Git suffix

Historical commit:

```text
ccfbb241f4d1a2dbefe684e747c1920da498cbfe
2016-12-09
Use git version as library_version
```

changed the Snes9x2005 libretro identification so later normal builds append a Git revision to the `v1.36` library version.

The immediately preceding source state (`fe3ecfc7e1207ec895bfc939447a9916b42af561`) still reports exactly:

```c
info->library_version = "v1.36";
info->library_name    = "Snes9x 2005";
```

XGO contains plain:

```text
v1.36
```

with no adjacent Snes9x Git suffix.

The most natural upstream fingerprint is therefore:

```text
2016-08-05 <= XGO SNES libretro ancestry <= 2016-12-08
```

This is a **STRONG SOURCE-WINDOW INFERENCE**, not an exact commit identification, because a later Data Frog fork could theoretically have removed `GIT_VERSION` while retaining the older API strings.

## Why this is important

This makes the XGO SNES core one of the oldest identifiable console emulator lineages in the firmware:

```text
Snes9x2005/CATSFC  ~Aug-Dec 2016 source window
PicoDrive           Apr 2017 exact commit
FCEUmm               Aug 2017 exact commit
TGB Dual             Jan 2020 exact commit
gpSP                  May 2021 exact commit
```

The SNES core is therefore a compelling future upgrade candidate on age alone.

However, XGO's stock `run_emulator()` contains a special SNES (`system ID 0x08`) setup/audio branch, unlike NES/Sega/GBA/GB. A SNES replacement should therefore come **after** the simpler native NES external-core proof even though the stock SNES source lineage appears older.

## Additional historical clues

The old Snes9x2005 history after the apparent XGO source window contains numerous relevant fixes and features, including later sound fixes, SPC7110 work, overclock/cycle options and sprite-limit changes. This reinforces the potential compatibility gain from an updated core, but no specific later build should be assumed compatible with XGO until its HC15xx build and frontend contract are audited.

## Confidence

**CONFIRMED:** XGO embeds Snes9x 2005 v1.36 and retains `catsfc_VideoMode`.

**CONFIRMED:** CATSFC source contains the same v1.36 lineage, extensions, RGB565 behavior and older SNES internals.

**CONFIRMED:** Snes9x2005 historical source at August 5, 2016 has the exact XGO-visible library name/version tuple and CATSFC option namespace.

**CONFIRMED:** upstream began appending Git version information on December 9, 2016.

**STRONG INFERENCE:** XGO's SNES libretro layer derives from the August 5-December 8, 2016 upstream window unless the vendor intentionally reverted/removed the Git-version identification later.
