# Arcade Test15 — CLASSIC-style publication HW result

Date: 2026-09-29

## Hardware result

User restored the IGS resource triplet to a clean pre-test state and removed the prior generated `The Gladiator.zfb`, then ran Test15.

Observed:
- Refresh reported **Games Added** and then hard-locked.
- After reboot, the IGS list contained the prior two bad historical entries plus a newly added **The Gladiator** entry.
- The new entry displays the generated artwork correctly.
- Launch begins normally and visibly parses the ROM files.
- Game music starts while the XGO remains on the Loading screen.
- Device then hard-locks on Loading.

## What Test15 proves

The CLASSIC-style identity correction is substantially correct:
- metadata-derived friendly title reaches the frontend as `The Gladiator` (no leaked `.zfb`);
- the correct enriched wrapper is found and its preview is rendered;
- the wrapper reaches the intended runtime ZIP strongly enough for the IGS loader to open/parse ROM members and begin audio execution.

Therefore the earlier catalog/wrapper identity failure is closed for the newly generated entry.

## Remaining failures

Two independent post-publication/runtime boundaries remain:

1. Refresh return/cleanup: publication completes but Refresh hard-locks after reporting Games Added.
2. IGS launch return/runtime: loader parses ROMs and game audio starts, but frontend remains on Loading and device hard-locks.

The old `theglad` and `The Gladiator.zfb` entries are historical Test13/Test14 catalog pollution, not evidence that Test15 generated duplicates.

Do not regress the Test15 friendly-title/artwork publication fix while investigating these boundaries.


## Investigation direction after Test15

Do not use CLASSIC as the next runtime/Refresh debugging ancestor. CLASSIC was useful to recover the friendly outer-wrapper/artwork publication contract, and that Test15 behavior is now protected.

The next comparison is **CPS1 vs CPS2 vs IGS directly** because CPS1 and CPS2 are HW-proven through Refresh, artwork, catalog publication, ROM parsing and gameplay, while IGS now reaches artwork/publication and begins ROM/audio execution but locks during Refresh return and launch transition.

Required method:
- preserve Test15 metadata/JPEG/RGB565/wrapper/catalog identity behavior byte-for-byte where possible;
- mechanically diff CPS1/CPS2/IGS helper binaries and family descriptors;
- classify every remaining executable delta as required family identity/path geometry vs unexplained specialization;
- compare list 7/8/9 stock launch routing, core/loader selection, pre/post launch callbacks, status/cleanup/return behavior, and any family-dependent globals;
- use CPS1/CPS2 as the immediate working controls;
- do not regress image acquisition/publication while fixing IGS runtime/return behavior.
