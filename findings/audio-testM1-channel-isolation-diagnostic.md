# XGO audio — Test M1 channel-isolation diagnostic

Date: 2026-10-02
Branch: `research-audio-mono-routing`
Status: **AUDITED HARDWARE DIAGNOSTIC READY**

## Purpose

Identify which digital S16 channel reaches the XGO built-in speaker before choosing any permanent stereo-to-mono policy.

This is deliberately a diagnostic pair, not a proposed final audio implementation.

## Exact ancestor

Both probes are built from HW-PASS Test A:

`060093e8fd2a3fa559c9b43e207c4bb495de82e87519b672a799d19b304b20b7`

Test A native-22050 behavior is otherwise unchanged.

## Patch boundary

Stock/Test-A callback:

`0x8035E800: jal 0x8035CBA0`

is redirected to a 40-byte diagnostic shim at:

`0x807DBB08`

The shim walks the existing interleaved S16 frames in place, zeroes exactly one halfword of each 4-byte stereo frame, and tail-jumps to the original `run_sound_advance`.

Arguments, frame count, stereo frame geometry, rate path, scheduler, ring behavior and lower SND configuration are unchanged.

The builder fails closed on exact Test-A SHA, original call word, zero cave bytes and CRC verification.

Source:
`tools/audio/build_mono_channel_probe.py`

## Probe L — LEFT ONLY

Operation:

`L,R -> L,0`

Firmware SHA-256:
`6d4d4cbb670ce4de003b700fc34552d3a7c3e7250e48ab051723bb2553a0e631`

LCFG CRC:
`0x86F9837C`

ZIP SHA-256:
`4b987b6b0ed7708009988839640e8246d938199919ec2a06a37b4002922c187a`

## Probe R — RIGHT ONLY

Operation:

`L,R -> 0,R`

Firmware SHA-256:
`e98611f3b79844f99d9bf23d94e4361d9d9dd50a3df87df989f1f9b89db04de7`

LCFG CRC:
`0x8A0316FA`

ZIP SHA-256:
`b2b2f1a04ac9e10bcf562429131a52a5c4e8e8930fcff2607039565ad87f5719`

## Hardware interpretation

Use the same known-audible game/moment for both probes and do not judge merely by subtle stereo placement.

- LEFT audible, RIGHT silent/nearly silent -> internal speaker consumes channel 0/left.
- RIGHT audible, LEFT silent/nearly silent -> internal speaker consumes channel 1/right.
- Both independently audible at comparable level -> board combines/sums both channels downstream; permanent software mono fold is likely unnecessary for the built-in speaker.
- Both audible but materially unequal -> analog/channel coupling is asymmetric and must be characterized before permanent policy.

After the pair, restore Test A. Neither diagnostic is promotable.

External AV is not required for this first gate; it remains a separate preservation question if software folding is shown necessary.
