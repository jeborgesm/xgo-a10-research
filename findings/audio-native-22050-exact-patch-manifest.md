# Native-22050 proof: exact instruction words and hypothetical reseal values

Date: 2026-10-02
Branch: `research-audio-fidelity-latency`
Status: **OFFLINE PATCH MANIFEST ONLY — NO USER CANDIDATE PRODUCED**

## Protected input

Authoritative stock XGO application:

```text
size    12,768,452 bytes
SHA256  869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf
base    0x80000000
```

Firmware words are little-endian.

## Exact three-word proof

### 1. Keep requested 22050 as selected hardware rate

```text
VA          0x80306E00
file offset 0x00306E00
old word    0x3402AC44   ori  v0,zero,0xAC44   ; 44100
new word    0x02401021   addu v0,s2,zero       ; requested rate
```

This location is reached specifically by the 22050 low-rate branch.

The 11025 branch has already selected 44100 earlier and does not execute this replacement as its selected-rate assignment.

### 2. Bypass first 22050 repetition branch

```text
VA          0x802FDFC8
file offset 0x002FDFC8
old word    0x24025622   addiu v0,zero,22050
new word    0x24025623   addiu v0,zero,22051
```

The retained source rate remains 22050, so the following `bne` takes the ordinary/non-22050 path and subsequently fails the untouched 11025 comparison as intended.

### 3. Bypass second parallel 22050 repetition branch

```text
VA          0x802FE068
file offset 0x002FE068
old word    0x24025622
new word    0x24025623
```

This covers the second object-state path through the same PCM submission callback.

## Why 22051 is used only as a comparison sentinel

No source rate is changed to 22051.

The value exists only in the comparison instruction so normal 22050 PCM no longer selects the x2 helper.

The actual retained source rate remains 22050 and the actual selected hardware rate becomes 22050.

Thus the intended runtime state is:

```text
source rate     22050
hardware rate   22050
repeat helper   bypassed
```

## Hypothetical reseal check

Applying only these three payload-word changes in memory and recomputing the already-closed LCFG CRC32/MPEG-2 gives:

```text
payload CRC32/MPEG-2  0x039A66A2
resulting SHA256      75c41c773277a2156703b95bf3b9614b9c80f65ebdc3e67bd228c2968cf8afef
```

These values are recorded solely as an offline reproducibility check.

No firmware candidate or ZIP is attached by this checkpoint.

## Boot-integrity discipline

Any eventual hardware artifact must:

1. verify the exact protected input SHA256 before patching;
2. verify all three old words before replacement;
3. refuse to patch if any expected word differs;
4. write a new copy, never modify the protected image in place;
5. recompute LCFG payload size/CRC;
6. verify only the three intended payload words plus the CRC field differ;
7. preserve the known-good SD image for immediate restoration.

## Remaining technical gate

Before producing the proof artifact, close one final question:

> Does the generic lower write path accept the unchanged 576-frame descriptor correctly when the selected SND rate is 22050, with no hidden requirement that low-rate sources have already been expanded?

Exact-XGO low-level native-rate programming and family native-11025 playback make this likely, but the lower descriptor path should be checked directly before hardware use.
