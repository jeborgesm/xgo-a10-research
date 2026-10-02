# XGO gameplay audio — Test A native 22050 hardware PASS

Date: 2026-10-02
Branch: `research-audio-fidelity-latency`
Status: **HW PASS**

## Baseline identity

The physical SD `bios/bisrv.asd` was re-audited before this test.

- size: 12,768,452 bytes
- SHA-256: `b5f1651b146b52070f2e89d51cc2694852af565150568f78d06404e9f9f461ab`
- LCFG payload size: `0x00C2D2C4`
- LCFG CRC-32/MPEG-2: `0x4AB4C686`
- independently recomputed CRC: exact match

This is the HW-proven cumulative `xgo-gb-gba-refresh-path-repair-v2` firmware. It supersedes the earlier `ea442b...` GBC/GBA golden for this audio investigation.

## Test A patch

Builder: `tools/audio/build_testA_native22050.py`

Only the generic 22050-Hz audio path was changed:

- `0x80306E00: 0x3402AC44 -> 0x02401021` — selected hardware rate 44100 -> requested s2
- `0x802FDFC8: 0x24025622 -> 0x24025623` — bypass first 22050 x2 repetition comparison
- `0x802FE068: 0x24025622 -> 0x24025623` — bypass second 22050 x2 repetition comparison
- LCFG CRC field resealed

No stereo-to-mono policy was added or changed. No scheduler, frontend quantum, `sample_num`, admission threshold, auto-resume, SNES, Refresh, Mapper, or Audio OSD code was changed.

Output firmware:

- SHA-256: `060093e8fd2a3fa559c9b43e207c4bb495de82e87519b672a799d19b304b20b7`
- LCFG CRC-32/MPEG-2: `0x17CBBF35`
- byte audit: only the three intended instruction words plus CRC bytes differ; zero unexpected changed bytes

## Hardware result

**PASS.**

User observation:

> sounding good, not missing any sounds and even when there is a small slow down in sfII it doesn't seem to stay behind the game or lag

Street Fighter II was specifically exercised. The audio sounded complete, with no noticed missing sounds. During a small gameplay slowdown, audio did not remain delayed behind gameplay.

## Interpretation

**HW:** Native 22050 output with the two 22050 x2 repetition comparisons bypassed is viable on the XGO hardware and materially improves the observed synchronization/recovery behavior.

**HW:** No stereo-to-mono change was required to obtain this result.

**INF:** The result supports the working hypothesis that the previous 22050 -> 44100 repetition path contributed to persistent audio latency after transient emulation slowdown. It does not by itself isolate which of the three Test A instruction changes is individually necessary.

## Next experimental discipline

Preserve Test A exactly as the positive audio checkpoint. Do not fold stereo-to-mono or another audio-policy change into this result. Any next test should change one additional variable or subdivide Test A if causal isolation is required.
