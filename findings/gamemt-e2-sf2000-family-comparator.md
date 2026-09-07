# GameMT E2 as an SF2000/H1512-family software comparator

Date: 2026-09-07

## Why E2 matters

GameMT E2 is a 2023 vertical game-console/power-bank product with a removable card, six face buttons, external/gamepad-oriented firmware features and a frontend that multiple independent community sources identify as an SF2000-family derivative.

It is not an XGO-branded product, but it is valuable because it appears to sit in the **same OEM software ecosystem** that supplied SF2000, X60, DY19 and ultimately the XGO A10 branch.

## Direct community behavioral evidence

A Japanese handheld-community owner who had both X60 and E2 reported that E2 was an **SF2000 variant**, could be modified in the same general way, and reproduced the characteristic SF2000/SFC behavior where SNES can launch extremely slowly until started a second time.

That behavioral fingerprint is especially relevant because the same underlying SNES/timing pathology has been central to XGO performance archaeology.

The same report describes:
- 3.5-inch vertical E2;
- six front buttons;
- analog-style directional control;
- SF2000-derived firmware behavior;
- button configuration;
- substantially shared modding concepts.

Source:
https://mevius.5ch.io/test/read.cgi/gsaloon/1582871341/504-n

## 4PDA attribution

Experienced SF2000 community contributors identify the device as **GAMEMT E2** and place it among a larger set of closely related consoles.

The same discussion attributes the firmware/frontend development lineage to **Cube Technology / Shenzhen Biikoo**, and notes that related models may deliberately vary SoC/package pin arrangements or board implementation enough to force model-specific work.

This is community attribution rather than manufacturer documentation, but it aligns with the already-preserved SF2000/X60 provenance investigation.

Source:
https://4pda.to/forum/index.php?showtopic=1067862&st=2600

## Recoverable stock image lead

A Chinese file-index page currently lists:

`Gamemt-e2.img 28.5GB`

This is strong evidence that a full E2 card image has circulated publicly. The file itself has **not** yet been retrieved or validated by this project.

Source:
https://www.xuebapan.com/info/52157fb9f60fb68dccd4c4f4bafce7cb.html

If recovered, the first extraction pass should compare:

1. `bios/bisrv.asd` presence and hash;
2. LCFG header/application size;
3. `Resources/` opaque filenames;
4. `Foldername.ini`;
5. Zxx packaged-ROM formats;
6. mapper resources and pause-menu states;
7. emulator/core strings;
8. H1512/SDK/compiler fingerprints;
9. game-list database record formats;
10. controller scanner signatures.

## Public catalog evidence

Handhelds Wiki describes E2 as:
- release 2023;
- 3.5-inch display;
- 6000mAh power-bank design;
- removable-card/Linux-class catalog category;
- firmware that "looks and feels like a re-skinned SF2000 firmware."

The Linux catalog label should not be taken literally for an H1512/SF2000 derivative; direct firmware evidence would control the OS classification.

Source:
https://www.handhelds.wiki/E2_Power_Bank_and_Game_Console

## Relationship to A10

E2 is currently best classified as a **software-family sibling**, not a direct Xinguo product ancestor.

Its value is that it demonstrates the SF2000 platform being repackaged into another power-bank handheld with:
- a different enclosure;
- six-button controls;
- a newer-looking mapper/UI layer;
- the same recognizable emulator behavior.

That makes E2 an unusually useful bridge between stock SF2000 and the more extensively customized XGO A10/DY19-style firmware branch.

## Next priority

Recover the 28.5-GB E2 image or a no-ROM/minimal backup. A single validated `bisrv.asd` from E2 would be more valuable than additional retail photographs because it could be compared directly against XGO at binary/function/resource level.
