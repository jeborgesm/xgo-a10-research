# Core #3 correction — shared arcade cleanup misidentified; Test 05 uses real runtime hook

Status: **STATICALLY CLOSED; TEST 05 HARDWARE PENDING**

## Hardware observations that forced re-analysis

Test 03/04 produced three seemingly contradictory results:

- Street Fighter II appeared to run with roughly stock-like performance;
- QUIT from CPS1 froze;
- the same QUIT problem affected CPS2/IGS/Neo Geo because all arcade sections share the same stock emulator path.

The user's observation that every arcade family was affected exposed an architectural mistake in the Test 03 hook.

## Root cause

The stock JAL at:

```text
0x80360e00
```

was previously labeled as the arcade runtime/launcher call.

That label was wrong.

The stock word there is:

```text
0x0c0d792d
jal 0x8035e4b4
```

Static disassembly of `0x8035e4b4` shows that it does not consume the game filename or launch `run_emulator()`. It clears/tears down FBA-side tables and returns.

Therefore:

```text
0x80360e00 -> stock arcade cleanup
```

not arcade execution.

Replacing this call with the external CPS1 loader caused exactly the hardware symptom observed:

```text
stock arcade game runs normally
 -> user selects QUIT
 -> stock arcade runtime returns
 -> patched cleanup site launches external CPS1 core at the wrong lifecycle point
 -> freeze
```

This also explains why Test 03 performance looked very similar to stock: the observed gameplay was almost certainly still the stock arcade emulator.

## Correct stock arcade runtime call

Immediately before cleanup:

```text
0x80360df4  move a0,s2
0x80360df8  jal  0x80360848
0x80360dfc  move a1,zero
0x80360e00  jal  0x8035e4b4
```

Disassembly of `0x80360848` shows the actual arcade runtime wrapper:

- installs active libretro callbacks;
- constructs/installs the stock game-info structure;
- installs video/audio/input/state callback slots;
- tail-jumps to:

```text
run_emulator @ 0x8035ed48
```

Therefore the correct interception point is:

```text
0x80360df8
```

and `0x80360e00` must remain stock.

## Arcade subtype discriminator

The stock frontend keeps the active menu/list ID in:

```text
0x80c33980
```

This byte is read immediately before `run_game()` and indexes per-list frontend tables.

Confirmed list mapping:

```text
7  CPS1
8  CPS2
9  IGS/PGM
10 Neo Geo
```

The shared arcade runner later collapses these into the common family bit:

```text
0x40 Arcade/FBA
```

So the list byte is the correct place to preserve subtype identity.

The corrected loader logic is:

```text
if active_list_id == 7:
    run external FBA2012 CPS1
else:
    call untouched stock arcade wrapper 0x80360848
```

After either path returns, execution continues naturally into untouched stock arcade cleanup at `0x80360e00`.

## Test 05 baseline

Test 05 is rebuilt from the exact hardware-passed Test 02 baseline, not from Test 03/04:

```text
Test 02 ZIP
6c8fec790fb8a3d2f93e3d405912aca46d4b1b6db6609775faea74ffdde95869
```

Preserved unchanged:

- mapper v19;
- mapper resource;
- NES path;
- external Snes9x2005 core;
- SNES loader/dispatch;
- stock arcade cleanup;
- CPS2/IGS/Neo Geo stock execution path.

## Test 05 candidate

```text
CPS1 runtime hook
0x80360df8 -> loader @ 0x80002780

stock arcade cleanup preserved
0x80360e00 -> 0x8035e4b4
bytes 2d 79 0d 0c
```

Loader:

```text
1,413 bytes
SHA-256
d2ae07431ce3c0e572bc4688bbe25ffacbddfcd349c9ca6e0fe0336b1549b3b0
```

External CPS1 core:

```text
FB Alpha 2012 CPS-1
SHA-256
b11ae69186fdef1e10bbd21e9a7dcee51782a41ad3de0b7ec2018fea18138c5e
```

Combined firmware:

```text
SHA-256
16233cbb0d7b7e5a90d72a0eed04b873a3754bcdbaaedcea64fc1b3b972e3f1f

LCFG CRC-32/MPEG-2
0xde6d5883
```

Package:

```text
xgo-core3-cps1-test05-correct-hook-v19-snes.zip
SHA-256
1e81bb6b1e85f99af45313fdf74c11223c4b5bef4a057c8be0acd8750125f5bb
```

Byte-level audit against Test 02:

```text
unexpected changed bytes = 0
```

## Test order

1. launch CPS2 or Neo Geo first; confirm stock gameplay and QUIT;
2. launch Street Fighter II from CPS1;
3. compare performance;
4. QUIT CPS1 through pause menu;
5. relaunch SFII;
6. verify Mapper;
7. verify external SNES still launches.

## Classification

**CORRECTED:** Test 03/04 did not establish external CPS1 gameplay.

**CONFIRMED:** all arcade families share the same stock FBA runtime/cleanup architecture.

**CONFIRMED:** 0x80360e00 is cleanup, not runtime entry.

**CONFIRMED:** 0x80360df8 calls the actual stock arcade runtime wrapper.

**CONFIRMED:** list ID byte 0x80c33980 preserves CPS1/CPS2/IGS/Neo Geo identity before family 0x40 collapses them.

**HARDWARE PENDING:** first true external CPS1 gameplay through the corrected Test 05 hook.
