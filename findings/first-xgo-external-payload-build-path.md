# First guarded XGO external-payload build path

Status: **offline build path validated; no hardware test performed and no SPI-NOR updater involved**.

## Result

The XGO firmware has now been reduced far enough that a minimal external-payload experiment can be built entirely from known stock addresses.

The research prototype consists of:

```text
xgo_probe_loader.bin
  linked at 0x80001500
  observed LLVM-17 size: 402 bytes
  available stock loader hole: 3200 bytes

core_87000000
  linked at 0x87000000
  observed LLVM-17 size: 472 bytes
  generated RGB565 display/input probe
```

The loader occupies only about 15% of the preserved `0x1500..0x217f` zero-filled region.

## Minimal loader behavior

The proof loader deliberately keeps the first test smaller than full SF2000 Multicore:

```text
normal GBA path
    -> call stock XGO run_gba(path, load_state)

semicolon-tagged probe path
    -> open /mnt/sda1/cores/xgoprobe/core_87000000
    -> load at 0x87000000
    -> close file
    -> flush data/instruction caches
    -> save current heap ceiling
    -> temporarily set RAMSIZE = 0x87000000
    -> execute payload
    -> restore previous heap ceiling
```

The proof loader does not modify the sound task, LCD driver, TV routing, battery logic, controller scanner, SPI NOR, or updater.

## Probe payload behavior

The external payload intentionally bypasses libretro for the very first transport test. It uses only already-confirmed stock XGO interfaces:

```text
run_screen_write = 0x8035c398
P1 final state   = 0x80c33ac4
P2 final state   = 0x80c33ac8
dly_tsk          = 0x8030f480
```

It renders a generated 320x240 RGB565 pattern and exposes controller-state bits visually in top/bottom strips for Player 1 and Player 2.

This would test:

1. loader injection and execution;
2. external code loading at `0x87000000`;
3. stock XGO display transport from external code;
4. both final controller-port state words;
5. clean return to the loader.

It is intentionally **not** an emulator and does not yet test stock audio-core handoff.

## Guarded ASD builder

`tools/multicore/probe/build_probe_asd.py` refuses to patch unless all of the following are true:

- input SHA-256 exactly matches the preserved XGO firmware;
- `0x1500..0x217f` is still all zero;
- loader is <= 3200 bytes;
- stock bytes at file offset `0x360cf4` exactly match XGO's original `jal run_gba` instruction;
- final LCFG payload size and CRC32/MPEG-2 self-verify.

The patch changes only three semantic regions:

```text
0x018c..0x018f       LCFG CRC32/MPEG-2
0x1500..             injected loader bytes inside the stock zero hole
0x360cf4..0x360cf7   GBA call-site redirect to 0x80001500
```

Payload size does not change.

## Offline test against preserved XGO firmware

Using the current 402-byte loader, the guarded local patch build produced:

```text
payload size     0x00c2d2c4
payload CRC32    0x1d84a1e0   (CRC-32/MPEG-2)
output SHA-256   367e044e25190df26c21df413eb201599616ffc391bf6db3282b2eafcc309ac5
```

These values describe the local research build from the exact preserved stock image and current prototype loader; changing compiler output will change the CRC/output hash.

## Why this is important

This is the first point in the research where an XGO executable modification is not just theoretical.

We now have a complete offline chain:

```text
exact stock bisrv.asd
    -> validate fingerprint/layout/instruction bytes
    -> compile tiny XGO-specific loader
    -> compile external MIPS proof payload
    -> inject loader into known unused firmware space
    -> redirect one known stock GBA call site
    -> recompute XGO LCFG CRC32/MPEG-2
    -> audit resulting image
```

No `Firmware.upk` is created and no internal-flash write mechanism is used.

## Remaining boundary before hardware test

A future first hardware test should still use a separate SD card and should be treated as experimental. Before that test, the generated image should be independently disassembled/audited again and the bootloader recovery assumptions should remain conservative.

The purpose of this stage is not to rush a device test; it is to establish that the patch mechanism is small, deterministic, reversible at the SD-card level, and grounded in verified XGO addresses.
