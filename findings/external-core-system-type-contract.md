# Active system-type contract for external cores

Status: **confirmed from the extension dispatcher, `set_keymap()`, and `run_emulator()` disassembly**.

## Headline

The XGO active emulator-family selector is stored at:

```text
0x80c33ad0 = $gp - 0x0ca4
```

The low 16 bits select the native emulator family:

```text
0x01 NES / Famicom
0x04 Mega Drive / Genesis / SMS
0x08 SNES / Super Famicom
0x10 GBA
0x20 GB / GBC / SGB
0x40 Arcade / FBA
```

An external core intercepted through the GBA launch hook would otherwise inherit `0x10`, even if the content being emulated is not GBA.

For external cores, temporarily setting this selector to the corresponding native family before entering stock `run_emulator()` allows the stock frontend to apply the correct family-specific defaults while the external emulator is active.

## Where the value comes from

The extension classifier at `0x80360a08` searches the 40-entry extension table. A matched entry ORs its system mask into the global at `0x80c33ad0`.

`run_game()` at `0x80360b88` clears this global before classifying a new launch.

Thus this is active per-launch state, not a static board configuration.

## Uses inside the stock runtime

### Default keymap selection

`set_keymap()` and the `.kmp` fallback path inspect the low system bits to select the six embedded family-specific 48-byte default mappings.

If an external NES core is launched through the GBA hook while the selector remains `0x10`, it would inherit the GBA fallback mapping rather than the NES mapping whenever no explicit `.kmp` exists.

### `run_emulator()` behavior

`run_emulator()` repeatedly reads the same low-halfword selector.

Most native families use the generic libretro path:

- obtain `retro_system_av_info` from the active core;
- initialize sound from the returned sample rate;
- obtain region from the active core;
- run through the common frame/input loop.

SNES (`0x08`) is the important exception: it takes a special stock setup/audio path with fixed parameters instead of the ordinary generic AV-info path.

Therefore an external core should not use `0x08` merely to obtain the SNES default keymap unless its compatibility layer also accounts for that stock SNES special case.

NES (`0x01`), Sega (`0x04`), GBA (`0x10`), and GB/GBC (`0x20`) are suitable generic-family identities for their corresponding external cores.

## FCEUmm consequence

A first external FCEUmm launch can safely use the following pattern:

```text
intercept special .gba launch
save old system selector (normally 0x10)
set selector low family = 0x01 (NES)
run external FCEUmm through stock run_emulator()
restore old selector after return
```

This lets stock XGO automatically provide its NES-family keymap/default behavior while the actual emulator implementation is external.

## Broader Multicore design

The external-core launcher should associate every core with an XGO frontend family profile rather than treating all Multicore launches as GBA:

```text
FCEUmm       -> 0x01
PicoDrive    -> 0x04
Gambatte     -> 0x20
GBA core     -> 0x10
Arcade core  -> 0x40
```

SNES should initially remain special-cased because stock `0x08` changes more than keymap selection.

The selector must be restored after the external core exits so the normal frontend remains internally consistent.
