# Game List Test02 — known-good duplicate control

Date: 2026-09-06
Branch: `research-game-list-scanning`

Status: **READY FOR HARDWARE TEST**

## Purpose

Test01 proved that an appended catalog entry appears and dispatches, but the physically present unindexed `Bomber Man 2.zfc` reaches only a black game screen.

Test02 isolates catalog/index/dispatch behavior from ROM compatibility by appending a second catalog reference to the already-stock-listed physical file:

`FC/Mega Man 1.zfc`

The preserved card inventory also contains four runtime save-state files for `Mega Man 1.zfc`, providing additional evidence that this wrapper has been exercised on-device.

## Exact lineage

Test02 builds directly from Test01's 745-entry synchronized FC triplet.

Expected tail:

`745  Bomber Man 2`
`746  Mega Man 1`

No ROM payload is added or modified.

## Test02 ZIP

`xgo-game-list-test02-megaman1-known-good-duplicate.zip`

SHA-256:

`40f6dce8380f61942f2f4f472b0c137fed8a6042cb00b0b3b669c99090d15a73`

## Output resource identities

`rdbui.tax` 745 -> 746, SHA-256 `263926964e4c5aa5508c7f44490f1e6ff397947c83f52c2c3c28069be71c1335`

`fhcfg.nec` 745 -> 746, SHA-256 `b9af569cb185187f506d51a2622caf9d41a5f9d9914effbd56451a0a3d8d2153`

`nethn.bvs` 745 -> 746, SHA-256 `0d0001520b645d795128d915a665c7e8c251ee29a57abc2f425043d824ed7ef1`

## Safety property

All original Test01 offsets and string bytes remain unchanged. The new entry is appended only.

The user's newly-created `Mega Man` Favorite is therefore a useful index-stability sentinel: it should continue to point to the original Mega Man list index even though another `Mega Man 1` reference now exists at entry 746.

## Hardware gate

1. Replace the three Test01 FC resource files with Test02.
2. Confirm tail entries 745 = Bomber Man 2 and 746 = Mega Man 1.
3. Launch entry 746.
4. Confirm normal Mega Man gameplay.
5. Open the existing Mega Man Favorite and confirm it still launches the same game.
6. Optionally Search for Mega Man and note duplicate-result behavior.

If entry 746 launches normally while the Favorite remains correct, stable append plus launch-index behavior is hardware-proven independently of Bomber Man 2 compatibility.

Do not promote Test02 to golden until hardware passes.