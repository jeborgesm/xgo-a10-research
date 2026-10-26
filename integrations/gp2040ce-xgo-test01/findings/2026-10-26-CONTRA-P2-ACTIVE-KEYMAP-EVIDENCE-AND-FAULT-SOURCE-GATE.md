# Contra P2 ghost-input investigation: what the active .kmp can and cannot establish

**Date:** 2026-10-26. **Branch:** `research-gp2040ce-xgo-integration`. **Status:** original XGO NES embedded fallback [BIN], keymap loader/compiler [SRC], observed intermittent P2 Contra JUMP [HW], prior Test49 unsolicited PAUSE [HW], negative native-R A-B-A [HW], attached current active Contra profile **OPEN**. No firmware, cabling, core, P2 configuration or game file modified.

## 1. The owner result controlling further work [HW]

The user reported spontaneous P2 Contra JUMPs with external GP2040 idle for each A–B–A condition:
- native R released — JUMP;
- native R held — JUMP;
- native R released again — JUMP.

The rate appeared about the same across all three. Actual counts were not supplied. This rules out the predicted **observable** difference of the four-instruction native-R-conditioned physical Handle R0 sample branch. It does **not** rule out a wider DATA loading problem, later serial bit, or CPU/clock issues. The experiment has been recorded and closed: [negative HW A–B–A](2026-10-25-HW-NATIVE-R-ABA-NEGATIVE-CONTRA-P2-GHOST-JUMPS.md). Do not repeat it.

## 2. Original firmware NES fallback [BIN, directly verified]

Actual locally available user original firmware: `/mnt/data/XGoAnalisis.zip` member `bios/bisrv.asd` SHA256 `869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf`, size `12,768,452` bytes. Direct read-only local extraction and `struct.unpack_from('<12I', bin, 0x8ddd34)` yielded:

```
P1 six records X,Y,L,A,B,R
00010008 00010000 00010000 00000008 00000000 00010008
P2 six records X,Y,L,A,B,R
00010008 00010000 00010000 00000008 00000000 00010008
```

Under FC/libretro selector semantics [SRC] `8=NES A/JUMP`, `0=NES B/FIRE`, bit16=`TURBO`:

| Physical Handle P2 action input | Wire slot | Embedded fallback | Visually plausible game action |
|---|---:|---|---|
| R | 0 | NES A + turbo | repeated JUMP |
| Y | 1 | NES B + turbo | repeated FIRE |
| X | 2 | NES A + turbo | repeated JUMP |
| L | 3 | NES B + turbo | repeated FIRE |
| A | 4 | NES A | JUMP |
| B | 5 | NES B | FIRE |

**Important: three separate physical bits can produce the same visible JUMP.** An unsolicited jump **does not identify a false slot0 R**, even if a first-bit DATA loading hypothesis remains plausible. Do not infer R from a single game animation.

## 3. Loaded per-game .kmp is not among available user artifacts [OPEN]

The XGO source-derived loader uses `%s/save/%s.kmp`, with **48 little-endian bytes**. It loads six independent records for each physical P1 and P2 (`X,Y,L,A,B,R`); when no matching profile loads it copies the embedded system fallback. P1/P2 can differ even if the stock writer often mirrors P1 into P2 when persisting a keymap.

Current available ZIP evidence (read-only local inspection):
- `XGoAnalisis.zip`: 115 entries, **zero `.kmp` or Contra paths**.
- `XGO-TRANSPARENT-RESTORED-OLED-PROTECTED-BASELINE.zip`: no Contra `.kmp`.
- `XGO-PAGED-OLED-HARDWARE-UNVERIFIED.zip`: no Contra `.kmp`.
- `xgo-transparent-linked-elf-audit.zip`: no Contra `.kmp`.

**That does not mean the actual device lacks a keymap.** The current SD `FC/save` contents and exact loaded ROM filename have not been supplied. The active mapping remains unknown. The embedded fallback is a **conditional control**, not a verified active profile.

## 4. The START/SELECT nuance and the historical unsolicited PAUSE

