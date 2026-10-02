# XGO gameplay audio — Test B producer-rate correction design checkpoint

Date: 2026-10-02
Branch: `research-audio-fidelity-latency`
Status: **BIN/INF DESIGN CHECKPOINT — NO HARDWARE CANDIDATE**

## Protected positive checkpoint

Test A remains the hardware-proven positive audio checkpoint and must not be modified in-place.

Test A firmware:

- SHA-256: `060093e8fd2a3fa559c9b43e207c4bb495de82e87519b672a799d19b304b20b7`
- LCFG CRC-32/MPEG-2: `0x17CBBF35`
- native hardware rate: 22050 Hz
- 22050 x2 repetition paths bypassed
- mono/stereo policy unchanged
- scheduler, frontend quantum, lower admission threshold, Mapper, Refresh, CLASSIC and Audio OSD unchanged

Hardware result: PASS. Street Fighter II sounded complete and transient slowdown no longer left audio persistently behind gameplay.

## Additional causal closure after Test A [BIN]

The three Test-A instruction changes are a coordinated semantic unit.

At `0x80306E00`, the selected hardware rate changes from normalized 44100 to requested 22050. The retained source-rate field remains 22050.

The two submission decisions at:

- `0x802FDFC8`
- `0x802FE068`

compare that retained source-rate field against 22050. Therefore changing only the hardware-rate instruction would **not** make the x2 converter irrelevant. The converter would still match retained source rate 22050 and expand the PCM while hardware ran at 22050.

Conversely, bypassing the converter while leaving hardware at 44100 would submit unexpanded 22050 PCM to a 44100 hardware clock.

Conclusion: Test A is already minimal as a coherent native-22050 transport change. Do not split it into one-word hardware tests.

## Remaining FBA producer-rate mismatch [BIN/SRC + arithmetic]

Stock HC15xx FBA uses:

```text
nBurnSoundRate = 22050
nBurnSoundLen  = 367
XGO scheduler  = 60 emulated frames/s
```

Therefore:

```text
367 * 60 = 22020 source frames/s
declared/drain rate = 22050 frames/s
deficit = 30 frames/s = 0.136054%
```

Test A intentionally preserves this mismatch.

The exact average producer count needed at the existing 60-Hz gameplay cadence is:

```text
22050 / 60 = 367.5 frames per emulated frame
```

Thus the smallest exact producer-domain schedule is:

```text
367, 368, 367, 368, ...
```

Every two emulated frames:

```text
367 + 368 = 735 source frames
735 * 30 pairs/s = 22050 frames/s
```

This is the same exact rational correction previously expressed as 735/734 relative to the fixed-367 producer, but it does **not** require a general-purpose resampler if FBA can safely generate alternating 367/368-length frames.

## Exact FBA binary surface already pinned [BIN]

Stock FBA `retro_run()` entry:

```text
0x8036C228
```

Stock load-time audio initialization:

```asm
8036D7F4  addiu t1,zero,22050
8036D7F8  addiu t0,zero,367
...
8036D804  sw    t2,-24108(gp)
8036D808  sw    t1,-24100(gp)   ; nBurnSoundRate-like global
8036D80C  sw    t0,-24104(gp)   ; nBurnSoundLen-like global
```

With authoritative XGO GP `0x80C34774`:

```text
0x80C2E948  pBurnSoundOut-like global
0x80C2E94C  nBurnSoundLen-like global
0x80C2E950  nBurnSoundRate-like global
```

The vendor wrapper's `retro_run()` always executes the emulated frame, including on render-skipped catch-up frames. Audio generation continues when `pBurnDraw` is NULL.

## Important implementation constraint [BIN/INF]

Changing only the count passed to `audio_batch_cb` is unsafe.

The wrapper structure is:

```text
InputMake()
ForceFrameStep() / BurnDrvFrame()
video callback when drawing
audio_batch_cb(g_audio_buf, nBurnSoundLen)
```

`nBurnSoundLen` is an FBA producer parameter, not merely a frontend submission count. A 368th sample must actually be generated before 368 samples are submitted.

Therefore a Test-B implementation must select the current 367/368 value **before the FBA frame engine generates audio**, and the same value must remain visible to the subsequent audio submission.

Do not implement Test B by appending or exposing a stale/uninitialized 368th sample after `BurnDrvFrame()`.

## Why a constant 368 is rejected

A one-word `367 -> 368` load-time patch would produce:

```text
368 * 60 = 22080 frames/s
```

which overshoots 22050 by 30 frames/s. It merely reverses the mismatch and is not an exact correction.

## Current minimal design target [INF]

Preferred Test-B shape:

1. preserve Test A byte-for-byte as the ancestor;
2. maintain one tiny one-bit/toggle state private to the FBA wrapper;
3. before each `BurnDrvFrame()`, select `nBurnSoundLen = 367` or `368`;
4. toggle every executed emulated frame, including render-skipped catch-up frames;
5. allow existing FBA generation and existing audio callback to consume the same selected count;
6. make no scheduler, frontend ring, lower SND, mono, OSD, Mapper, Refresh or CLASSIC changes.

This gives exact 22050 production at the actual XGO 60-frame execution cadence with no interpolation and no fabricated PCM sample.

## Remaining offline gates before Test B

Do **not** build a hardware candidate until these are closed from the exact cumulative binary:

- complete instruction sequence at the beginning/output portions of `0x8036C228`;
- exact point before `BurnDrvFrame()` where `nBurnSoundLen` is read by the FBA engine;
- whether changing the global once per frame is sufficient or another derived sound-length value is cached;
- a safe persistent toggle-state location that does not collide with FBA, frontend, Mapper, Refresh, Audio OSD or other cumulative modifications;
- a safe code-cave / branch patch with correct XGO/FBA `$gp` ownership;
- reset semantics on game load/unload so phase is deterministic;
- mechanical diff and LCFG reseal against the Test-A firmware.

## Experimental interpretation

Test B should answer only:

> With the already hardware-proven native-22050 Test-A transport held constant, does eliminating FBA's fixed 367-at-60-Hz 30-frame/s deficit remove any remaining periodic audio roughness without changing gameplay timing or latency behavior?

If Test B produces no audible improvement, retain Test A and treat the 0.136% mismatch as non-material for the observed use case.

If Test B improves a remaining periodic disturbance while preserving Test-A synchronization, the producer mismatch becomes hardware-relevant evidence.

## Hardware gate

**NOT YET REACHED.**

The arithmetic and desired producer schedule are closed. The exact binary injection/state surface must be closed before another hardware ZIP is justified.
