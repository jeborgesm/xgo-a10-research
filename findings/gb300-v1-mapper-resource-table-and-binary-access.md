# GB300 v1 mapper resource table and local binary access

Status: **DIRECT GB300 BINARY EVIDENCE; MAPPER HANDLER LIFT IN PROGRESS**

## Firmware pinned and locally analyzable

The public GB300 v1 firmware executable is now preserved in the mapper-lift GitHub Actions artifact and was downloaded for local binary analysis.

- file: `bios/bisrv.asd`
- size: `7,299,832` bytes
- SHA-256: `4084798a21d4abd93893f03f8fc4e1e4a8c9e31d4c60857328a9cab0cf892627`
- workflow run: `33773074262`
- artifact ID: `9900442996`
- artifact digest: `sha256:d1c9e4e29f1921f741b7eb64981f8f6c111572e3176d27a09caca5eabccd34b3`

This removes the previous tooling limitation where the GitHub text connector could expose firmware metadata but not the non-UTF8 binary itself.

## Mapper strings in GB300 v1

Direct firmware offsets:

```text
gpapi.bvs                   0x00666c84 -> 0x80666c84
hctml.ers                   0x00666a98 -> 0x80666a98
ztrba.nec                   0x00666ab0 -> 0x80666ab0
lk7tc.bvs                   0x00666abc -> 0x80666abc
mczwq.ikb                   0x00666ac8 -> 0x80666ac8
%s/Resources/KeyMapInfo.kmp 0x00666e58 -> 0x80666e58
KeyMapInfo.kmp              0x00666e65 -> 0x80666e65
```

## Mapper/resource pointer table

The firmware contains a dense pointer table beginning in the `0x806cecxx` runtime region. The mapper assets occupy consecutive entries:

```text
0x806cec90 -> hctml.ers
0x806cec94 -> kmbcj.acp
0x806cec98 -> ztrba.nec
0x806cec9c -> lk7tc.bvs
0x806ceca0 -> mczwq.ikb
```

This is stronger than loose resource-name coexistence: the native firmware groups the mapper assets together in its resource dispatch table.

## Pause-menu resource table continuity

A second contiguous part of the same resource table contains:

```text
0x806ced80 -> dism.cef
0x806ced84 -> d2d1.hgp
0x806ced88 -> bisrv.nec
0x806ced8c -> pwsso.occ
0x806ced90 -> gpapi.bvs
0x806ced94 -> fhshl.skb
```

The critical observation is that `gpapi.bvs` again occupies the fifth position (zero-based index 4) after the same four menu resources already recovered on XGO.

Therefore the XGO hardware result and GB300 v1 binary layout converge directly:

```text
index 0 -> dism.cef
index 1 -> d2d1.hgp
index 2 -> bisrv.nec
index 3 -> pwsso.occ
index 4 -> gpapi.bvs   # mapper screen
```

GB300 then continues with at least one additional resource (`fhshl.skb`), reflecting the later/expanded menu branch.

This is now direct binary evidence that the working GB300 mapper retained the exact same position-5 pause-menu resource lineage as XGO's dormant screen.

## GB300 global-pointer value

Cross-checking known libretro callback globals from the public multicore linker map against GP-relative accesses yields:

```text
GB300 stock $gp = 0x80c65d78
```

For example:

```text
gfn_state_load = 0x80c5ffb8
0x80c5ffb8 - 0x80c65d78 = -24000
```

and stock libretro code contains GP-relative accesses at `-24000(gp)` in the expected runtime region.

This gives a stable base for resolving GB300 global variables while lifting the native mapper.

## Important negative result

Simple direct address-xref scans do **not** find code materializing the exact mapper pointer-table entry addresses. That indicates the resource table is reached through an indirect/table-indexed path rather than each UI function embedding absolute asset addresses.

This explains why string-xref-only archaeology was insufficient and shifts the lift toward:

1. identify the pause-menu resource-table indexer;
2. trace its index-4 dispatch/state path;
3. identify mapper state globals through GP-relative accesses;
4. locate `KeyMapInfo.kmp` persistence through call/data flow rather than literal-string xrefs alone.

## Current binary-comparison result

A first normalized-opcode comparison against XGO functions shows that naive short-signature matching produces false positives; later GB300 code has diverged enough that function identity must be established structurally.

The correct discriminator set is now:

- position-5 pause-menu resource-table use;
- six physical-button states;
- 4-byte mapping-record arithmetic;
- logical target + turbo state;
- `KeyMapInfo.kmp` persistence;
- mapper-specific grouped resources;
- calls into the same frontend/input/render service family.

## Next lift target

The immediate target is the GB300 code that indexes the pause-menu table around `0x806ced80` and the action dispatch associated with index 4. Once isolated, compare that state machine against XGO's hardware-proven hidden index-4 path and adapt only the editor behavior while retaining XGO's per-ROM `.kmp` writer.
