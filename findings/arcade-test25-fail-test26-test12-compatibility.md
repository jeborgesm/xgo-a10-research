# Arcade Test25 hardware fail and Test26 Test12-compatibility candidate

Date: 2026-09-08
Branch: `research-game-list-arcade-expansion`

## Test25 hardware result

Test25 true-family MAME2000 did not reach gameplay.

Observed Pac-Man behavior:

```text
select Pac-Man
 -> Loading.....
 -> black screen
```

This is a hardware FAIL.

The result closes the recent family-API-table direction for the immediate Classic Arcade implementation. It does not contradict the older XGO MAME2000 result because Test10-12 used a different, already hardware-proven loader/core ownership contract.

## Recovered authoritative historical MAME2000 result

Repository evidence from 2026-09-04 confirms:

- Test10 reached real MAME2000 SFII gameplay on physical XGO.
- Test11 repaired the XGO input contract; Cadillacs & Dinosaurs was playable.
- Test12 isolated MAME state and made SFII playable with working coin/start/gameplay controls.
- Test12 failed only on CPS1 performance/timing: the entire game ran in slow motion with choppy/out-of-sync audio.
- The external core used the pinned MAME2000/SF2000 lineage and the XGO custom frontend ABI `entry(filename, load_state)`.
- The hardware-working core is preserved exactly in the private vault:
  `xgo-core3-cps1-test12-clean-state-v19-snes.zip`.

Exact Test12 core:

```text
SHA-256
abf8e4ec6eb7c6d4c2162076e8faa868954a3663b8210c820e1267857b345461
```

Historical loader contract:

```text
hook 0x80360df8
 -> CPS1/list-7 discriminator
 -> historical XGOC loader
 -> /mnt/sda1/cores/fbalpha2012_cps1/core.xgc
 -> stop stock sound task
 -> RAMSIZE ceiling -> 0x87000000
 -> copy/CRC/BSS
 -> historical IRQ-GP repair
 -> cache flush
 -> entry(filename, load_state)
 -> Test12 XGO MAME frontend
 -> stock run_emulator()
 -> return into untouched stock arcade cleanup @ 0x80360e00
```

This path was hardware-proven. The recent Classic Arcade attempts repeatedly reimplemented parts of this contract instead of reusing it directly.

## Test26 architecture

Test26 changes direction: list 11 gets a compatibility shim around the proven Test12 path.

Golden firmware baseline remains exact Test08.

At the real arcade runtime call `0x80360df8`:

```text
lists 7-10
 -> shim sees not-list-11
 -> tail-jump untouched stock run_fba

list 11
 -> shim saves caller return state
 -> ACTIVE_LIST_ID 11 -> 7
 -> call relocated historical Test12-era CPS1 loader
 -> loader sees its original list-7 identity
 -> loader uses its original core pathname
 -> exact archived Test12 MAME2000 core executes
 -> loader returns
 -> shim restores ACTIVE_LIST_ID 7 -> 11
 -> return naturally into stock arcade cleanup
```

The historical loader source is recovered from commit:

```text
3470f0e320f47fb7deef5f64f7c0346b21adb4e8
```

Only its linker location changes:

```text
historical 0x80002780 -> Test26 0x80001980
```

This relocation is required because golden Audio OSD now owns the old 0x80002780 cave.

The compatibility shim occupies the start of the already-verified golden-zero cave:

```text
shim       0x80001900
loader     0x80001980
cave end   0x80002180
```

The loader's list guard, XGOC ABI, core pathname, sound-task sequencing, RAMSIZE handling, IRQ-GP repair, cache behavior and external entry ABI are otherwise kept historical.

## Exact Test26 candidate

```text
xgo-arcade-test26-test12-compat-shim.zip
size              7,400,813 bytes
ZIP SHA-256        15bb71a267181fa2260a6be03de3252d09ef9211d4bdf151f18d8740ca569a24
firmware SHA-256   3cd4b957fe558475a5a5519281b4bbcc96a7e5c06ac8fc607b2ee0e871b55934

compat shim
size               88 bytes
SHA-256             99eb1a504a09c995c97d6cb4c7f080ab8857aea224cd18a12d21dfb89b7cbc67

relocated historical loader
size               1,373 bytes
SHA-256             0231bd3f132bc79a885bd5090592f54984393dc08ca5b57cb4f7d38e5ecb0921

exact Test12 core
size               9,127,952 bytes
SHA-256             abf8e4ec6eb7c6d4c2162076e8faa868954a3663b8210c820e1267857b345461
```

Private CI:

```text
run       34283009246
artifact  10078376651
```

All immutable-input checks, loader/shim compilation, cave-size checks, no-`$gp` checks, firmware composition, ZIP integrity, artifact upload and private-vault archival passed.

## Hardware gate

This is intentionally one decisive candidate, not another diagnostic ladder.

Test order:

1. verify menu Volume OSD;
2. launch Cadillacs & Dinosaurs from stock Arcade and confirm stock audio/pause/quit;
3. launch Pac-Man from fifth Arcade;
4. if Pac-Man reaches gameplay, verify audio, controls, pause/quit, Volume OSD and speed;
5. test Ms. Pac-Man only after Pac-Man reaches gameplay.

If Test26 reaches MAME gameplay, the correct long-term Classic Arcade architecture is this first-class list-11 compatibility shim around the proven XGO Test12 MAME contract.

If Test26 still fails before gameplay, do not return to speculative loader variants. The next action must compare the relocated historical loader machine code/control flow against the exact Test12 loader binary and close the relocation-specific difference before another hardware candidate.
