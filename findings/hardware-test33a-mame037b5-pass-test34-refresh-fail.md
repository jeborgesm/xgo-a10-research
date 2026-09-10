# Hardware result — Test33A ROM compatibility resolved; Test34 Refresh failed

Date: 2026-09-09
Branch: research-game-list-arcade-expansion

## Test33A / MAME2000 ROM-set result

User replaced the previous Pac-Man and Ms. Pac-Man archives with files from the specific MAME2000-compatible set and also copied approximately 41 ROM ZIPs from that set into CLASSIC/bin.

Hardware result:
- Pac-Man now launches successfully from CLASSIC.
- Ms. Pac-Man now launches successfully from CLASSIC.
- Both have working sound.
- Controls/pause/OSD and the expected runtime features work.
- Cadillacs and Dinosaurs already worked from CLASSIC under the same Test33 execution path.

Conclusion:
The prior Pac-Man/Ms. Pac-Man freezes were ROM-set incompatibility, not a CLASSIC launch-contract defect.

For MAME2000, use the MAME 0.37b5 ROM set. Prefer non-merged archives for isolated testing so clone/parent dependencies cannot masquerade as loader failures.

## Test34 Refresh result — FAIL

User attempted Test34 after placing roughly 41 MAME 0.37b5 ZIPs under CLASSIC/bin.

Observed:
- CLASSIC display became transparent/stale and composited with previously visited system artwork (Neo Geo or Family Computer).
- Selecting Refresh Games caused the menu to become stuck; user could not exit normally.
- Volume OSD still functioned while stuck.
- After restart, no newly added CLASSIC ROMs appeared in the CLASSIC list.

Conclusion:
Test34 is rejected.

The attempted strategy—extending the Test08 six-pass console scanner loop and mapping a synthetic seventh iteration to list 11—was incorrect and disturbed state used by the game-list UI.

Further archaeology also clarifies why raw CLASSIC ROMs would not have appeared through the stock Test08 worker even without the hang:
- the Test08 Refresh feature discovers existing XGO wrapper files and stable-merges them into catalogs;
- it does not create wrappers from raw ROM ZIPs;
- CLASSIC stores raw MAME archives under /CLASSIC/bin/*.zip and therefore needs a CLASSIC-specific refresh/import worker.

Correct CLASSIC Refresh design:
1. Preserve the stock Test08 six-system refresh loop byte-for-byte.
2. After the stock loop completes, invoke a separate CLASSIC worker.
3. Scan /CLASSIC/bin for .zip archives.
4. Detect archives already referenced by existing CLASSIC .zfb wrappers to avoid duplicates.
5. For newly discovered archives, generate the minimal CLASSIC .zfb wrapper contract already hardware-proven by Test33.
6. Stable-append the new wrapper names to the CLASSIC clm.tax/clm.nec/clm.bvs catalog triplet.
7. Restore all state and return through the stock Refresh completion/status path.

Do not use Test34 as a base. Return to hardware-good Test33A (stretched artwork) for the next candidate.
