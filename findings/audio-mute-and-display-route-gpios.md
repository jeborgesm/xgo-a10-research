# XGO Audio Mute and LCD/TV Route GPIOs

Status: **active GPIO roles substantially narrowed by static analysis; R05 backlight role independently corroborated by SF2000-family hardware work**.

## Scope

This pass follows two small GPIO helper functions in the XGO firmware and then traces their callers in the frontend state machine.

The useful helpers are:

- `0x801b3fb4` — configures and drives GPIO `R05`;
- `0x801b4024` — configures and drives GPIO `L23`.

Both helpers manipulate the HC15xx GPIO direction and output registers directly.

## GPIO L23 — strong evidence for audio mute / amplifier gate

Function `0x801b4024` does the following:

```text
GPIO_L_DIR    = 0xb8800058
GPIO_L_OUTPUT = 0xb8800054
bit           = 23
```

It forces L23 to output mode and writes the caller's boolean value to that bit.

The strongest semantic evidence comes from the physical-volume path at approximately `0x8035d670..0x8035d6a8`.

The XGO volume button advances the persisted volume by 33:

```text
0 -> 33 -> 66 -> 99 -> 0
```

Immediately after computing the new value, firmware does:

```text
if wrapped to volume 0:
    L23 = 1
else:
    L23 = 0

set software/audio-driver volume
persist Archive.sys
```

In simplified form:

```c
volume += 33;
if (volume >= 101) {
    volume = 0;
    gpio_L23(1);
} else {
    gpio_L23(0);
}
set_audio_volume(volume);
```

The next call, `0x801b3b40`, forwards the 8-bit volume value into the sound subsystem through an SDK device/control call.

L23 is also asserted/deasserted around frontend/game transitions, consistent with suppressing pops/noise while audio state changes.

### Current conclusion

**STRONG EVIDENCE:** L23 is the XGO board's hardware audio mute / speaker-amplifier gate.

Observed polarity is:

```text
L23 = 0 -> audio output enabled/unmuted
L23 = 1 -> hardware mute/gate closed
```

The exact downstream analog component (amplifier enable pin, mute input, transistor gate, etc.) is not yet physically traced, so that electrical destination remains open.

This is important for a future UniFrog port because current SF2000 and GB300 targets use different board audio gates: SF2000 uses R07 and GB300 uses L15. The XGO firmware instead provides strong evidence for a third board-specific route on L23.

## GPIO R05 — LCD backlight hard gate

Function `0x801b3fb4` configures and drives:

```text
GPIO_R_DIR    = 0xb88000f8
GPIO_R_OUTPUT = 0xb88000f4
bit           = 5
```

The XGO's active LCD/TV mode detector reads L15. Its two branches include literal diagnostics:

```text
===============LCD Mode
===============TV Mode
```

When entering LCD mode, firmware calls:

```text
R05 = 0
```

When entering TV mode, firmware calls:

```text
R05 = 1
```

This exactly matches independently recovered SF2000-family hardware behavior: R05 is an active-low LCD backlight gate, and on compatible boards the same pin can be muxed to PWM2 for brightness control.

Therefore:

```text
R05 = 0 -> LCD backlight on
R05 = 1 -> LCD backlight off
```

### Confidence

**CONFIRMED by XGO executable behavior + independently corroborated family hardware contract:** R05 is used as the XGO LCD backlight hard gate.

No evidence has yet been found that the stock XGO frontend exposes variable PWM brightness; the observed XGO path uses hard GPIO on/off switching.

## GPIO L24 — complementary LCD/TV routing output

The same L15 mode-switch routine manipulates L24 directly through `GPIO_L_OUTPUT`.

The states are complementary to R05:

```text
LCD mode:
    R05 = 0   # backlight on
    L24 = 1

TV mode:
    R05 = 1   # backlight off
    L24 = 0
```

Because L24 changes exactly with the LCD/TV transition, it is clearly part of the external-video route control.

**STRONG EVIDENCE:** L24 controls some board-level LCD/TV routing or TV-output enable function.

The exact electrical destination is not yet proven. Possibilities include a video-output gate, analog switch, amplifier/power enable, or related CVBS path control. Do not label the downstream component more specifically until physically or statically resolved.

## Updated board GPIO map

Current useful XGO board-specific signals are therefore:

```text
B15  serial controller data P1
L0   serial controller data P2
B7   shared serial-controller clock

L15  LCD / TV-mode detector input
R05  active-low LCD backlight gate
L24  complementary LCD/TV route control

L23  strong evidence: active-high audio mute / amp gate
L29  physical volume button input
```

## Custom-firmware implication

A generic SF2000/GB300 board profile should not be expected to handle XGO audio correctly without modification.

For an XGO-specific HC1512 target, the current best board model is:

```text
audio transport: HC15xx SND / I2SO family
software volume: SDK sound-device control
hardware mute/gate: L23, active high
LCD backlight hard gate: R05, active low
LCD/TV detect: L15
additional LCD/TV route output: L24
```

The most valuable next step is to trace the initialization structure around the HC15xx SND/I2SO driver and determine whether the XGO uses the same mono/stereo transport and DAC configuration as SF2000, or another OEM variant.

## Confidence summary

### CONFIRMED

- `0x801b4024` drives GPIO L23 as an output;
- `0x801b3fb4` drives GPIO R05 as an output;
- volume-zero transition drives L23 high while nonzero volume drives it low;
- software volume is changed immediately after the L23 operation;
- LCD mode drives R05 low;
- TV mode drives R05 high;
- L24 changes complementarily during LCD/TV switching;
- L15 selects the LCD-vs-TV branch.

### STRONG EVIDENCE

- L23 is the XGO hardware audio mute/amplifier gate;
- L24 is a board-level external-video route/enable control.

### OPEN

- exact analog component connected to L23;
- exact downstream component/function controlled by L24;
- whether XGO supports PWM brightness on R05 even though the stock frontend only uses hard on/off;
- exact XGO I2SO channel count, DAC configuration, and speaker topology.
