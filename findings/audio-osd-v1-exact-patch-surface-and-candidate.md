# Audio OSD v1 — exact patch surface and first hardware candidate

Date: 2026-09-05
Branch: `research-audio-osd`

Status: **STATICALLY AUDITED; READY FOR HARDWARE TEST**

## Exact protected input

Artifact ID:

```text
cps1-scheduler-v1-on-snes-test02
```

Firmware SHA-256:

```text
9136479687e921fc478ad89ccce3af94296366768a83600312b3bed5ee294607
```

The exact binary was scanned rather than assuming old caves remained free.

## Verified cave

The protected image contains an all-zero region:

```text
ASD/runtime 0x00002780 / 0x80002780
through      0x00002fff / 0x80002fff
capacity     2176 bytes
```

This is the old Core #3 experimental cave. Core #3 is not part of the current protected scheduler baseline, and the successful CPS1 scheduler patch is in-place at `0x8035ee..`, so this cave is genuinely free again.

OSD v1 occupies:

```text
0x80002780...
1548 bytes
SHA-256 2556cad397c66f5ac98a4f772b05d67eb86eb946bc785c781f1e426ec8954227
headroom 628 bytes
```

## One-instruction hook

`run_screen_write @ 0x8035c398` ends by restoring its saved registers and tail-jumping to:

```text
0x8035c458  j 0x8035c31c
0x8035c45c  addiu sp,sp,0x30
```

At that point the stock call contract is already prepared:

```text
a0 = RGB565 source frame
a1 = width
a2 = height
a3 = pixel pitch
ra = original caller
```

OSD v1 changes only the jump instruction:

```text
0x8035c458
0x080d70c7 -> 0x080009e0
j run_osd_region_write -> j 0x80002780
```

The original delay slot remains unchanged.

The injected routine then returns to the original display path.

## Display-write invariant

When no OSD is visible the hook simply tail-jumps to the original `run_osd_region_write`.

When visible:

1. save the 64x8 source-frame rectangle;
2. draw the volume bar into that rectangle;
3. call the original `run_osd_region_write` exactly once;
4. restore the source-frame pixels;
5. return to the original caller.

Therefore the display path still performs **one stock OSD write per frame**.

No second display transaction is introduced.

## Audio/timing invariants

OSD v1 does not modify:

- GPIO L29 volume-button handling;
- `g_volume` write policy;
- `Archive.sys`;
- `set_audio_volume @ 0x801b3b40`;
- GPIO L23 mute gate;
- libretro audio callback;
- sound task;
- CPS1 sibling scheduler;
- mapper code;
- SNES loader.

The hook only reads `g_volume @ 0x80c33a54`.

## State and behavior

The first frame initializes `last_volume` without displaying anything.

A later value change arms 120 presentation frames.

The stock four levels map to:

```text
0  ->  0 / 64 pixels
33 -> 21 / 64
66 -> 42 / 64
99 -> 64 / 64
```

The bar is 64x8 RGB565 pixels near the bottom-left at:

```text
x = 8
y = height - 16
```

White represents filled volume; black represents unfilled volume.

## Static composition result

Final candidate firmware:

```text
SHA-256 1fc85114909d6107ff80be6e199d54dd1d9b918454ceede61d5108246d6f50c1
LCFG CRC-32/MPEG-2 0x3e6d5666
```

Byte audit relative to the protected input:

```text
allowed surfaces:
  0x0000018c..0x0000018f  LCFG CRC
  0x00002780..            OSD blob
  0x0035c458..0x0035c45b  one tail-jump

unexpected changed bytes: 0
```

Candidate ZIP:

```text
xgo-audio-osd-v1-on-cps1-scheduler.zip
SHA-256 bdf66f60b0ed105449582e7845a9c9d8d98e3e8e6ae0a695ec9c73dc28685f76
```

## Hardware gate

Test with a known working game:

1. press Volume repeatedly;
2. confirm empty / low / mid / full bar progression;
3. confirm the bar disappears automatically;
4. confirm audio behavior is unchanged;
5. re-test SF2 Ryu-vs-Guile performance;
6. confirm Start+Select and Mapper;
7. confirm native SNES still behaves normally.

Do not promote to `golden/` unless the complete regression gate passes.
