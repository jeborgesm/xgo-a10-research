# Test97 — second Refresh after successful reboot

Hardware sequence:
1. repaired MD catalog state;
2. exact Test97 -> MD Games Updated;
3. immediate MD entry -> hard lock;
4. reboot -> MD opens, imported games and artwork are present;
5. Refresh run again:
   - FC -> No New Games
   - SFC -> No New Games
   - MD -> Refresh Failed

This is strong evidence that MD's second-run failure is persistent-state/idempotency related, not merely the immediate frontend hard-lock lifecycle. FC/SFC handle the no-change path; MD does not after its imported wrappers/catalog entries exist.

Keep two defects distinct:
A. successful MD update leaves resident frontend state unsafe until reboot;
B. subsequent MD Refresh on already-imported state returns Refresh Failed instead of No New Games.

Do not collapse B into the live-cache hypothesis. Investigate MD/refresh.xgc behavior when source .md + generated .zmd/catalog entry already coexist, and compare against FC/SFC materializers' idempotent existing-output path.
