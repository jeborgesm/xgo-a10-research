# Hardware Test132 — GB materializer-only returns No New Games

Date: 2026-09-23
Status: HW FAIL / materializer input acceptance isolated

Test132 was Test128 materializer-only with only the corrected GB refresh pathname
HI16. The catalog call remained bypassed.

Hardware result:
- Refresh Games -> Game Boy: **No New Games**
- no /GB/Tetris.zgb generated
- /GB/import/Tetris.gb is confirmed present

This proves the misleading Test131 first-run Games Updated came from the catalog
side, not successful materialization.

It also isolates the remaining defect inside GB/refresh.xgc input discovery/
acceptance before wrapper generation. The generic runner and command-3 invocation
are now proven sufficiently functional to execute the helper and receive return 0.

Do not investigate catalog/frontend until materializer creates a .zgb.

Next offline gate: compare Test97 MD's exact accepted input filename(s) and helper
filename predicate with Tetris.gb, including case, directory-entry structure,
minimum-length checks, suffix offsets, and every branch from readdir through the
0x027C NOP to the accepted path. No firmware candidate until a concrete predicate
difference is identified.
