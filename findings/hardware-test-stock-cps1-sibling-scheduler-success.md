# Hardware test — stock CPS1 sibling scheduler transplant

Date: 2026-09-05
Branch: `research-post-mapper-runtime`

## Result

**Hardware-confirmed success.**

The first scheduler-only candidate was composed onto the exact protected baseline:

```text
Mapper v19
+ native Snes9x2005 Core #2 Test02
input firmware SHA-256:
8db8d091f7896e0847d63455ec325bdc9889a2caeebd3d37525c0005006a226a
```

Generated scheduler candidate:

```text
bisrv.asd SHA-256:
9136479687e921fc478ad89ccce3af94296366768a83600312b3bed5ee294607

LCFG CRC-32/MPEG-2:
0xf9b3715e
```

The patch changed only the stock frontend pacing/catch-up scheduler. It preserved:

- stock embedded FBA;
- C68K ordinary-68000 backend;
- 22050-Hz / 367-sample FBA audio;
- stock input/audio/video callbacks;
- private FBA `gfn_frameskip` draw-skip hook;
- Mapper v19;
- native SNES Core #2 Test02 baseline.

## Hardware observation

Street Fighter II was used as the known stress case.

Previously, the Ryu-vs-Guile fight produced obvious slowdown and dropped frames, with the characteristic prolonged "underwater" feel.

With the sibling-derived scheduler candidate:

- no underwater slowdown was observed;
- the fight remained normally playable;
- the user completed and won the fight;
- frame drops were minimal compared with the prior XGO scheduler behavior.

The device otherwise behaved as expected.

## Interpretation

This is strong hardware evidence that the major pathological CPS1 slowdown was not caused primarily by:

- ROM loading;
- missing A68K execution;
- a fundamentally inadequate stock FBA core;
- hidden CPU overclock settings.

The important XGO-specific regression was the frontend pacing/recovery policy.

The family-wide stock design already contained the correct performance mechanisms:

```text
C68K
+ 22050-Hz FBA audio
+ private render-only frameskip
+ normal emulation/audio on skipped-render frames
```

SF2000/GB300's wall-time / bounded-catchup policy makes substantially better use of that mechanism than XGO's incremental debt scheduler.

## Hardware-confirmed mechanism

The successful candidate uses:

```text
absolute wall-time anchor
-> ideal frame count
-> bounded catch-up burst (up to 3)
-> gfn_frameskip(1) while catching up
-> FBA pBurnDraw = NULL
-> emulation + audio continue
-> render restored when caught up
```

The patch fits entirely inside XGO's existing scheduler code and uses timing-owned state words. No new code cave or new RAM allocation is required.

## Preservation decision

Treat this scheduler policy as a successful XGO optimization candidate and preserve it as the baseline result of the post-mapper-runtime branch.

The branch's central conclusion is:

> Stock CPS1 did not need a replacement emulator. XGO needed the sibling family's better pacing/recovery policy.

## Lessons learned

The failed A68K/external-FBA investigation was still useful because it exposed several false assumptions:

1. "native MIPS A68K must be the vendor fast path" was wrong for ordinary CPS1.
2. wrapper version alone does not describe the shipped runtime; vendor frontend integration matters.
3. audio workload and frontend pacing must be analyzed as part of emulator performance.
4. sibling firmware is often a better specification of intended behavior than repeated black-box patch bisection.
5. performance archaeology should establish the manufacturer's working contract before replacing a subsystem wholesale.

These lessons should guide future core experiments.
