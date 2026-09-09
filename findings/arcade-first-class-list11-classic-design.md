# First-class Classic Arcade list-11 design

Date: 2026-09-08
Branch: `research-game-list-arcade-expansion`

## Objective

Convert dormant fifth Arcade page / list ID 11 into a genuine stock-style game category before relying on external MAME2000.

The page gets its own visible identity and filesystem tree:

```text
CLASSIC/
  Pac-Man.zfb
  Ms Pac-Man.zfb
  bin/
    pacman.zip
    mspacman.zip
```

## Why this is structurally different from Tests 15-26

Stock firmware has fixed synchronized metadata triplets for lists 0-10.

List 11 instead points to:

```text
0x80a3c3b0 -> None
0x80a3c3b4 -> None
0x80a3c3b8 -> None
```

Earlier Classic Arcade candidates created `Resources/None`, which was enough to render rows, but they continued to launch from a dormant list identity.

The first-class design patches the list-11 metadata table itself to three real resource names:

```text
clm.tax
clm.nec
clm.bvs
```

All three use the normal stock count + uint32 offsets + NUL strings format and remain position-aligned.

## Separate folder is safe and desirable

`Foldername.ini` is the stock source for per-list directory names. The fifth visible entry can therefore be changed from the repeated `ARCADE` directory to `CLASSIC` without inventing a new filesystem mechanism.

This keeps stock Arcade content isolated from future Classic Arcade imports/scanning.

## Launch lifecycle

The critical change is moving compatibility to before stock `run_game()`.

Direct browser/favorites launch calls that normally target:

```text
run_game @ 0x80360b88
```

are wrapped by a list-aware bridge.

For lists other than 11:

```text
bridge -> tail-jump stock run_game
```

For list 11:

```text
save caller return
set private CLASSIC launch flag
ACTIVE_LIST_ID 11 -> 7
call stock run_game with original wrapper-path arguments
  -> full CPS1 extension classification
  -> full stock arcade preprocessing
  -> current directory/archive globals populated by stock lifecycle
  -> family 0x40 path
  -> runtime dispatcher
restore ACTIVE_LIST_ID 7 -> 11
clear private flag
return to browser
```

The final arcade runtime call is also wrapped:

```text
private flag == 0 -> untouched stock run_fba
private flag == 1 -> relocated historical Test12 MAME loader
```

This preserves golden stock CPS1 on real list 7 while giving list 11 the complete list-7 preprocessing contract.

## Historical MAME contract remains exact

The MAME side still uses the archived Test12 core:

```text
SHA-256
abf8e4ec6eb7c6d4c2162076e8faa868954a3663b8210c820e1267857b345461
```

The historical loader source comes from commit:

```text
3470f0e320f47fb7deef5f64f7c0346b21adb4e8
```

Its only required change is relocation from the old Audio-OSD-owned cave to the verified golden zero cave.

## Golden protection

The intended invariants are:

- list 7 real CPS1 -> golden stock FBA;
- list 8 -> golden stock CPS2;
- list 9 -> golden stock PGM/IGS;
- list 10 -> golden stock Neo Geo;
- list 11 -> first-class CLASSIC page -> Test12 MAME2000;
- mapper v19 unchanged;
- native SNES unchanged;
- game-list Refresh unchanged;
- Audio OSD unchanged.

No new hardware candidate should be accepted unless offline assertions verify the list-11 metadata pointers, both run-game call hooks, runtime dispatcher, cave boundaries, exact Test12 core hash and ZIP integrity.
