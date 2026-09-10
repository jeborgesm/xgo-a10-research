# Hardware result — Test36 raw ZIP direct launch fails

Date: 2026-09-09
Branch: research-game-list-arcade-expansion

Test36 deliberately kept the hardware-good Test33A firmware/core/artwork unchanged and changed only CLASSIC browsing from outer .zfb wrappers to raw ZIP entries rooted at /CLASSIC/bin.

Hardware result:
- selecting a CLASSIC raw ZIP transitions to black;
- device then freezes and does not recover.

Conclusion:
Raw ZIP entries cannot replace the arcade-style .zfb frontend contract on this XGO build. The outer .zfb is not merely optional artwork metadata: it is required by the frontend launch path that reaches the hardware-proven Test33 MAME loader.

Retain the proven CLASSIC layout:
- /CLASSIC/*.zfb = 59,904-byte 144x208 RGB565 thumbnail + 4 zero bytes + ZIP basename + NUL trailer
- /CLASSIC/bin/*.zip = actual MAME ROM archive
- CLASSIC catalogs reference the outer .zfb filename

Test36 is rejected. Do not pursue direct raw-ZIP catalog entries.

Refresh implication:
A correct CLASSIC importer must create/maintain .zfb reference wrappers and catalogs. Future artwork can be sourced from an optional /CLASSIC/img directory, but the runtime browser should continue consuming .zfb wrappers rather than being modified to render external images.
