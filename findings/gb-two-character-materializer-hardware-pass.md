# GB two-character materializer — HW pass with metadata title override

Date: 2026-09-23
Branch: `research-refresh-gb-gbc-gba`
Status: HW PASS — materializer contract

## Hardware result

Combined two-byte GB helper repair:
- +0x009C 05 -> 06: two-character .gb extension geometry
- +0x0DF8 FB -> FC: two-character stem length

Hardware:
- Refresh Games -> Game Boy: Games Updated
- wrapper created successfully
- generated wrapper: `/GB/Tetris.zgb`
- user confirms the generated name is taken from the metadata text file

This resolves the apparent discrepancy between the raw ROM basename and generated wrapper name. The previous malformed wrapper was a real stem defect; after the -5 -> -4 correction, metadata lookup succeeds and the materializer follows its intended title override/sanitization path.

## Proven boundary

GB materializer now has hardware proof for:
- /GB/import discovery
- ordinary two-character .gb suffix acceptance
- correct source stem derivation
- metadata lookup
- metadata-derived output title
- .zgb wrapper generation
- successful changed return reflected as Games Updated

No bios/bisrv.asd modification was involved.

## Remaining boundary

Visible GB catalog/list propagation remains to be verified independently. Do not modify the now-proven materializer while investigating list propagation.

If the generated `Tetris.zgb` is not visible in the GB frontend, the next task is catalog/scanner invocation and GB list-ID/cache invalidation only.
