# Stock XGO 1941 runtime-data contract — BIN closure

Date: 2026-09-26
Branch: research-arcade-refresh-four-family
Status: BIN finding. No hardware candidate authorized.

Exact XGO bios/bisrv.asd contains a contiguous twelve-record descriptor table associated with the 1941 World driver. The record layout is directly recoverable as a 32-byte member name followed by little-endian size, checksum and type fields.

Key architectural finding: the stock XGO driver uses its own FBA-era member aliases rather than the newer external naming convention. The descriptor table therefore gives us an exact XGO-side compatibility oracle instead of relying on upstream assumptions.

This closes only the XGO-side runtime-data contract. The exact Test04 imported archive is not present in the current preserved analysis material, so compatibility of that archive remains OPEN. Do not promote compatibility to the cause of the launch failure.

Next offline work:
- recover the known-good Cadillacs descriptor contract from the same XGO BIN;
- compare wrapper/catalog/selected-list identity between Cadillacs and generated 1941;
- if the exact Test04 archive is recovered from preserved artifacts, compare its member identities, sizes and checksums against the XGO descriptor table;
- keep live-list/cache invalidation separate from launch correctness.

No Test05 is authorized.
