# Core #3 Test 14 candidate — FBA2012 CPS1 with native-MIPS A68K backend

Status: **OFFLINE AUDIT PASS / HARDWARE TEST JUSTIFIED**

## Why this candidate exists

Hardware Test 13 closed the MAME2000 performance question:

- adaptive frameskip works;
- visible frame skipping becomes noticeable;
- gameplay remains slower than the stock XGO arcade emulator.

Therefore MAME2000 is not a viable performance replacement for CPS1 on XGO.

The dedicated FBA2012 CPS1 core remains much smaller and more specialized, but the original SF2000 build used the portable Musashi 68000 interpreter and froze inside the first frame on XGO.

The source tree contains an older native-MIPS A68K backend:

```text
src/cpu/a68k/mips/a68k.s
src/cpu/a68k/mips/a68ktbl.inc
```

## Runtime selection contract

FBA's current interface supports dual backends.

When `BUILD_A68K` is defined:

```text
bBurnUseASMCPUEmulation = true
```

and for a plain 68000 CPU, `SekInit()` selects `SekInitCPUA68K()`.

CPS1 uses a 68000, so this candidate will enter A68K rather than silently falling back to Musashi.

## Porting the Allegrex assembly to XGO baseline MIPS32

The bundled MIPS A68K source was written for PSP Allegrex and declares:

```text
.set arch=allegrex
```

It contains:

```text
634 x seb
596 x seh
1   x ror
4   x rorv
```

These instructions are not valid under the baseline `-march=mips32` contract used by XGO.

The audit patch rewrites them mechanically:

```text
seb rd,rs -> sll rd,rs,24 ; sra rd,rd,24
seh rd,rs -> sll rd,rs,16 ; sra rd,rd,16
ror/rorv  -> baseline shift/or sequences using $1 as scratch
```

The original source contains zero explicit uses of `$1`, making that scratch choice safe.

The source also contained an old private 13-word `a68k_memory_intf` allocation. Current `m68000_intf.cpp` already owns and initializes that structure, so the assembly copy was converted to an external reference.

## Offline build result

GitHub Actions:

```text
workflow: XGO FBA2012 A68K MIPS audit
run: 33919868046
commit: fcbf762751cff3b40db6c7c5b8d4c9007b14031c
result: SUCCESS
```

Final link:

```text
undefined symbols: 0

M68000_RESET   @ 0x870018e4
M68000_RUN     @ 0x870018ec
bBurnUseASMCPUEmulation present and enabled by BUILD_A68K
```

XGOC footprint:

```text
payload   2,753,560 bytes
runtime   3,637,208 bytes
headroom  9,842,216 bytes
```

Core:

```text
core-fbalpha2012-cps1-a68k.xgc
SHA-256 e7ddb6eb0bc36f1f93ee1cfc17eb4aba5b7f80e758a1d4ea622c90978ada8174
```

## ISA safety audit

The final linked disassembly contains zero instances of:

```text
seb
seh
ror
rorv
wsbh
ext
ins
rdhwr
synci
ehb
```

The normalized A68K backend therefore no longer exposes the obvious Allegrex/MIPS32r2 instruction surface.

## Hardware-test architecture

Test 14 returns to the known corrected FBA2012 architecture from Test 08:

```text
CPS1 list ID 7
 -> corrected runtime hook
 -> stock XGO path globals
 -> ARCADE/bin/<game>.zip
 -> FBA2012 CPS1
 -> A68K native-MIPS 68000 backend
```

CPS2/IGS/Neo Geo remain stock.

Mapper v19, NES and Snes9x2005 remain unchanged.

## Acceptance questions

1. Does SFII progress beyond the self-test where Musashi FBA2012 froze?
2. Do other CPS1 games reach gameplay rather than black-screen freeze?
3. If gameplay works, is speed better than stock XGO CPS1?
4. Is frame pacing better than stock?
5. Is audio usable and synchronized?
6. Does pause/QUIT return correctly?
7. Are CPS2, Mapper and SNES still unaffected?
