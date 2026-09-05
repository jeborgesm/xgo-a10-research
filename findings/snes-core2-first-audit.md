# SNES Core #2 — first post-mapper compatibility audit

Status: **active on `research-post-mapper-runtime`**.

## Why SNES is the next proof

The external-core runtime has already reached the milestones that previously blocked a second core:

- native XGOC loading is hardware-proven;
- bidirectional stock/external GP crossing is hardware-proven;
- stock video/audio/input adapters are hardware-proven;
- the generic libretro input contract is documented;
- generic `retro_serialize` / `retro_unserialize` save/load is hardware-proven through the stock XGO save UI.

The remaining architectural proof is to run a second libretro core without rebuilding the runtime around FCEUmm assumptions.

SNES is deliberately first because stock XGO SNES performance is visibly weak on hardware and because the SF2000 family already has a maintained Snes9x2005 port using the exact HC15xx Codescape toolchain.

## Pinned comparison core

SF2000 Multicore currently pins:

```text
madcock/snes9x2005
fa69dd6a3caf279cc1f457e65e360f8b9a3683ed
```

This is the first comparison/build target. It is lineage evidence and a porting accelerator, not authority over XGO behavior.

## Immediate compatibility findings

### 1. ISA/toolchain shape is already correct

The fork contains a `platform=sf2000` target using:

```text
/opt/mips32-mti-elf/2019.09-03-2
-EL
-march=mips32
-mtune=mips32
-msoft-float
-G0
-mno-abicalls
-fno-pic
static archive
```

This matches the HC15xx build contract already proven by the external FCEUmm work.

### 2. SF2000 audio is intentionally 11025 Hz

The fork's `libretro.c` selects:

```c
#if !defined(SF2000)
#define AUDIO_SAMPLE_RATE 32040
#else
#define AUDIO_SAMPLE_RATE 11025
#endif
```

This is **not compatible with the ordinary XGO generic run-loop timing contract** without another adaptation layer. XGO's ordinary stock frame scheduler budgets audio as 44.1-kHz stereo PCM even though it initializes the low-level sound driver from the core-advertised sample rate.

Therefore a direct NES-profile reuse of the SF2000 SNES archive would create a timing mismatch.

### 3. XGO's native SNES family is special for exactly this class of problem

XGO family selector `0x08` takes a dedicated setup/audio branch in stock `run_emulator()` rather than the ordinary AV-info-driven path used by NES/Sega/GBA/GB.

The next static task is therefore to close the exact `0x08` branch contract before choosing between:

- **SNES-native profile:** external Snes9x2005 uses XGO family `0x08` and deliberately satisfies the stock SNES fixed setup contract; or
- **generic 44.1-kHz profile:** keep the proven generic runtime path and adapt/resample the external core to 44.1 kHz.

We should not choose between these by analogy with SF2000.

### 4. SF2000 build defaults to path/VFS loading

The same SF2000 target sets `LOAD_FROM_MEMORY = 0`. Its libretro initialization requests the VFS interface and expects path-backed content.

The proven XGO external-core architecture instead already owns a stock-preloaded ROM buffer. The audit therefore builds a second candidate with:

```text
platform=sf2000 LOAD_FROM_MEMORY=1
```

GNU make command-line variables override the ordinary Makefile assignment, allowing us to test whether the core can reuse the XGO preloaded-buffer contract without carrying the SF2000 VFS dependency into Core #2.

## Reproducible audit

Workflow:

```text
.github/workflows/xgo-snes-core2-audit.yml
```

The workflow pins the exact SF2000 Multicore Snes9x2005 commit, builds both the unmodified SF2000 archive and the XGO memory-load variant, and preserves:

- exact toolchain version;
- submodule identities;
- SF2000 build block;
- sample-rate definition;
- environment-command surface;
- pixel-format negotiation;
- serializer exports;
- archive size/sections;
- defined/undefined symbol surfaces;
- differences caused by `LOAD_FROM_MEMORY=1`.

## Decision gate

Before producing a hardware candidate, close these in order:

1. exact XGO stock SNES `0x08` setup/audio branch;
2. audit result for the pinned Snes9x2005 archive;
3. choose native-SNES-profile vs generic-44.1-kHz strategy;
4. define the SNES content handoff and environment shim;
5. link the second core against the already-proven XGO GP/state/runtime infrastructure;
6. only then generate a guarded hardware package.

The important result of this first pass is that Core #2 is **not blocked by MIPS portability**. The real compatibility boundary is now sharply narrowed to frontend policy: audio timing, SNES family behavior, and path/VFS expectations.
