# Hardware result — Test47 generalized CLASSIC importer PASS

Date: 2026-09-09
Branch: research-game-list-arcade-expansion

Observed:
- Generalized scan/import succeeded on the user's CLASSIC MAME 0.37b5 library.
- Newly discovered ZIPs were imported into CLASSIC.
- The combined wrapper/catalog pipeline is therefore hardware-proven.

Remaining branch blocker:
- CLASSIC save/load states do not work.
- This predates Test47 and is independent of Refresh.

Repository evidence:
- working CLASSIC runtime inherits the exact Test12 MAME2000 core path;
- its frontend installs MAME state callbacks but the pinned core exposes nonfunctional/size-zero libretro serialization;
- newer MAME2000 lineage implements serialization using the internal MAME state registry.

Next:
Audit the pinned Test12 MAME2000 source for state_get_dump_size/state_save_* and CPU context helpers. If present, backport only the serializer functions and retain all working Test12 runtime behavior.
