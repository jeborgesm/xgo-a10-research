# XGO SND underrun-fade bit and HC15xx family noise-control crosscheck

Date: 2026-10-01  
Branch: `research-audio-fidelity-latency`  
Status: **BIN + FAMILY HW/SRC CORROBORATION — NO HARDWARE CANDIDATE**

## Major closure

Current UniFrog HC15xx/SF2000/GB300 hardware work names:

```text
SND0 base                 0xB880A000
SND0 underrun-fade reg    +0x3C
underrun-fade bit         0x40
```

XGO stock `bisrv.asd` contains an exact low-level helper at `0x8030A61C` operating on the same register and bit:

```text
if a1 == 1:
    [a0 + 0x3C] |= 0x40
elif a1 == 0:
    [a0 + 0x3C] &= ~0x40
```

The helper has two direct XGO callers:

```text
0x803063F0
0x80306650
```

Both calls execute with `a1 = 1` in the MIPS delay slot.

Therefore:

> **XGO stock explicitly enables SND0 +0x3C bit 0x40 during its audio setup paths.** [BIN]

UniFrog's independently hardware-derived HC15xx naming identifies that exact bit as **underrun fade**. [UP/HW-family]

This is the strongest evidence so far for what XGO's lower SND engine does when PCM starvation occurs.

## Evidence classification

### BIN

XGO:

- SND register helper operates at offset `+0x3C`;
- bit `0x40` is set/cleared;
- both recovered setup callers request the set state;
- therefore stock XGO enables that hardware feature.

### Family HW/SRC

UniFrog:

```c
#define SND0_BASE ((volatile uint32_t *)0xb880a000u)
#define SND0_UNDERRUN_FADE_REG (0x3cu / sizeof(uint32_t))
#define SND0_UNDERRUN_FADE_BIT 0x40u
```

Its hardware notes distinguish SF2000 underrun-fade policy from GB300 and warn not to apply the SF2000 policy blindly to GB300.

### INF

Because the register address and bit are identical on the same HC15xx SND block, XGO's enabled `+0x3C/0x40` feature can now be identified with high confidence as the HC15xx **underrun-fade enable**.

Exact fade curve, fade duration, terminal DAC sample, and whether the engine eventually stops remain OPEN.

## Noise-path significance

UniFrog hardware work reports:

- digital zero alone does not eliminate physical board noise when the DAC/amplifier path remains enabled;
- opening only the physical amplifier gate can expose DAC idle noise;
- the stable policy configures/mutes the low-level SND/DAC path before opening the external amplifier gate;
- SF2000 preserves underrun fade across short starvation and closes the amplifier gate only after sustained silence.

This aligns strongly with XGO's separate L23 amplifier gate and the newly identified enabled underrun-fade bit.

Thus XGO has **at least two distinct silence/noise mechanisms**:

```text
digital/SND layer:
  HC15xx underrun fade enabled (+0x3C bit 0x40)

physical board layer:
  GPIO L23 active-high mute / amplifier gate
```

Do not collapse these into one mute mechanism.

## Stock XGO 0x5A / 90 lower-volume setup [BIN + family corroboration]

In the XGO lower SND setup near `0x80306418`, the sound-control helper is called with:

```text
a1 = 0x5A = 90
```

Current UniFrog stock-firmware archaeology independently reports that the SF2000 stock sound-init path sets sound-device volume to `0x5A`.

The open SF2000 HCRTOS DTS also uses:

```text
i2so volume = 90
```

with an explicit note that 90% is used to avoid clipping.

This establishes `90` as a recurring HC15xx-family lower-audio setup value. [BIN/UP]

It does **not** prove that XGO's user-facing level 99 clips. The XGO frontend later passes its own 0..99 volume state through the SDK control path, and the exact gain curve remains to be measured/recovered.

However, the 90-vs-99 distinction is now a legitimate fidelity lead for a future isolated gain/clipping experiment.

## Underrun question update

Previous possibilities included stop, zero, stale-repeat, wrap, or explicit underrun handling.

We can now narrow that:

- XGO enables the HC15xx underrun-fade feature before playback. [BIN + family semantic corroboration]
- therefore a hardware fade response is expected to participate in starvation behavior. [INF]
- exact post-fade behavior remains OPEN.

This is materially stronger than the earlier generic "hardware behavior unknown" state.

## UniFrog latency evidence relevant to future XGO experiments [family HW]

UniFrog reports direct HC15xx I2SO DMA playback and has hardware-tested smaller period configurations. Its current documentation identifies small periods as the low-latency direction and explicitly tracks:

- audio delay/backlog;
- write failures/backpressure;
- underrun count/likelihood;
- queue occupancy;
- amplifier-gate state;
- clipping.

This supplies an excellent experimental grammar for XGO once static archaeology reaches the hardware boundary.

It does **not** authorize transplanting UniFrog period sizes into XGO stock firmware yet.

## Next offline targets

1. Find XGO's equivalent of the HC15xx `SND_IOCTL_DELAY` / queued-frame calculation.
2. Find the old driver's auto-start transition and determine whether the 482-unit gate is also its two-period start threshold.
3. Trace XGO SND `+0x90` and neighboring fade/mute controls.
4. Recover the gain/volume helper called with `0x5A` and compare it to the later user-volume path.
5. Compare XGO's fixed low-rate repetition with the later HC15xx kernel `resample` API.

## Hardware gate

Not reached. No firmware candidate or hardware test is requested.
