# Native FCEUmm ↔ XGO stock frontend ABI

Status: **statically confirmed for the pinned HC15xx FCEUmm core; physical execution pending**.

This finding records the field-by-field compatibility work performed after the first complete native FCEUmm image linked successfully. The important distinction is that a zero-undefined-symbol ELF is not by itself proof that the external core is using the stock frontend correctly. Each libretro boundary must also match the XGO firmware's actual callback semantics.

## Pinned core and firmware

FCEUmm:

```text
repository  madcock/libretro-fceumm
commit      e6111e684e7a7761f3f1d6c80d0a825e2c8cdc7e
```

XGO firmware:

```text
bios/bisrv.asd SHA-256
869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf
```

Relevant stock callbacks:

```text
retro_video_refresh_cb      0x8035e70c
retro_audio_sample_batch_cb 0x8035e7d8
retro_input_poll_cb         0x8035ea30
retro_input_state_cb        0x8035eb20
retro_environment_cb        0x8035eb64
run_emulator                0x8035ed48
```

## Preloaded ROM path: correction to the first implementation

The native interception occurs after stock `run_game()` has already opened the selected `.nes` file and preloaded it into `gp_buf_64m`. The native frontend therefore populated ordinary `struct retro_game_info` as:

```text
path = selected filename
data = gp_buf_64m
size = exact ROM size
```

The initial assumption was that the pinned FCEUmm `retro_load_game()` would consume `info->data` directly.

Static inspection proved that assumption wrong.

In pinned FCEUmm, `retro_load_game()` initializes:

```text
content_data = NULL
content_size = 0
content_path[2048]
```

and first asks the frontend for:

```text
RETRO_ENVIRONMENT_GET_GAME_INFO_EXT = 66
```

If that query fails, FCEUmm copies only `info->path`; it does **not** copy ordinary `info->data` into `content_data`. The subsequent `FCEUI_LoadGame()` therefore receives a null data pointer and reopens the ROM through the filesystem.

Consequently, the first fully linked native image could still have worked, but it would have silently performed a second ROM read. The preloaded-ROM heap reservation would have been conservative rather than the active content handoff.

### Corrected command-65/66 contract

Commit `24ddf84bde691311a5779a2fc41fb722b2990387` added `RETRO_ENVIRONMENT_GET_GAME_INFO_EXT` to `xgo_minimal_environment_shim.c`.

The shim synthesizes the pinned 32-bit `retro_game_info_ext` structure from stock `g_retro_game_info`:

```text
full_path       = selected stock path
data            = stock-preloaded gp_buf_64m
size            = exact ROM size
file_in_archive = false
persistent_data = true
```

The Codescape link map independently confirms that this structure is exactly `0x28` bytes, matching the pinned 32-bit libretro ABI.

Commit `6756de55e2a3e5cf2b967a7fef01e9ec42d7645f` then implemented:

```text
RETRO_ENVIRONMENT_SET_CONTENT_INFO_OVERRIDE = 65
```

and returns success for FCEUmm's declared:

```text
extensions      fds|nes|unf|unif
need_fullpath   false
persistent_data false (core requirement)
```

The frontend can legitimately accept that override because the XGO native path already owns a complete memory-backed copy of the selected NES content before FCEUmm starts.

The resulting negotiation is now internally consistent:

```text
FCEUmm SET_CONTENT_INFO_OVERRIDE(65)
        ↓ success
FCEUmm retro_load_game()
        ↓
GET_GAME_INFO_EXT(66)
        ↓
XGO returns gp_buf_64m + exact ROM length
        ↓
FCEUI_LoadGame(path, preloaded_data, size)
```

### FCEUmm truly aliases the stock ROM buffer

Inspection of pinned `src/fceu.c` and `src/file.c` closes the remaining memory question.

`FCEUI_LoadGame(name, databuf, databufsize)` passes the supplied memory buffer to `FCEU_fopen()`. The memory wrapper created by `MakeMemWrapBuffer()` stores:

```text
tmp->data_int = NULL
tmp->data     = buffer
```

It does not allocate or copy the ROM payload. `FCEU_fclose()` likewise does not free the caller-owned buffer when `data_int == NULL`.

Therefore the native path is now genuinely zero-copy after stock preload:

```text
SD → stock run_game() → gp_buf_64m → FCEUmm memory stream
```

There is no second full-ROM allocation and no second ROM-file read.

The custom external-core `sbrk()` begins above the stock-preloaded ROM prefix, so the aliased buffer remains persistent for the complete core lifetime.

## Input ABI

Pinned FCEUmm probes:

```text
RETRO_ENVIRONMENT_GET_INPUT_BITMASKS = 51 | 0x10000
```

If supported, FCEUmm would call the input callback using `RETRO_DEVICE_ID_JOYPAD_MASK` (`id = 256`).

Direct XGO disassembly proves that stock `retro_input_state_cb` at `0x8035eb20` has no id-256 fast path. It performs a per-button table lookup:

```text
port < 2
mask = table[(port * 16) + id]
return g_joy_state[port] & mask
```

The stock environment currently returns false for the experimental bitmask capability, so pinned FCEUmm naturally falls back to individual button queries. Commit `29747005773f95783149f3c68d0dc0110032da1f` makes that false result explicit in the external environment shim rather than depending on the stock handler's unknown-command behavior.

### XGO joypad mask table

The table begins at XGO address:

```text
0x80a3d4d0
```

Both ports contain the same 16 entries. Indexed by standard libretro joypad ID order:

