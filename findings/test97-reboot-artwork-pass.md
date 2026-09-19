# Test97 — MD artwork and launch state after reboot

Hardware observation after clean Test97 reproduction and reboot:

1. Known-good MD catalog triplet restored after SD-card corruption was discovered.
2. Exact Test97 Refresh -> **Games Updated**.
3. Entering Mega Drive immediately after Refresh -> **hard lock**.
4. Device rebooted.
5. Entering Mega Drive after reboot -> **new imported games visible WITH their images**.

This materially revises the earlier interpretation of Test97.

## Hardware-proven conclusions

- Test97 MD import/materialization works.
- Test97 MD artwork lookup/conversion/wrapper preview works.
- The inherited stem helper does **not** need the speculative -5 -> -4 modification for the current .md workflow; Tests100–102 were unnecessary/confounded experiments.
- Generated MD catalog state is usable after reboot.
- The remaining reproducible defect is specifically the **live post-refresh frontend state**: entering MD before reboot hard-locks, while reboot reloads a working catalog/list with artwork.

## Investigation priority

Freeze extension/stem work. Do not alter the Test97 MD materializer.

Investigate only the post-import runtime refresh boundary:
- MD catalog helper's cache invalidation at 0x80D2895C;
- additional frontend list pointers/counts/state retained across Refresh;
- differences between FC/SFC successful live behavior and MD;
- whether selector must force a list reload/re-entry transition after MD/catalog.xgc completes.

Treat reboot as evidence that persistent catalog/wrapper data is valid and runtime state is stale/inconsistent.
