# XGO Emulator Runtime and Libretro Environment Contract

Status: **the six statically linked emulator cores, five exact upstream commit IDs, the Snes9x 2005 revision family, and the frontend's restricted core-option contract are confirmed by static analysis**.

## Scope and specimen

This pass analyzes the XGO `bios/bisrv.asd` specimen with SHA-256:

```text
869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf
```

Virtual addresses below use the firmware's established `0x80000000 + file offset` mapping, including the `LCFG` header.

The goals were to answer four questions:

1. Which emulator cores and revisions are actually compiled into the XGO firmware?
2. Are they loaded as external modules or linked into the main executable?
3. Do the many embedded core-option strings represent functional settings?
4. How closely does this runtime match the Data Frog SF2000 software lineage?

## Confirmed core inventory and provenance

The binary retains upstream library/version strings for all six cores. Five include exact Git commit IDs.

| Native family bit | System family | Embedded core/version string | Firmware string offset | Upstream comparison | Confidence |
| --- | --- | --- | ---: | --- | --- |
| `0x01` | NES | `FCEUmm`, `git 7cdfc7e` | `0x009b52e0` | [libretro-fceumm `7cdfc7e`](https://github.com/libretro/libretro-fceumm/commit/7cdfc7e) | **Exact commit ID embedded** |
| `0x04` | Sega | `PicoDrive`, `1.91 cbc93b6` | `0x009b7810` | [PicoDrive `cbc93b6`](https://github.com/libretro/picodrive/commit/cbc93b6) | **Exact version and commit ID embedded** |
| `0x08` | SNES | `Snes9x 2005`, `v1.36` | `0x009b88cc` | [Snes9x 2005 `b94a804`](https://github.com/libretro/snes9x2005/commit/b94a804) | **Version and interface fingerprint match** |
| `0x10` | GBA | `v0.91 261b2db` | `0x009b9d70` | [gpSP `261b2db`](https://github.com/libretro/gpsp/commit/261b2db) | **Exact version and commit ID embedded** |
| `0x20` | GB/GBC | `TGB Dual`, `v0.8.3 9be31d3` | `0x009ba2ac` | [TGB Dual `9be31d3`](https://github.com/libretro/tgbdual-libretro/commit/9be31d3) | **Exact version and commit ID embedded** |
| `0x40` | Arcade | `FB Alpha`, `v0.2.97.42 621e371` | `0x009a4a50` | [FBA libretro wrapper `621e371`](https://github.com/Aftnet/fbalpha/commit/621e371) | **Exact version and commit ID embedded** |

Snes9x does not preserve a Git hash in its library-version string. Its `v1.36` identity, `Snes9x 2005` library name, supported-extension string, and single legacy option:

```text
catsfc_VideoMode = Video Mode; auto|NTSC|PAL
```

match the `b94a804` source fingerprint used in the SF2000 analysis.

The other five revisions are not inferences from nearby strings: their commit IDs are literal data returned by the compiled cores.

## Same emulator bundle as the SF2000 firmware

The six-version set is the same set independently documented for the Data Frog SF2000 custom libretro frontend:

- FCEUmm `7cdfc7e`;
- PicoDrive 1.91 `cbc93b6`;
- Snes9x 2005 v1.36 / `b94a804` interface family;
- gpSP v0.91 `261b2db`;
- TGB Dual v0.8.3 `9be31d3`;
- FBA libretro wrapper v0.2.97.42 `621e371`.

See [pt13762104/sf2000 emulator documentation](https://github.com/pt13762104/sf2000/blob/master/docs/sf2000/emulators.md) and [vonmillhausen/sf2000](https://github.com/vonmillhausen/sf2000).

This confirms more than generic HC15xx or libretro ancestry. The XGO firmware contains the same identifiable emulator bundle used by the SF2000 frontend. Combined with the existing `LCFG`, resource-name, save-state, `.skp`, `Foldername.ini`, input-bus, and literal `SF2000` evidence, the software is best described as an OEM port/fork of that firmware family to different physical hardware.

This does **not** establish that an unmodified SF2000 firmware image is electrically safe on XGO hardware.

### Arcade qualification

The XGO string proves the FBA libretro wrapper revision `621e371`. SF2000 community analysis found that its arcade implementation combines that wrapper with an older/customized FBA engine and ROM database. The XGO's full internal arcade driver/database equivalence has not yet been hash-proven, so this document does not silently promote that deeper SF2000 result to XGO fact.

## The cores are statically linked into `bisrv.asd`

The launcher installs the same frontend environment callback into six different compiled `retro_set_environment()` entry points. There is no external `.so`/DLL core loader in this path.

| System/core | Frontend call site | Core `retro_set_environment()` entry | Callback passed |
| --- | ---: | ---: | ---: |
| FCEUmm | `0x8035f6b4` | `0x80657f74` | `0x8035eb64` |
| Snes9x 2005 | `0x8035fa50` | `0x8073f154` | `0x8035eb64` |
| PicoDrive | `0x8035fdec` | `0x806af91c` | `0x8035eb64` |
| gpSP | `0x80360188` | `0x8012f93c` | `0x8035eb64` |
| TGB Dual | `0x80360524` | `0x8018cec4` | `0x8035eb64` |
| FB Alpha | `0x803608c0` | `0x8036ca00` | `0x8035eb64` |

The launcher also installs common XGO video, audio, input-poll, and input-state callbacks immediately around these calls. The firmware is therefore a single statically linked frontend-plus-core executable, not RetroArch launching interchangeable core files.

## Core option registration is real

The legacy cores contain real null-terminated `struct retro_variable` arrays and call:

```c
environ_cb(RETRO_ENVIRONMENT_SET_VARIABLES, vars); // command 0x10
```

Examples confirmed in the binary include:

- FCEUmm palette, sprite limit, 2x overclock, overscan, turbo, aspect, and region;
- PicoDrive 3/6-button devices, sprite limit, Mega-CD RAM cart, region, frame-rate region, aspect, and overscan;
- Snes9x video mode;
- TGB Dual link cable, screen placement/switching, single-screen multiplayer, and audio source;
- FBA Neo Geo mode, diagnostics, control layouts, hiscores, SH2 mode, CPU adjustment, and aspect.

gpSP `261b2db` uses the newer core-options definitions. Its `retro_set_environment()` first probes command `52` (`RETRO_ENVIRONMENT_GET_CORE_OPTIONS_VERSION`). When the XGO frontend rejects that command, gpSP converts its modern definitions into legacy `retro_variable` pairs and calls command `16` at `0x8012fb60`.

The option strings are therefore compiled functional branches of the original cores, not abandoned UI text. The limiting component is the XGO frontend.

## The XGO frontend implements only a tiny environment subset

The environment callback begins at `0x8035eb64`. Its command dispatch recognizes only the following cases:

| Command | Libretro meaning | XGO behavior |
| ---: | --- | --- |
| `1` | `RETRO_ENVIRONMENT_SET_ROTATION` | Stores/logs the requested rotation and adjusts geometry, but returns false |
| `10` | `RETRO_ENVIRONMENT_SET_PIXEL_FORMAT` | Returns true without a general format negotiation layer |
| `15` | `RETRO_ENVIRONMENT_GET_VARIABLE` | Returns values only for three hard-coded keys listed below |
| `27` | `RETRO_ENVIRONMENT_GET_LOG_INTERFACE` | Returns the XGO logging callback and true |
| all others | Including `GET_SYSTEM_DIRECTORY`, `SET_VARIABLES`, `GET_VARIABLE_UPDATE`, `GET_PERF_INTERFACE`, and modern core-options commands | Returns false |

### The only serviced core variables

The command-15 path at `0x8035ec6c` compares the requested key against exactly three strings:

```text
fceumm_region
picodrive_region_fps
catsfc_VideoMode
```

For a match, it returns one entry from the table at `0x80a3d4c4`:

```text
0 -> NTSC
1 -> PAL
2 -> AUTO
```

The selected index is the frontend's global TV/video-mode state. This connects the user-visible NTSC/PAL setting to exactly three core queries:

- FCEUmm region override;
- PicoDrive output frame-rate region;
- Snes9x video mode.

No other key reaches a value-return path.

### `SET_VARIABLES` is rejected

Command `16` has no handler and falls through to false. This means the frontend does not retain the core's option table, build an options menu, or expose generic configuration storage.

Legacy cores ignore the failed registration and continue. During their later option reads, the XGO callback returns false for every key except the three above, leaving each core's internal defaults in effect.

gpSP demonstrates the same limitation in a newer API form:

1. command `52` core-options-version probe returns false;
2. gpSP builds a legacy option array from its modern definitions;
3. command `16` registration returns false;
4. later `GET_VARIABLE` calls receive false;
5. compiled defaults remain active.

## What is actually configurable on stock firmware

| Core | Stock frontend-controlled option | Other compiled options |
| --- | --- | --- |
| FCEUmm | Region via NTSC/PAL global | Present but fixed at core defaults |
| PicoDrive | Region FPS via NTSC/PAL global | Present but fixed at core defaults |
| Snes9x 2005 | Video mode via NTSC/PAL global | No other option in this revision's table |
| gpSP | None through generic core options | BIOS mode, frameskip, color correction, frame mixing, save method, turbo period remain defaults |
| TGB Dual | None through generic core options | Link/layout/audio options remain defaults |
| FB Alpha | None through generic core options | Neo Geo, diagnostics, control, hiscore, CPU, aspect, and related options remain defaults |

This corrects a tempting but wrong interpretation of the binary strings: their presence proves compiled capability, not stock UI accessibility.

## Vendor patches around the restricted contract

The frontend does not implement command `9` (`RETRO_ENVIRONMENT_GET_SYSTEM_DIRECTORY`). The firmware instead contains vendor-specific absolute paths, including:

```text
/mnt/sda1/bios/gba_bios.bin
/mnt/sda1/bios/%s
```

These full paths do not occur in the compared upstream gpSP/FBA source snapshots. They are consistent with direct OEM patching used to make cores operate under the minimal XGO/SF2000-style frontend rather than a full RetroArch environment.

The hard-coded GBA BIOS path also explains why relocating or nesting ROM content can produce surprising BIOS lookup behavior in this firmware family.

## Patch and porting implications

### Editing option text is insufficient

Changing a `"key; value1|value2"` string cannot select an option because the frontend neither registers nor stores the table. A patch must alter the command-15 value-return path or implement a real option registry.

### Smallest practical static patch

For one fixed option, the smallest design is:

1. add the desired key/value strings in unused space;
2. extend or trampoline the `GET_VARIABLE` chain at `0x8035ec6c`;
3. return a valid upstream value string;
4. leave the core's existing option parser unchanged.

This could experimentally activate one setting such as a palette, PicoDrive six-button mode, or gpSP frame mixing without replacing the emulator core.

### General solution

A reusable options implementation would need to:

1. accept and retain command-16 variable tables;
2. expose or load selected values;
3. answer command-15 queries for arbitrary keys;
4. optionally implement command 17 for runtime updates;
5. support modern commands 52/53/54 if avoiding gpSP's legacy fallback is desirable.

The existing `.kmp` system is not such a registry. It changes frontend-to-RetroPad button mapping only.

### Core replacement

Because the cores are statically linked, replacing one is a firmware-linking/patching task, not an SD-card core-file swap. The six callback installation sites nevertheless provide a clean architecture map for an SF2000-multicore-style trampoline or a reconstructed frontend.

## Confidence summary

### CONFIRMED

- six statically linked libretro cores;
- exact embedded commits for FCEUmm, PicoDrive, gpSP, TGB Dual, and the FBA libretro wrapper;
- Snes9x 2005 v1.36 with the `b94a804` interface fingerprint;
- the core set matches the documented SF2000 emulator bundle;
- all six receive the same XGO environment callback;
- real core-option registration attempts occur;
- command 16 is rejected;
- only three `GET_VARIABLE` keys are serviced;
- NTSC/PAL is the only generic core-setting state wired through the stock frontend;
- absolute `/mnt/sda1/bios/...` paths are OEM patches absent from the compared upstream snapshots.

### OPEN

- exact internal FBA engine/database equivalence to the SF2000's older/custom hybrid;
- whether the Snes9x object is byte-for-byte built from `b94a804` or a nearby tree with the same v1.36 interface;
- safe code-cave/trampoline locations for a first hard-coded core-option experiment;
- whether a later OEM firmware revision implements additional environment commands;
- byte compatibility of save states with separately built upstream cores at the identified revisions.

## Reproduction anchors

Useful firmware anchors for an independent trace:

```text
frontend environment callback     0x8035eb64
GET_VARIABLE comparison chain     0x8035ec6c
NTSC/PAL/AUTO pointer table        0x80a3d4c4

FCEUmm variable table              0x80939700
PicoDrive variable table           0x8093a9d0
Snes9x variable table              0x8093d04c
TGB Dual variable table            0x8099a0b4
gpSP v2 option definitions         0x80c1c0a0

gpSP legacy SET_VARIABLES fallback 0x8012fb60
```

All addresses are from the specimen hash at the top of this document.
