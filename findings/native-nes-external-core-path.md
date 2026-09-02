# Native NES external-core path

Status: **offline implementation path substantially complete; hardware execution not yet attempted**.

Firmware SHA-256:

`869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf`

## Why native NES interception is cleaner than the fake-GBA proof

XGO `run_game()` preloads ordinary NES content into `gp_buf_64m` and only then calls the NES runner:

```text
0x80360c18..0x80360c88  open/size/read selected file into gp_buf_64m
0x80360e20              jal 0x8035f63c ; run_nes
```

Therefore replacing only the JAL at `0x80360e20` allows a newer FCEUmm core to launch from the normal XGO NES lists without fake `.gba` stubs or User Games.

The original instruction is:

```text
runtime/address  0x80360e20
ASD offset       0x00360e20
bytes            8f 7d 0d 0c
instruction      jal 0x8035f63c
```

## Stock NES runner contract

`run_nes = 0x8035f63c`:

1. clears bit 0 of `g_snd_task_flags` and waits for the sound task to stop;
2. installs the embedded NES/FCEUmm function pointers into the common frontend globals;
3. tail-jumps to `run_emulator = 0x8035ed48`.

The external loader only has to replace steps 2/3 after safely loading the modern core. It reproduces the sound-task shutdown after all XGOC validation succeeds.

## Native loader

Implementation:

`tools/multicore/native_nes/xgo_nes_loader.c`

Behavior:

```text
if live stock heap >= 0x87000000
    -> call stock run_nes

reserve stock upper heap window
open /mnt/sda1/cores/fceumm/core.xgc
validate XGOC header, bounds, header CRC, payload CRC
load at 0x87000000
zero runtime/BSS tail
stop stock sound task
flush full HC15xx D/I cache index space
call external entry(filename, load_state)
restore RAMSIZE
```

Every validation/file failure restores `RAMSIZE` and calls untouched stock `run_nes()`.

## Native frontend

Implementation:

`tools/multicore/native_nes/xgo_nes_native_frontend.c`

The frontend uses the ROM already loaded by stock `run_game()`:

```text
GAME_INFO.path = original NES filename
GAME_INFO.data = gp_buf_64m
GAME_INFO.size = exact file length
```

Because `run_game()` rounds `g_run_file_size` upward to four bytes before reading, the bridge reopens the file only to recover the exact byte length; it does not copy the ROM again.

The core links with:

`tools/multicore/xgo_preloaded_rom_sbrk.c`

which starts external newlib after the 64-byte-aligned preloaded ROM prefix and leaves those ROM bytes intact.

## Normal teardown

XGO `run_emulator()` calls `GFN_UNLOAD_GAME` itself at `0x8035f284`, then returns.

The native bridge therefore:

1. lets stock `run_emulator()` invoke FCEUmm `retro_unload_game()`;
2. calls `retro_deinit()` after return;
3. restores all borrowed stock frontend globals.

## Guarded ASD patcher

Implementation:

`tools/multicore/native_nes/build_native_nes_asd.py`

The patcher requires:

- exact XGO stock SHA-256;
- zero-filled `0x1500..0x217f` loader cave;
- exact stock NES JAL bytes `8f 7d 0d 0c` at `0x00360e20`;
- loader length <= 3200 bytes.

It writes `jal 0x80001500`, recomputes LCFG payload size/CRC32-MPEG2, and writes a separate ASD image.

It does not create or touch `Firmware.upk` or SPI NOR.

## Offline loader build result

Using LLVM MIPS32 little-endian soft-float flags:

```text
--target=mipsel-none-elf
-march=mips32
-msoft-float
-G0
-mno-abicalls
-fno-pic
-ffreestanding
-fno-builtin
-Os
```

the current native loader builds to:

```text
1035 bytes / 3200-byte cave
entry: 0x80001500
$gp references: 0
.got: absent after hardened linker script
.sdata/.sbss: absent
```

The machine-code audit confirms the first safety branch reads `XGO_HEAP_BREAK` at `0x80c337b0`, compares it with `0x87000000`, and directly calls stock `run_nes @ 0x8035f63c` when the upper-memory reservation would be unsafe.

## Linker hardening

The shared injected-loader linker script now discards orphan `.got/.sdata/.sbss` sections and the native build script fails if emitted loader code references `$gp`.

This is intentionally stricter than the external emulator image itself: the tiny injected loader has no private global-pointer startup and must remain completely GP-independent.

## Result

The direct-main-list experiment now has a concrete offline chain:

```text
normal NES main-list entry
    -> stock run_game preloads ROM
    -> one guarded JAL redirect
    -> 1035-byte native XGOC loader
    -> external FCEUmm image @ 0x87000000
    -> stock XGO video/audio/P1/P2/run loop
    -> restore stock frontend state
```

If the external core cannot be validated, the same patched firmware falls back to the original embedded NES emulator.

## Confidence

**CONFIRMED:** stock ROM preload path and native NES dispatch call.

**CONFIRMED:** stock run_nes sound-shutdown / function-install / tail-call structure.

**CONFIRMED:** native loader fits the existing injection cave and emits no `$gp` references under the current LLVM build.

**CONFIRMED:** guarded patcher modifies only the exact NES dispatch JAL plus loader cave and LCFG CRC metadata.

**NOT YET DEVICE-PROVEN:** execution of the native external FCEUmm path on physical XGO hardware.
