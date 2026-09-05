# XGO stock arcade: exact libretro wrapper identity, hybrid engine lineage

Status: **CORRECTED — exact wrapper revision confirmed; whole-emulator identity is hybrid/vendor-modified**

## Exact identity that is genuinely confirmed

Direct string extraction from the preserved stock XGO `bios/bisrv.asd` yields:

```text
FB Alpha
v0.2.97.42 621e371
```

The abbreviated Git revision resolves to:

```text
621e371e553eb7814f12504b23f78de4715b7d11
```

in the historical FB Alpha source lineage, and that revision identifies the libretro-facing core as `v0.2.97.42`.

Therefore the following is exact:

> XGO's embedded arcade **libretro-facing wrapper identity** is FB Alpha v0.2.97.42 / 621e371.

## Correction: this does not make the stock binary an untouched 621e371 build

Family-wide binary archaeology now proves that the stock HC15xx arcade implementation differs materially from an untouched upstream 621e371 configuration.

Across XGO, SF2000 08/03, SF2000 1.71, and GB300 v2, the vendor build preserves:

```text
22050-Hz FBA audio
367-sample FBA frame audio length
three-way Sek backend machinery
C68K default for ordinary 68000 CPUs
private frontend -> FBA frameskip callback
render suppression by disabling the active draw buffer
alternating FBA frame buffers when rendering
```

By contrast, the public 621e371 libretro wrapper uses:

```text
48000 Hz
801 samples
```

and does not by itself explain the HC15xx private `gfn_frameskip` integration.

The documented SF2000 family archaeology also ties the underlying ROM/driver ancestry to an older FBA-a320 / ~0.2.96.86-era engine combined with the later 0.2.97.42 libretro layer and vendor changes.

The correct model is therefore:

```text
older handheld/FBA-a320 engine ancestry
        +
621e371 / v0.2.97.42 libretro-facing layer
        +
HC15xx vendor modifications
        +
device/frontend integration
```

## Why the distinction matters

Treating 621e371 as the exact complete stock source would send optimization work in the wrong direction.

A clean build of upstream 621e371 would not automatically reproduce the properties now shown to matter for stock CPS1 performance:

- C68K selection;
- 22.05-kHz audio workload;
- the private frontend lateness signal;
- render-only frame skipping;
- stock double-buffer selection.

The high-value target is therefore not "rebuild 621e371 unchanged."

It is:

> Reproduce the proven stock-family runtime contract around a known CPS1 engine, then measure whether that contract explains the stock advantage.

## Relationship to the frozen FBA2012 CPS1 experiment

The frozen FBA2012 CPS1 tree differs in two particularly important ways:

1. its default build selects Musashi rather than C68K;
2. its newer CPS1 loop gates drawing with `nSkipFrame`, and its normal libretro auto-frameskip depends on `RETRO_ENVIRONMENT_SET_AUDIO_BUFFER_STATUS_CALLBACK`.

The untouched XGO stock environment does not provide that libretro audio-buffer-status facility. Stock family firmware instead drives its own private `gfn_frameskip` callback directly.

Therefore "newer FBA under stock callbacks" is not runtime-equivalent to stock arcade even when ROM compatibility is otherwise correct.

## Current decision

Do not use this file as evidence that XGO stock is an untouched upstream 621e371 emulator.

Use:

`findings/stock-fba-cpu-backend-and-frontend-timing-comparison.md`

as the current detailed performance/runtime record.

The exact 621e371 identity remains highly valuable for wrapper/API and ROM-lineage archaeology, but the family binary is a hybrid vendor build.
