# HC15xx family DAI corroboration for native 22050 and hardware mono capability

Date: 2026-10-02
Branch: `research-audio-fidelity-latency`
Status: **UP FAMILY CORROBORATION — NOT XGO BOARD PROOF**

## Source

Public HC15xx HCRTOS source:

```text
bnister/sf2000_hcrtos
components/kernel/source/drivers/aplatform/cjc8988-dai.c
```

This is family/upstream evidence, not proof that the XGO PCB contains the CJC8988 codec.

## Native-rate capability

The CJC8988 DAI capability explicitly groups:

```text
SND_PCM_RATE_11025
SND_PCM_RATE_22050
SND_PCM_RATE_44100
SND_PCM_RATE_88200
```

and exposes those rates to the I2SO DAI.

This independently corroborates the broader HC15xx software stack's intended support for native 22050 playback.

It strengthens the XGO binary finding that the local clock programmer contains a dedicated 22050 configuration.

It does **not** replace the XGO binary evidence and does not prove the XGO uses this external codec.

## Hardware mono capability in family DAI

The same DAI source documents codec register R23:

```text
DAC mono mix:
00 = stereo
01 = DACL
10 = DACR
11 = mono ((L+R)/2) into DACL and DACR
```

The family driver programs:

```text
R23 = 0x00
```

so this particular reference configuration leaves the DAC stereo.

This is useful architecture evidence: the HC15xx family can place mono folding at the codec/DAC boundary rather than destructively rewriting the libretro PCM stream.

However, because XGO's exact downstream codec/amplifier topology remains unproven, this cannot yet be used as an XGO patch point.

## Consequence

The family evidence supports two independent design directions:

1. native 22050 is a normal supported member of the 44.1-kHz rate family;
2. an ideal one-speaker solution may be downstream mono mixing, preserving digital stereo until the speaker-specific boundary.

For XGO Test A only item 1 is relevant.

Do not combine mono changes with native-rate proof.

## Evidence levels

- family DAI 22050 capability: **UP**
- family CJC8988 hardware mono register: **UP**
- XGO uses CJC8988: **OPEN**
- XGO native 22050 clock programming: **BIN** (separate finding)
- XGO external/AV stereo topology: **OPEN**
