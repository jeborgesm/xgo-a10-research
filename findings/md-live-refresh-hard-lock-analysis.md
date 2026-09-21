# MD live Refresh hard-lock analysis

Hardware discriminator:
- exact Test97 on repaired/pre-Test97 catalog state -> Games Updated;
- entering MD immediately -> hard lock;
- reboot -> MD opens, imported games are present with artwork (and prior testing proved launch/play).

Offline comparison of FC/SFC/MD catalog.xgc:
- all three are exactly 2642 bytes;
- code is structurally identical;
- only meaningful code differences are extension characters and cache slot;
- cache invalidation instruction sequence is identical:
  - FC -> 0x80D2894C
  - SFC -> 0x80D28954
  - MD -> 0x80D2895C
- remaining differences are the expected catalog triplet paths and root folder.

Thus MD/catalog.xgc is not missing a special write/close/invalidation operation relative to FC/SFC. It performs the same algorithm and explicitly clears 0x80D2895C after successful writes.

This shifts the fault boundary out of the catalog helper itself and into the resident frontend state. The on-disk MD catalog is valid (reboot consumes it correctly), but the running frontend retains state that is not fully reconstructed by clearing the count slot alone.

Likely classes of stale resident state to prove next: decoded catalog/list buffer pointer, per-page item table, selection/page bounds, allocation ownership, or a second cache adjacent to the count table. Do not patch these speculatively.

Important: the earlier SD corruption plausibly came from repeated hard locks/nonbootable experiments, but that causality is not proven. Preserve as hypothesis only.
