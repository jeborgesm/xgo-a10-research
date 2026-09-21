# MD.zip forensic review — clean Test97 output

User supplied the complete MD directory produced by the latest clean Test97 run.

## Proven contents
Generated wrappers are:
- NBA Jam Tournament Edition.zmd (3,205,804 bytes)
- Ninja Gaiden.zmd (1,108,640 bytes)
- Streets of Rage.zmd (584,342 bytes)
- Super Street Fighter II - The New Challengers.zmd (5,302,990 bytes)

All four retain the 59,904-byte RGB565 preview followed by WQW payload. The Super Street Fighter II wrapper preview SHA-256 exactly matches art/.xgo.rgb565, proving the generated preview was consumed by the wrapper path.

refresh.xgc SHA-256 is c0af2dea8291f86b411e819356e7b6b877ca69e39a444f0780348906f610e087: exact Test97.

The wrapper basenames exactly match the friendly titles in the four meta/*.txt files, not the raw ROM stems. This proves metadata lookup succeeded in the clean Test97 run. Artwork also succeeded for all observed frontend entries.

## Important correction
The previous claim that the inherited DCC stem arithmetic necessarily causes Test97 metadata/art lookup failure is contradicted by the produced artifacts. Whatever the static interpretation of that helper, hardware output proves Test97 resolved the supplied metadata and artwork correctly. Do not use the stem theory to justify another patch without reconciling it with these artifacts.

## Second-run implication
The generated .zmd filenames are normal and exactly the expected friendly names. There is no malformed one-character-short or extension-corrupted wrapper basename to explain the second Refresh failure.

The directory still contains all four source .md files and all four generated .zmd files. Therefore this supplied directory is the exact persistent state in which the rebooted second MD Refresh returns Refresh Failed.

Next target: trace the existing-output check using the friendly metadata-derived output name and determine whether it actually checks /MD/<friendly>.zmd, or whether the no-change path depends on a different pre-metadata/raw-stem name. Do not alter the card.
