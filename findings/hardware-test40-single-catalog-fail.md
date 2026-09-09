# Hardware result — Test40 single CLASSIC catalog diagnostic FAIL

Date: 2026-09-09
Branch: research-game-list-arcade-expansion

Observed:
- Test39 wrapper-only path: PASS ("Games Updated").
- Test40, which retains the proven execution/wrapper state but calls patchcat() only for Resources/clm.tax: "Refresh Failed".

Conclusion:
Failure is isolated to patchcat()/catalog access or rewrite. It is not caused by:
- firmware-resident execution at 0x80A38000;
- finding galaga.zip;
- reading Pac-Man.zfb;
- creating/writing Galaga.zfb;
- fs sync;
- multiple-catalog sequencing.

Next action:
Do not perform another mutating catalog test yet. Recover the exact stock Test08 catalog writer contract and compare its file paths, fopen/fseek/ftell/fread/fwrite behavior and binary serialization with Test40. Then build a read-only catalog probe before another rewrite.
