# CLASSIC Test54 — isolated bottom-label fix candidate

Date: 2026-09-10
Branch: `research-game-metadata-enrichment`

## Purpose

Restore the CLASSIC bottom-list label on top of the hardware-passed Test53 metadata-enrichment lineage without touching Refresh, catalogs, MAME2000, Mapper v19, Audio OSD, or Test52 Save/Load.

## Base

Test53 hardware-passed candidate:

```text
xgo-classic-test53-metadata-enrichment.zip
SHA-256 5e64494ebf4339a0bb8e19924f363a891d6fcd5b719732d282d1692df7876d17
firmware 40083d8d05297bef6fd4dc6122f09151ddba6c6db1c4060b917ecbc2ee40c217
core     60a62e463fd6faf92744a7be666602dd1621b9fd706f90d20e3b55ee3382bb1e
```

## Current renderer contract

At the bottom-label draw site:

```text
0x803597d4  lw    t2,-3452(gp)
...
0x80359838  jal   0x803528a4
0x8035983c  sw    s7,24(sp)      # delay slot / text pointer
```

`t2` is already the active list index used immediately above to index the bottom-label table. This lets the repair stay local to the renderer call.

## Test54 patch

The old Test34 scanner-tail area is zero in the Test53 firmware. Test54 uses:

```text
0x807dba64..0x807dba83  32-byte list-aware wrapper
0x807dba90..0x807dba97  "CLASSIC\0"
```

The call at `0x80359838` is redirected to `0x807dba64`.

Wrapper behavior:

```text
if (t2 == 11)
    *(sp + 24) = "CLASSIC";

tail-jump stock renderer 0x803528a4;
```

The original delay-slot store remains unchanged, so non-CLASSIC lists receive the exact stock source pointer. For list 11 only, the wrapper overwrites stack +24 before tail-calling the stock renderer.

## Isolation audit

Allowed firmware deltas are restricted to:

- firmware CRC word `0x18c..0x18f`;
- call instruction at `0x80359838`;
- wrapper bytes `0x807dba64..0x807dba83`;
- string bytes `0x807dba90..0x807dba97`.

No other firmware byte differs from Test53.

Candidate identities:

```text
xgo-classic-test54-label-fix.zip
SHA-256 b5153cf3cd4068964cd706c4135e45be3183590428759280f233fbae0e618172
firmware 8e848b321356e4d57b0b35106e5d3265bd5b8631c6f11e339500c264f1e7a98e
core     60a62e463fd6faf92744a7be666602dd1621b9fd706f90d20e3b55ee3382bb1e
```

## Hardware gate

1. Boot normally.
2. Enter CLASSIC and verify the garbled bottom strip is replaced by `CLASSIC` in stock position/style.
3. Visit at least one stock console and stock Arcade list and verify their bottom label is unchanged.
4. Run Refresh with no changes; confirm stable no-change path.
5. Launch the Test53 metadata/artwork game and verify launch remains normal.
6. Verify CLASSIC Save and Load still work.

Do not promote Test54 until the above hardware checks pass.