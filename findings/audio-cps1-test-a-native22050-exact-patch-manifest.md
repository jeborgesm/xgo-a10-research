# CPS1 Test A — exact three-word native-22050 patch manifest

Date: 2026-10-02
Branch: `research-audio-fidelity-latency`
Status: **PATCH WORDS CLOSED — NO HARDWARE ARTIFACT BUILT**

## Protected input

Authoritative stock firmware:

```text
size    12,768,452 bytes
SHA256  869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf
base    0x80000000
MIPS    little-endian
```

All three original words below were re-read directly from that protected input on 2026-10-02.

## Word 1 — retain native 22050 hardware rate

Address:

```text
0x80306E00
file offset 0x00306E00
```

Stock:

```text
bytes  44 AC 02 34
word   0x3402AC44
       ori v0,zero,44100
```

Context immediately above distinguishes 11025 and 22050.

For the 22050 branch stock stores 44100 to the hardware-rate field and preserves 22050 separately as source rate.

Test A:

```text
word   0x34025622
       ori v0,zero,22050
bytes  22 56 02 34
```

Effect:

```text
requested 22050 -> selected hardware rate 22050
retained source rate remains 22050
```

The 11025 branch remains unchanged and continues selecting 44100.

## Word 2 — bypass first 22050 x2 converter

Address:

```text
0x802FDFC8
file offset 0x002FDFC8
```

Stock:

```text
bytes  22 56 02 24
word   0x24025622
       addiu v0,zero,22050
```

The following instruction compares retained source rate against this constant and enters the x2 repetition path on equality.

Test A:

```text
word   0x24020000
       addiu v0,zero,0
bytes  00 00 02 24
```

No valid emulator source rate of zero reaches this configured path, so retained 22050 follows the generic no-expansion submission path.

## Word 3 — bypass second 22050 x2 converter

Address:

```text
0x802FE068
file offset 0x002FE068
```

Stock:

```text
bytes  22 56 02 24
word   0x24025622
       addiu v0,zero,22050
```

This is the second equivalent 22050 conversion decision in the same submission callback.

Test A:

```text
word   0x24020000
       addiu v0,zero,0
bytes  00 00 02 24
```

## Exact byte diff

Only these 12 bytes are permitted to differ before the normal firmware reseal:

```text
offset 0x00306E00  44 AC 02 34 -> 22 56 02 34
offset 0x002FDFC8  22 56 02 24 -> 00 00 02 24
offset 0x002FE068  22 56 02 24 -> 00 00 02 24
```

No code cave.
No branch displacement change.
No scheduler change.
No frontend-ring change.
No lower-threshold change.
No Audio OSD change.
No mono fold.
No auto-resume change.
No SNES-path change.

## Why both converter comparisons must be patched

The submission callback contains two 22050 decisions on separate control-flow paths.

Patching only one would leave rate-dependent behavior dependent on which path is active.

Test A deliberately neutralizes both while retaining every 11025 comparison and x4 path.

## Scope

The patch words are generic to a source rate of 22050, not FBA-private.

Recovered stock firmware identifies FBA as the ordinary built-in 22050 libretro user.

An external/custom core advertising exactly 22050 would also use the native path.

## Expected FBA transport after Test A

```text
FBA core
  367 stereo-S16 source frames / emulated frame
  declared 22050

frontend ring
  unchanged 576-source-frame consumer quantum

submission
  no x2 repetition
  576 source frames -> 576 output frames

lower packing
  1 cursor unit = 2 PCM time frames
  576 output frames -> 288 lower units

hardware-facing rate
  22050
```

The fixed-367 producer still supplies 22020 frames/s at the protected 60-FPS scheduler. Test A intentionally does not correct that 0.136% deficit.

## Static acceptance before packaging

A builder must fail unless:

1. input size is exactly 12,768,452;
2. input SHA-256 equals the protected stock hash above;
3. all three original words match exactly;
4. after patching, exactly the expected three 32-bit words differ before reseal;
5. the normal XGO firmware integrity/LCFG reseal is then applied;
6. final diff outside the expected words plus integrity field is rejected.

## Experiment interpretation

Test A answers one question only:

> Does removing XGO's software x2 repetition and using the native 22050 hardware path improve/stabilize CPS1 gameplay audio?

If pitch is grossly wrong, silence occurs, or playback cadence is obviously incorrect, restore baseline and reject the native-clock assumption.

If fidelity improves but a small periodic glitch remains, proceed to isolated rate-correction Test B rather than altering buffers.

## Artifact gate

No ZIP or patched firmware is produced by this finding.
