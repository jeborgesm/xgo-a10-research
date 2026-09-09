# Hardware result — Test42 corrected-root probe FAIL + packaging/core audit

Date: 2026-09-09
Branch: research-game-list-arcade-expansion

Hardware:
- Test42 still reports Refresh Failed.
- User inspected SD/package and questioned cores/fbalpha2012_cps1/core.xgc vs mame2000 folders.

Repository-authoritative audit:
1. CLASSIC launch path is intentionally based on the exact hardware-working Test12 loader. Test33 relocates Test12 bytes and changes only its list gate from 7 to 11.
2. That exact Test12 loader contains the literal core pathname:
   /mnt/sda1/cores/fbalpha2012_cps1/core.xgc
3. Test33 verifies core.xgc SHA-256 abf8e4ec6eb7c6d4c2162076e8faa868954a3663b8210c820e1267857b345461 from xgo-core3-cps1-test12-clean-state-v19-snes.zip.
4. Hardware later proved Cadillac launches from CLASSIC through this exact contract. Therefore fbalpha2012_cps1 is NOT a random accidental core path; despite the directory name, it is the proven launch-core location inherited from Test12.
5. /cores/classic/loader.bin and refresh.bin belong to the separate CLASSIC Refresh mechanism (Test35 lineage), not game emulation.
6. Existing /cores/mame2000 and /bios/mame2000* directories are remnants/inputs from earlier MAME2000 experiments and are not what the proven Test33 CLASSIC loader invokes.

Critical Test42 finding:
The package includes clm.tax/clm.nec/clm.bvs under ZIP Resources, but the user's SD screenshot does not show Resources because that directory was not expanded. Test42's read-only open still failed even with literal /mnt/sda1 + confirmed %s/Resources/%s. Before any Test43 firmware change, inspect package resource files and catalog format and verify whether the updater/install process actually places Resources/clm.tax on SD, versus these resources being consumed into another storage location at boot/update.

Do not switch CLASSIC to /cores/mame2000 merely because of naming. That would discard the hardware-proven Test33/Cadillac contract.
