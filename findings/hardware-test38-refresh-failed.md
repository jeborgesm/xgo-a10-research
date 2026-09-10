# Hardware result — Test38 one-ROM importer reached Refresh Failed

Date: 2026-09-09
Branch: research-game-list-arcade-expansion

Observed on hardware:
- Test38 does not freeze.
- Refresh returns through the frontend's Refresh Failed condition.

Interpretation:
This is materially different from Test35. The hardware-proven 0x80A38000 execution path remains healthy; the importer returned its explicit error path during filesystem/wrapper/catalog work.

Because Test38 can write Galaga.zfb and then update the three catalogs sequentially, its failure may have occurred after a partial write. The next package must reinstall the known-good Test37/Test33A CLASSIC catalogs before testing and isolate wrapper creation from catalog mutation.

Next diagnostic: Test39 wrapper-only import. It will create /CLASSIC/Galaga.zfb from /CLASSIC/Pac-Man.zfb + galaga.zip reference, but will not modify clm.tax/clm.nec/clm.bvs. This identifies whether the failure is in wrapper I/O or catalog rewrite without another multi-stage mutation.
