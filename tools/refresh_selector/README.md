# Refresh Games selector replacement module — reconstruction specification

This directory owns the replacement for the Test85/Test106 diagnostic selector.

Baseline firmware SHA256:
`b66dbcd86ad785875a6804bb7d07c6eb1195ceedb01c0bce8107f65eee2ab66e`

Reserved module range:
`0x80A389C8..0x80A391F8` (0x830 bytes).

## Behavioral contract

```text
normal state 14
  row 0..2 -> exact stock behavior
  row 3    -> enter Refresh Games selector

Refresh Games
  UP       -> stock state-14 navigation with active terminal 7
  DOWN     -> stock state-14 navigation with active terminal 7
  B        -> selector-active Test118 close/redraw; inactive path reproduces exact stock B
  A        -> stock confirm seam; command=selected; enter native Refresh 0x807DB5CC
```

Module IDs:
0 FC, 1 SFC, 2 MD, 3 GB, 4 GBC, 5 GBA, 6 Arcade, 7 CLASSIC.

CLASSIC dispatch after native workspace initialization:
`s5=0; j 0x80A38000`.

## Hard constraints

- no direct UI -> 0x80A38000 call;
- no invented frontend state;
- no guessed resource triplets or /REFRESH resource directory;
- no blocking/modal controller loop;
- no custom Up/Down/A event decoder; preserve stock state-14 input lifecycle;
- B interception is allowed only at the HW-proven Test118 seam with exact stock inactive behavior;
- no change to Test106 MD/catalog.xgc or MD/catalog-safe.xgc;
- no change to protected status strings/logging/Volume OSD;
- no GB/GBC/GBA execution adapter until separately authorized;
- patcher must verify original words before every firmware write;
- emitted module must fit entirely below 0x80A391F8.

## Known call/data surfaces

```text
native Refresh entry       0x807DB5CC
post-workspace hook        0x807DB67C
CLASSIC continuation       0x80A38000
stock text draw            0x803528A4
User Menu redraw           0x80359ABC
User Menu confirm seam     0x80359E94
User Menu row dispatch     0x80359EA8
up-wrap terminal site      0x80359AA4
down terminal site         0x80359E60
framebuffer                0x80C33364
screen width               0x80C3395C
screen height              0x80C33958
present                    0x8035C398
```

## Construction status

Cave allocation and control contracts are closed. Exact instruction-level replacement is being built next. No hardware artifact is authorized by this specification alone.


## Test106 state ownership correction

Exact binary inspection proves `0x80A389C0` and `0x80A389C4` are live inherited selector state words referenced by the Test85/Test106 dispatcher and renderer. They are zero-initialized data, not free cave. Executable allocation begins at `0x80A389C8` unless those references are deliberately migrated first.


## 2026-09-21 B-cancel / allocation correction

Direct Test113/Test116/Test117 comparison closed two important gaps.

1. Test113's renderer is live through `0x80A38FC8`.  Its second register-restore
   epilogue occupies `0x80A38F70..0x80A38FC8`.  Tests116/117 incorrectly
   placed a helper at `0x80A38F90`, corrupting that epilogue.  This explains
   the late regression/hard lock.  For a Test113-derived layout, the remaining
   verified free tail begins at `0x80A38FD0`.

2. Test113 still inherits Test106's old active-dispatch special case
   `selected_row == 3 -> close selector + redraw User Menu`.  Because the new
   UI labels row 3 **Game Boy**, selecting Game Boy in Test113 executes the old
   diagnostic Back/close operation rather than Refresh.  That exact close
   sequence is now the BIN-pinned semantic target for B.

Final selector contract is therefore:

```text
A row 0..7 -> command 0..7 -> native Refresh lifecycle
B active   -> old proven selector-close state transition -> User Menu redraw
B inactive -> exact stock B path
```

The A dispatcher must be repaired so row 3 is no longer overloaded as Back.

See `findings/refresh-selector-b-cancel-and-test117-root-cause.md`.


## HW checkpoint — Test119 PASS

Test119 is the current protected selector checkpoint.

Firmware SHA-256:
`d357a86a79175d7c07877026ccfaa94c352fd571ba7d54b08d1e9acf1cdf4c15`

LCFG CRC-32/MPEG-2:
`0x39A338DE`

HW-proven cumulative behavior:
- clean eight-row REFRESH GAMES overlay;
- navigation through all eight rows;
- B closes selector to normal Setup and device remains responsive;
- A is an individual command for rows 0..7, including Game Boy at row 3;
- caller state-14 selection is normalized to ordinary User Menu row 3 before native Refresh;
- after a Refresh operation/status return, REFRESH GAMES can be entered again.

Deterministic emitter:
`build_test119_from_test106.py`

The emitter accepts only exact Test106, reconstructs the HW-proven Test118 selector/renderer/B state, asserts its exact SHA, emits the Test119 A-dispatch delta from MIPS instruction constructors, preserves the renderer epilogue, reseals LCFG, and asserts the final Test119 SHA/CRC.

Future feature: `Refresh All` is an explicit ninth row/command only. It is never implicit in A on one of the eight system rows.


## HW checkpoint — Test122 PASS and execution-wiring correction

Test122 is the current HW-positive selector/UI checkpoint. It conditionally bypasses the native state-14 172x172 Setup selector compositor while `selector_active != 0`, eliminating the blue selection border behind REFRESH GAMES without changing Test119 input/navigation/Refresh lifecycle.

Firmware SHA-256: `6378e4a9cbf560afa53c38836826c294c9b2316310d65eb9860894c221cb2f0d`
LCFG CRC: `0x0EFF6110`.
Builder: `build_test122_from_test119.py`.

Residual OPEN UI issue: B close can expose stale `No New Games` on ordinary Setup until another option is selected.

Important command correction: the UI command bridge is eight-way, but the inherited execution dispatcher is not. Exact BIN audit shows command 0 -> FC, command 1 -> SFC, and every other value -> MD. Thus GB/GBC/GBA/Arcade/CLASSIC are not yet functionally wired and must not be described as individual working Refresh operations.

Current priority is CLASSIC rescue. Command 7 must branch after native Refresh workspace initialization to the preserved CLASSIC continuation `s5=0; j 0x80A38000`. Commands 3..6 must cease aliasing MD before they are exposed as working operations. GB/GBC/GBA follow; Arcade is separately classified across CPS1/CPS2/NeoGeo/IGS.
