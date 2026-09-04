# Hardware Test 15 — A68K ABI fix still hangs at Loading

Status: **HARDWARE FAIL / ABI MISMATCH WAS REAL BUT NOT SUFFICIENT**

Observed on physical XGO:

```text
select CPS1 game
 -> stock "Loading....."
 -> freeze
```

Behavior is unchanged from Test 14.

## What Test 15 changed

Test 15 corrected the legacy MIPS A68K register-block ABI to match the assembly's exact expected layout:

```text
0x40 ISP
0x44 SR_H
0x48 packed flags
0x4c PC
0x50 IRQ
0x54 IRQ callback
0x58 PPC
0x5c reset callback
0x60 SFC
0x64 DFC
0x68 USP
0x6c VBR
0x70 CPU version
0x74 FullPC
```

The prior Test 14 wrapper layout was incompatible.

## Conclusion

The context ABI mismatch was a genuine static defect, but fixing it does not get A68K through CPS1 initialization.

The remaining failure still occurs before the stock Loading overlay is cleared and before any CPS1 video is produced.

Therefore the next useful step is not another speculative A68K patch. It is instrumentation of the FBA2012 load/init sequence to identify the exact blocking call.

Highest-value checkpoints:

- entry to external core;
- before/after `retro_init()`;
- before/after `retro_load_game()`;
- inside `BurnDrvInit()`;
- before/after CPS1 driver init;
- before/after `SekInit()`;
- before/after `SekReset()`;
- before first `M68000_RESET` / `M68000_RUN`.

## Current CPS1 candidate status

MAME2000:
- functional;
- controls fixed;
- too slow to replace stock.

FBA2012 Musashi:
- reaches SFII self-test;
- freezes at first-frame boundary.

FBA2012 A68K Test14:
- hangs during Loading.

FBA2012 A68K Test15 ABI-fixed:
- same Loading hang.

Stock XGO CPS1 remains the only acceptable gameplay baseline.

## Baseline protection

Mapper v19, NES, Snes9x2005 and stock CPS2/IGS/Neo Geo remain untouched.
