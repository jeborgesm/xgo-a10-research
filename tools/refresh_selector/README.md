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
  B        -> preserve native state-14 Back behavior (no custom B hook)
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
- no custom Up/Down/A/B event decoder; preserve stock state-14 input lifecycle;
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