```text
id  button   XGO mask
0   B        0x4000
1   Y        0x8000
2   Select   0x0001
3   Start    0x0008
4   Up       0x0010
5   Down     0x0040
6   Left     0x0080
7   Right    0x0020
8   A        0x2000
9   X        0x1000
10  L        0x0400
11  R        0x0800
12  L2       0x0100
13  R2       0x0200
14  L3       0x0002
15  R3       0x0004
```

Thus FCEUmm's individual joypad queries line up directly with the XGO stock callback ABI.

## Audio ABI

Stock `retro_audio_sample_batch_cb` at `0x8035e7d8` forwards `(data, frames)` to `run_sound_advance()` at `0x8035cba0`.

`run_sound_advance()` computes:

```text
byte_count = frames << 2
```

and copies exactly that many bytes into the stock PCM ring buffer.

Four bytes per libretro frame means:

```text
2 channels × 16-bit signed PCM = 4 bytes/frame
```

which is exactly the FCEUmm audio-batch format.

The XGO callback returns zero rather than the conventional number of consumed frames. This is nonstandard, but it is harmless for the pinned core: `retro_run()` invokes `audio_batch_cb(sound, ssize)` and ignores the return value.

The minimal environment shim advertises 44.1 kHz through the target-sample-rate query. Later stock-audio archaeology corrected the earlier assumption that `3528/2940` were enforced PCM byte budgets: those values are write-only diagnostic/state fields, while `run_emulator()` initializes the sound driver from the core-advertised sample rate and the batch callback copies exactly the frame count supplied by the core.

Therefore FCEUmm's 44.1-kHz rate remains a valid configuration, but it is **not required by a hard-wired 44.1-kHz scheduler model**. See `findings/stock-libretro-audio-timing.md` for the corrected data-flow analysis.

## Video ABI

The external shim accepts only:

```text
RETRO_PIXEL_FORMAT_RGB565
```

because that is the proven XGO stock transport format.

Pinned FCEUmm's ordinary software renderer uses:

```text
pitch  = 512 bytes
width  = 256 pixels before optional horizontal crop
height = 240 pixels before optional vertical crop
```

The stock XGO video callback forwards all four libretro arguments to `run_screen_write()` at `0x8035c398`.

`run_screen_write()` converts the supplied byte pitch to 16-bit-pixel stride using:

```text
pixel_stride = pitch >> 1
```

before passing the surface to `run_osd_region_write()`.

Therefore a 512-byte FCEUmm pitch becomes a 256-pixel source stride exactly as required. Visible width and height remain independent, so FCEUmm's overscan crop can reduce visible geometry without breaking row stepping.

A null video pointer returns without writing a new surface. The existing display remains intact, which satisfies the practical semantics of frame duplication advertised through `GET_CAN_DUPE`.

## Stock emulator-loop state alignment

Direct disassembly of stock `run_nes()` showed that every stock emulator wrapper clears the shared word at:

```text
0x80c2e964
```

immediately before installing the core callbacks. `run_emulator()` later reads/increments this word in its timing/frameskip bookkeeping.

Commit `ee138342e1398b3d7108a1f4b141768fece7d5ac` added the same reset to the native frontend, preventing stale timing state from the previously active core from leaking into FCEUmm.

The private stock frameskip function pointer remains intentionally null for external FCEUmm because no equivalent stock-private hook exists in the upstream libretro core.

## Current reproducible image after ABI hardening

Full-link Actions run:

```text
33650557023
```

Source commit:

```text
29747005773f95783149f3c68d0dc0110032da1f
```

Result: **success, zero undefined symbols, valid XGOC**.

Current layout:

```text
image_start       0x87000000
entry             0x87000000
file_end          0x87186fd0
payload_size      1,601,488 bytes
bss_start         0x87186fd0
image_end         0x873b2068
memory_size       3,874,920 bytes
reserved_size    13,479,424 bytes
headroom           9,604,504 bytes
```

Current output hashes:

```text
xgo-native-fceumm.elf
001db9815bcb3f0a22d64e854c476e7ce6ae7ef6a33927f78c393b03b80da8fe

xgo-native-fceumm.bin
c640393af0703d499a04a4acc3ce6a8353ca1c126b222e276bd548ecf5c12d4a

core-native-nes.xgc
9b7f153a205dbde7c8e4abd2904cb70dc3d9a69ae1d43719306719b4d0401db5
```

XGOC metadata:

```text
load          0x87000000
entry         0x87000000
payload       1,601,488 bytes
runtime       3,874,920 bytes
zero tail     2,273,432 bytes
payload CRC   0xdc6498d7
header CRC    0x104d0390
```

## Remaining boundary

For an ordinary NES launch, the major core/frontend interfaces are now statically aligned:

```text
content   stock-preloaded buffer, direct memory alias
input     standard libretro per-button IDs
video     RGB565, byte pitch correctly converted to 16-bit stride
audio     stereo signed 16-bit PCM, 4 bytes/frame, 44.1 kHz
loop      stock timing accumulator reset before core initialization
```

Save/load-state integration remains intentionally disabled and is a feature gap rather than a first-launch requirement.

The remaining high-value unknowns are physical observations:

- actual live heap-break value when a normal NES is launched;
- large XGOC read into the reserved upper-RAM window;
- cache/IRQ transition with the production FCEUmm payload;
- first real frame/audio/input behavior on XGO hardware;
- clean physical return to the stock UI.
