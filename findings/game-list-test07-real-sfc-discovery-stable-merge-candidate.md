# Game-List Test07 — real SFC discovery + stable-merge candidate

Date: 2026-09-07
Branch: `research-game-list-general-scanner`

Status: **offline-composed hardware candidate; NOT golden pending hardware test**

## Protected parent

Test07 is derived directly from the hardware-confirmed golden Test06b ZIP, not reconstructed from older component artifacts.

```text
game-list-test06b-explicit-refresh-timed-status
xgo-game-list-test06b-timed-status.zip
ZIP SHA-256      2d859b3ca3f0644a461c197fcfe0b58f2650c26bc6a7c8d28a189da196aa1042
firmware SHA-256 5d15cbe1cef380b3517cbd64727526e1b837df5160ba5275ccde6fec01324f4e
```

All Test06b User Menu/UI/status resources are carried forward. Only the firmware cave writer/status implementation is replaced, and `Resources/refresh.bin` is deliberately removed from the output package.

## What Test07 proves

This is the first candidate in which pressing **Refresh** performs actual filesystem discovery rather than copying a staged catalog payload.

Runtime path:

```text
Refresh command
  -> read current SFC slot-0/slot-1/slot-2 catalogs
  -> verify synchronized counts
  -> open real /SFC directory through stock directory wrappers
  -> skip directories
  -> classify extensions through stock 0x80360a08 classifier
  -> compare exact filenames against existing slot 0
  -> collect only missing physical filenames
  -> build all three complete stable-append outputs in RAM
  -> append full filename to slot 0
  -> append basename fallback to slots 1 and 2
  -> rewrite synchronized triplet
  -> fs_sync
  -> invalidate only cached SFC count
  -> return to golden Test06b User Menu/status path
```

Existing entries are never reordered or deleted, so all previous indices remain unchanged.

The classifier global system-mask side effect is saved before scanning and restored before returning to the frontend.

## Candidate

```text
xgo-game-list-test07-general-sfc-scanner.zip
size              4,995,560 bytes
ZIP SHA-256        0b07d1b4cd83b4a54b80740d646f85e72e3994598c19c089941b76ad56268719
firmware SHA-256   238331cf5cf56f9fb31891e197c12bfaa86a280a65dbeacc83e1b34d99c858c1
scanner/status     3,009 bytes
scanner SHA-256    9ef681888972c01bca94b50c0ea1a51df0f4246d9889ac007aa9907c3b1fe0c8
builder SHA-256    534882b371ef79fcf9592199a4ce459095c25c8197957abe08e27f2099343bf6
```

Offline audit passed:
- exact golden Test06b parent ZIP verified;
- exact golden Test06b firmware verified;
- exact Test06b 1,370-byte writer/status cave prefix verified before replacement;
- original 929-entry SFC triplet hashes/sizes verified;
- `SFC/XGO Import Test.zsf` exact wrapper hash verified;
- scanner blob fits the proven cave;
- output ZIP integrity passes;
- `SFC/XGO Import Test.zsf` is present;
- `Resources/refresh.bin` is absent;
- independent local rebuild reproduced the exact same scanner, firmware, size, and ZIP hashes.

Builder:

`tools/game_lists/build_test07_general_sfc_scanner.py`

Builder commit:

`d2ca23b21e3b909af48646c9bc7242f74f212b7c`

## Hardware gate — disposable clone only

Test07 is deliberately still non-transactional. Do not test it on the canonical card and do not interrupt power during Refresh.

Expected initial state:
- SFC catalog count = 929;
- `SFC/XGO Import Test.zsf` physically present;
- XGO Import Test absent from the SFC catalog;
- no `Resources/refresh.bin` exists in the candidate package.

First Refresh:
1. select User Menu -> Refresh;
2. expect `Games Updated`;
3. status should disappear after about three seconds;
4. SFC count should become 930;
5. `XGO Import Test` should appear as the appended final entry;
6. launch it and verify the known controller-test wrapper behaves normally.

Second Refresh:
1. select Refresh again;
2. expect `No New Games`;
3. no catalog rewrite should occur;
4. status should again expire normally.

Regression gate:
- reboot and confirm 930 persists;
- existing Favorite/save remains valid;
- Search remains aligned;
- Chinese-mode SFC list/search access does not crash or mis-index;
- User Games, Language, and TV System remain normal;
- footer/selector/NTSC-PAL layout remains the golden Test06b behavior;
- Audio OSD, native SNES, and CPS1 scheduler behavior remain unchanged.

## Safety boundary

The three complete new catalogs are constructed in RAM before canonical writes begin, but canonical replacement is still an in-place three-file sequence. A power loss or failed write can therefore leave the triplet inconsistent.

Transaction marker + backup/recovery is the next safety layer after real discovery/stable-merge receives hardware confirmation. Test07 must not be promoted to `golden/` before hardware PASS.
