# CPS1 known-good comparator — Cadillacs versus 1941 BIN contract

Date: 2026-09-26
Branch: research-arcade-refresh-four-family
Status: BIN comparison. No hardware candidate authorized.

The exact XGO bios/bisrv.asd contains contiguous ROM descriptor tables for both the known-good Cadillacs & Dinosaurs driver family and 1941.

Cadillacs uses the same stock-FBA descriptor architecture and the same FBA-era archive-member alias convention observed for 1941. Examples include cde_23a.rom / cde_22a.rom / cde_21a.rom plus cd_gfx*.rom, cd_q.rom and cd_q1..q4.rom.

This matters because the 1941 table is not an anomalous or synthetic format. Its .rom / gfx-alias naming is normal stock-XGO FBA behavior shared by a current HW-working CPS1 comparator.

Existing repository findings already establish that Arcade launch identity is distributed across:
- active list/system route;
- catalog physical wrapper filename;
- wrapper trailer archive basename;
- stock run_game preprocessing, which constructs the /bin/<archive> path.

For the current comparison:
- known-good Cadillacs wrapper resolves to dino.zip;
- generated Test04 wrapper resolves to 1941.zip;
- both enter the stock CPS1/FBA family path when selected from the CPS1 list.

No additional per-entry title/system field has yet been demonstrated that would explain the launch divergence.

OPEN:
- exact Test04 1941.zip member names/sizes/checksums;
- any index-dependent state not covered by the known catalog/wrapper contract;
- live-list/cache invalidation after catalog mutation;
- exact first runtime divergence after stock preprocessing.

The strongest next offline discriminator is therefore the exact Test04 archive content, if recoverable from preserved artifacts. Do not infer incompatibility merely from the archive basename.

No Test05 authorized.
