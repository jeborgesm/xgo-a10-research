# Embedded XGO emulator identities

Status: **multiple stock libretro cores identified directly from the preserved XGO firmware; two exact upstream commits resolved**.

Firmware fingerprint:

`869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf`

## Why this matters

The XGO firmware is not built around one opaque monolithic emulator. It embeds several recognizable libretro cores, each carrying upstream-style library names, versions, extension lists, option keys and in several cases short Git commit identifiers.

This gives us an unusually strong upgrade path: instead of replacing mysterious OEM emulators, we can identify the exact stock lineage, compare it with later HC15xx-compatible forks, and replace one family at a time through the already-mapped `run_game()` dispatcher.

## NES: FCEUmm, exact 2017 upstream revision

The firmware contains a dense FCEUmm block including option keys such as:

```text
fceumm_palette
fceumm_region
fceumm_spritelimit
fceumm_overclocking
fceumm_overscan_*
fceumm_turbo_*
```

along with:

```text
git 7cdfc7e
FCEUmm
retro_init
fds|nes|unf|unif
Frontend supports RGB565 - will use that instead of XRGB1555.
```

The short SHA resolves exactly to upstream libretro FCEUmm:

```text
7cdfc7ead41bbd58cfee8f35d67fe28d39046f69
```

Date:

```text
2017-08-11 13:51:06 UTC
```

Commit message:

```text
(MSVC 2017) We need to check if VsInstallRoot is empty instead of undefined
```

Therefore the XGO stock NES emulator is **CONFIRMED to be based on an August 2017 FCEUmm source tree**.

### Distance to an HC15xx-ready replacement

The Data-Frog-Central Multicore core bundle pins its known HC15xx/SF2000-capable FCEUmm fork at:

```text
e6111e684e7a7761f3f1d6c80d0a825e2c8cdc7e
```

Date:

```text
2024-06-14
```

Commit message:

```text
add SF2000 platform
```

A repository comparison from the exact XGO stock commit to that HC15xx-ready snapshot reports:

```text
ahead_by     1055
total_commits 1055
```

Representative intervening changes visible near the HC15xx snapshot include additional/fixed mapper support such as mappers 128, 196, 319, 362, 398, 454 and 551, among many other changes.

This reframes the first external-core experiment:

**The proposed FCEUmm replacement is an in-family upgrade from an exact 2017 embedded FCEUmm revision to a 2024 HC15xx-ready FCEUmm lineage, not a foreign emulator substitution.**

That also explains why XGO's stock environment callback explicitly knows the `fceumm_region` core variable.

## Sega: PicoDrive 1.91, exact 2017 revision

The firmware identifies its Sega core as:

```text
PicoDrive
1.91 cbc93b6
bin|gen|smd|md|32x|cue|iso|sms
```

The short SHA resolves exactly in upstream `libretro/picodrive` to:

```text
cbc93b68dca1d72882d07b54bbe1ef25b980558a
```

Date:

```text
2017-04-18 20:22:19 UTC
```

Commit message:

```text
Merge pull request #54 from leiradel/master
Return correct memory info for SMS
```

That exact commit changed Master System system-RAM reporting from VRAM to Z80 RAM and corrected the reported size to `0x2000`.

Thus XGO's embedded PicoDrive is also **CONFIRMED to descend from a 2017 libretro tree**.

This is particularly interesting because the XGO frontend only exposes a subset of the formats that the embedded PicoDrive advertises internally. The dormant 32X/Sega-CD capability strings documented previously therefore belong to this exact old PicoDrive lineage rather than an unrelated OEM stub.

## GBA: gpSP v0.91, short SHA present

Firmware strings identify:

```text
gpSP
v0.91 261b2db
gba|bin|agb|gbz
```

The embedded core also exposes gpSP-style options for save method, frameskip threshold/interval, color correction, frame mixing and turbo, and uses the confirmed `/mnt/sda1/bios/gba_bios.bin` path.

The short Git SHA `261b2db` is present in the binary. Exact upstream/fork resolution is pending.

Status: **core identity/version CONFIRMED; exact repository commit not yet resolved**.

## Game Boy / Game Boy Color: TGB Dual v0.8.3, short SHA present

Firmware strings identify:

```text
TGB Dual
v0.8.3 9be31d3
gb|gbc|sgb
```

The embedded option surface includes link-cable emulation, screen layout/switching, single-screen multiplayer and audio-output controls characteristic of the TGB Dual libretro core.

The short Git SHA `9be31d3` is present in the binary. Exact upstream/fork resolution is pending.

Status: **core identity/version CONFIRMED; exact repository commit not yet resolved**.

## SNES: Snes9x 2005 v1.36

Firmware strings identify:

```text
Snes9x 2005
v1.36
smc|fig|sfc|gd3|gd7|dx2|bsx|swc
```

No short Git SHA has yet been found adjacent to this core's embedded metadata.

Status: **core identity/version CONFIRMED; exact source revision pending**.

## Architectural consequence

The stock core set is heterogeneous and old. At least the NES and Sega cores are directly tied to 2017 upstream revisions, while the firmware itself was assembled much later.

This strongly supports a staged upgrade strategy:

```text
stock main-list dispatcher
        |
        +-- NES  -> old embedded FCEUmm 2017 | external newer FCEUmm
        +-- Sega -> old embedded PicoDrive   | external newer core
        +-- SNES -> embedded Snes9x 2005     | external replacement
        +-- GBA  -> embedded gpSP            | external replacement
        +-- GB   -> embedded TGB Dual        | external replacement
```

The already-confirmed independent `run_game()` call sites allow each family to be upgraded independently while preserving the stock XGO menu, LCD, audio, input, battery and SD infrastructure.

## Save-state warning

Core lineage continuity does **not** imply save-state binary compatibility across multi-year emulator revisions. A first external-core build should use a separate save-state namespace or disable automatic state loading until compatibility is explicitly tested.
