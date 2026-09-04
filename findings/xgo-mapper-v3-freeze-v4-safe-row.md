# XGO mapper v3 pause freeze and v4 safe-row correction

Status: **V3 HARDWARE FAILED; V4 STATICALLY CLOSED, HARDWARE TEST PENDING**

## Hardware result

Mapper v3 freezes the device immediately when START+SELECT opens the pause menu. The failure occurs before any mapper interaction, so the regression is in pause-menu rendering/control flow rather than mapper mutation or persistence.

## Root cause

V3 changed the stock generic pause-row loop at:

```text
0x80354710  li s1,3 -> li s1,4
0x80354718  li s2,0x106 -> li s2,0x146
```

Static re-analysis shows that this loop is not just a geometric text loop. It consumes a stock temporary text buffer associated with the native QUIT/LOAD/SAVE entries. Increasing the iteration count to four advances beyond the stock three-entry buffer and can corrupt renderer state during pause-screen construction. This matches the hardware freeze exactly.

Therefore the native loop bound must remain untouched.

## Safe v4 design

V4 restores the stock QUIT/LOAD/SAVE loop byte-for-byte and appends MAPPER with one independent invocation of the same stock text primitive after the native rows finish.

Renderer hook:

```text
0x803547bc  stock: lw s0,-3524(gp)
             v4: j menu_row_hook
0x803547c0  stock: slti s5,s0,2
             v4: nop
```

The cave hook:

1. recreates the displaced page-state load,
2. computes the same selected/unselected color convention used by the native rows,
3. draws the literal `MAPPER` at x=0x50, y=0x146 (326),
4. recreates `slti s5,s0,2`, and
5. resumes stock renderer flow at 0x803547c4.

The stock three-entry text buffer is never extended or indexed beyond its original bounds.

V4 retains the previously proven mapper mutation/persistence architecture and the corrected full-ROM-name .kmp writer path.

## Candidate identity

```text
firmware SHA-256: 362a47730bb0144fa1a0dd07ddf1e798e060722bd010a6423b10384c3b1606c0
ZIP SHA-256:      720f0b347b51098d14e03b41e61e1575151aeb68ae04c5410802dbb562f5d70e
LCFG CRC-32/MPEG-2: 0xf62c8f88
```

## First hardware gate

Before testing any remap:

1. open pause menu with START+SELECT,
2. verify it renders and remains responsive,
3. verify MAPPER appears below SAVE,
4. only then enter the mapper.

If step 2 fails, stop immediately; no mapper or persistence behavior should be evaluated from that build.
