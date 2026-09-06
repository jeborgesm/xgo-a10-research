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