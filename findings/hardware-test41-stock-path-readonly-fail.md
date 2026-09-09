# Hardware result — Test41 stock-path read-only probe FAIL

Date: 2026-09-09
Branch: research-game-list-arcade-expansion

Observed:
- Test41 returned Refresh Failed.
- Test41 performed no catalog mutation.
- It attempted to resolve/read "clm.tax" using the stock Test04 ROOT/PATHFMT/PATHBUF/sprintf contract.

Important correction:
This does NOT by itself prove the CLASSIC catalog filename is wrong. The package resources are named clm.tax/clm.nec/clm.bvs, but the stock Test04 PATHFMT may target a different directory/namespace than the package's Resources directory. Test04's contract was proven for the stock SFC resource names in its own runtime context, not automatically for our new CLASSIC files.

Therefore the next step must inspect the actual PATHFMT/ROOT strings and the known-good Test08 runtime path construction, then compare that with where clm.tax physically resides. Do not mutate catalogs again until this namespace mismatch is closed.
