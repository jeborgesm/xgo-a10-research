# LCD/TV route transition does not switch the XGO audio gate

Date: 2026-10-01  
Branch: `research-audio-fidelity-latency`  
Status: **DIRECT STOCK BIN**

## Question

Can the stock LCD/TV-mode branch provide a software discriminator for applying mono fold only to the internal speaker while preserving external/AV stereo?

## Exact mode detector [BIN]

The frontend mode task at `0x8035C70C` reads:

```text
GPIO_L_INPUT = 0xB8800050
```

and extracts bit 15:

```text
0x8035C734  lw   t1,0(a1)       ; GPIO_L_INPUT
0x8035C73C  srl  t0,t1,15
0x8035C740  andi a2,t0,1
```

This directly closes the previously inferred L15 LCD/TV detector.

## LCD branch [BIN]

The branch containing the literal:

```text
===============LCD Mode
```

performs the already identified video/display operations, including:

```text
0x8035C7A8  gpio_R05(0)    ; LCD backlight on
...
GPIO_L_OUTPUT bit 24 set
```

## TV branch [BIN]

The branch containing:

```text
===============TV Mode
```

performs:

```text
0x8035C854  gpio_R05(1)    ; LCD backlight off
...
GPIO_L_OUTPUT bit 24 clear
```

## Audio result [BIN]

The complete LCD/TV transition routine contains **no call to**:

```text
gpio_L23 @ 0x801B4024
set_audio_volume @ 0x801B3B40
```

and does not reconfigure the recovered libretro PCM ring or SND setup in the mode branches.

Therefore stock firmware's active LCD/TV transition visibly changes the display/video route but does **not** software-switch the known XGO audio mute/amplifier gate.

This is an important negative result.

## Consequence for mono preservation

L15 is a real LCD/TV-mode discriminator, but the stock firmware does not prove that audio is independently rerouted by this mode switch.

Several hardware arrangements remain possible:

1. external AV audio is electrically tapped from the same DAC stereo outputs while L23 gates only the internal speaker amplifier;
2. external AV audio shares an analog path downstream of some board-level mixer;
3. the AV connector is mono or otherwise hardware-combined;
4. another hardware route not touched by this frontend transition controls audio.

The binary evidence does **not** currently distinguish these.

Therefore a global software:

```text
L,R -> mono,mono
```

at the libretro callback would certainly protect the one internal speaker from missing left/right-only content, but it could also collapse external stereo if the AV audio connector receives the same two-channel DAC stream.

Do not make that global change permanent yet.

## Useful design direction

The L15 mode state can still become a deliberate policy input if external AV is later proven stereo:

```text
LCD/internal-speaker mode:
    fold L+R safely to mono and duplicate

TV/external mode:
    preserve original stereo
```

That would be a firmware policy improvement rather than replication of stock behavior.

Before choosing it, establish whether L15 state actually corresponds to the external audio use case on this exact board and whether the AV connector carries one or two audio channels.

## Additional L23 caller observation [BIN]

Direct call enumeration shows L23 is used independently around startup/game/frontend transitions and volume-zero handling. Calls include both asserted and deasserted states.

The LCD/TV transition routine itself is absent from that L23 caller set.

This further separates:

```text
display/TV route: L15 detector + R05/L24
audio mute/gate:  L23
```

at the software level.

## Hardware gate

Not yet reached for the wider audio investigation. External-connector channel topology remains a later hardware/electrical boundary, but substantial offline work remains in the resampling, queue, and mute lanes.
