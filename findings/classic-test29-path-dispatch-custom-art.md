# Test29 — native CLASSIC path dispatch + dedicated platform artwork

Date: 2026-09-08
Branch: research-game-list-arcade-expansion

## Hardware input from Test28

Test28 result:
- CLASSIC page visible again;
- Pac-Man / Ms Pac-Man visible;
- selecting either game: Loading.... -> return to game list;
- CLASSIC page still displayed the stock CPS2 platform artwork.

This means the CLASSIC menu/category provisioning itself is now working. The launch failure occurs before the Test12 MAME runtime takes ownership.

## Root cause found for artwork

The stock firmware has a per-list platform-art pointer table beginning at runtime 0x80a3c428.

Recovered mapping includes:

list 7  -> CPS1 resource
list 8  -> CPS2 resource
list 9  -> IGS resource
list 10 -> Neo Geo resource
list 11 -> CPS2 resource fallback

The list11 entry is firmware offset 0x00a3c454 and originally points to runtime 0x809a32c8, string dsuei.cpl (the CPS2 640x480 RGB565 artwork).

Test29 patches only the list11 artwork entry to a new dedicated resource name stored in free low-memory string space:

Resources/clssic.r56

The real CPS2 resource and list8 pointer are untouched.

The resource is a native 640x480 RGB565 screen made from the user-selected CLASSIC/Pac-Man crop. The 385x465 source is aspect-preserved at 397x480 and centered with black side bars.

Artwork SHA-256:
00ecf4913ee58b46f642f05ea150ffa1d67cd5a36d6674f44aedc5dedffd6cd0

## Launch correction

Test28 gated the native launcher on ACTIVE_LIST_ID == 11.

Static analysis of the actual browser call sites shows a stronger discriminator is already passed in a0: the fully constructed selected wrapper path.

Test29 therefore removes ACTIVE_LIST_ID gating completely.

Launch rule:

- if selected wrapper path contains /CLASSIC/ -> native CLASSIC launcher;
- otherwise -> untouched stock run_game @ 0x80360b88.

For CLASSIC, the native launcher:
1. opens the selected CLASSIC .zfb directly;
2. seeks to the proven embedded ZIP-name offset 59,908;
3. reads the ZIP basename;
4. writes /mnt/sda1/CLASSIC to stock system-dir global 0x810a0eb0;
5. writes ZIP basename to stock game-name global 0x8109fce8;
6. loads the exact archived Test12 MAME2000 core;
7. performs the proven RAMSIZE / sound-task / IRQ-GP / cache handoff;
8. enters the Test12 frontend, which owns callbacks and stock run_emulator();
9. restores the previous path globals on return.

Stock Arcade configuration and runtime hook remain untouched.

## Exact candidate

xgo-classic-test29-path-launch-custom-art.zip
size              7,477,721 bytes
ZIP SHA-256        d96b4d7d06f46d56c6b7e06c45adcf32d09ae0b9681bfc17ce7b0910d66e7241
firmware SHA-256   48a9bf4e5a3efdd2317028a1c5bbc4332d9b7dc006a0860f1c8b26848bf5f5f8
launcher size      2,109 bytes
launcher SHA-256   850fa1f1303d990bd141c8144bcd149d6764d808834c3372d803d57fb36fcac4
art SHA-256        00ecf4913ee58b46f642f05ea150ffa1d67cd5a36d6674f44aedc5dedffd6cd0
Test12 core SHA    abf8e4ec6eb7c6d4c2162076e8faa868954a3663b8210c820e1267857b345461

ZIP integrity passed offline.

## Hardware gate

1. confirm CLASSIC remains visible;
2. confirm CLASSIC now uses the custom CLASSIC/Pac-Man artwork rather than CPS2 art;
3. verify stock CPS2 page still has its original art;
4. verify Cadillacs / stock CPS1 remains golden;
5. launch Pac-Man from CLASSIC;
6. if gameplay starts, verify controls/audio/pause/quit/OSD and then Ms Pac-Man.

