# Modification handoff — revive Test13 audio improvement on cumulative baseline

Date: 2026-09-15
Branch: `research-audio-test13-revival`
Status: **modification-path handoff; no firmware candidate built yet**

## User intent

Revive the historical Test13 stereo-to-dual-mono audio improvement now that the fine-grained volume control has survived into the cumulative firmware.

The earlier experiment was not abandoned because the basic idea was unwanted. The practical problem was the stock four-state volume policy: 0/33/66/99 made improved/louder audio difficult to use because the useful choices were effectively very low, medium, and very high. The current cumulative firmware instead provides 9-point increments through 99, making precise comfortable adjustment possible.

## Binary audit result: current audio baseline versus stock

A direct byte/bit comparison of the original stock `bios/bisrv.asd` against the current cumulative Test75 firmware established that the known core audio transport/configuration paths remain stock-identical, including:

- `set_audio_volume @ 0x801b3b40`;
- HC15xx two-channel SND/I2SO initialization;
- sample-precision configuration;
- DAC-format configuration;
- frame/clock configuration;
- `run_sound_advance @ 0x8035cba0`;
- `retro_audio_sample_batch_cb @ 0x8035e7d8`;
- the old Test13 interception site `0x8035e800`;
- inspected MusicEngine/WAV and I2SO configuration/diagnostic regions.

The intentional surviving audio behavior change is the fine-volume immediate at runtime `0x8035d67c`:

```text
stock:   addiu t4,t5,33
current: addiu t4,t5,9
```

Current cycle:

```text
0, 9, 18, 27, 36, 45, 54, 63, 72, 81, 90, 99, 0
```

The stock `set_audio_volume` path and L23 mute gate remain protected.

## Historical Test13

Test13 intercepted the stock libretro batch callback before `run_sound_advance` and, for Arcade list IDs 7..11, converted each interleaved stereo frame to dual mono:

```text
mono = (left + right) / 2
left = mono
right = mono
```

Historical addresses:

```text
retro_audio_sample_batch_cb   0x8035e7d8
run_sound_advance             0x8035cba0
patched JAL site              0x8035e800
old dual-mono shim            0x807db9c0
```

The old implementation did NOT survive. The JAL site is stock-identical in Test72/Test74/Test75 and the old cave at file offset `0x7db9c0` has been repurposed by Refresh/CLASSIC data. Do not reuse that cave.

## Family corroboration

`madcock/sf2000_multicore` independently implements a single-speaker stereo downmix at the libretro callbacks. Its batch strategy places a headroom-safe sum into the audible channel:

```text
left = (left >> 1) + (right >> 1)
```

This is useful family precedent but does not override XGO-specific hardware findings.

## Next modification steps

1. Start from the current protected cumulative baseline, not historical Test13 firmware.
2. Find a currently free, audited code cave; `0x807db9c0` is forbidden because later Refresh/CLASSIC uses it.
3. Rebuild the Test13 interception additively while preserving the current `+9` fine-volume policy, Audio OSD v8, Mapper v19, CPS1 pacing, Refresh, CLASSIC, Save/Load, stock consoles, and stock Arcade.
4. Prefer the overflow-safe family expression `(L >> 1) + (R >> 1)` unless static analysis shows a reason to preserve the historical `(L + R) / 2` implementation.
5. First candidate should be deliberately narrow and reversible. Preserve normal buffer size/count semantics and return behavior of `retro_audio_sample_batch_cb`.
6. Hardware A/B at matched volume values, especially 45/54/63 and 99, comparing current cumulative baseline versus downmix candidate on the same device and same game/audio scene.
7. Check whether stereo content previously losing one channel becomes more complete and whether perceived loudness/clarity improves without clipping/distortion.
8. Regression-test CPS1 performance/audio, stock Arcade, representative stock consoles, Start+Select/Mapper, volume OSD, mute, and save/load.
9. If hardware passes, archive exact ZIP and hashes in `jeborgesm/xgo-a10-artifacts` before promotion.

## Research-path separation

The general archaeology/research branch remains `research-audio-capability-map`. This branch is specifically the modification path for reviving Test13. Do not mix unrelated hardware-lineage or speculative MusicEngine work into the modification candidate.
