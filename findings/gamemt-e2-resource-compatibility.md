# GameMT E2 ↔ SF2000 resource compatibility evidence

Date: 2026-09-07

## New evidence beyond visual similarity

The E2 relationship to SF2000 is now supported by **resource-level compatibility**, not only by owner descriptions of similar firmware.

### 4PDA / GB300-family discussion

In the GB300 technical thread, an owner reports that the compared clone behaves **identically to SF2000** at the emulator level except for a platform-set difference (PCE replacing arcade in that unit), and explicitly states:

> some graphics files are fully compatible with SF2000, including the menu music.

The same discussion recommends GameMT E2 as another device in this class and separately identifies E2 in the SF2000 thread as a Cube Technology/Biikoo product-family member.

Sources:
- https://4pda.to/forum/index.php?showtopic=1082011&st=20
- https://4pda.to/forum/index.php?showtopic=1067862&st=2600

## SF2000 theme community independently preserves an "E2-PB" UI target

Q-ta-s's mature SF2000 theme/tooling site contains explicit downloadable themes named:

- `E2-PB like style theme`
- `E2-PB like style Dark theme`

These are SF2000 resource replacements installed by overwriting `Resources/` after backing up `bios` and `Resources`.

This does not prove byte-identical E2 resource formats by itself—the theme is a recreation—but it demonstrates that the SF2000 modding community recognizes E2-PB as a closely related frontend/UI target and can reproduce its UI entirely within the SF2000 resource system.

Source:
https://q-ta-s.github.io/sf2000_theme.html

## Boot/runtime architecture clarification

The technical SF2000 documentation on 4PDA states:

- bootloader reads `bios/bisrv.asd` from the first FAT/exFAT partition;
- validates CRC32;
- executes it;
- stock firmware uses **ALi TDS2**;
- Shenzhen Biikoo developed the frontend;
- emulator payloads are modified libretro cores.

The same contributor identifies GAMEMT E2 among roughly a dozen related consoles and claims Cube Technology/Biikoo deliberately varies chip pin arrangements across models.

This is highly consistent with our A10 evidence: shared software architecture with board-specific adaptation rather than universally interchangeable images.

## Why the E2 image is now especially valuable

A recovered `Gamemt-e2.img` can answer whether E2 is:

A. merely visually inspired by SF2000;  
B. resource-compatible but rebuilt;  
C. binary-near-identical with model-specific GPIO/display adaptation; or  
D. an intermediate Biikoo frontend generation closer to XGO/DY19 than to stock SF2000.

Given the resource compatibility evidence and independent behavioral reports, C or D are now plausible enough to justify exact binary comparison.

## First extraction target

Do **not** begin by processing the 28.5GB ROM payload.

Extract only:
- partition table / filesystem metadata;
- `bios/`;
- `Resources/`;
- root configuration files;
- game-list/database metadata.

Then hash and compare those against XGO/SF2000/DY19/GB300.

## Relevance to XGO game-list scanning

E2 is particularly attractive for the next XGO priority because its UI is reported to have:
- faster/more direct game access;
- in-game button mapping;
- a newer-looking menu generation.

If E2 contains a later Biikoo game-list implementation, it may expose a cleaner scanner/database path than stock SF2000 and could help identify the code lineage behind XGO's own list handling.
