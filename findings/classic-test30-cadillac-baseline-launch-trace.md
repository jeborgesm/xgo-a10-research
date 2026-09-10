# Test30 — Cadillac baseline, launch-stage trace, and CLASSIC artwork fit

Date: 2026-09-08
Branch: research-game-list-arcade-expansion

## Hardware input from Test29

Test29:
- CLASSIC page visible;
- dedicated CLASSIC artwork worked;
- Pac-Man still failed to launch.

The user requested:
1. resize the CLASSIC artwork by cropping top/bottom and making it wider;
2. add a known-working MAME2000 title as a baseline;
3. use Cadillacs and Dinosaurs because it was already hardware-proven under Test11-era MAME2000.

## Known-good baseline identity

Repository evidence confirms:
- packaged stock filename: Cadillacs and Dinosaurs.zfb;
- real archive basename used by the XGO/MAME path: dino.zip;
- preserved runtime state files include ARCADE/save/dino.zip.sa0..sa3;
- Test11 hardware explicitly reported Cadillacs & Dinosaurs playable under the MAME2000 core.

Test30 therefore adds:

CLASSIC/Cadillacs and Dinosaurs.zfb
 -> embedded archive basename dino.zip

User must copy:
 /CLASSIC/bin/dino.zip

## CLASSIC catalog

The synchronized list11 triplet now contains three entries:

1. Pac-Man.zfb
2. Ms Pac-Man.zfb
3. Cadillacs and Dinosaurs.zfb

## Launch-stage trace

To avoid another blind hardware result, Test30 writes:

/CLASSIC/launch.stg

The file contains one byte representing the last completed launch stage:

A = native CLASSIC launcher was entered
B = selected wrapper opened and embedded ZIP basename extracted successfully
E = external core loaded, CRC verified, BSS prepared, IRQ-GP repaired, caches flushed; immediately before Test12 core entry
F = Test12 core returned to the launcher

Interpretation:

no launch.stg
 -> generic browser hook did not identify/enter CLASSIC launcher

A
 -> launcher entered but wrapper/path parsing failed before archive basename extraction

B
 -> wrapper parsed; failure occurred during external-core file/header/load preparation

E
 -> all native launcher/core-loader plumbing completed; failure is inside Test12 core entry/runtime handoff

F
 -> Test12 core returned cleanly; frontend/core declined or exited before gameplay

The stage helper is a separate 180-byte routine placed in verified-zero firmware space at runtime 0x80000e00..0x80001000.

The main native CLASSIC launcher remains in 0x80001900..0x8000217f and is 2,153 bytes.

## Artwork revision

The selected CLASSIC/Pac-Man image is cropped vertically and widened relative to Test29.

Source: 385x465 user-selected crop.
Test30 crop: y=50..410 -> 385x360.
Scaled to approximately 513x480, centered in a 640x480 black canvas.
Converted to native little-endian RGB565.

Only Resources/clssic.r56 changes.
Stock CPS1/CPS2/IGS/NeoGeo artwork remains untouched.

## Exact candidate

xgo-classic-test30-cadillac-trace-art.zip
size              7,547,515 bytes
ZIP SHA-256        25ee41ac0ced58496fa1746e11473e0ff86b8903bc4d399ca26a2c6d2030b13e
firmware SHA-256   f4168fc129b18b454fb3fda3391e3423a3106bbee2e100e424a94b73839f6d66
launcher SHA-256   af9d984fa9827fd9840d4715359ce268702e72b49ad2ebcf6bfa773cdeda6ddc
trace SHA-256      e65fe8eef6fafe8f99ef3f2e5cf28dcb629cb990105342f10e808f61ba31050b
art SHA-256        62c7636d8f2285aba1c2a05803e43b39c5483b9739ed85fdca56cee27adf501a

ZIP integrity passed offline.

## Hardware gate

Place:
 /CLASSIC/bin/pacman.zip
 /CLASSIC/bin/mspacman.zip
 /CLASSIC/bin/dino.zip

Then:
1. confirm CLASSIC page and revised artwork;
2. confirm stock Arcade/CPS2 artwork remains unchanged;
3. launch Cadillacs and Dinosaurs from CLASSIC first;
4. if it fails, power off and inspect /CLASSIC/launch.stg;
5. report the single stage byte;
6. only if Cadillac runs, retry Pac-Man and Ms Pac-Man.

This one test separates MAME-ROM compatibility from CLASSIC launcher/core-handoff failure.
