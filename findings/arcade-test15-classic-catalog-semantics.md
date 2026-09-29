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


## Direct CPS1/CPS2/IGS comparison — concrete list-ID defect found

Mechanical Test15 helper comparison shows CPS1 vs CPS2 differs only in family pathname literals and the dynamic validator family selector. After the already-corrected IGS import-prefix length, CPS1 vs IGS likewise has no unexplained executable delta in the materializer: remaining differences are path bytes plus family selector. This supports protecting the Test15 image/materializer path rather than changing it again.

A separate direct comparison against the repository's established stock Arcade map exposed a real four-family descriptor defect:

- stock list 7 = CPS1 = mswb7/msdtc/mfpmp
- stock list 8 = CPS2 = kjbyr/djoin/ke89a
- stock list 9 = **NeoGeo** = rmapi/pcadm/ntdll
- stock list 10 = **IGS/PGM** = subst/aepic/sensc

The current Arcade descriptor source had IGS labeled list 9 with cache 0x80D28970 and NeoGeo list 10 with cache 0x80D28974 — reversed relative to the proven stock map. Resource filenames themselves were correct, which is why the IGS game appears on the correct physical page, but any list-index/count-cache behavior derived from those descriptor IDs is wrong. This is a strong candidate for the post-Refresh hard lock after successful publication.

Source corrected in commit 73117a3282f67cefb8c97c62f590677494ce7f54. Do not change the Test15 JPEG/RGB565/wrapper/title acquisition path.

The launch lock is not yet attributed to this descriptor defect: the stock IGS resource triplet routes through list 10, and Test15 reaches ROM parsing plus game audio. That may be a separate `theglad` runtime/core compatibility boundary. First fix/audit list-ID-derived Refresh cleanup; then discriminate generated-wrapper launch from title-specific runtime behavior using a stock-known IGS driver if necessary.