The physical serial word has distinct `SELECT` (slot6) and `START` (slot7) bits and the keymap compiler processes **six face/shoulder inputs only**. Thus the physical START/SELECT slots are not among the twelve `.kmp` source records. **But** each remappable face/shoulder record's low16 is a libretro target button ID, and the real mask table supports `2=SELECT` and `3=START`. A custom per-game `.kmp` could therefore map, e.g., physical P2 L to logical START. This is a *selector capability* [SRC], **not evidence that Contra's current .kmp contains that mapping**.

The native frontend's own SELECT+START menu shortcut and a game's response to logical START are not necessarily the same path. **Do not call historical Test49 PAUSE proof of a corrupted physical START bit** without knowing whether the action was the native frontend menu versus the game's internal pause and the active keymap. It remains evidence of a wider unexplained action class in an older diagnostic firmware, with different setup from current A.

## 5. Completed exact-file analyzer, not a patch

[`tools/xgo-protocol-audit/audit_fc_keymap.py`](../../../tools/xgo-protocol-audit/audit_fc_keymap.py) reads an existing 48-byte `.kmp` from a specified absolute path **without editing it**, decodes **both** P1 and P2, identifies P2 inputs targeting Jump/Fire and logical START/SELECT, and flags unusual high bits. If supplied an exact SD FC root and active ROM basename, it constructs the expected `FC/save/<rom full filename>.kmp`. If absent, it emits `NO_FILE_AT_SPECIFIED_PATH`, explicitly marks runtime mapping UNKNOWN until the exact root/filename are validated, and does not invent the loaded default.

Example when the real SD becomes available:

```sh
python3 tools/xgo-protocol-audit/audit_fc_keymap.py --kmp "/path/to/existing/FC/save/Contra (USA).nes.kmp" --json
python3 tools/xgo-protocol-audit/audit_fc_keymap.py --fc-root /path/to/SD/FC --rom-filename "Contra (USA).nes"
```

`Contra (USA).nes` in examples is **illustrative only**, NOT established as the user's ROM filename.

Five [unit tests](../../../tools/xgo-protocol-audit/test_audit_fc_keymap.py) cover the original embedded NES table, custom asymmetric P2 mapping, logical START/SELECT target possibility, exact filename/missing-file semantics, and rejection of non-48-byte data. [Existing fast serial GitHub Actions #40334342549](https://github.com/jeborgesm/xgo-a10-research/actions/runs/40334342549) **PASS**, including new five tests and protected earlier regressions. The tests' fallback words are independently checked locally on SHA-pinned actual original `bisrv.asd`. **No actual Contra `.kmp` has been read or fabricated.**

## 6. Revised investigative consequence

A useful next data item is the **actual ROM basename and matching FC/save 48-byte `.kmp` if present**. That will identify which raw P2 face/shoulder bits *could* produce JUMP in this exact game and whether any logical START target exists. A profile alone still cannot identify a bad signal's electrical origin.

Other true hardware evidence remains:
- P3 RX-only native USB-PHY and earlier GREEN probe triggered spontaneous P2 jumping without any transmitted button bits (different cable, not necessarily current Frankie root cause).
- P5 native USB-PHY diagnostic could not classify a valid 12-clock wave and showed only occasional JUMP; do not treat native PHY passive jump as proof that its input decoder was seeing the whole serial bus.
- The protected GP2040 A compiled seven-instruction SRAM CLOCK observer is fast in principle but its current actual electrical edge-loss rate is unmeasured.
- The previous GOLD Handle=P1 OR merge is unnecessary for the newly witnessed independently routed Handle=P2 ghost.

Avoid prematurely changing clock timeout or slot0 wait, altering protected GOLD `bisrv.asd`, swapping the native PHY pull overrides (the DM override froze XGO), injecting attack pulses, or touching Frankie connector wiring. No new test firmware produced or requested. The next physical root-cause proof still requires the actual host-decoded P2 word or non-perturbing physical DATA/CLOCK evidence associated with a spontaneous action.
