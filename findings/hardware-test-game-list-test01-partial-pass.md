# Hardware test — Game List Test01 partial pass

Date: 2026-09-06
Branch: `research-game-list-scanning`

Artifact:

`xgo-game-list-test01-bomberman2-static-triplet.zip`

ZIP SHA-256:

`45182596fd1f0598f356901b06ffc3cca94dcfcb445ac8e3b272702c6f9a3350`

## Hardware observation

The FC list increased from 744 to 745 entries.

Entry 745 displayed as:

`Bomber Man 2`

Selecting the new entry reached the game-launch path. The display flashed briefly and then remained black.

The stock in-game pause menu remained functional, and the user could quit back out normally.

Therefore:

- catalog append/display: PASS;
- list count/index handling: PASS;
- stock game selection/dispatch reached: PASS;
- pause/quit runtime remained functional: PASS;
- actual Bomber Man 2 gameplay: FAIL / black screen.

## Interpretation

This is not evidence that stable catalog append failed. The new entry is visible, selectable, and reaches the emulator/runtime path.

The black screen is now a ROM-wrapper/payload compatibility question for the physically present but previously unindexed `FC/Bomber Man 2.zfc` file.

The fact that the pause menu works after selection strongly suggests the frontend entered the normal game runtime rather than crashing the browser.

## Additional test-state note

The user had no prior Favorites entry in this FC list during Test01, so Favorites index-preservation was not independently verified in this run.

The user has now added `Mega Man` as a Favorite specifically to provide a stable reference for future list-mutation tests.

## Card inventory context

Captured card inventory records:

`FC/Bomber Man 2.zfc` size 127,333 bytes

for comparison:

`FC/Contra 1.zfc` size 149,936 bytes
`FC/Mega Man 1.zfc` size 139,029 bytes
`FC/Commando.zfc` size 119,872 bytes
`FC/Star Soldier.zfc` size 92,232 bytes

The size alone does not identify the failure mode.

## Classification

Game-list architecture milestone: **hardware-confirmed partial pass**.

Do not promote Test01 to golden because the selected game does not reach playable output.

Next step: choose a better control that isolates list expansion from ROM compatibility, while preserving the new `Mega Man` Favorite as an index-stability sentinel.
## Test02 follow-up control — HARDWARE PASS

Artifact: `xgo-game-list-test02-megaman1-known-good-duplicate.zip`

ZIP SHA-256: `40f6dce8380f61942f2f4f472b0c137fed8a6042cb00b0b3b669c99090d15a73`

Test02 appended a second catalog reference to the already-stock-listed physical `FC/Mega Man 1.zfc` as new final FC entry 746, while preserving all existing indices.

Hardware-confirmed observations:

- entry 746 displayed as Mega Man at the end of the FC list;
- launching from the new appended index loaded the existing Mega Man game normally;
- previous Mega Man save data was visible from the appended entry;
- button remapping worked normally from the appended entry;
- Audio OSD/volume adjustment worked normally in the launched game;
- gameplay was normal.

### Conclusion

**HARDWARE CONFIRMED:** a stable-appended built-in catalog entry is treated as a normal first-class game entry by the XGO runtime.

The launch/save/remap/audio behavior proves the catalog index is only a frontend reference into the same physical ROM identity/runtime state; adding a new catalog index does not create a separate save/remap identity.

This cleanly isolates the Test01 Bomber Man 2 black screen as a compatibility/payload issue for that wrapper, not a failure of the catalog append architecture.

The user also created a Mega Man Favorite before Test02 for future index-stability tests. Explicit Favorite-launch verification remains to be recorded separately if needed.